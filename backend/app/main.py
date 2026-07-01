from pathlib import Path
from uuid import uuid4
from typing import Annotated
from uuid import UUID
from email.message import EmailMessage
import json
import os
import re
import secrets
import smtplib
import time
import urllib.error
import urllib.request

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, EmailStr

from .auth import admin_user, agent_user, create_token, current_user, hash_password, is_master_admin, public_user, verify_password
from .config import APP_ENV, OPENAI_API_KEY, SMTP_FROM, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER, UPLOAD_DIR
from .db import execute, fetch_all, fetch_one


UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_AVATAR_BYTES = 5 * 1024 * 1024
MAX_DOCUMENT_BYTES = 10 * 1024 * 1024
AVATAR_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
RESUME_EXTENSIONS = {".pdf", ".doc", ".docx"}
CERTIFICATE_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}
AVATAR_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
RESUME_MIME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
CERTIFICATE_MIME_TYPES = AVATAR_MIME_TYPES | {"application/pdf"}
RATE_LIMITS: dict[str, list[float]] = {}
RATE_LIMIT_RULES = (
    ("/api/auth/login", 8, 300),
    ("/api/auth/verify-mfa", 8, 300),
    ("/api/auth/register", 5, 300),
    ("/api/auth/verify-registration", 8, 300),
    ("/api/contact", 5, 300),
    ("/api/account/avatar", 20, 3600),
    ("/api/account/documents", 20, 3600),
    ("/api/support/messages", 60, 300),
)

app = FastAPI(title="Rawabet API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://35.174.9.208:5173",
    "http://35.174.9.208",
    "https://35.174.9.208",
    "http://rawabet-sy.com",
    "http://www.rawabet-sy.com",
    "https://rawabet-sy.com",
    "https://www.rawabet-sy.com",
    "https://localhost",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return request.client.host if request.client else "unknown"


def matched_rate_limit(path: str):
    for prefix, limit, window in RATE_LIMIT_RULES:
        if path.startswith(prefix):
            return limit, window
    return None


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    rule = matched_rate_limit(request.url.path)
    if rule:
        limit, window = rule
        now = time.time()
        key = f"{client_ip(request)}:{request.url.path}"
        recent = [item for item in RATE_LIMITS.get(key, []) if now - item < window]
        if len(recent) >= limit:
            return JSONResponse(status_code=429, content={"detail": "Too many requests. Please try again later."})
        recent.append(now)
        RATE_LIMITS[key] = recent
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if APP_ENV in {"production", "prod"}:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


def upload_search_dirs() -> list[Path]:
    configured = [Path(item).expanduser() for item in os.getenv("UPLOAD_FALLBACK_DIRS", "").split(":") if item.strip()]
    sibling_uploads = sorted(UPLOAD_DIR.parent.glob("uploads*"), key=lambda path: path.stat().st_mtime if path.exists() else 0, reverse=True)
    dirs = [UPLOAD_DIR, *configured, *sibling_uploads]
    unique_dirs = []
    seen = set()
    for directory in dirs:
        resolved = directory.resolve()
        if resolved in seen or not directory.exists() or not directory.is_dir():
            continue
        seen.add(resolved)
        unique_dirs.append(directory)
    return unique_dirs


def newest_matching_upload(filename: str) -> Path | None:
    match = re.match(r"^([0-9a-fA-F-]{36})_(avatar|resume|certificate)_", Path(filename).name)
    if not match:
        return None
    user_id, kind = match.groups()
    candidates = []
    for directory in upload_search_dirs():
        candidates.extend(path for path in directory.glob(f"{user_id}_{kind}_*") if path.is_file())
    return max(candidates, key=lambda path: path.stat().st_mtime, default=None)


def delete_upload_file(path_or_url: str | None):
    if not path_or_url:
        return
    name = Path(path_or_url).name
    for directory in upload_search_dirs():
        (directory / name).unlink(missing_ok=True)


def delete_user_uploads(user_id: UUID | str, kind: str):
    if kind not in {"avatar", "resume", "certificate"}:
        return
    for directory in upload_search_dirs():
        for path in directory.glob(f"{user_id}_{kind}_*"):
            if path.is_file():
                path.unlink(missing_ok=True)


def looks_like_allowed_file(content: bytes, suffix: str) -> bool:
    if suffix == ".pdf":
        return content.startswith(b"%PDF")
    if suffix in {".jpg", ".jpeg"}:
        return content.startswith(b"\xff\xd8\xff")
    if suffix == ".png":
        return content.startswith(b"\x89PNG\r\n\x1a\n")
    if suffix == ".webp":
        return len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP"
    if suffix in {".doc", ".docx"}:
        return content.startswith(b"PK\x03\x04") or content.startswith(b"\xd0\xcf\x11\xe0")
    return False


def validate_upload(content: bytes, original_name: str, content_type: str | None, kind: str):
    suffix = Path(original_name).suffix.lower()
    if kind == "avatar":
        allowed_extensions, allowed_mimes, max_size = AVATAR_EXTENSIONS, AVATAR_MIME_TYPES, MAX_AVATAR_BYTES
    elif kind == "resume":
        allowed_extensions, allowed_mimes, max_size = RESUME_EXTENSIONS, RESUME_MIME_TYPES, MAX_DOCUMENT_BYTES
    else:
        allowed_extensions, allowed_mimes, max_size = CERTIFICATE_EXTENSIONS, CERTIFICATE_MIME_TYPES, MAX_DOCUMENT_BYTES
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(content) > max_size:
        raise HTTPException(status_code=400, detail="Uploaded file is too large")
    if suffix not in allowed_extensions:
        raise HTTPException(status_code=400, detail="File type is not allowed")
    if content_type and content_type not in allowed_mimes:
        raise HTTPException(status_code=400, detail="File content type is not allowed")
    if not looks_like_allowed_file(content, suffix):
        raise HTTPException(status_code=400, detail="File signature does not match the expected type")


@app.get("/uploads/{filename:path}")
def serve_upload(filename: str):
    safe_name = Path(filename).name
    if not safe_name or safe_name in {".", ".."}:
        raise HTTPException(status_code=404, detail="File not found")
    for directory in upload_search_dirs():
        candidate = directory / safe_name
        if candidate.is_file():
            return FileResponse(candidate)
    fallback = newest_matching_upload(safe_name)
    if fallback:
        return FileResponse(fallback)
    raise HTTPException(status_code=404, detail="File not found")


def ensure_runtime_schema():
    for sql in (
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS phone TEXT",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS dob DATE",
        "ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check",
        "ALTER TABLE users ADD CONSTRAINT users_role_check CHECK (role IN ('member', 'recruiter', 'company', 'admin', 'agent', 'master_admin'))",
        "ALTER TABLE pending_registrations ADD COLUMN IF NOT EXISTS phone TEXT",
        "ALTER TABLE pending_registrations ADD COLUMN IF NOT EXISTS dob DATE",
        "ALTER TABLE pending_registrations DROP CONSTRAINT IF EXISTS pending_registrations_role_check",
        "ALTER TABLE pending_registrations ADD CONSTRAINT pending_registrations_role_check CHECK (role IN ('member', 'recruiter', 'company', 'admin', 'agent', 'master_admin'))",
        """
        CREATE TABLE IF NOT EXISTS mfa_challenges (
          id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
          user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          otp_hash TEXT NOT NULL,
          expires_at TIMESTAMPTZ NOT NULL,
          used_at TIMESTAMPTZ,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """,
        "CREATE INDEX IF NOT EXISTS idx_mfa_challenges_user ON mfa_challenges(user_id)",
        "CREATE SEQUENCE IF NOT EXISTS jobs_job_number_seq START WITH 1001",
        "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS job_number INTEGER",
        "UPDATE jobs SET job_number = nextval('jobs_job_number_seq') WHERE job_number IS NULL",
        "SELECT setval('jobs_job_number_seq', GREATEST(1000, COALESCE((SELECT MAX(job_number) FROM jobs), 1000)))",
        "ALTER TABLE jobs ALTER COLUMN job_number SET DEFAULT nextval('jobs_job_number_seq')",
        "ALTER SEQUENCE jobs_job_number_seq OWNED BY jobs.job_number",
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_job_number ON jobs(job_number)",
        "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS screening_questions JSONB NOT NULL DEFAULT '[]'::jsonb",
        "ALTER TABLE applications ADD COLUMN IF NOT EXISTS screening_answers JSONB NOT NULL DEFAULT '[]'::jsonb",
        "ALTER TABLE interviews DROP CONSTRAINT IF EXISTS interviews_status_check",
        "ALTER TABLE interviews ADD CONSTRAINT interviews_status_check CHECK (status IN ('scheduled', 'completed', 'cancelled', 'accepted', 'rejected'))",
        """
        CREATE TABLE IF NOT EXISTS agent_profile_shares (
          id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
          agent_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
          shared_by UUID REFERENCES users(id) ON DELETE SET NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          UNIQUE(agent_id, application_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS agent_user_shares (
          id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
          agent_id UUID NOT NULL,
          user_id UUID NOT NULL,
          shared_by UUID,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          UNIQUE(agent_id, user_id)
        )
        """,
    ):
        try:
            execute(sql)
        except Exception:
            pass


ensure_runtime_schema()


PENDING_META_SEPARATOR = "\nRAWABET_PENDING_META:"


def has_table_column(table_name: str, column_name: str) -> bool:
    row = fetch_one(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s AND column_name = %s
        """,
        (table_name, column_name),
    )
    return bool(row)


def has_table(table_name: str) -> bool:
    row = fetch_one("SELECT to_regclass(%s) AS table_name", (f"public.{table_name}",))
    return bool(row and row.get("table_name"))


def pack_pending_otp_hash(otp_hash: str, phone: str, dob: str | None) -> str:
    metadata = json.dumps({"phone": phone, "dob": dob}, separators=(",", ":"))
    return f"{otp_hash}{PENDING_META_SEPARATOR}{metadata}"


def unpack_pending_otp_hash(value: str | None) -> tuple[str, dict]:
    if not value:
        return "", {}
    otp_hash, separator, metadata = value.partition(PENDING_META_SEPARATOR)
    if not separator:
        return value, {}
    try:
        return otp_hash, json.loads(metadata)
    except json.JSONDecodeError:
        return otp_hash, {}


class RegisterBody(BaseModel):
    fullName: str
    email: EmailStr
    phone: str
    dob: str
    password: str
    role: str = "member"


class LoginBody(BaseModel):
    email: EmailStr
    password: str


class VerifyRegistrationBody(BaseModel):
    email: EmailStr
    otp: str


class VerifyMfaBody(BaseModel):
    challengeId: UUID
    otp: str


class ProfileBody(BaseModel):
    fullName: str
    phone: str | None = None
    dob: str | None = None
    headline: str | None = None
    location: str | None = None
    about: str | None = None
    skills: list[str] = []
    languages: list[str] = ["English", "Arabic"]


class ExperienceBody(BaseModel):
    title: str
    company: str
    location: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    isCurrent: bool = False
    description: str | None = None


class AdminUserPatch(BaseModel):
    fullName: str | None = None
    email: EmailStr | None = None
    newPassword: str | None = None
    phone: str | None = None
    dob: str | None = None
    headline: str | None = None
    location: str | None = None
    role: str | None = None
    plan: str | None = None
    status: str | None = None


class AdminCreateUserBody(BaseModel):
    fullName: str
    email: EmailStr
    password: str
    phone: str | None = None
    dob: str | None = None
    headline: str | None = None
    location: str | None = None
    role: str = "member"
    plan: str = "free"
    status: str = "active"


class AdminProfilePatch(AdminUserPatch):
    about: str | None = None
    skills: list[str] | None = None


class JobBody(BaseModel):
    companyName: str
    title: str
    category: str = "General"
    location: str
    type: str = "Full-time"
    salaryRange: str | None = None
    description: str | None = None
    status: str = "active"
    screeningQuestions: list[str] = []


class ApplyBody(BaseModel):
    answers: list[dict[str, str]] = []


class InterviewBody(BaseModel):
    userId: UUID
    jobId: UUID | None = None
    scheduledAt: str
    channel: str = "Video call"
    notes: str | None = None


class ApplicationStatusBody(BaseModel):
    status: str


class InterviewStatusBody(BaseModel):
    status: str


class ApplicationShareBody(BaseModel):
    applicationId: UUID
    agentId: UUID


class UserShareBody(BaseModel):
    userId: UUID
    agentId: UUID


class AgentInterviewBody(BaseModel):
    userId: UUID
    jobId: UUID | None = None
    scheduledAt: str
    channel: str = "Video call"
    notes: str | None = None


class SupportMessageBody(BaseModel):
    message: str
    userId: UUID | None = None


class ClearSupportBody(BaseModel):
    userId: UUID | None = None


class ContactBody(BaseModel):
    name: str
    email: EmailStr
    subject: str | None = None
    message: str


@app.get("/api/health")
def health():
    return {"ok": True, "service": "rawabet-python-api"}


@app.get("/api/support/bot-version")
def support_bot_version():
    return {
        "version": "rawabet-guide-2026-06-28-apply-intents",
        "sample": platform_bot_reply("كيف اتقدم ارشدني"),
    }


def send_plain_email(email: str, subject: str, body: str) -> tuple[bool, str | None]:
    if not SMTP_HOST or not SMTP_PASSWORD or SMTP_PASSWORD == "PUT_GMAIL_APP_PASSWORD_HERE":
        return False, "SMTP is not configured."
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = SMTP_FROM
    message["To"] = email
    message.set_content(body)
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            if SMTP_USER:
                smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.send_message(message)
        return True, None
    except smtplib.SMTPAuthenticationError:
        return False, "Gmail rejected the SMTP login. Use a Google App Password, not your normal Gmail password."
    except smtplib.SMTPException as exc:
        return False, f"SMTP failed: {exc}"
    except OSError as exc:
        return False, f"SMTP connection failed: {exc}"


def send_verification_email(email: str, otp: str) -> tuple[bool, str | None]:
    return send_plain_email(email, "Rawabet verification code", f"Your Rawabet verification code is: {otp}\n\nThis code expires in 15 minutes.")


def send_mfa_email(email: str, otp: str) -> tuple[bool, str | None]:
    return send_plain_email(email, "Rawabet secure sign-in code", f"Your Rawabet secure sign-in code is: {otp}\n\nThis code expires in 10 minutes. If you did not try to sign in, contact the platform administrator immediately.")


@app.post("/api/contact")
def send_contact_message(body: ContactBody):
    name = body.name.strip()
    subject = (body.subject or "Rawabet contact request").strip()
    message = body.message.strip()
    if len(name) < 2:
        raise HTTPException(status_code=400, detail="Please enter your name.")
    if len(message) < 10:
        raise HTTPException(status_code=400, detail="Please enter a message with at least 10 characters.")
    email_sent, email_error = send_plain_email(
        "loutfi.abouzaid@gmail.com",
        f"Rawabet contact: {subject[:80]}",
        (
            "New contact message from Rawabet.\n\n"
            f"Name: {name}\n"
            f"Email: {body.email}\n"
            f"Subject: {subject or '-'}\n\n"
            f"{message}\n"
        ),
    )
    if not email_sent:
        raise HTTPException(status_code=500, detail=email_error or "Could not send contact message.")
    return {"message": "Message sent successfully."}


def send_interview_email(email: str, full_name: str, job: dict | None, scheduled_at: str, channel: str, notes: str | None) -> tuple[bool, str | None]:
    job_line = f"Job: {job['title']} - {job['company_name']} ({job['location']})" if job else "Job: General interview"
    return send_plain_email(
        email,
        "Rawabet interview scheduled",
        (
            f"Hello {full_name},\n\n"
            "Your interview has been scheduled on Rawabet.\n\n"
            f"{job_line}\n"
            f"Time: {scheduled_at}\n"
            f"Channel: {channel}\n"
            f"Notes: {notes or '-'}\n\n"
            "Please log in to Rawabet to review the interview and related job.\n\n"
            "Rawabet Team"
        ),
    )


RAWABET_CONTEXT = """
Rawabet / روابط is a professional employment platform for Arab professionals.
It has a user platform and an admin platform.

User platform:
- Register with full name, email, phone, date of birth, and password.
- Verify registration by email OTP before the account is created.
- Log in only when the account is active or verified; suspended accounts must not log in.
- Use Home to see profile strength, applied jobs count, profile completion shortcuts, admin-posted jobs, and upcoming interviews.
- Use Profile to edit name, phone, date of birth, headline, location, about, skills, profile picture, resume, certificates, and work history.
- Profile picture uploads replace the previous picture.
- Resume uploads replace the previous resume.
- Certificate uploads can add up to five certificates.
- Use Jobs to search job title/company, filter by category and salary, view details, apply, and track application status.
- Applied jobs can be filtered by status, category, salary, and company.
- Support chat lets users ask the bot or request live admin support.
- Clear chat removes the current support conversation.

Admin platform:
- Overview shows analytics for users, jobs posted, applications, outcomes, categories, profile health, pending documents, active jobs, suspended users, and interviews.
- User Management lets admins search users, open a user profile, change plan between free/premium, verify, activate, deactivate/suspend, delete, and view attachments.
- User profile editing lets admins update user information, plan, role, status, about, skills, profile picture, resume, and certificates.
- Job Management lets admins add jobs, edit jobs, delete jobs, search by job number/title/company, and manage job status.
- Applications lets admins review applicants and change application status to submitted, review, interview, accepted, or rejected.
- Interviews lets admins select a user, select a job, schedule date/time, channel, notes, mark application as interview, and send email notification.
- Support Inbox shows users who messaged support, unread counts by user, and lets admin open each chat and reply.

Statuses:
- Application statuses: submitted, review, interview, accepted, rejected.
- User statuses: active, verified, review, suspended.
- Job statuses: active, paused, closed.
- Plans: free, premium.

Bot rules:
- Answer only questions about Rawabet and how to use this platform.
- Prefer clear numbered steps and mention the exact page/menu/button names.
- Use Arabic by default unless the user writes English.
- If a question is outside Rawabet or cannot be answered from this context, ask whether the user wants live support or wants to end the conversation.
"""

LIVE_AGENT_REPLY = "تم إشعار فريق الدعم بطلبك. سيقوم موظف دعم مباشر بالرد عليك من صندوق الدعم."
END_CHAT_REPLY = "حسنا، يمكنك إنهاء المحادثة الآن. إذا احتجت مساعدة لاحقا افتح نافذة الدعم مرة أخرى."
UNKNOWN_REPLY = "لا أملك إجابة مؤكدة عن هذا السؤال داخل معلومات منصة روابط. هل تريد التحدث مع موظف دعم مباشر أم إنهاء المحادثة؟"


def normalize_arabic_text(value: str) -> str:
    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ى": "ي",
        "ة": "ه",
        "ؤ": "و",
        "ئ": "ي",
    }
    normalized = value.lower()
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    return normalized


def contains_any_intent(value: str, stems: list[str]) -> bool:
    normalized = normalize_arabic_text(value)
    return any(stem in normalized for stem in stems)


RAWABET_GUIDES = [
    {
        "terms": ["register", "sign up", "create account", "otp", "verification", "تسجيل", "إنشاء حساب", "حساب جديد", "رمز", "تحقق", "تأكيد"],
        "answer": "لإنشاء حساب في روابط:\n1. من صفحة الدخول اختر إنشاء حساب.\n2. أدخل الاسم الكامل، البريد الإلكتروني، رقم الهاتف، تاريخ الميلاد، وكلمة المرور.\n3. اضغط إنشاء حساب وانتظر ظهور صفحة التحقق.\n4. افتح بريدك وخذ رمز OTP.\n5. أدخل الرمز واضغط تأكيد البريد.\n6. بعد نجاح التحقق يتم إنشاء الحساب ثم تنتقل إلى الصفحة الرئيسية."
    },
    {
        "terms": ["login", "sign in", "suspended", "تسجيل الدخول", "دخول", "موقوف", "معلق"],
        "answer": "لتسجيل الدخول:\n1. افتح صفحة الدخول.\n2. أدخل البريد الإلكتروني وكلمة المرور.\n3. اضغط تسجيل الدخول.\n4. إذا كان الحساب موقوفا فلن يسمح النظام بالدخول ويجب التواصل مع الدعم أو الإدارة.\n5. إذا نسيت بيانات الدخول اطلب مساعدة الدعم المباشر."
    },
    {
        "terms": ["complete profile", "profile strength", "profile", "headline", "about", "skills", "أكمل الملف", "قوة الملف", "الملف", "العنوان المهني", "نبذة", "المهارات"],
        "answer": "لإكمال الملف ورفع قوة الملف:\n1. اضغط الملف أو أكمل الملف من الشريط العلوي.\n2. حدّث الاسم، الهاتف، تاريخ الميلاد، العنوان المهني، الموقع، والنبذة.\n3. أضف المهارات مفصولة بفواصل.\n4. ارفع الصورة الشخصية.\n5. ارفع السيرة الذاتية.\n6. أضف الشهادات إن وجدت.\n7. أضف تاريخ العمل من قسم الخبرات.\n8. اضغط حفظ الملف. قوة الملف تتحسن حسب اكتمال الصورة والسيرة والشهادات والمهارات والخبرات."
    },
    {
        "intent": "profile_photo",
        "stems": ["صور", "فوتو", "بروفايل"],
        "terms": ["profile picture", "avatar", "photo", "صورة", "الصورة", "الصورة الشخصية", "صورتي", "تعديل صورتي", "اغير صورتي", "تغيير صورتي"],
        "answer": "لتغيير الصورة الشخصية:\n1. افتح صفحة الملف أو اضغط أكمل الملف.\n2. في قسم الصورة والسيرة والشهادات اختر الصورة الشخصية.\n3. اختر صورة من جهازك.\n4. يتم رفع الصورة واستبدال أي صورة قديمة تلقائيا.\n5. تظهر الصورة الجديدة في ملفك وفي شاشة الإدارة."
    },
    {
        "intent": "resume",
        "stems": ["سير", "cv"],
        "terms": ["resume", "cv", "سيرة", "السيرة", "السيرة الذاتية", "سيرتي", "تعديل سيرتي", "ارفع سيرتي"],
        "answer": "لرفع السيرة الذاتية:\n1. افتح الملف أو أكمل الملف.\n2. اختر حقل السيرة الذاتية.\n3. ارفع ملف PDF أو DOC أو DOCX.\n4. روابط يحتفظ بسيرة واحدة فقط، لذلك أي رفع جديد يستبدل السيرة السابقة.\n5. يظهر رابط السيرة في مرفقات ملفك ولدى الإدارة."
    },
    {
        "intent": "certificates",
        "stems": ["شهاد", "رخص", "جوايز", "جوائز"],
        "terms": ["certificate", "certificates", "license", "award", "شهادة", "الشهادات", "شهادتي", "شهاداتي", "رخص", "جوائز"],
        "answer": "لإضافة الشهادات:\n1. افتح الملف أو أكمل الملف.\n2. اختر حقل الشهادة.\n3. ارفع ملف PDF أو صورة.\n4. يمكنك إضافة حتى 5 شهادات.\n5. تظهر الشهادات كرابط في المرفقات ويمكن للإدارة مراجعتها أو حذفها من ملف المستخدم."
    },
    {
        "terms": ["work history", "experience", "career", "خبرة", "تاريخ العمل", "الخبرات", "مسار"],
        "answer": "لإضافة تاريخ العمل:\n1. افتح صفحة الملف.\n2. انتقل إلى قسم الخبرات.\n3. أدخل المسمى الوظيفي واسم الشركة.\n4. اضغط إضافة خبرة.\n5. ستظهر الخبرة في ملفك وتساعد في تحسين قوة الملف."
    },
    {
        "terms": ["job", "jobs", "search job", "category", "salary", "filter", "وظيفة", "وظائف", "بحث", "فئة", "راتب", "فلتر"],
        "answer": "للبحث عن وظيفة:\n1. افتح صفحة الوظائف من الشريط العلوي.\n2. استخدم مربع البحث للبحث باسم الوظيفة أو الشركة.\n3. اختر الفئة المناسبة من فلتر الفئات.\n4. اختر نطاق الراتب إذا أردت تضييق النتائج.\n5. اضغط تفاصيل الوظيفة لعرض الوصف والموقع والراتب والنوع.\n6. اضغط تقديم لإرسال طلبك."
    },
    {
        "intent": "apply_job",
        "stems": ["تقدم", "اتقدم", "اقدم", "وظيف", "مناسب", "طلب"],
        "terms": ["apply", "application", "application status", "applied", "guide me apply", "تقديم", "اتقدم", "اقدم", "التقدم", "قدم", "كيف اتقدم", "ارشدني", "مناسبا", "مناسبه", "طلب", "طلبات", "حالة الطلب", "حاله الطلب", "الوظائف المقدمة", "الوظائف المقدمه"],
        "answer": "للتقديم على وظيفة مناسبة:\n1. افتح صفحة الوظائف من الشريط العلوي.\n2. استخدم البحث لكتابة اسم الوظيفة أو الشركة التي تهمك.\n3. استخدم فلتر الفئة ونطاق الراتب لتقليل النتائج حسب اهتمامك.\n4. اضغط تفاصيل الوظيفة لقراءة الوصف، الشركة، الموقع، الراتب، والنوع.\n5. إذا وجدت نفسك مناسبا، اضغط تقديم.\n6. بعد التقديم افتح الوظائف المقدمة فقط لمتابعة حالة الطلب.\n7. الحالات الممكنة هي: تم التقديم، قيد المراجعة، مقابلة، مقبول، أو مرفوض."
    },
    {
        "terms": ["interview", "schedule interview", "مقابلة", "المقابلات", "جدولة"],
        "answer": "بالنسبة للمقابلات:\n1. الإدارة تفتح لوحة الإدارة ثم المقابلات.\n2. تختار المستخدم والوظيفة.\n3. تحدد التاريخ والوقت والقناة وتضيف الملاحظات.\n4. عند الحفظ يتم تحديث حالة الطلب إلى مقابلة.\n5. يصل للمستخدم إشعار بريد بالمقابلة، وتظهر المقابلة في الصفحة الرئيسية وتُميّز الوظيفة."
    },
    {
        "terms": ["support", "chat", "clear chat", "live support", "دعم", "محادثة", "مسح المحادثة", "دعم مباشر"],
        "answer": "لاستخدام الدعم:\n1. اضغط الدعم من الشريط العلوي.\n2. اكتب سؤالك عن منصة روابط.\n3. سيجيبك المساعد عن خطوات استخدام المنصة.\n4. إذا لم يجد جوابا سيعرض خيار التحدث مع دعم مباشر أو إنهاء المحادثة.\n5. لمسح المحادثة اضغط مسح المحادثة، وسيتم حذف رسائل هذه المحادثة فقط.\n6. في لوحة الإدارة تظهر رسائل المستخدمين في صندوق الدعم ويمكن فتح محادثة كل مستخدم والرد عليه."
    },
    {
        "terms": ["admin", "dashboard", "analytics", "reports", "إدارة", "لوحة", "تحليلات", "تقارير"],
        "answer": "لاستخدام لوحة الإدارة:\n1. سجّل الدخول بحساب مدير.\n2. اضغط الإدارة من الشريط العلوي.\n3. من القائمة الجانبية اختر: نظرة عامة، إدارة المستخدمين، إدارة الوظائف، طلبات التقديم، المقابلات، أو صندوق الدعم.\n4. نظرة عامة تعرض تحليلات المستخدمين والوظائف والتقديمات والنتائج والفئات وجودة الملفات.\n5. كل قسم له أدواته الخاصة للتحكم والمتابعة."
    },
    {
        "terms": ["user management", "manage users", "verify", "activate", "deactivate", "delete user", "إدارة المستخدمين", "توثيق", "تفعيل", "إيقاف", "حذف المستخدم"],
        "answer": "لإدارة المستخدمين كمدير:\n1. افتح الإدارة ثم إدارة المستخدمين.\n2. استخدم البحث للعثور على المستخدم.\n3. غيّر الخطة مباشرة من عمود الخطة بين مجاني ومميز.\n4. من قائمة الإجراءات اختر تعديل المستخدم، توثيق، تفعيل، إيقاف، أو حذف.\n5. عند اختيار تعديل المستخدم يتم فتح ملفه لتعديل البيانات والمرفقات والمهارات والنبذة.\n6. المستخدم الموقوف لا يستطيع تسجيل الدخول."
    },
    {
        "terms": ["plan", "premium", "free", "الخطة", "مميز", "مجاني", "بريميوم"],
        "answer": "لتغيير خطة المستخدم:\n1. افتح الإدارة ثم إدارة المستخدمين.\n2. ابحث عن المستخدم المطلوب.\n3. في عمود الخطة اختر مجاني أو مميز.\n4. يتم حفظ التغيير مباشرة.\n5. يمكنك أيضا فتح تعديل المستخدم وتغيير الخطة من داخل ملفه."
    },
    {
        "terms": ["add job", "edit job", "delete job", "manage job", "post job", "job number", "job id", "إضافة وظيفة", "اضافة وظيفة", "أضيف وظيفة", "اضيف وظيفة", "أعدل وظيفة", "اعدل وظيفة", "تعديل وظيفة", "حذف وظيفة", "رقم الوظيفة", "إدارة الوظائف", "ادارة الوظائف"],
        "answer": "لإدارة الوظائف كمدير:\n1. افتح الإدارة ثم إدارة الوظائف.\n2. لإضافة وظيفة، املأ الشركة، المسمى، الفئة، الموقع، الراتب، والوصف ثم اضغط إضافة وظيفة.\n3. النظام يعرض رقم وظيفة تلقائيا في جدول إدارة الوظائف.\n4. للبحث عن وظيفة استخدم رقم الوظيفة أو المسمى أو الشركة.\n5. من قائمة الإجراءات اختر تعديل الوظيفة أو حذف الوظيفة.\n6. عند التعديل حدّث البيانات والحالة ثم اضغط حفظ."
    },
    {
        "terms": ["application management", "approve", "reject", "review", "طلبات التقديم", "قبول", "رفض", "مراجعة"],
        "answer": "لإدارة طلبات التقديم:\n1. افتح الإدارة ثم طلبات التقديم.\n2. راجع اسم المتقدم والوظيفة والشركة والموقع.\n3. من قائمة الحالة اختر تم التقديم، قيد المراجعة، مقابلة، مقبول، أو مرفوض.\n4. تظهر الحالة الجديدة للمستخدم في الوظائف المقدمة."
    },
    {
        "terms": ["language", "arabic", "english", "لغة", "عربي", "إنجليزي", "english"],
        "answer": "لتغيير اللغة:\n1. اضغط زر اللغة في الشريط العلوي.\n2. إذا كانت الواجهة عربية سيظهر زر EN للتبديل للإنجليزية.\n3. إذا كانت الواجهة إنجليزية سيظهر زر ع للتبديل للعربية.\n4. الشعار يبقى في الجهة اليسرى كما طلبت."
    }
]


def local_platform_reply(question: str) -> str | None:
    lowered = question.lower()
    normalized_question = normalize_arabic_text(question)
    wants_live = ["live agent", "human", "support agent", "موظف", "دعم مباشر", "شخص", "انسان", "إنسان"]
    wants_end = ["end conversation", "close chat", "انهاء", "إنهاء", "انهي", "إنهي", "نهاية"]
    if any(term in lowered or normalize_arabic_text(term) in normalized_question for term in wants_live):
        return LIVE_AGENT_REPLY
    if any(term in lowered or normalize_arabic_text(term) in normalized_question for term in wants_end):
        return END_CHAT_REPLY
    best_guide = None
    best_score = 0
    for guide in RAWABET_GUIDES:
        stem_score = 4 if guide.get("stems") and contains_any_intent(question, guide["stems"]) else 0
        score = stem_score + sum(
            3 if " " in term else 1
            for term in guide["terms"]
            if term in lowered or normalize_arabic_text(term) in normalized_question
        )
        if score > best_score:
            best_score = score
            best_guide = guide
    return best_guide["answer"] if best_guide and best_score else None


def platform_bot_reply(question: str) -> str:
    lowered = question.lower()
    normalized_question = normalize_arabic_text(question)
    platform_terms = [
        "rawabet", "روابط", "platform", "profile", "resume", "cv", "certificate", "job", "jobs", "apply", "application",
        "interview", "support", "admin", "dashboard", "analytics", "plan", "premium", "free", "status", "otp", "register",
        "login", "upload", "attachment", "photo", "avatar", "skill", "experience", "salary", "category", "filter",
        "ملف", "وظيفة", "وظائف", "تقديم", "اتقدم", "اقدم", "التقدم", "قدم", "ارشدني", "مناسب", "مناسبا", "طلب", "طلبات", "حالة", "مقابلة", "دعم", "شهادة", "شهادات", "سيرة",
        "الخطة", "مميز", "مجاني", "الحالة", "تسجيل", "دخول", "تحقق", "رمز", "رفع", "مرفق", "مرفقات", "صورة", "صورتي", "صور",
        "مهارات", "خبرات", "راتب", "فئة", "بحث", "فلتر", "إدارة", "لوحة", "تحليلات", "مستخدم", "مستخدمين"
    ]
    if not any(term in lowered or normalize_arabic_text(term) in normalized_question for term in platform_terms):
        return UNKNOWN_REPLY
    local_reply = local_platform_reply(question)
    if local_reply:
        return local_reply
    fallback = UNKNOWN_REPLY
    if not OPENAI_API_KEY:
        return fallback
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": f"You are Rawabet's in-platform support guide. Answer only questions about Rawabet. Use Arabic by default unless the user writes English. Give practical numbered steps using page/menu/button names from the context. Be specific and helpful. If the user asks about a feature not in the context, reply exactly with: {UNKNOWN_REPLY}\n\n{RAWABET_CONTEXT}"},
            {"role": "user", "content": question},
        ],
        "temperature": 0.2,
        "max_tokens": 520,
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
    except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError):
        return fallback


def jobs_have_job_number_column() -> bool:
    row = fetch_one(
        """
        SELECT EXISTS (
          SELECT 1
          FROM information_schema.columns
          WHERE table_name = 'jobs' AND column_name = 'job_number'
        ) AS exists
        """
    )
    return bool(row and row.get("exists"))


def list_jobs_with_number(active_only: bool = False):
    outer_where = "WHERE status = 'active'" if active_only else ""
    if jobs_have_job_number_column():
        return fetch_all(
            f"""
            SELECT id, job_number, company_name, title, category, location, type, salary_range, description, status, created_at,
                   COALESCE(screening_questions, '[]'::jsonb) AS screening_questions
            FROM jobs
            {outer_where}
            ORDER BY created_at DESC
            """
        )
    return fetch_all(
        f"""
        SELECT *
        FROM (
          SELECT id,
            (1000 + ROW_NUMBER() OVER (ORDER BY created_at ASC))::int AS job_number,
            company_name, title, category, location, type, salary_range, description, status, created_at,
            COALESCE(screening_questions, '[]'::jsonb) AS screening_questions
          FROM jobs
        ) numbered_jobs
        {outer_where}
        ORDER BY created_at DESC
        """
    )


def calculate_profile_strength(user_id: UUID | str) -> int:
    data = fetch_one(
        """
        SELECT
          u.avatar_url,
          u.headline,
          u.location,
          COALESCE(p.about, '') AS about,
          COALESCE(array_length(p.skills, 1), 0) AS skill_count,
          EXISTS (SELECT 1 FROM documents WHERE user_id = u.id AND kind = 'resume') AS has_resume,
          EXISTS (SELECT 1 FROM documents WHERE user_id = u.id AND kind = 'certificate') AS has_certificate,
          EXISTS (SELECT 1 FROM experiences WHERE user_id = u.id) AS has_experience
        FROM users u
        LEFT JOIN profiles p ON p.user_id = u.id
        WHERE u.id = %s
        """,
        (user_id,),
    )
    if not data:
        return 0
    strength = 0
    strength += 15 if data.get("avatar_url") else 0
    strength += 20 if data.get("has_resume") else 0
    strength += 15 if data.get("has_certificate") else 0
    strength += min(15, int(data.get("skill_count") or 0) * 5)
    strength += 10 if data.get("headline") else 0
    strength += 10 if data.get("about") else 0
    strength += 5 if data.get("location") else 0
    strength += 10 if data.get("has_experience") else 0
    return min(100, strength)


def sync_profile_strength(user_id: UUID | str) -> int:
    strength = calculate_profile_strength(user_id)
    execute(
        """
        INSERT INTO profiles (user_id, about, skills, profile_strength, updated_at)
        VALUES (%s, '', '{}', %s, NOW())
        ON CONFLICT (user_id) DO UPDATE
        SET profile_strength = EXCLUDED.profile_strength,
            updated_at = NOW()
        """,
        (user_id, strength),
    )
    return strength


@app.post("/api/auth/register")
def register(body: RegisterBody):
    if body.role != "member":
        raise HTTPException(status_code=403, detail="Privileged accounts must be created by an administrator")
    existing = fetch_one("SELECT id, email_verified, status FROM users WHERE email = %s", (body.email.lower(),))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    otp = f"{secrets.randbelow(1000000):06d}"
    pending_has_contact_columns = has_table_column("pending_registrations", "phone") and has_table_column("pending_registrations", "dob")
    otp_hash = hash_password(otp)
    if pending_has_contact_columns:
        execute(
            """
            INSERT INTO pending_registrations (full_name, email, phone, dob, password_hash, role, otp_hash, expires_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,NOW() + interval '15 minutes')
            ON CONFLICT (email) DO UPDATE
            SET full_name = EXCLUDED.full_name,
                phone = EXCLUDED.phone,
                dob = EXCLUDED.dob,
                password_hash = EXCLUDED.password_hash,
                role = EXCLUDED.role,
                otp_hash = EXCLUDED.otp_hash,
                expires_at = EXCLUDED.expires_at,
                created_at = NOW()
            """,
            (body.fullName, body.email.lower(), body.phone, body.dob or None, hash_password(body.password), body.role, otp_hash),
        )
    else:
        execute(
            """
            INSERT INTO pending_registrations (full_name, email, password_hash, role, otp_hash, expires_at)
            VALUES (%s,%s,%s,%s,%s,NOW() + interval '15 minutes')
            ON CONFLICT (email) DO UPDATE
            SET full_name = EXCLUDED.full_name,
                password_hash = EXCLUDED.password_hash,
                role = EXCLUDED.role,
                otp_hash = EXCLUDED.otp_hash,
                expires_at = EXCLUDED.expires_at,
                created_at = NOW()
            """,
            (body.fullName, body.email.lower(), hash_password(body.password), body.role, pack_pending_otp_hash(otp_hash, body.phone, body.dob or None)),
        )
    email_sent, email_error = send_verification_email(body.email.lower(), otp)
    response = {"ok": True, "needsVerification": True, "emailSent": email_sent, "message": "Check your email for the verification code."}
    if not email_sent:
        response["devOtp"] = otp
        response["message"] = f"{email_error} Use the displayed development OTP to verify this account."
    return response


@app.post("/api/auth/verify-registration")
def verify_registration(body: VerifyRegistrationBody):
    pending = fetch_one(
        """
        SELECT *
        FROM pending_registrations
        WHERE email = %s AND expires_at > NOW()
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (body.email.lower(),),
    )
    otp_hash, pending_metadata = unpack_pending_otp_hash(pending["otp_hash"] if pending else None)
    if not pending or not verify_password(body.otp, otp_hash):
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    if fetch_one("SELECT id FROM users WHERE email = %s", (pending["email"],)):
        execute("DELETE FROM pending_registrations WHERE id = %s", (pending["id"],))
        raise HTTPException(status_code=409, detail="Email already registered")
    verified_user = execute(
        """
        INSERT INTO users (full_name, email, phone, dob, password_hash, role, status, email_verified)
        VALUES (%s,%s,%s,%s,%s,%s,'active',true)
        RETURNING id, full_name, email, phone, dob, role, plan, status, headline, location, avatar_url
        """,
        (
            pending["full_name"],
            pending["email"],
            pending.get("phone") or pending_metadata.get("phone"),
            pending.get("dob") or pending_metadata.get("dob"),
            pending["password_hash"],
            pending["role"],
        ),
    )
    execute("INSERT INTO profiles (user_id, about, skills, profile_strength) VALUES (%s, '', '{}', 0)", (verified_user["id"],))
    sync_profile_strength(verified_user["id"])
    execute("DELETE FROM pending_registrations WHERE id = %s", (pending["id"],))
    return {"user": public_user(verified_user), "token": create_token(verified_user)}


@app.post("/api/auth/login")
def login(body: LoginBody):
    user = fetch_one("SELECT * FROM users WHERE email = %s", (body.email.lower(),))
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.get("email_verified"):
        raise HTTPException(status_code=403, detail="Please verify your email before signing in")
    if user.get("status") == "suspended":
        raise HTTPException(status_code=403, detail="This account is suspended")
    if user["role"] in {"admin", "agent", "master_admin"} or is_master_admin(user):
        otp = f"{secrets.randbelow(1000000):06d}"
        challenge = execute(
            """
            INSERT INTO mfa_challenges (user_id, otp_hash, expires_at)
            VALUES (%s,%s,NOW() + interval '10 minutes')
            RETURNING id
            """,
            (user["id"], hash_password(otp)),
        )
        email_sent, email_error = send_mfa_email(user["email"], otp)
        response = {
            "mfaRequired": True,
            "challengeId": str(challenge["id"]),
            "emailSent": email_sent,
            "message": "Enter the verification code sent to your email.",
        }
        if not email_sent and APP_ENV not in {"production", "prod"}:
            response["devOtp"] = otp
            response["message"] = f"{email_error} Use the displayed development OTP to complete sign-in."
        elif not email_sent:
            raise HTTPException(status_code=503, detail="Could not send sign-in verification code. Contact administrator.")
        return response
    execute("UPDATE users SET last_active_at = NOW() WHERE id = %s", (user["id"],))
    return {"user": public_user(user), "token": create_token(user)}


@app.post("/api/auth/verify-mfa")
def verify_mfa(body: VerifyMfaBody):
    challenge = fetch_one(
        """
        SELECT
          m.id AS challenge_id,
          m.otp_hash,
          m.expires_at,
          m.used_at,
          u.id,
          u.full_name,
          u.email,
          u.phone,
          u.dob,
          u.role,
          u.plan,
          u.status,
          u.headline,
          u.location,
          u.avatar_url
        FROM mfa_challenges m
        JOIN users u ON u.id = m.user_id
        WHERE m.id = %s AND m.used_at IS NULL AND m.expires_at > NOW()
        """,
        (body.challengeId,),
    )
    if not challenge or not verify_password(body.otp, challenge["otp_hash"]):
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    if challenge.get("status") == "suspended":
        raise HTTPException(status_code=403, detail="This account is suspended")
    execute("UPDATE mfa_challenges SET used_at = NOW() WHERE id = %s", (body.challengeId,))
    execute("UPDATE users SET last_active_at = NOW() WHERE id = %s", (challenge["id"],))
    return {"user": public_user(challenge), "token": create_token(challenge)}


@app.get("/api/auth/login")
def login_get_hint():
    return {"detail": "Login requires the Rawabet frontend form. Open http://35.174.9.208:5173 and sign in there."}


@app.get("/api/account")
def me(user: Annotated[dict, Depends(current_user)]):
    sync_profile_strength(user["id"])
    profile = fetch_one("SELECT about, skills, languages, profile_strength FROM profiles WHERE user_id = %s", (user["id"],))
    experiences = fetch_all("SELECT * FROM experiences WHERE user_id = %s ORDER BY start_date DESC NULLS LAST", (user["id"],))
    education = fetch_all("SELECT * FROM education WHERE user_id = %s ORDER BY end_year DESC NULLS LAST", (user["id"],))
    documents = fetch_all(
        """
        SELECT id, kind, file_name, mime_type, file_size, verification_status, created_at,
          '/uploads/' || split_part(file_path, '/', array_length(string_to_array(file_path, '/'), 1)) AS file_url
        FROM documents
        WHERE user_id = %s
        ORDER BY created_at DESC
        """,
        (user["id"],),
    )
    job_number_select = "j.job_number" if jobs_have_job_number_column() else "NULL::integer AS job_number"
    applications = fetch_all(
        f"""
        SELECT a.id, a.status, a.created_at, COALESCE(a.screening_answers, '[]'::jsonb) AS screening_answers,
          j.id AS job_id, {job_number_select}, j.company_name, j.title, j.category, j.location, j.type, j.salary_range, j.description,
          j.status AS job_status, COALESCE(j.screening_questions, '[]'::jsonb) AS screening_questions
        FROM applications a
        JOIN jobs j ON j.id = a.job_id
        WHERE a.user_id = %s
        ORDER BY a.created_at DESC
        """,
        (user["id"],),
    )
    interviews = fetch_all(
        """
        SELECT i.id, i.job_id, i.scheduled_at, i.channel, i.notes, i.status,
          j.title AS job_title, j.company_name, j.location, j.salary_range
        FROM interviews i
        JOIN applications a ON a.user_id = i.user_id AND a.job_id = i.job_id AND a.status = 'interview'
        LEFT JOIN jobs j ON j.id = i.job_id
        WHERE i.user_id = %s AND i.status = 'scheduled' AND i.scheduled_at >= NOW()
        ORDER BY i.scheduled_at ASC
        """,
        (user["id"],),
    )
    stats = fetch_one(
        """
        SELECT
          (SELECT COUNT(*)::int FROM profile_views WHERE profile_user_id = %s) AS profile_views,
          (
            SELECT COUNT(*)::int
            FROM connections
            WHERE status = 'accepted'
              AND (requester_id = %s OR addressee_id = %s)
          ) AS connections
        """,
        (user["id"], user["id"], user["id"]),
    )
    return {"user": public_user(user), "profile": profile, "experiences": experiences, "education": education, "documents": documents, "applications": applications, "interviews": interviews, "stats": stats}


@app.put("/api/account/profile")
def update_profile(body: ProfileBody, user: Annotated[dict, Depends(current_user)]):
    execute(
        "UPDATE users SET full_name = %s, phone = %s, dob = %s, headline = %s, location = %s WHERE id = %s",
        (body.fullName, body.phone, body.dob or None, body.headline, body.location, user["id"]),
    )
    execute(
        """
        INSERT INTO profiles (user_id, about, skills, languages, profile_strength, updated_at)
        VALUES (%s,%s,%s,%s,%s,NOW())
        ON CONFLICT (user_id) DO UPDATE
        SET about = EXCLUDED.about, skills = EXCLUDED.skills, languages = EXCLUDED.languages,
            profile_strength = EXCLUDED.profile_strength, updated_at = NOW()
        """,
        (user["id"], body.about, body.skills, body.languages, calculate_profile_strength(user["id"])),
    )
    sync_profile_strength(user["id"])
    return {"ok": True}


@app.post("/api/account/experience", status_code=201)
def add_experience(body: ExperienceBody, user: Annotated[dict, Depends(current_user)]):
    experience = execute(
        """
        INSERT INTO experiences (user_id, title, company, location, start_date, end_date, is_current, description)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING *
        """,
        (user["id"], body.title, body.company, body.location, body.startDate, body.endDate, body.isCurrent, body.description),
    )
    sync_profile_strength(user["id"])
    return experience


@app.post("/api/account/documents", status_code=201)
async def upload_document(
    user: Annotated[dict, Depends(current_user)],
    kind: Annotated[str, Form()] = "resume",
    file: UploadFile = File(...),
):
    safe_kind = "certificate" if kind == "certificate" else "resume"
    if safe_kind == "resume":
        old_documents = fetch_all("SELECT id, file_path FROM documents WHERE user_id = %s AND kind = 'resume'", (user["id"],))
        for old_document in old_documents:
            delete_upload_file(old_document.get("file_path"))
        execute("DELETE FROM documents WHERE user_id = %s AND kind = 'resume'", (user["id"],))
        delete_user_uploads(user["id"], "resume")
    else:
        certificate_count = fetch_one("SELECT COUNT(*)::int AS count FROM documents WHERE user_id = %s AND kind = 'certificate'", (user["id"],))["count"]
        if certificate_count >= 5:
            raise HTTPException(status_code=400, detail="You can upload up to 5 certificates")

    original_name = file.filename or safe_kind
    suffix = Path(original_name).suffix.lower()
    content = await file.read()
    validate_upload(content, original_name, file.content_type, safe_kind)
    target = UPLOAD_DIR / f"{user['id']}_{safe_kind}_{uuid4().hex}{suffix}"
    target.write_bytes(content)
    file_url = f"/uploads/{target.name}"
    document = execute(
        """
        INSERT INTO documents (user_id, kind, file_name, file_path, mime_type, file_size)
        VALUES (%s,%s,%s,%s,%s,%s)
        RETURNING id, kind, file_name, mime_type, file_size, verification_status, created_at, %s AS file_url
        """,
        (user["id"], safe_kind, original_name, str(target), file.content_type, len(content), file_url),
    )
    sync_profile_strength(user["id"])
    return document


@app.post("/api/account/avatar")
async def upload_avatar(user: Annotated[dict, Depends(current_user)], file: UploadFile = File(...)):
    original_name = file.filename or "avatar.jpg"
    suffix = Path(original_name).suffix.lower() or ".jpg"
    if not Path(original_name).suffix:
        original_name = f"{original_name}{suffix}"
    content = await file.read()
    validate_upload(content, original_name, file.content_type, "avatar")
    delete_upload_file(user.get("avatar_url"))
    delete_user_uploads(user["id"], "avatar")
    target = UPLOAD_DIR / f"{user['id']}_avatar_{uuid4().hex}{suffix}"
    target.write_bytes(content)
    avatar_url = f"/uploads/{target.name}"
    updated = execute(
        """
        UPDATE users
        SET avatar_url = %s
        WHERE id = %s
        RETURNING id, full_name, email, role, plan, status, headline, location, avatar_url
        """,
        (avatar_url, user["id"]),
    )
    sync_profile_strength(user["id"])
    return {"user": public_user(updated)}


@app.get("/api/jobs")
def list_jobs(user: Annotated[dict, Depends(current_user)]):
    return list_jobs_with_number(active_only=True)


@app.get("/api/admin/jobs")
def list_admin_jobs(user: Annotated[dict, Depends(admin_user)]):
    return list_jobs_with_number()


@app.post("/api/jobs/{job_id}/apply", status_code=201)
def apply_to_job(job_id: UUID, body: ApplyBody, user: Annotated[dict, Depends(current_user)]):
    job = fetch_one("SELECT id, COALESCE(screening_questions, '[]'::jsonb) AS screening_questions FROM jobs WHERE id = %s AND status = 'active'", (job_id,))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    questions = job.get("screening_questions") or []
    answers_by_question = {str(item.get("question", "")).strip(): str(item.get("answer", "")).strip() for item in body.answers}
    missing = [question for question in questions if not answers_by_question.get(str(question).strip())]
    if missing:
        raise HTTPException(status_code=400, detail="Please answer all application questions")
    answers = [{"question": str(question), "answer": answers_by_question.get(str(question).strip(), "")} for question in questions]
    execute(
        """
        INSERT INTO applications (job_id, user_id, screening_answers)
        VALUES (%s,%s,%s::jsonb)
        ON CONFLICT (job_id, user_id) DO UPDATE
        SET screening_answers = EXCLUDED.screening_answers
        """,
        (job_id, user["id"], json.dumps(answers)),
    )
    return {"ok": True}


@app.get("/api/admin/applications")
def list_admin_applications(user: Annotated[dict, Depends(admin_user)]):
    return fetch_all(
        """
        SELECT
          a.id, a.status, a.created_at, COALESCE(a.screening_answers, '[]'::jsonb) AS screening_answers,
          u.id AS user_id, u.full_name, u.email, u.headline, u.avatar_url,
          j.id AS job_id, j.title AS job_title, j.company_name, j.location,
          COALESCE(j.screening_questions, '[]'::jsonb) AS screening_questions
        FROM applications a
        JOIN users u ON u.id = a.user_id
        JOIN jobs j ON j.id = a.job_id
        ORDER BY a.created_at DESC
        """
    )


@app.patch("/api/admin/applications/{application_id}")
def update_admin_application(application_id: UUID, body: ApplicationStatusBody, user: Annotated[dict, Depends(admin_user)]):
    allowed = {"submitted", "review", "interview", "accepted", "rejected"}
    if body.status not in allowed:
        raise HTTPException(status_code=400, detail="Invalid application status")
    updated = execute("UPDATE applications SET status = %s WHERE id = %s RETURNING id, user_id, job_id", (body.status, application_id))
    if not updated:
        raise HTTPException(status_code=404, detail="Application not found")
    if body.status != "interview":
        execute(
            """
            UPDATE interviews
            SET status = 'cancelled'
            WHERE user_id = %s AND job_id = %s AND status = 'scheduled'
            """,
            (updated["user_id"], updated["job_id"]),
        )
    return {"ok": True}


@app.post("/api/admin/application-shares", status_code=201)
def share_application_with_agent(body: ApplicationShareBody, user: Annotated[dict, Depends(admin_user)]):
    agent = fetch_one("SELECT id FROM users WHERE id = %s AND role = 'agent'", (body.agentId,))
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    application = fetch_one("SELECT id FROM applications WHERE id = %s", (body.applicationId,))
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return execute(
        """
        INSERT INTO agent_profile_shares (agent_id, application_id, shared_by)
        VALUES (%s,%s,%s)
        ON CONFLICT (agent_id, application_id) DO UPDATE
        SET shared_by = EXCLUDED.shared_by, created_at = NOW()
        RETURNING *
        """,
        (body.agentId, body.applicationId, user["id"]),
    )


@app.post("/api/admin/user-shares", status_code=201)
def share_user_with_agent(body: UserShareBody, user: Annotated[dict, Depends(admin_user)]):
    if not has_table("agent_user_shares"):
        raise HTTPException(status_code=503, detail="Agent user sharing table is not ready")
    agent = fetch_one("SELECT id FROM users WHERE id = %s AND role = 'agent'", (body.agentId,))
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    target_user = fetch_one("SELECT id FROM users WHERE id = %s", (body.userId,))
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    return execute(
        """
        INSERT INTO agent_user_shares (agent_id, user_id, shared_by)
        VALUES (%s,%s,%s)
        ON CONFLICT (agent_id, user_id) DO UPDATE
        SET shared_by = EXCLUDED.shared_by, created_at = NOW()
        RETURNING *
        """,
        (body.agentId, body.userId, user["id"]),
    )


@app.get("/api/agent/shares")
def list_agent_shares(user: Annotated[dict, Depends(agent_user)]):
    job_number_select = "j.job_number" if jobs_have_job_number_column() else "NULL::integer AS job_number"
    application_shares = fetch_all(
        f"""
        SELECT
          'application' AS share_type,
          s.id AS share_id,
          s.created_at AS shared_at,
          a.id AS application_id,
          a.status AS application_status,
          a.created_at AS applied_at,
          COALESCE(a.screening_answers, '[]'::jsonb) AS screening_answers,
          u.id AS user_id,
          u.full_name,
          u.email,
          u.phone,
          u.dob,
          u.headline,
          u.location AS user_location,
          u.avatar_url,
          p.about,
          COALESCE(p.skills, '{{}}') AS skills,
          j.id AS job_id,
          {job_number_select},
          j.title AS job_title,
          j.company_name,
          j.category,
          j.location AS job_location,
          j.salary_range,
          COALESCE(j.screening_questions, '[]'::jsonb) AS screening_questions,
          COALESCE(docs.documents, '[]'::jsonb) AS documents,
          COALESCE(exps.experiences, '[]'::jsonb) AS experiences
        FROM agent_profile_shares s
        JOIN applications a ON a.id = s.application_id
        JOIN users u ON u.id = a.user_id
        LEFT JOIN profiles p ON p.user_id = u.id
        JOIN jobs j ON j.id = a.job_id
        LEFT JOIN LATERAL (
          SELECT jsonb_agg(jsonb_build_object(
            'id', d.id,
            'kind', d.kind,
            'file_name', d.file_name,
            'verification_status', d.verification_status,
            'created_at', d.created_at,
            'file_url', '/uploads/' || split_part(d.file_path, '/', array_length(string_to_array(d.file_path, '/'), 1))
          ) ORDER BY d.created_at DESC) AS documents
          FROM documents d
          WHERE d.user_id = u.id
        ) docs ON true
        LEFT JOIN LATERAL (
          SELECT jsonb_agg(jsonb_build_object(
            'id', e.id,
            'title', e.title,
            'company', e.company,
            'location', e.location,
            'start_date', e.start_date,
            'end_date', e.end_date,
            'is_current', e.is_current,
            'description', e.description
          ) ORDER BY e.start_date DESC NULLS LAST) AS experiences
          FROM experiences e
          WHERE e.user_id = u.id
        ) exps ON true
        WHERE s.agent_id = %s
        ORDER BY s.created_at DESC
        """,
        (user["id"],),
    )
    user_shares = []
    if has_table("agent_user_shares"):
        user_shares = fetch_all(
            """
            SELECT
              'user' AS share_type,
              s.id AS share_id,
              s.created_at AS shared_at,
              NULL::uuid AS application_id,
              NULL::text AS application_status,
              NULL::timestamptz AS applied_at,
              '[]'::jsonb AS screening_answers,
              u.id AS user_id,
              u.full_name,
              u.email,
              u.phone,
              u.dob,
              u.headline,
              u.location AS user_location,
              u.avatar_url,
              p.about,
              COALESCE(p.skills, '{}') AS skills,
              NULL::uuid AS job_id,
              NULL::integer AS job_number,
              NULL::text AS job_title,
              NULL::text AS company_name,
              NULL::text AS category,
              NULL::text AS job_location,
              NULL::text AS salary_range,
              '[]'::jsonb AS screening_questions,
              COALESCE(docs.documents, '[]'::jsonb) AS documents,
              COALESCE(exps.experiences, '[]'::jsonb) AS experiences
            FROM agent_user_shares s
            JOIN users u ON u.id = s.user_id
            LEFT JOIN profiles p ON p.user_id = u.id
            LEFT JOIN LATERAL (
              SELECT jsonb_agg(jsonb_build_object(
                'id', d.id,
                'kind', d.kind,
                'file_name', d.file_name,
                'verification_status', d.verification_status,
                'created_at', d.created_at,
                'file_url', '/uploads/' || split_part(d.file_path, '/', array_length(string_to_array(d.file_path, '/'), 1))
              ) ORDER BY d.created_at DESC) AS documents
              FROM documents d
              WHERE d.user_id = u.id
            ) docs ON true
            LEFT JOIN LATERAL (
              SELECT jsonb_agg(jsonb_build_object(
                'id', e.id,
                'title', e.title,
                'company', e.company,
                'location', e.location,
                'start_date', e.start_date,
                'end_date', e.end_date,
                'is_current', e.is_current,
                'description', e.description
              ) ORDER BY e.start_date DESC NULLS LAST) AS experiences
              FROM experiences e
              WHERE e.user_id = u.id
            ) exps ON true
            WHERE s.agent_id = %s
            ORDER BY s.created_at DESC
            """,
            (user["id"],),
        )
    return sorted([*application_shares, *user_shares], key=lambda item: item["shared_at"], reverse=True)


def agent_can_access_application(agent_id: UUID, application_id: UUID):
    return fetch_one(
        """
        SELECT a.id, a.user_id, a.job_id
        FROM applications a
        JOIN agent_profile_shares s ON s.application_id = a.id
        WHERE s.agent_id = %s AND a.id = %s
        """,
        (agent_id, application_id),
    )


def agent_can_access_user_job(agent_id: UUID, user_id: UUID, job_id: UUID | None = None):
    application_match = fetch_one(
        """
        SELECT a.id
        FROM agent_profile_shares s
        JOIN applications a ON a.id = s.application_id
        WHERE s.agent_id = %s
          AND a.user_id = %s
          AND (%s::uuid IS NULL OR a.job_id = %s)
        LIMIT 1
        """,
        (agent_id, user_id, job_id, job_id),
    )
    if application_match:
        return True
    if not has_table("agent_user_shares"):
        return False
    user_match = fetch_one(
        """
        SELECT id
        FROM agent_user_shares
        WHERE agent_id = %s AND user_id = %s
        LIMIT 1
        """,
        (agent_id, user_id),
    )
    return bool(user_match)


@app.patch("/api/agent/applications/{application_id}")
def update_agent_application(application_id: UUID, body: ApplicationStatusBody, user: Annotated[dict, Depends(agent_user)]):
    allowed = {"submitted", "review", "interview", "accepted", "rejected"}
    if body.status not in allowed:
        raise HTTPException(status_code=400, detail="Invalid application status")
    application = agent_can_access_application(user["id"], application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Shared application not found")
    execute("UPDATE applications SET status = %s WHERE id = %s", (body.status, application_id))
    if body.status != "interview":
        execute(
            """
            UPDATE interviews
            SET status = 'cancelled'
            WHERE user_id = %s AND job_id = %s AND status = 'scheduled'
            """,
            (application["user_id"], application["job_id"]),
        )
    return {"ok": True}


@app.get("/api/agent/interviews")
def list_agent_interviews(user: Annotated[dict, Depends(agent_user)]):
    return fetch_all(
        """
        SELECT i.*, u.full_name, u.email, u.headline, u.avatar_url,
          j.title AS job_title, j.company_name, j.location AS job_location
        FROM interviews i
        JOIN users u ON u.id = i.user_id
        LEFT JOIN jobs j ON j.id = i.job_id
        WHERE i.status = 'scheduled'
          AND i.scheduled_at >= NOW()
          AND (
            EXISTS (
              SELECT 1
              FROM agent_profile_shares s
              JOIN applications a ON a.id = s.application_id
              WHERE s.agent_id = %s
                AND a.user_id = i.user_id
                AND (i.job_id IS NULL OR a.job_id = i.job_id)
            )
            OR (
              %s
              AND EXISTS (
                SELECT 1
                FROM agent_user_shares us
                WHERE us.agent_id = %s AND us.user_id = i.user_id
              )
            )
          )
        ORDER BY i.scheduled_at ASC
        """,
        (user["id"], has_table("agent_user_shares"), user["id"]),
    )


@app.patch("/api/agent/interviews/{interview_id}")
def update_agent_interview(interview_id: UUID, body: InterviewStatusBody, user: Annotated[dict, Depends(agent_user)]):
    allowed = {"scheduled", "completed", "cancelled", "accepted", "rejected"}
    if body.status not in allowed:
        raise HTTPException(status_code=400, detail="Invalid interview status")
    existing = fetch_one("SELECT * FROM interviews WHERE id = %s", (interview_id,))
    if not existing or not agent_can_access_user_job(user["id"], existing["user_id"], existing["job_id"]):
        raise HTTPException(status_code=404, detail="Shared interview not found")
    interview = execute(
        """
        UPDATE interviews
        SET status = %s
        WHERE id = %s
        RETURNING id, user_id, job_id, status
        """,
        (body.status, interview_id),
    )
    if body.status in {"accepted", "rejected"} and interview["job_id"]:
        execute(
            "UPDATE applications SET status = %s WHERE user_id = %s AND job_id = %s",
            (body.status, interview["user_id"], interview["job_id"]),
        )
    return {"ok": True}


@app.post("/api/agent/interviews", status_code=201)
def create_agent_interview(body: AgentInterviewBody, user: Annotated[dict, Depends(agent_user)]):
    if not agent_can_access_user_job(user["id"], body.userId, body.jobId):
        raise HTTPException(status_code=404, detail="Shared candidate not found")
    interview = execute(
        """
        INSERT INTO interviews (user_id, admin_id, job_id, scheduled_at, channel, notes)
        VALUES (%s,%s,%s,%s,%s,%s)
        RETURNING *
        """,
        (body.userId, user["id"], body.jobId, body.scheduledAt, body.channel, body.notes),
    )
    if body.jobId:
        execute("UPDATE applications SET status = 'interview' WHERE user_id = %s AND job_id = %s", (body.userId, body.jobId))
    recipient = fetch_one("SELECT full_name, email FROM users WHERE id = %s", (body.userId,))
    job = fetch_one("SELECT title, company_name, location FROM jobs WHERE id = %s", (body.jobId,)) if body.jobId else None
    email_sent = False
    email_error = "Recipient not found."
    recipient_email = None
    if recipient:
        recipient_email = recipient["email"]
        email_sent, email_error = send_interview_email(recipient["email"], recipient["full_name"], job, body.scheduledAt, body.channel, body.notes)
    return {**interview, "emailSent": email_sent, "emailError": email_error, "recipientEmail": recipient_email}


@app.get("/api/admin/overview")
def admin_overview(user: Annotated[dict, Depends(admin_user)]):
    metrics = {
        "users": fetch_one("SELECT COUNT(*)::int AS count FROM users")["count"],
        "verifiedProfiles": fetch_one("SELECT COUNT(*)::int AS count FROM users WHERE status = 'verified'")["count"],
        "activeJobs": fetch_one("SELECT COUNT(*)::int AS count FROM jobs WHERE status = 'active'")["count"],
        "applications": fetch_one("SELECT COUNT(*)::int AS count FROM applications")["count"],
        "pendingDocuments": fetch_one("SELECT COUNT(*)::int AS count FROM documents WHERE verification_status = 'pending'")["count"],
        "suspendedUsers": fetch_one("SELECT COUNT(*)::int AS count FROM users WHERE status = 'suspended'")["count"],
        "pendingInterviews": fetch_one("SELECT COUNT(*)::int AS count FROM interviews WHERE status = 'scheduled'")["count"],
    }
    users_growth = fetch_all(
        """
        SELECT to_char(month, 'Mon') AS label,
          COALESCE(COUNT(u.id), 0)::int AS value
        FROM generate_series(date_trunc('month', NOW()) - interval '5 months', date_trunc('month', NOW()), interval '1 month') AS month
        LEFT JOIN users u ON date_trunc('month', u.created_at) = month
        GROUP BY month
        ORDER BY month
        """
    )
    jobs_posted = fetch_all(
        """
        SELECT to_char(month, 'Mon') AS label,
          COALESCE(COUNT(j.id), 0)::int AS value
        FROM generate_series(date_trunc('month', NOW()) - interval '5 months', date_trunc('month', NOW()), interval '1 month') AS month
        LEFT JOIN jobs j ON date_trunc('month', j.created_at) = month
        GROUP BY month
        ORDER BY month
        """
    )
    monthly_applications = fetch_all(
        """
        SELECT to_char(month, 'Mon') AS label,
          COALESCE(COUNT(a.id), 0)::int AS value
        FROM generate_series(date_trunc('month', NOW()) - interval '5 months', date_trunc('month', NOW()), interval '1 month') AS month
        LEFT JOIN applications a ON date_trunc('month', a.created_at) = month
        GROUP BY month
        ORDER BY month
        """
    )
    application_outcomes = fetch_all(
        """
        SELECT statuses.label, COALESCE(COUNT(a.id), 0)::int AS value
        FROM (
          VALUES
            ('submitted', 'submitted'),
            ('review', 'review'),
            ('interview', 'interview'),
            ('accepted', 'approved'),
            ('rejected', 'rejected')
        ) AS statuses(status, label)
        LEFT JOIN applications a ON a.status = statuses.status
        GROUP BY statuses.status, statuses.label
        ORDER BY CASE statuses.status
          WHEN 'submitted' THEN 1
          WHEN 'review' THEN 2
          WHEN 'interview' THEN 3
          WHEN 'accepted' THEN 4
          WHEN 'rejected' THEN 5
        END
        """
    )
    job_categories = fetch_all(
        """
        SELECT category AS label, COUNT(*)::int AS value
        FROM jobs
        GROUP BY category
        ORDER BY value DESC, category
        LIMIT 8
        """
    )
    profile_health = fetch_all(
        """
        SELECT bucket AS label, COUNT(*)::int AS value
        FROM (
          SELECT CASE
            WHEN profile_strength >= 85 THEN 'excellent'
            WHEN profile_strength >= 55 THEN 'good'
            ELSE 'needs work'
          END AS bucket
          FROM profiles
        ) grouped
        GROUP BY bucket
        ORDER BY bucket
        """
    )
    segments = fetch_all("SELECT role, COUNT(*)::int AS count FROM users GROUP BY role ORDER BY count DESC")
    return {
        "metrics": metrics,
        "analytics": {
            "usersGrowth": users_growth,
            "jobsPosted": jobs_posted,
            "monthlyApplications": monthly_applications,
            "applicationOutcomes": application_outcomes,
            "jobCategories": job_categories,
            "profileHealth": profile_health,
        },
        "segments": segments,
        "reports": [
            {"title": "تقرير نمو المستخدمين", "type": "PDF", "size": "2.4 MB"},
            {"title": "تحليل الوظائف والتقديمات", "type": "XLSX", "size": "840 KB"},
            {"title": "التحقق وجودة الملفات", "type": "PDF", "size": "1.1 MB"},
        ],
    }


@app.get("/api/admin/users")
def admin_users(user: Annotated[dict, Depends(admin_user)], search: str = ""):
    query = f"%{search}%"
    return fetch_all(
        """
        SELECT
          u.id, u.full_name, u.email, u.phone, u.dob, u.role, u.plan, u.status, u.headline, u.location, u.avatar_url, u.created_at, u.last_active_at,
          COALESCE(
            json_agg(
              json_build_object(
                'id', d.id,
                'kind', d.kind,
                'file_name', d.file_name,
                'verification_status', d.verification_status,
                'created_at', d.created_at,
                'file_url', '/uploads/' || split_part(d.file_path, '/', array_length(string_to_array(d.file_path, '/'), 1))
              )
              ORDER BY d.created_at DESC
            ) FILTER (WHERE d.id IS NOT NULL),
            '[]'::json
          ) AS documents
        FROM users u
        LEFT JOIN documents d ON d.user_id = u.id
        WHERE u.full_name ILIKE %s OR u.email ILIKE %s OR u.role ILIKE %s OR u.plan ILIKE %s OR u.status ILIKE %s
        GROUP BY u.id
        ORDER BY u.created_at DESC
        LIMIT 100
        """,
        (query, query, query, query, query),
    )


@app.post("/api/admin/users", status_code=201)
def create_admin_user(body: AdminCreateUserBody, user: Annotated[dict, Depends(admin_user)]):
    allowed_roles = {"member", "agent", "admin", "master_admin"}
    if body.role not in allowed_roles:
        raise HTTPException(status_code=400, detail="Invalid user role")
    if body.role == "master_admin" and not is_master_admin(user):
        raise HTTPException(status_code=403, detail="Only master admin can create master admin accounts")
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if fetch_one("SELECT id FROM users WHERE email = %s", (str(body.email).lower(),)):
        raise HTTPException(status_code=409, detail="Email already registered")
    created_user = execute(
        """
        INSERT INTO users (full_name, email, phone, dob, password_hash, role, plan, status, headline, location, email_verified)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,true)
        RETURNING id, full_name, email, phone, dob, role, plan, status, headline, location, avatar_url, created_at, last_active_at
        """,
        (
            body.fullName,
            str(body.email).lower(),
            body.phone,
            body.dob or None,
            hash_password(body.password),
            body.role,
            body.plan,
            body.status,
            body.headline,
            body.location,
        ),
    )
    execute("INSERT INTO profiles (user_id, about, skills, profile_strength) VALUES (%s, '', '{}', 0) ON CONFLICT (user_id) DO NOTHING", (created_user["id"],))
    sync_profile_strength(created_user["id"])
    return created_user


@app.get("/api/admin/users/{user_id}/profile")
def admin_user_profile(user_id: UUID, user: Annotated[dict, Depends(admin_user)]):
    sync_profile_strength(user_id)
    target_user = fetch_one(
        "SELECT id, full_name, email, phone, dob, role, plan, status, headline, location, avatar_url, created_at, last_active_at FROM users WHERE id = %s",
        (user_id,),
    )
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    profile = fetch_one("SELECT about, skills, languages, profile_strength FROM profiles WHERE user_id = %s", (user_id,))
    experiences = fetch_all("SELECT * FROM experiences WHERE user_id = %s ORDER BY start_date DESC NULLS LAST", (user_id,))
    education = fetch_all("SELECT * FROM education WHERE user_id = %s ORDER BY end_year DESC NULLS LAST", (user_id,))
    documents = fetch_all(
        """
        SELECT id, kind, file_name, mime_type, file_size, verification_status, created_at,
          '/uploads/' || split_part(file_path, '/', array_length(string_to_array(file_path, '/'), 1)) AS file_url
        FROM documents
        WHERE user_id = %s
        ORDER BY created_at DESC
        """,
        (user_id,),
    )
    return {"user": target_user, "profile": profile, "experiences": experiences, "education": education, "documents": documents}


@app.patch("/api/admin/users/{user_id}/profile")
def update_admin_profile(user_id: UUID, body: AdminProfilePatch, user: Annotated[dict, Depends(admin_user)]):
    target_user = fetch_one("SELECT id, email, role FROM users WHERE id = %s", (user_id,))
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    if body.role == "master_admin" and not is_master_admin(user):
        raise HTTPException(status_code=403, detail="Only master admin can assign master admin role")
    if target_user["role"] == "master_admin" and not is_master_admin(user):
        raise HTTPException(status_code=403, detail="Only master admin can edit master admin accounts")
    password_hash = None
    if body.newPassword:
        if len(body.newPassword) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        password_hash = hash_password(body.newPassword)
    updated = execute(
        """
        UPDATE users
        SET full_name = COALESCE(%s, full_name),
            email = COALESCE(%s, email),
            password_hash = COALESCE(%s, password_hash),
            phone = COALESCE(%s, phone),
            dob = COALESCE(%s, dob),
            headline = COALESCE(%s, headline),
            location = COALESCE(%s, location),
            role = COALESCE(%s, role),
            plan = COALESCE(%s, plan),
            status = COALESCE(%s, status)
        WHERE id = %s
        RETURNING id
        """,
        (body.fullName, str(body.email).lower() if body.email else None, password_hash, body.phone, body.dob or None, body.headline, body.location, body.role, body.plan, body.status, user_id),
    )
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    profile = fetch_one("SELECT about, skills, languages FROM profiles WHERE user_id = %s", (user_id,))
    about = body.about if body.about is not None else (profile or {}).get("about", "")
    skills = body.skills if body.skills is not None else (profile or {}).get("skills", [])
    languages = (profile or {}).get("languages", ["English", "Arabic"])
    execute(
        """
        INSERT INTO profiles (user_id, about, skills, languages, profile_strength, updated_at)
        VALUES (%s,%s,%s,%s,%s,NOW())
        ON CONFLICT (user_id) DO UPDATE
        SET about = EXCLUDED.about, skills = EXCLUDED.skills, languages = EXCLUDED.languages,
            profile_strength = EXCLUDED.profile_strength, updated_at = NOW()
        """,
        (user_id, about, skills, languages, calculate_profile_strength(user_id)),
    )
    sync_profile_strength(user_id)
    return {"ok": True}


@app.post("/api/admin/users/{user_id}/documents", status_code=201)
async def upload_admin_document(
    user_id: UUID,
    user: Annotated[dict, Depends(admin_user)],
    kind: Annotated[str, Form()] = "resume",
    file: UploadFile = File(...),
):
    if not fetch_one("SELECT id FROM users WHERE id = %s", (user_id,)):
        raise HTTPException(status_code=404, detail="User not found")
    safe_kind = "certificate" if kind == "certificate" else "resume"
    if safe_kind == "resume":
        old_documents = fetch_all("SELECT file_path FROM documents WHERE user_id = %s AND kind = 'resume'", (user_id,))
        for old_document in old_documents:
            delete_upload_file(old_document.get("file_path"))
        execute("DELETE FROM documents WHERE user_id = %s AND kind = 'resume'", (user_id,))
        delete_user_uploads(user_id, "resume")
    else:
        certificate_count = fetch_one("SELECT COUNT(*)::int AS count FROM documents WHERE user_id = %s AND kind = 'certificate'", (user_id,))["count"]
        if certificate_count >= 5:
            raise HTTPException(status_code=400, detail="You can upload up to 5 certificates")
    original_name = file.filename or safe_kind
    suffix = Path(original_name).suffix.lower()
    content = await file.read()
    validate_upload(content, original_name, file.content_type, safe_kind)
    target = UPLOAD_DIR / f"{user_id}_{safe_kind}_{uuid4().hex}{suffix}"
    target.write_bytes(content)
    file_url = f"/uploads/{target.name}"
    document = execute(
        """
        INSERT INTO documents (user_id, kind, file_name, file_path, mime_type, file_size)
        VALUES (%s,%s,%s,%s,%s,%s)
        RETURNING id, kind, file_name, mime_type, file_size, verification_status, created_at, %s AS file_url
        """,
        (user_id, safe_kind, original_name, str(target), file.content_type, len(content), file_url),
    )
    sync_profile_strength(user_id)
    return document


@app.post("/api/admin/users/{user_id}/avatar")
async def upload_admin_avatar(user_id: UUID, user: Annotated[dict, Depends(admin_user)], file: UploadFile = File(...)):
    target_user = fetch_one("SELECT id, avatar_url FROM users WHERE id = %s", (user_id,))
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    original_name = file.filename or "avatar.jpg"
    suffix = Path(original_name).suffix.lower() or ".jpg"
    if not Path(original_name).suffix:
        original_name = f"{original_name}{suffix}"
    content = await file.read()
    validate_upload(content, original_name, file.content_type, "avatar")
    delete_upload_file(target_user.get("avatar_url"))
    delete_user_uploads(user_id, "avatar")
    target = UPLOAD_DIR / f"{user_id}_avatar_{uuid4().hex}{suffix}"
    target.write_bytes(content)
    avatar_url = f"/uploads/{target.name}"
    execute("UPDATE users SET avatar_url = %s WHERE id = %s", (avatar_url, user_id))
    sync_profile_strength(user_id)
    return {"avatarUrl": avatar_url}


@app.delete("/api/admin/documents/{document_id}")
def delete_admin_document(document_id: UUID, user: Annotated[dict, Depends(admin_user)]):
    document = execute("DELETE FROM documents WHERE id = %s RETURNING user_id, file_path", (document_id,))
    if not document:
        raise HTTPException(status_code=404, detail="Attachment not found")
    delete_upload_file(document.get("file_path"))
    sync_profile_strength(document["user_id"])
    return {"ok": True}


@app.patch("/api/admin/users/{user_id}")
def update_admin_user(user_id: UUID, body: AdminUserPatch, user: Annotated[dict, Depends(admin_user)]):
    target_user = fetch_one("SELECT id, email, role FROM users WHERE id = %s", (user_id,))
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    if body.role == "master_admin" and not is_master_admin(user):
        raise HTTPException(status_code=403, detail="Only master admin can assign master admin role")
    if target_user["role"] == "master_admin" and not is_master_admin(user):
        raise HTTPException(status_code=403, detail="Only master admin can edit master admin accounts")
    password_hash = None
    if body.newPassword:
        if len(body.newPassword) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        password_hash = hash_password(body.newPassword)
    updated = execute(
        """
        UPDATE users
        SET full_name = COALESCE(%s, full_name),
            email = COALESCE(%s, email),
            password_hash = COALESCE(%s, password_hash),
            phone = COALESCE(%s, phone),
            dob = COALESCE(%s, dob),
            headline = COALESCE(%s, headline),
            location = COALESCE(%s, location),
            role = COALESCE(%s, role),
            plan = COALESCE(%s, plan),
            status = COALESCE(%s, status)
        WHERE id = %s
        RETURNING id, full_name, email, phone, dob, role, plan, status, headline, location, created_at, last_active_at
        """,
        (body.fullName, str(body.email).lower() if body.email else None, password_hash, body.phone, body.dob or None, body.headline, body.location, body.role, body.plan, body.status, user_id),
    )
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


@app.delete("/api/admin/users/{user_id}")
def delete_admin_user(user_id: UUID, user: Annotated[dict, Depends(admin_user)]):
    if str(user_id) == str(user["id"]):
        raise HTTPException(status_code=400, detail="You cannot delete your own admin account")
    target_user = fetch_one("SELECT id, email, role, avatar_url FROM users WHERE id = %s", (user_id,))
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    if target_user["role"] in {"admin", "master_admin"} and not is_master_admin(user):
        raise HTTPException(status_code=403, detail="Only master admin can delete admin accounts")
    documents = fetch_all("SELECT file_path FROM documents WHERE user_id = %s", (user_id,))
    for document in documents:
        delete_upload_file(document.get("file_path"))
    delete_upload_file(target_user.get("avatar_url"))
    for kind in ("avatar", "resume", "certificate"):
        delete_user_uploads(user_id, kind)
    deleted = execute("DELETE FROM users WHERE id = %s RETURNING id, email", (user_id,))
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    still_exists = fetch_one("SELECT id FROM users WHERE email = %s", (target_user["email"],))
    return {"ok": True, "deletedEmail": deleted["email"], "emailAvailable": still_exists is None}


@app.post("/api/admin/jobs", status_code=201)
def create_admin_job(body: JobBody, user: Annotated[dict, Depends(admin_user)]):
    questions = [question.strip() for question in body.screeningQuestions if question.strip()]
    return execute(
        """
        INSERT INTO jobs (company_name, title, category, location, type, salary_range, description, status, screening_questions)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
        RETURNING *
        """,
        (body.companyName, body.title, body.category, body.location, body.type, body.salaryRange, body.description, body.status, json.dumps(questions)),
    )


@app.patch("/api/admin/jobs/{job_id}")
def update_admin_job(job_id: UUID, body: JobBody, user: Annotated[dict, Depends(admin_user)]):
    questions = [question.strip() for question in body.screeningQuestions if question.strip()]
    updated = execute(
        """
        UPDATE jobs
        SET company_name = %s,
            title = %s,
            category = %s,
            location = %s,
            type = %s,
            salary_range = %s,
            description = %s,
            status = %s,
            screening_questions = %s::jsonb
        WHERE id = %s
        RETURNING *
        """,
        (body.companyName, body.title, body.category, body.location, body.type, body.salaryRange, body.description, body.status, json.dumps(questions), job_id),
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Job not found")
    return updated


@app.delete("/api/admin/jobs/{job_id}")
def delete_admin_job(job_id: UUID, user: Annotated[dict, Depends(admin_user)]):
    deleted = execute("DELETE FROM jobs WHERE id = %s RETURNING id", (job_id,))
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"ok": True}


@app.get("/api/admin/interviews")
def list_admin_interviews(user: Annotated[dict, Depends(admin_user)]):
    return fetch_all(
        """
        SELECT i.*, u.full_name, u.email, j.title AS job_title, j.company_name, j.location AS job_location
        FROM interviews i
        JOIN users u ON u.id = i.user_id
        LEFT JOIN jobs j ON j.id = i.job_id
        WHERE i.status = 'scheduled' AND i.scheduled_at >= NOW()
        ORDER BY i.scheduled_at ASC
        """
    )


@app.patch("/api/admin/interviews/{interview_id}")
def update_admin_interview(interview_id: UUID, body: InterviewStatusBody, user: Annotated[dict, Depends(admin_user)]):
    allowed = {"scheduled", "completed", "cancelled", "accepted", "rejected"}
    if body.status not in allowed:
        raise HTTPException(status_code=400, detail="Invalid interview status")
    interview = execute(
        """
        UPDATE interviews
        SET status = %s
        WHERE id = %s
        RETURNING id, user_id, job_id, status
        """,
        (body.status, interview_id),
    )
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if body.status in {"accepted", "rejected"} and interview["job_id"]:
        execute(
            "UPDATE applications SET status = %s WHERE user_id = %s AND job_id = %s",
            (body.status, interview["user_id"], interview["job_id"]),
        )
    return {"ok": True}


@app.get("/api/admin/support/threads")
def list_support_threads(user: Annotated[dict, Depends(admin_user)]):
    return fetch_all(
        """
        WITH last_admin AS (
          SELECT user_id, MAX(created_at) AS last_admin_at
          FROM support_messages
          WHERE sender_role = 'admin'
          GROUP BY user_id
        ),
        latest AS (
          SELECT DISTINCT ON (user_id) user_id, sender_role, message, created_at
          FROM support_messages
          ORDER BY user_id, created_at DESC
        )
        SELECT
          u.id AS user_id,
          u.full_name,
          u.email,
          latest.sender_role AS last_sender_role,
          latest.message AS last_message,
          latest.created_at AS last_message_at,
          COUNT(sm.id) FILTER (
            WHERE sm.sender_role = 'user'
              AND sm.created_at > COALESCE(last_admin.last_admin_at, 'epoch'::timestamptz)
          )::int AS unread_count
        FROM users u
        JOIN latest ON latest.user_id = u.id
        LEFT JOIN support_messages sm ON sm.user_id = u.id
        LEFT JOIN last_admin ON last_admin.user_id = u.id
        GROUP BY u.id, u.full_name, u.email, latest.sender_role, latest.message, latest.created_at
        ORDER BY unread_count DESC, latest.created_at DESC
        """
    )


@app.post("/api/admin/interviews", status_code=201)
def create_admin_interview(body: InterviewBody, user: Annotated[dict, Depends(admin_user)]):
    interview = execute(
        """
        INSERT INTO interviews (user_id, admin_id, job_id, scheduled_at, channel, notes)
        VALUES (%s,%s,%s,%s,%s,%s)
        RETURNING *
        """,
        (body.userId, user["id"], body.jobId, body.scheduledAt, body.channel, body.notes),
    )
    if body.jobId:
        execute("UPDATE applications SET status = 'interview' WHERE user_id = %s AND job_id = %s", (body.userId, body.jobId))
    recipient = fetch_one("SELECT full_name, email FROM users WHERE id = %s", (body.userId,))
    job = fetch_one("SELECT title, company_name, location FROM jobs WHERE id = %s", (body.jobId,)) if body.jobId else None
    email_sent = False
    email_error = "Recipient not found."
    recipient_email = None
    if recipient:
        recipient_email = recipient["email"]
        email_sent, email_error = send_interview_email(recipient["email"], recipient["full_name"], job, body.scheduledAt, body.channel, body.notes)
    return {**interview, "emailSent": email_sent, "emailError": email_error, "recipientEmail": recipient_email}


@app.get("/api/support/messages")
def list_support_messages(user: Annotated[dict, Depends(current_user)], user_id: UUID | None = None):
    is_support_admin = user["role"] in {"admin", "master_admin"} or is_master_admin(user)
    target_user_id = user_id if is_support_admin and user_id else user["id"]
    return fetch_all(
        """
        SELECT sm.*, u.full_name, u.email
        FROM support_messages sm
        JOIN users u ON u.id = sm.user_id
        WHERE sm.user_id = %s
        ORDER BY sm.created_at ASC
        """,
        (target_user_id,),
    )


@app.post("/api/support/messages", status_code=201)
def create_support_message(body: SupportMessageBody, user: Annotated[dict, Depends(current_user)]):
    is_support_admin = user["role"] in {"admin", "master_admin"} or is_master_admin(user)
    target_user_id = body.userId if is_support_admin and body.userId else user["id"]
    sender_role = "admin" if is_support_admin else "user"
    message = execute(
        """
        INSERT INTO support_messages (user_id, sender_role, message)
        VALUES (%s,%s,%s)
        RETURNING *
        """,
        (target_user_id, sender_role, body.message),
    )
    bot_reply = None
    if sender_role == "user":
        bot_reply = execute(
            """
            INSERT INTO support_messages (user_id, sender_role, message)
            VALUES (%s,'bot',%s)
            RETURNING *
            """,
            (target_user_id, platform_bot_reply(body.message)),
        )
    return {"message": message, "botReply": bot_reply}


def clear_support_thread(user: dict, user_id: UUID | None = None):
    is_support_admin = user["role"] in {"admin", "master_admin"} or is_master_admin(user)
    target_user_id = user_id if is_support_admin and user_id else user["id"]
    result = fetch_one(
        """
        WITH deleted AS (
          DELETE FROM support_messages
          WHERE user_id = %s
          RETURNING 1
        )
        SELECT COUNT(*)::int AS deleted_count FROM deleted
        """,
        (target_user_id,),
    )
    return {"ok": True, "userId": target_user_id, "deletedCount": result["deleted_count"] if result else 0}


@app.post("/api/support/messages/clear")
def clear_support_messages_post(body: ClearSupportBody, user: Annotated[dict, Depends(current_user)]):
    return clear_support_thread(user, body.userId)


@app.delete("/api/support/messages")
def clear_support_messages(user: Annotated[dict, Depends(current_user)], user_id: UUID | None = None):
    return clear_support_thread(user, user_id)
