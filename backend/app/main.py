from pathlib import Path
from uuid import uuid4
from typing import Annotated
from uuid import UUID
from email.message import EmailMessage
from io import BytesIO
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
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel, EmailStr

from .auth import admin_user, agent_user, create_token, current_user, hash_password, is_master_admin, public_user, verify_password
from .config import APP_ENV, OPENAI_API_KEY, SMTP_FROM, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER, UPLOAD_DIR
from .db import execute, fetch_all, fetch_one

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    REPORTLAB_AVAILABLE = True
    REPORTLAB_IMPORT_ERROR = ""
except Exception as exc:
    REPORTLAB_AVAILABLE = False
    REPORTLAB_IMPORT_ERROR = str(exc)

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_PDF_AVAILABLE = True
except Exception:
    arabic_reshaper = None
    get_display = None
    ARABIC_PDF_AVAILABLE = False


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
    ("/api/support/messages", 500, 300),
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


def resume_count_for(user_id: UUID | str) -> int:
    row = fetch_one("SELECT COUNT(*)::int AS count FROM documents WHERE user_id = %s AND kind = 'resume'", (user_id,))
    return int((row or {}).get("count") or 0)


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
        "ALTER TABLE applications ADD COLUMN IF NOT EXISTS resume_document_id UUID REFERENCES documents(id) ON DELETE SET NULL",
        "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS agency_name TEXT",
        "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS agency_about TEXT",
        "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS website TEXT",
        "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS resume_education TEXT",
        "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS resume_certifications TEXT",
        "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS resume_tools TEXT",
        "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS resume_additional_info TEXT",
        "ALTER TABLE interviews DROP CONSTRAINT IF EXISTS interviews_status_check",
        "ALTER TABLE interviews ADD CONSTRAINT interviews_status_check CHECK (status IN ('scheduled', 'completed', 'cancelled', 'accepted', 'rejected'))",
        """
        CREATE TABLE IF NOT EXISTS courses (
          id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
          user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          added_by UUID REFERENCES users(id) ON DELETE SET NULL,
          title TEXT NOT NULL,
          provider TEXT,
          completion_date DATE,
          certificate_url TEXT,
          notes TEXT,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """,
        "CREATE INDEX IF NOT EXISTS idx_courses_user ON courses(user_id)",
        """
        CREATE TABLE IF NOT EXISTS agent_job_assignments (
          id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
          agent_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
          assigned_by UUID REFERENCES users(id) ON DELETE SET NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          UNIQUE(agent_id, job_id)
        )
        """,
        "CREATE INDEX IF NOT EXISTS idx_agent_job_assignments_agent ON agent_job_assignments(agent_id)",
        "CREATE INDEX IF NOT EXISTS idx_agent_job_assignments_job ON agent_job_assignments(job_id)",
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


def resume_profile_columns_available() -> bool:
    return all(
        has_table_column("profiles", column)
        for column in ("resume_education", "resume_certifications", "resume_tools", "resume_additional_info")
    )


def resume_profile_select_sql() -> str:
    if resume_profile_columns_available():
        return "resume_education, resume_certifications, resume_tools, resume_additional_info"
    return "NULL::text AS resume_education, NULL::text AS resume_certifications, NULL::text AS resume_tools, NULL::text AS resume_additional_info"


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
    resumeEducation: str | None = None
    resumeCertifications: str | None = None
    resumeTools: str | None = None
    resumeAdditionalInfo: str | None = None


class ExperienceBody(BaseModel):
    title: str
    company: str
    location: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    isCurrent: bool = False
    description: str | None = None


class EducationBody(BaseModel):
    school: str
    degree: str
    field: str | None = None
    startYear: int | str | None = None
    endYear: int | str | None = None


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
    resumeDocumentId: UUID | None = None


class ResumeBuilderBody(BaseModel):
    summary: str | None = None
    education: str | None = None
    certifications: str | None = None
    tools: str | None = None
    languages: str | None = None
    additionalInfo: str | None = None


class CourseBody(BaseModel):
    userId: UUID
    addedById: UUID | None = None
    title: str
    provider: str | None = None
    completionDate: str | None = None
    certificateUrl: str | None = None
    notes: str | None = None


class AgentProfileBody(BaseModel):
    headline: str | None = None
    location: str | None = None
    about: str | None = None
    agencyName: str | None = None
    agencyAbout: str | None = None
    website: str | None = None


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


class JobAgentBody(BaseModel):
    jobId: UUID
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
        "version": "rawabet-guide-2026-06-30-greetings",
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


def pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def make_simple_pdf(title: str, lines: list[str]) -> bytes:
    clean_lines = []
    for line in lines:
        encoded = line.encode("latin-1", "replace").decode("latin-1")
        clean_lines.append(encoded[:110])
    stream_lines = ["BT", "/F1 16 Tf", "50 790 Td", f"({pdf_escape(title.encode('latin-1', 'replace').decode('latin-1'))}) Tj", "/F1 10 Tf", "0 -28 Td"]
    for line in clean_lines:
        stream_lines.append(f"({pdf_escape(line)}) Tj")
        stream_lines.append("0 -15 Td")
    stream_lines.append("ET")
    stream = "\n".join(stream_lines).encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_at = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_at}\n%%EOF\n".encode("ascii"))
    return bytes(pdf)


def has_arabic(value: str | None) -> bool:
    return bool(value and re.search(r"[\u0600-\u06FF]", value))


RESUME_FONT_CACHE: dict[str, str] = {}


def resume_font_name(weight: str = "medium") -> str:
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError(f"ReportLab is not installed or could not be imported: {REPORTLAB_IMPORT_ERROR}")
    weight = weight if weight in {"light", "medium", "bold", "black"} else "medium"
    if weight in RESUME_FONT_CACHE:
        return RESUME_FONT_CACHE[weight]
    font_paths = {
        "light": [
            str(Path(__file__).resolve().parent / "fonts" / "NotoKufiArabic-Regular.ttf"),
            "/usr/share/fonts/rawabet/NotoKufiArabic-Regular.ttf",
        ],
        "medium": [
            str(Path(__file__).resolve().parent / "fonts" / "NotoKufiArabic-Medium.ttf"),
            str(Path(__file__).resolve().parent / "fonts" / "NotoKufiArabic-Regular.ttf"),
            "/usr/share/fonts/rawabet/NotoKufiArabic-Medium.ttf",
            "/usr/share/fonts/rawabet/NotoKufiArabic-Regular.ttf",
        ],
        "bold": [
            str(Path(__file__).resolve().parent / "fonts" / "NotoKufiArabic-Bold.ttf"),
            str(Path(__file__).resolve().parent / "fonts" / "NotoKufiArabic-Medium.ttf"),
            "/usr/share/fonts/rawabet/NotoKufiArabic-Bold.ttf",
            "/usr/share/fonts/rawabet/NotoKufiArabic-Medium.ttf",
        ],
        "black": [
            str(Path(__file__).resolve().parent / "fonts" / "NotoKufiArabic-ExtraBold.ttf"),
            str(Path(__file__).resolve().parent / "fonts" / "NotoKufiArabic-Bold.ttf"),
            "/usr/share/fonts/rawabet/NotoKufiArabic-ExtraBold.ttf",
            "/usr/share/fonts/rawabet/NotoKufiArabic-Bold.ttf",
        ],
    }
    fallback_candidates = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
        "/usr/share/fonts/noto/NotoNaskhArabic-Regular.ttf",
        "/usr/share/fonts/noto/NotoSansArabic-Regular.ttf",
        "/usr/share/fonts/google-noto/NotoNaskhArabic-Regular.ttf",
        "/usr/share/fonts/google-noto/NotoSansArabic-Regular.ttf",
        "/usr/share/fonts/google-noto-vf/NotoSansArabic[wght].ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    candidates = font_paths[weight] + font_paths["medium"] + fallback_candidates
    for path in candidates:
        if Path(path).exists():
            try:
                font_name = f"RawabetResume{weight.title()}"
                pdfmetrics.registerFont(TTFont(font_name, path))
                RESUME_FONT_CACHE[weight] = font_name
                return font_name
            except Exception:
                continue
    raise RuntimeError("No Arabic-capable TrueType font was found. Install DejaVu Sans or Noto Arabic fonts on the server.")


def pdf_text(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if has_arabic(text) and arabic_reshaper and get_display:
        try:
            return get_display(arabic_reshaper.reshape(text))
        except Exception:
            return text
    return text


def wrap_resume_arabic_line(text: str, limit: int = 68) -> list[str]:
    words = re.sub(r"\s+", " ", str(text or "")).strip().split()
    if not words:
        return []
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > limit:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def split_lines(value: str | None) -> list[str]:
    return [line.strip(" •-\t") for line in str(value or "").splitlines() if line.strip(" •-\t")]


def trim_resume_line(value: object, limit: int = 520) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= limit:
        return text
    return f"{text[:limit].rstrip()}..."


def normalize_resume_description_lines(value: str | None) -> list[str]:
    raw_lines = split_lines(value)
    merged: list[str] = []
    pending = ""
    dangling_arabic_starts = {"قمت", "عملت", "اشرفت", "أشرفت", "اسست", "أسست", "قدت", "طورت", "ادرت", "أدرت"}
    dangling_norms = {normalize_arabic_text(item) for item in dangling_arabic_starts}
    for line in raw_lines:
        compact = line.strip(" .،")
        if pending:
            merged.append(trim_resume_line(f"{pending} {line}", 360))
            pending = ""
            continue
        if normalize_arabic_text(compact) in dangling_norms:
            pending = line
        else:
            merged.append(trim_resume_line(line, 360))
    if pending:
        merged.append(pending)
    return merged


def polish_arabic_bullet(line: str, title: str = "", company: str = "") -> str:
    text = trim_resume_line(line, 260).strip(" .،")
    replacements = [
        (r"^قمت\s+بأتمتة", "أتمتت"),
        (r"^قمت\s+باتمتة", "أتمتت"),
        (r"^قمت\s+ب", ""),
        (r"^قمت\s+", ""),
        (r"^عملت\s+على\s+", ""),
        (r"^انا\s+", ""),
        (r"^أنا\s+", ""),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE).strip()
    text = re.sub(r"^اسست\b", "أسست", text)
    text = re.sub(r"^ادرت\b", "أدرت", text)
    text = re.sub(r"^اشرفت\b", "أشرفت", text)
    text = re.sub(r"^اقود\b", "قدت", text)
    text = re.sub(r"^أقود\b", "قدت", text)
    if not text:
        text = f"إدارة مسؤوليات {title or 'الدور'} لدى {company or 'الجهة'}"
    normalized = normalize_arabic_text(text)
    if normalized.startswith(("اسست", "ادرت", "قدت", "طورت", "صممت", "بنيت", "اشرفت", "حسنت", "نفذت")):
        return text
    if normalized.startswith(("بناء", "تطوير", "اداره", "قياده", "تصميم", "تشغيل", "تحسين", "متابعه")):
        return f"توليت {text}"
    return f"أنجزت {text}"


def role_specific_arabic_bullets(item: dict, profile: dict | None = None, minimum: int = 4) -> list[str]:
    title = item.get("title") or "الدور الوظيفي"
    company = item.get("company") or "الجهة"
    ignored_norms = {normalize_arabic_text(title), normalize_arabic_text(company)}
    description_lines = []
    for line in normalize_resume_description_lines(item.get("description")):
        normalized_line = normalize_arabic_text(line)
        if not normalized_line or normalized_line in ignored_norms or len(normalized_line) < 12:
            continue
        description_lines.append(line)
    bullets = [polish_arabic_bullet(line, title, company) for line in description_lines if line.strip()]
    title_norm = normalize_arabic_text(title)
    company_norm = normalize_arabic_text(company)
    if any(term in title_norm for term in ["ذكاء", "ai", "تحليل", "بيانات"]):
        bullets.extend([
            "قدت مبادرات ذكاء اصطناعي لتحويل الاحتياجات التشغيلية إلى حلول عملية قابلة للاستخدام.",
            "حللت المتطلبات وربطت مخرجات النماذج بمؤشرات أداء تساعد على اتخاذ القرار.",
            "نسقت مع الفرق الفنية وأصحاب المصلحة لضمان جودة الحلول واستقرارها."
        ])
    if any(term in title_norm for term in ["مؤسس", "founder", "صاحب"]) or any(term in company_norm for term in ["اتصالات", "انترنت", "internet"]):
        bullets.extend([
            "أسست نموذج عمل يخدم الأفراد والشركات مع بناء عمليات تشغيل ومتابعة للعملاء.",
            "طورت بنية تشغيلية وسيرفرات قادرة على استيعاب نمو الاتصالات وحجم الاستخدام.",
            "أدرت العلاقات التجارية والتقنية لضمان استمرارية الخدمة وتحسين تجربة العملاء."
        ])
    if any(term in title_norm for term in ["مدير", "مشرف", "رئيس"]):
        bullets.extend([
            "أدرت فريق العمل ووزعت المسؤوليات بما يضمن وضوح الأولويات وسرعة الإنجاز.",
            "تابعت جودة المخرجات اليومية وراجعت المخاطر التشغيلية قبل تأثيرها على العمل.",
            "حسنت آليات التواصل والتوثيق بين الفرق لرفع كفاءة التنفيذ."
        ])
    if not bullets:
        bullets = [
            f"أدرت مسؤوليات {title} لدى {company} من خلال تنظيم المهام ومتابعة جودة التنفيذ.",
            "طورت أسلوب العمل اليومي عبر تحسين الإجراءات وتوثيق المتطلبات والمخرجات.",
            "حللت احتياجات العمل وربطتها بأولويات واضحة تساعد الإدارة على اتخاذ قرارات أفضل.",
            "نسقت المتابعة بين أصحاب العلاقة لضمان سرعة الاستجابة وتقليل التعطيل التشغيلي."
        ]
    deduped = []
    seen = set()
    for bullet in bullets:
        cleaned = trim_resume_line(bullet, 260).strip(" .،")
        key = normalize_arabic_text(cleaned)
        if cleaned and key not in seen:
            seen.add(key)
            deduped.append(cleaned)
    return deduped[: max(minimum, min(6, len(deduped)))]


def weak_arabic_resume_bullet(value: str) -> bool:
    normalized = normalize_arabic_text(value)
    weak_terms = [
        "نفذت مهام",
        "مع التركيز علي الجوده والموثوقيه",
        "تحقيق نتائج قابله للقياس",
        "تعاونت مع فرق العمل واصحاب المصلحه",
        "دعمت مخرجات العمل من خلال تنظيم المهام",
    ]
    return len(normalized) < 18 or any(term in normalized for term in weak_terms)


def clean_arabic_resume_bullet(value: str) -> str:
    text = trim_resume_line(value, 260).strip(" .،")
    replacements = [
        (r"^أنجزت\s+اقود\b", "قدت"),
        (r"^أنجزت\s+أقود\b", "قدت"),
        (r"^أنجزت\s+قمت\s+بأتمتة", "أتمتت"),
        (r"^أنجزت\s+قمت\s+باتمتة", "أتمتت"),
        (r"^أنجزت\s+قمت\s+ب", "أنجزت"),
        (r"^انجزت\s+اقود\b", "قدت"),
        (r"^قمت\s+بأتمتة", "أتمتت"),
        (r"^قمت\s+باتمتة", "أتمتت"),
        (r"^اقود\b", "قدت"),
        (r"^أقود\b", "قدت"),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text).strip()
    return text


def date_range(start: object = None, end: object = None, is_current: bool = False, current_text: str = "Present") -> str:
    start_text = str(start or "").strip()
    end_text = current_text if is_current else str(end or "").strip()
    if start_text and end_text:
        return f"{start_text} - {end_text}"
    return start_text or end_text


def empty_to_none(value: object):
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    return value


def optional_year(value: object):
    value = empty_to_none(value)
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid year")


def default_resume_sections(user: dict, profile: dict, experiences: list[dict], education: list[dict], courses: list[dict], body: ResumeBuilderBody) -> dict:
    rtl = has_arabic(" ".join([
        str(user.get("full_name") or ""),
        str(user.get("headline") or ""),
        str(profile.get("about") or ""),
        str(body.summary or ""),
        str(user.get("headline") or ""),
    ]))
    current_text = "حتى الآن" if rtl else "Present"
    skills = profile.get("skills") if isinstance(profile.get("skills"), list) else []
    languages = split_lines(body.languages) or profile.get("languages") or ["Arabic", "English"]
    certs = split_lines(body.certifications)
    certs.extend([f"{course.get('title')} - {course.get('provider') or ''}".strip(" -") for course in courses if course.get("title")])
    education_lines = split_lines(body.education)
    education_lines.extend([
        " - ".join([part for part in [item.get("degree"), item.get("school"), date_range(item.get("start_year"), item.get("end_year"), current_text=current_text)] if part])
        for item in education
    ])
    experience_items = []
    for item in experiences:
        description_lines = normalize_resume_description_lines(item.get("description"))
        if rtl:
            fallback_bullets = role_specific_arabic_bullets(item, profile, minimum=4)
        else:
            fallback_bullets = description_lines or [
                f"Delivered work for {item.get('company') or 'the organization'} with focus on quality, reliability, and measurable outcomes.",
                "Collaborated with stakeholders to improve processes, documentation, and execution."
            ]
        experience_items.append({
            "title": item.get("title") or "-",
            "company": item.get("company") or "-",
            "location": item.get("location") or "",
            "dates": date_range(item.get("start_date"), item.get("end_date"), item.get("is_current"), current_text=current_text),
            "bullets": fallback_bullets[:6],
        })
    return {
        "summary": body.summary or profile.get("about") or ("محترف لديه خبرات ومهارات ومسار عملي موثق." if rtl else f"{user.get('headline') or 'Professional'} with verified experience, skills, and career history."),
        "target_title": user.get("headline") or "",
        "skills": skills,
        "languages": languages,
        "certifications": certs,
        "education": education_lines,
        "projects": [],
        "tools": split_lines(body.tools),
        "achievements": [],
        "additional_info": split_lines(body.additionalInfo),
        "experiences": experience_items,
    }


def openai_resume_sections(user: dict, profile: dict, experiences: list[dict], education: list[dict], courses: list[dict], body: ResumeBuilderBody, fallback: dict) -> dict:
    if not OPENAI_API_KEY:
        return fallback
    prompt = {
        "name": user.get("full_name"),
        "email": user.get("email"),
        "phone": user.get("phone"),
        "location": user.get("location"),
        "headline": user.get("headline"),
        "about": profile.get("about"),
        "skills": profile.get("skills"),
        "targetTitle": user.get("headline"),
        "summaryNotes": body.summary,
        "education": body.education,
        "educationFromProfile": education,
        "certifications": body.certifications,
        "coursesFromProfile": courses,
        "projects": "",
        "tools": body.tools,
        "achievements": "",
        "languages": body.languages,
        "additionalInfo": body.additionalInfo,
        "experiences": experiences,
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": (
                "Create a polished professional Arabic resume from the provided Rawabet profile. "
                "Return strict JSON only with keys: summary, target_title, skills, languages, certifications, education, projects, tools, achievements, additional_info, experiences. "
                "experiences must be an array of objects with title, company, location, dates, bullets. "
                "For every experience, write 4 to 6 strong Arabic bullets based on the job title, company, skills, tools, and the user's raw description. "
                "Do not copy weak raw wording. Rewrite it into executive, measurable, professional Arabic. "
                "Start bullets with strong verbs such as: أسست، قدت، أدرت، طورت، صممت، بنيت، حسنت، أطلقت، نسقت، حللت، أشرفت. "
                "Never use generic bullets like: نفذت مهام، تعاونت مع فرق العمل، مع التركيز على الجودة والموثوقية، تحقيق نتائج قابلة للقياس. "
                "Each bullet should be one clear sentence, 12 to 28 words, with no numbering and no trailing punctuation required. "
                "If the user gives short notes, infer realistic responsibilities from the role without inventing fake employers, dates, degrees, or certifications. "
                "Keep user-entered English proper nouns, company names, tools, technologies, emails, and degrees exactly as provided when already in English. "
                "Write summary, bullets, achievements, additional_info, and generated wording in Arabic by default."
            )},
            {"role": "user", "content": json.dumps(prompt, default=str, ensure_ascii=False)},
        ],
        "temperature": 0.35,
        "max_tokens": 2600,
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=16) as response:
            data = json.loads(response.read().decode("utf-8"))
            text = data["choices"][0]["message"]["content"].strip()
            text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                merged = {**fallback, **{key: value for key, value in parsed.items() if value}}
                if not isinstance(merged.get("experiences"), list) or not merged["experiences"]:
                    merged["experiences"] = fallback["experiences"]
                return merged
            return fallback
    except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError):
        return fallback


def paragraph(text: object, style):
    return Paragraph(pdf_text(text).replace("\n", "<br/>"), style)


def pre_shaped_paragraph(lines: list[str], style):
    return Paragraph("<br/>".join(lines), style)


def underlined_paragraph(text: object, style):
    return Paragraph(f"<u>{pdf_text(text).replace(chr(10), '<br/>')}</u>", style)


def bullet_rows(items: list[str], style, rtl: bool):
    rows = []
    for item in items:
        if rtl and has_arabic(item):
            logical_lines = wrap_resume_arabic_line(item, 62)
            shaped_lines = []
            for index, line in enumerate(logical_lines):
                prefix = "• " if index == 0 else "  "
                shaped_lines.append(pdf_text(f"{prefix}{line}"))
            rows.append([pre_shaped_paragraph(shaped_lines, style)])
        else:
            rows.append([paragraph(f"• {item}", style)])
    return rows


def make_resume_pdf(user: dict, profile: dict, experiences: list[dict], education: list[dict], courses: list[dict], body: ResumeBuilderBody) -> bytes:
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError(f"ReportLab is not installed or could not be imported: {REPORTLAB_IMPORT_ERROR}")
    if not ARABIC_PDF_AVAILABLE:
        raise RuntimeError("Arabic PDF support is not installed. Install arabic-reshaper and python-bidi.")
    fallback = default_resume_sections(user, profile, experiences, education, courses, body)
    sections = openai_resume_sections(user, profile, experiences, education, courses, body, fallback)
    def listify(value):
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        return split_lines(str(value or ""))
    for key in ("skills", "languages", "certifications", "education", "projects", "tools", "achievements", "additional_info"):
        sections[key] = listify(sections.get(key))
    rtl = has_arabic(" ".join([
        str(user.get("full_name") or ""),
        str(user.get("headline") or ""),
        str(sections.get("summary") or ""),
        str(sections.get("target_title") or ""),
    ]))
    normalized_experiences = []
    original_experiences = experiences or []
    for index, item in enumerate(sections.get("experiences") or []):
        if isinstance(item, dict):
            bullets = [trim_resume_line(bullet) for bullet in listify(item.get("bullets"))[:7]]
            if rtl:
                source_item = original_experiences[index] if index < len(original_experiences) else item
                stronger_bullets = role_specific_arabic_bullets({**source_item, **item}, profile, minimum=4)
                bullets = [clean_arabic_resume_bullet(bullet) for bullet in bullets if has_arabic(bullet) and not weak_arabic_resume_bullet(bullet)]
                for bullet in stronger_bullets:
                    bullet = clean_arabic_resume_bullet(bullet)
                    if len(bullets) >= 6:
                        break
                    if normalize_arabic_text(bullet) not in {normalize_arabic_text(existing) for existing in bullets}:
                        bullets.append(bullet)
                bullets = bullets[:6]
            normalized_experiences.append({**item, "bullets": bullets})
    sections["experiences"] = normalized_experiences or fallback["experiences"]
    font = resume_font_name("medium")
    font_light = resume_font_name("light")
    font_bold = resume_font_name("bold")
    font_black = resume_font_name("black")
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=48, bottomMargin=42)
    styles = getSampleStyleSheet()
    blue = colors.HexColor("#0070c0")
    red = colors.HexColor("#c0392b")
    ink = colors.black
    muted = colors.HexColor("#595959")
    base = ParagraphStyle("BaseResume", parent=styles["Normal"], fontName=font, fontSize=9.0, leading=12.0, textColor=ink)
    name_style = ParagraphStyle("NameResume", parent=base, fontName=font_bold, fontSize=32, leading=38, textColor=colors.black, spaceAfter=18, alignment=TA_LEFT)
    title_style = ParagraphStyle("TitleResume", parent=base, fontName=font_light, fontSize=10.1, leading=12.5, textColor=muted, alignment=TA_LEFT)
    contact_style = ParagraphStyle("ContactResume", parent=base, fontSize=10.1, leading=15, textColor=colors.black, alignment=TA_LEFT)
    section_style = ParagraphStyle("SectionResume", parent=base, fontName=font_bold, fontSize=10.8, leading=13.5, textColor=blue, spaceBefore=0, spaceAfter=24, alignment=TA_CENTER)
    side_section_style = ParagraphStyle("SideSectionResume", parent=section_style, alignment=TA_RIGHT, spaceBefore=0, spaceAfter=20)
    company_style = ParagraphStyle("CompanyResume", parent=base, fontName=font_bold, fontSize=9.9, leading=13, textColor=colors.black, alignment=TA_CENTER, spaceAfter=10)
    role_style = ParagraphStyle("RoleResume", parent=base, fontSize=9.4, leading=12, textColor=red, alignment=TA_CENTER, spaceAfter=10)
    meta_style = ParagraphStyle("MetaResume", parent=base, fontSize=8.8, leading=11.5, textColor=muted, alignment=TA_CENTER, spaceAfter=11)
    responsibilities_style = ParagraphStyle("ResponsibilitiesResume", parent=base, fontName=font_bold, fontSize=8.8, leading=11.5, textColor=muted, alignment=TA_CENTER, spaceAfter=18)
    bullet_style = ParagraphStyle("BulletResume", parent=base, fontSize=8.9, leading=12.5, textColor=colors.black, alignment=TA_RIGHT)
    side_item = ParagraphStyle("SideItemResume", parent=base, fontName=font_bold, fontSize=8.9, leading=17.5, textColor=muted, alignment=TA_LEFT)
    if rtl:
        for style in (base, section_style, side_section_style, company_style, role_style, meta_style, responsibilities_style, bullet_style):
            style.alignment = TA_RIGHT

    contact_lines = [part for part in [user.get("phone"), user.get("email"), user.get("location")] if part]
    header_left = [
        paragraph(user.get("full_name") or "Rawabet Resume", name_style),
        paragraph(sections.get("target_title") or user.get("headline") or "", title_style),
    ]
    header_right = [paragraph("<br/>".join(contact_lines), contact_style)]
    header = Table([[header_left, header_right]], colWidths=[380, 132], hAlign="LEFT")
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    def section_block(title: str, items: list[str]):
        if not items:
            return []
        flow = [paragraph(title, side_section_style)]
        for item in items:
            flow.append(paragraph(item, side_item))
        return flow

    sidebar = [
        paragraph("Skills" if not rtl else "المهارات", side_section_style),
        *[paragraph(item, side_item) for item in (sections.get("skills") or [])],
        Spacer(1, 48),
        *section_block("Languages" if not rtl else "اللغات", sections.get("languages") or []),
        *section_block("Certifications" if not rtl else "الشهادات", sections.get("certifications") or []),
    ]
    if sections.get("tools"):
        sidebar.extend([Spacer(1, 34), *section_block("Tools" if not rtl else "الأدوات", sections.get("tools") or [])])

    main_intro = [paragraph("Work Experience" if not rtl else "الخبرات العملية", section_style)]
    table_rows = []
    for index, item in enumerate(sections.get("experiences", [])):
        company_line = " - ".join([part for part in [item.get("company"), item.get("location")] if part])
        role_line = item.get("title") or ""
        job_flow = [
            paragraph(company_line, company_style),
            underlined_paragraph(role_line, role_style) if role_line else Spacer(1, 0),
            paragraph(item.get("dates") or "", meta_style),
            paragraph("Roles and responsibilities:" if not rtl else "الأدوار والمسؤوليات:", responsibilities_style),
        ]
        bullets = (item.get("bullets") or [])[:7]
        if bullets:
            rows = bullet_rows(bullets, bullet_style, rtl)
            widths = [328]
            bullet_table = Table(rows, colWidths=widths, hAlign="RIGHT" if rtl else "LEFT")
            bullet_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 1.2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
            ]))
            job_flow.append(bullet_table)
        job_flow.append(Spacer(1, 20))
        if index == 0:
            table_rows.append([main_intro + job_flow, sidebar])
        else:
            table_rows.append([job_flow, []])
    if not table_rows:
        table_rows.append([main_intro, sidebar])
    for title, key in [
        ("Education" if not rtl else "التعليم", "education"),
        ("Projects" if not rtl else "المشاريع", "projects"),
        ("Achievements" if not rtl else "الإنجازات", "achievements"),
        ("Additional Information" if not rtl else "معلومات إضافية", "additional_info"),
    ]:
        items = sections.get(key) or []
        if items:
            section_flow = [paragraph(title, section_style)]
            rows = bullet_rows(items, bullet_style, rtl)
            widths = [328]
            item_table = Table(rows, colWidths=widths, hAlign="RIGHT" if rtl else "LEFT")
            item_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 1.2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
            ]))
            section_flow.append(item_table)
            section_flow.append(Spacer(1, 8))
            table_rows.append([section_flow, []])

    story = [header, Spacer(1, 58)]
    table = Table(table_rows, colWidths=[335, 130], hAlign="LEFT", splitByRow=1)
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, -1), 22),
        ("LEFTPADDING", (1, 0), (1, -1), 18),
        ("RIGHTPADDING", (1, 0), (1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(table)
    doc.build(story)
    return buffer.getvalue()


RAWABET_CONTEXT = """
Rawabet / روابط is a professional employment platform for Arab professionals.

User capabilities:
- Register with full name, email, phone, date of birth, and password.
- Verify registration by email OTP before the account is created.
- Log in only when the account is active or verified; suspended accounts must not log in.
- Use Home to see profile strength, applied jobs count, profile completion shortcuts, admin-posted jobs, and upcoming interviews.
- Use Profile to edit name, phone, date of birth, headline, location, about, skills, profile picture, resume, certificates, and work history.
- Profile picture uploads replace the previous picture.
- Users can keep up to two uploaded resumes.
- If a user does not have a CV/resume, they can use Create smart resume to generate and download a PDF resume from their profile, skills, work history, education, courses, certifications, projects, tools, achievements, and extra notes.
- Generated smart resumes download directly and are not automatically saved into uploaded resumes.
- Certificate uploads can add up to five certificates.
- Use Jobs to search job title/company, filter by category and salary, view details, apply, and track application status.
- Applied jobs can be filtered by status, category, salary, and company.
- AI assistant chat lets users ask about using Rawabet, jobs, profiles, applications, interviews, and documents.
- Users can request live support when the assistant cannot help or when they need a person.
- Clear chat removes the current support conversation.

Statuses:
- Application statuses: submitted, review, interview, accepted, rejected.
- User statuses: active, verified, review, suspended.
- Job statuses: active, paused, closed.
- Plans: free, premium.

Bot rules:
- Answer only questions about what normal users can do in Rawabet.
- Do not explain admin tools, agent tools, internal dashboards, analytics, user management, or job management.
- Prefer clear numbered steps or bullets and put every bullet/step on its own line.
- Mention exact user-facing page/menu/button names.
- Use Arabic by default unless the user writes English.
- If a user asks for jobs and there are no matching active jobs, answer naturally that there are no matching jobs at this moment and suggest checking Jobs again later or changing search terms. Do not send them to live support just because no matching job exists.
- If a question is outside Rawabet or truly cannot be answered from this context, ask whether the user wants live support or wants to end the conversation.
"""

LIVE_AGENT_REPLY = "تم إشعار فريق الدعم بطلبك. سيقوم موظف دعم مباشر بالرد عليك من صندوق الدعم."
END_CHAT_REPLY = "حسنا، يمكنك إنهاء المحادثة الآن. إذا احتجت مساعدة لاحقا افتح نافذة الدعم مرة أخرى."
UNKNOWN_REPLY = "لا أملك إجابة مؤكدة عن هذا السؤال داخل معلومات منصة روابط. يمكنني مساعدتك في البحث عن الوظائف، التقديم، الملف الشخصي، السيرة، الشهادات، المقابلات، وحالات الطلبات. هل تريد التحدث مع دعم مباشر أم إنهاء المحادثة؟"
UNKNOWN_REPLY_EN = "I do not have a confirmed answer from Rawabet platform information. I can help with jobs, applications, profile updates, resumes, certificates, interviews, and application statuses. Would you like to speak with live support or end the conversation?"
NO_JOB_MATCH_REPLY = "لا توجد وظائف مطابقة لهذا البحث حاليا. يمكنك تجربة كلمات أخرى أو فتح صفحة الوظائف لاحقا لأن الإدارة تضيف وظائف جديدة باستمرار."
NO_JOB_MATCH_REPLY_EN = "We do not have matching jobs at this moment. You can try different keywords or check the Jobs page again later because new jobs may be added."


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


def text_tokens(value: str) -> list[str]:
    return [normalize_arabic_text(token) for token in re.findall(r"[\w\u0600-\u06FF]+", value) if len(normalize_arabic_text(token)) >= 3]


def contains_any_intent(value: str, stems: list[str]) -> bool:
    normalized = normalize_arabic_text(value)
    return any(stem in normalized for stem in stems)


def question_is_english(value: str) -> bool:
    return bool(re.search(r"[A-Za-z]", value)) and not bool(re.search(r"[\u0600-\u06FF]", value))


def unknown_reply_for(question: str) -> str:
    return UNKNOWN_REPLY_EN if question_is_english(question) else UNKNOWN_REPLY


def no_job_match_reply_for(question: str) -> str:
    return NO_JOB_MATCH_REPLY_EN if question_is_english(question) else NO_JOB_MATCH_REPLY


def greeting_reply(question: str) -> str | None:
    normalized = normalize_arabic_text(question).strip()
    lowered = question.lower().strip()
    normalized = re.sub(r"[^\w\u0600-\u06FF\s]", " ", normalized)
    lowered = re.sub(r"[^\w\s]", " ", lowered)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    lowered = re.sub(r"\s+", " ", lowered).strip()
    if not normalized:
        return None

    arabic_phrases = {
        "السلام عليكم",
        "سلام عليكم",
        "وعليكم السلام",
        "مرحبا",
        "اهلا",
        "اهلا وسهلا",
        "هلا",
        "صباح الخير",
        "مساء الخير",
        "يعطيك العافيه",
        "كيفك",
        "كيف الحال",
    }
    english_phrases = {
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "how are you",
        "thanks",
        "thank you",
    }
    arabic_tokens = {"السلام", "عليكم", "سلام", "وعليكم", "مرحبا", "اهلا", "وسهلا", "هلا", "صباح", "الخير", "مساء", "يعطيك", "العافيه", "كيفك", "كيف", "الحال"}
    english_tokens = {"hi", "hello", "hey", "good", "morning", "afternoon", "evening", "how", "are", "you", "thanks", "thank", "thankyou"}

    if normalized in arabic_phrases or lowered in english_phrases:
        return "أهلا بك في روابط. كيف يمكنني مساعدتك؟" if not question_is_english(question) else "Hello, welcome to Rawabet. How can I help you?"

    tokens = re.findall(r"[\w\u0600-\u06FF]+", normalized if not question_is_english(question) else lowered)
    if tokens and len(tokens) <= 4:
        allowed = english_tokens if question_is_english(question) else arabic_tokens
        if all(token in allowed for token in tokens):
            return "أهلا بك في روابط. كيف يمكنني مساعدتك؟" if not question_is_english(question) else "Hello, welcome to Rawabet. How can I help you?"
    return None


def is_live_support_request(value: str) -> bool:
    lowered = value.lower()
    normalized = normalize_arabic_text(value)
    live_terms = ["live agent", "human", "support agent", "live support", "موظف", "دعم مباشر", "شخص", "انسان", "إنسان"]
    return any(term in lowered or normalize_arabic_text(term) in normalized for term in live_terms)


def live_support_requested(user_id: UUID) -> bool:
    row = fetch_one(
        """
        SELECT EXISTS (
          SELECT 1
          FROM support_messages
          WHERE user_id = %s
            AND sender_role = 'user'
            AND (
              message ILIKE '%%live support%%'
              OR message ILIKE '%%live agent%%'
              OR message ILIKE '%%human%%'
              OR message ILIKE '%%دعم مباشر%%'
              OR message ILIKE '%%موظف%%'
            )
        ) AS requested
        """,
        (user_id,),
    )
    return bool(row and row.get("requested"))


def active_jobs_context() -> str:
    try:
        job_number_expr = "job_number" if jobs_have_job_number_column() else "NULL::integer AS job_number"
        jobs = fetch_all(
            f"""
            SELECT {job_number_expr}, company_name, title, category, location, type, salary_range, description,
                   COALESCE(screening_questions, '[]'::jsonb) AS screening_questions
            FROM jobs
            WHERE status = 'active'
            ORDER BY created_at DESC
            LIMIT 80
            """
        )
    except Exception:
        jobs = []
    if not jobs:
        return "Current active jobs: No active jobs are available in the database."
    lines = ["Current active jobs users can ask about:"]
    for job in jobs:
        number = f"#{job.get('job_number')} " if job.get("job_number") else ""
        questions = job.get("screening_questions") or []
        if not isinstance(questions, list):
            questions = []
        description = re.sub(r"\s+", " ", (job.get("description") or "")).strip()
        if len(description) > 260:
            description = f"{description[:260].rstrip()}..."
        lines.append(
            f"- {number}{job.get('title')} at {job.get('company_name')} | "
            f"Category: {job.get('category')} | Location: {job.get('location')} | "
            f"Type: {job.get('type')} | Salary: {job.get('salary_range') or '-'} | "
            f"Description: {description or '-'} | Screening questions: {'; '.join(map(str, questions)) or '-'}"
        )
    return "\n".join(lines)


def active_agents_context() -> str:
    try:
        agents = fetch_all(
            """
            SELECT u.full_name, u.headline, u.location,
                   COALESCE(p.agency_name, '') AS agency_name,
                   COALESCE(p.agency_about, '') AS agency_about,
                   COALESCE(p.website, '') AS website,
                   COUNT(j.id)::int AS open_jobs
            FROM users u
            LEFT JOIN profiles p ON p.user_id = u.id
            LEFT JOIN agent_job_assignments aja ON aja.agent_id = u.id
            LEFT JOIN jobs j ON j.id = aja.job_id AND j.status = 'active'
            WHERE u.role = 'agent' AND u.status IN ('active', 'verified')
            GROUP BY u.id, p.agency_name, p.agency_about, p.website
            ORDER BY open_jobs DESC, u.full_name
            LIMIT 40
            """
        )
    except Exception:
        agents = []
    if not agents:
        return "Current companies/agencies: No public agency profiles are available."
    lines = ["Current companies/agencies users can browse:"]
    for agent in agents:
        about = re.sub(r"\s+", " ", (agent.get("agency_about") or "")).strip()
        if len(about) > 220:
            about = f"{about[:220].rstrip()}..."
        lines.append(
            f"- {agent.get('agency_name') or agent.get('full_name')} | "
            f"Representative: {agent.get('full_name')} | Headline: {agent.get('headline') or '-'} | "
            f"Location: {agent.get('location') or '-'} | Open jobs: {agent.get('open_jobs') or 0} | About: {about or '-'}"
        )
    return "\n".join(lines)


def matching_jobs_reply(question: str) -> str | None:
    lowered = question.lower()
    normalized = normalize_arabic_text(question)
    resume_terms = ["resume", "cv", "سيره", "سيرة", "سي في", "السي في"]
    if any(term in lowered or normalize_arabic_text(term) in normalized for term in resume_terms):
        return None
    search_intents = ["search", "find", "show me", "available", "have", "looking", "ابحث", "اعثر", "اريد", "أريد", "يوجد", "عندكم", "متاح"]
    job_terms = ["job", "jobs", "position", "vacancy", "work", "وظيفة", "وظائف", "شاغر", "عمل"]
    has_search_intent = any(term in lowered or normalize_arabic_text(term) in normalized for term in search_intents)
    has_job_term = any(term in lowered or normalize_arabic_text(term) in normalized for term in job_terms)
    if not (has_search_intent or has_job_term):
        return None
    stop_words = {
        "search", "find", "show", "me", "do", "you", "have", "any", "job", "jobs", "position", "vacancy", "work", "in", "at", "for", "about", "rawabet",
        "ابحث", "اعثر", "اريد", "أريد", "هل", "يوجد", "هناك", "لي", "عن", "في", "على", "وظيفة", "وظائف", "الوظائف", "مناسبه", "مناسبة"
    }
    normalized_stop_words = {normalize_arabic_text(item) for item in stop_words}
    words = re.findall(r"[\w\u0600-\u06FF]+", question)
    keywords = []
    for word in words:
        normalized_word = normalize_arabic_text(word)
        if normalized_word in {"it", "ايتي"}:
            keywords.extend(["technology", "information", "technical", "تقنيه", "معلومات", "حاسوب"])
            continue
        if normalized_word in {"tech", "technology", "تقني", "تقنيه", "تكنولوجيا"}:
            keywords.extend(["technology", "technical", "تقنيه"])
            continue
        if len(normalized_word) < 3 or normalized_word in normalized_stop_words:
            continue
        keywords.append(normalized_word)
    if not keywords and not has_job_term:
        return None
    try:
        job_number_expr = "job_number" if jobs_have_job_number_column() else "NULL::integer AS job_number"
        jobs = fetch_all(
            f"""
            SELECT id, {job_number_expr}, company_name, title, category, location, type, salary_range, description
            FROM jobs
            WHERE status = 'active'
            ORDER BY created_at DESC
            LIMIT 200
            """,
        )
    except Exception:
        return None
    if not jobs:
        return no_job_match_reply_for(question)

    location_tokens = set()
    for job in jobs:
        location_tokens.update(text_tokens(job.get("location") or ""))
    non_location_keywords = [keyword for keyword in keywords if keyword not in location_tokens]

    exact_company_matches = []
    for job in jobs:
        company = normalize_arabic_text(job.get("company_name") or "")
        company_base = re.split(r"[-–|،,]", company, maxsplit=1)[0].strip()
        if company and company in normalized:
            exact_company_matches.append(job)
            continue
        if len(company_base) >= 4 and company_base in normalized:
            exact_company_matches.append(job)

    matched_jobs = exact_company_matches
    if not matched_jobs:
        scored_jobs = []
        for job in jobs:
            title = normalize_arabic_text(job.get("title") or "")
            company = normalize_arabic_text(job.get("company_name") or "")
            category = normalize_arabic_text(job.get("category") or "")
            description = normalize_arabic_text(job.get("description") or "")
            location = normalize_arabic_text(job.get("location") or "")
            searchable = " ".join([title, company, category, description])
            score = sum(1 for keyword in non_location_keywords if keyword in searchable)
            if not non_location_keywords:
                score = sum(1 for keyword in keywords if keyword in location)
            if score:
                scored_jobs.append((score, job))
        scored_jobs.sort(key=lambda item: (-item[0], item[1].get("job_number") or 0))
        matched_jobs = [job for _, job in scored_jobs[:10]]

    if not matched_jobs:
        return no_job_match_reply_for(question)

    lines = ["I found these matching job IDs:" if question_is_english(question) else "وجدت أرقام الوظائف المطابقة لبحثك:"]
    for job in matched_jobs[:10]:
        job_id = f"#{job.get('job_number')}" if job.get("job_number") else str(job.get("id"))
        lines.append(f"Job ID: {job_id}" if question_is_english(question) else f"رقم الوظيفة: {job_id}")
    return "\n".join(lines)


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
        "intent": "smart_resume",
        "stems": ["سير", "cv", "ذكي", "انشاء", "انشئ", "اعمل", "اصنع"],
        "terms": ["create smart resume", "smart resume", "resume builder", "ai resume", "create resume", "generate resume", "no cv", "no resume", "do not have cv", "dont have cv", "don't have cv", "إنشاء سيرة ذكية", "انشاء سيرة ذكية", "سيرة ذكية", "السي في", "سي في", "ليس لدي سيرة", "ليس عندي سيرة", "لا يوجد لدي سي في", "لا املك سيرة", "ماهو انشاء سيرة ذكية", "ما هو انشاء سيرة ذكية", "ساعدني في السيرة", "اعمل سيرة", "أنشئ سيرة", "انشئ سيرة"],
        "answer": "إذا لم يكن لديك سيرة ذاتية، استخدم إنشاء سيرة ذكية داخل روابط:\n1. افتح القائمة أو مساحة العمل واختر إنشاء سيرة ذكية.\n2. قبل الإنشاء، حاول إكمال ملفك بإضافة المسمى المهني، النبذة، المهارات، تاريخ العمل، التعليم، الدورات، والشهادات.\n3. ستجد أن النظام يسحب المهارات وتاريخ العمل من ملفك تلقائيا.\n4. أضف أي شهادات مع التواريخ، مشاريع، أدوات تستخدمها، إنجازات، ولغات.\n5. اضغط تحميل السيرة.\n6. سيستخدم الذكاء الاصطناعي معلومات ملفك والمعلومات التي كتبتها لصياغة نقاط احترافية وإنشاء ملف PDF.\n7. السيرة الذكية يتم تحميلها مباشرة ولا تُحفظ تلقائيا ضمن مرفقاتك.\n8. إذا أردت استخدامها في التقديم، ارفع ملف PDF الناتج في قسم السيرة الذاتية داخل الملف.\n9. يمكنك الاحتفاظ بما يصل إلى سيرتين ذاتيتين مرفوعتين في ملفك واختيار أي واحدة عند التقديم على وظيفة."
    },
    {
        "intent": "resume",
        "stems": ["سير", "cv"],
        "terms": ["resume", "cv", "سيرة", "السيرة", "السيرة الذاتية", "سيرتي", "تعديل سيرتي", "ارفع سيرتي"],
        "answer": "لرفع السيرة الذاتية:\n1. افتح الملف أو أكمل الملف.\n2. اختر حقل السيرة الذاتية.\n3. ارفع ملف PDF أو DOC أو DOCX.\n4. يمكنك الاحتفاظ بما يصل إلى سيرتين ذاتيتين في ملفك.\n5. عند التقديم على وظيفة يمكنك اختيار السيرة التي تريد إرسالها.\n6. إذا لم يكن لديك سيرة جاهزة، استخدم إنشاء سيرة ذكية أولا لتحميل PDF ثم ارفعه في ملفك."
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
        "answer": "لمتابعة المقابلات كمستخدم:\n1. عندما يتم تحديد مقابلة لك، تظهر في الصفحة الرئيسية ضمن المقابلات القادمة.\n2. ستصلك رسالة بريد تحتوي على معلومات المقابلة إذا كان بريدك صحيحا.\n3. تظهر الوظيفة المرتبطة بالمقابلة بشكل مميز حتى تنتبه لها.\n4. إذا تغيرت نتيجة المقابلة إلى مقبول أو مرفوض، يتم تحديث حالة طلبك وتختفي من المقابلات القادمة."
    },
    {
        "terms": ["support", "chat", "clear chat", "live support", "دعم", "محادثة", "مسح المحادثة", "دعم مباشر"],
        "answer": "لاستخدام المساعد الذكي:\n1. اضغط المساعد الذكي من الشريط العلوي.\n2. اكتب سؤالك عن منصة روابط أو الوظائف المتاحة.\n3. سيجيبك المساعد بخطوات واضحة عن استخدام المنصة.\n4. إذا لم يجد جوابا سيعرض خيار التحدث مع دعم مباشر أو إنهاء المحادثة.\n5. عند اختيار الدعم المباشر، اكتب رسالتك وسيظهر رد فريق الدعم داخل نفس المحادثة.\n6. لمسح المحادثة اضغط مسح المحادثة."
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
        "answer": "حول الخطة في روابط:\n1. قد يظهر حسابك بخطة مجاني أو مميز.\n2. الخطة تظهر ضمن بيانات حسابك عند مراجعة الملف.\n3. إذا أردت تغيير الخطة أو معرفة الصلاحيات المتاحة لك، تواصل مع الدعم المباشر.\n4. لا يمكن للمستخدم تغيير الخطة بنفسه من واجهة المستخدم."
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
    wants_end = ["end conversation", "close chat", "انهاء", "إنهاء", "انهي", "إنهي", "نهاية"]
    restricted_terms = [
        "admin", "administrator", "agent", "dashboard", "analytics", "report", "reports", "manage users", "user management",
        "add job", "edit job", "delete job", "manage job", "post job", "approve", "reject application", "application management",
        "إدارة المستخدمين", "ادارة المستخدمين", "لوحة الإدارة", "لوحة الادارة", "تحليلات", "تقارير", "وكيل", "الوكيل", "مدير", "الإدارة", "الادارة"
    ]
    if any(term in lowered or normalize_arabic_text(term) in normalized_question for term in restricted_terms):
        return unknown_reply_for(question)
    if is_live_support_request(question):
        return LIVE_AGENT_REPLY
    if any(term in lowered or normalize_arabic_text(term) in normalized_question for term in wants_end):
        return END_CHAT_REPLY
    smart_resume_terms = [
        "smart resume", "resume builder", "ai resume", "create resume", "generate resume", "no cv", "no resume",
        "do not have cv", "dont have cv", "don't have cv", "انشاء سيره ذكيه", "سيره ذكيه", "السي في",
        "سي في", "لا يوجد لدي سي في", "ليس لدي سيره", "ليس عندي سيره", "لا املك سيره", "ساعدني في السيره",
        "ماهو انشاء سيره ذكيه", "ما هو انشاء سيره ذكيه", "اعمل سيره", "انشي سيره", "انشاء سيره"
    ]
    if any(term in lowered or normalize_arabic_text(term) in normalized_question for term in smart_resume_terms):
        smart_guide = next((guide for guide in RAWABET_GUIDES if guide.get("intent") == "smart_resume"), None)
        if smart_guide:
            return smart_guide["answer"]
    detailed_job_terms = ["description", "details", "salary", "requirements", "وصف", "تفاصيل", "راتب", "شروط", "متطلبات", "معلومات"]
    job_terms = ["job", "jobs", "وظيفة", "وظائف"]
    if any(term in lowered or normalize_arabic_text(term) in normalized_question for term in detailed_job_terms) and any(term in lowered or normalize_arabic_text(term) in normalized_question for term in job_terms):
        return None
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
    greeting = greeting_reply(question)
    if greeting:
        return greeting
    platform_terms = [
        "rawabet", "روابط", "platform", "profile", "resume", "cv", "certificate", "job", "jobs", "apply", "application",
        "interview", "support", "plan", "premium", "free", "status", "otp", "register",
        "login", "upload", "attachment", "photo", "avatar", "skill", "experience", "salary", "category", "filter",
        "ملف", "وظيفة", "وظائف", "تقديم", "اتقدم", "اقدم", "التقدم", "قدم", "ارشدني", "مناسب", "مناسبا", "طلب", "طلبات", "حالة", "مقابلة", "دعم", "شهادة", "شهادات", "سيرة", "سيره", "سي في",
        "الخطة", "مميز", "مجاني", "الحالة", "تسجيل", "دخول", "تحقق", "رمز", "رفع", "مرفق", "مرفقات", "صورة", "صورتي", "صور",
        "مهارات", "خبرات", "راتب", "فئة", "بحث", "فلتر"
    ]
    if not any(term in lowered or normalize_arabic_text(term) in normalized_question for term in platform_terms):
        return unknown_reply_for(question)
    job_match_reply = matching_jobs_reply(question)
    if job_match_reply:
        return job_match_reply
    local_reply = local_platform_reply(question)
    if local_reply:
        return local_reply
    fallback = unknown_reply_for(question)
    if not OPENAI_API_KEY:
        return fallback
    context = f"{RAWABET_CONTEXT}\n\n{active_jobs_context()}\n\n{active_agents_context()}"
    unknown = unknown_reply_for(question)
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": f"You are Rawabet's AI assistant for normal platform users only. Act like a helpful human support assistant and try to resolve common user questions before offering live support. Answer only from the context below. Do not answer admin, agent, internal dashboard, analytics, or management questions. Use Arabic by default unless the user writes English. If you use bullets or numbered steps, every bullet or step must be on its own separate line. If the user asks about jobs, search the active jobs context semantically by title, company, category, location, and description; include matching job numbers only when available. If no active jobs match, say there are no matching jobs at this moment and suggest trying another keyword or checking Jobs later; do not offer live support for a normal no-match job search. If the user asks about companies/agencies, use the public companies/agencies context. If the user asks how to use the platform, guide them step by step using user-facing page and button names. If the user asks something truly outside Rawabet, reply exactly with: {unknown}\n\n{context}"},
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
            SELECT j.id, j.job_number, j.company_name, j.title, j.category, j.location, j.type, j.salary_range, j.description, j.status, j.created_at,
                   COALESCE(j.screening_questions, '[]'::jsonb) AS screening_questions,
                   COALESCE(assignments.agents, '[]'::jsonb) AS assigned_agents
            FROM jobs j
            LEFT JOIN LATERAL (
              SELECT jsonb_agg(jsonb_build_object('id', u.id, 'full_name', u.full_name) ORDER BY u.full_name) AS agents
              FROM agent_job_assignments aja
              JOIN users u ON u.id = aja.agent_id
              WHERE aja.job_id = j.id
            ) assignments ON true
            {outer_where}
            ORDER BY j.created_at DESC
            """
        )
    return fetch_all(
        f"""
        SELECT *
        FROM (
          SELECT id,
            (1000 + ROW_NUMBER() OVER (ORDER BY created_at ASC))::int AS job_number,
            company_name, title, category, location, type, salary_range, description, status, created_at,
            COALESCE(screening_questions, '[]'::jsonb) AS screening_questions,
            '[]'::jsonb AS assigned_agents
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
    resume_profile_columns = resume_profile_select_sql()
    profile = fetch_one(
        f"""
        SELECT about, skills, languages, profile_strength, agency_name, agency_about, website,
               {resume_profile_columns}
        FROM profiles
        WHERE user_id = %s
        """,
        (user["id"],),
    )
    experiences = fetch_all("SELECT * FROM experiences WHERE user_id = %s ORDER BY start_date DESC NULLS LAST", (user["id"],))
    education = fetch_all("SELECT * FROM education WHERE user_id = %s ORDER BY end_year DESC NULLS LAST", (user["id"],))
    courses = fetch_all("SELECT * FROM courses WHERE user_id = %s ORDER BY completion_date DESC NULLS LAST, created_at DESC", (user["id"],))
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
          a.resume_document_id, rd.file_name AS resume_file_name,
          CASE WHEN rd.file_path IS NULL THEN NULL ELSE '/uploads/' || split_part(rd.file_path, '/', array_length(string_to_array(rd.file_path, '/'), 1)) END AS resume_file_url,
          j.id AS job_id, {job_number_select}, j.company_name, j.title, j.category, j.location, j.type, j.salary_range, j.description,
          j.status AS job_status, COALESCE(j.screening_questions, '[]'::jsonb) AS screening_questions
        FROM applications a
        JOIN jobs j ON j.id = a.job_id
        LEFT JOIN documents rd ON rd.id = a.resume_document_id
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
    return {"user": public_user(user), "profile": profile, "experiences": experiences, "education": education, "courses": courses, "documents": documents, "applications": applications, "interviews": interviews, "stats": stats}


@app.put("/api/account/profile")
def update_profile(body: ProfileBody, user: Annotated[dict, Depends(current_user)]):
    execute(
        "UPDATE users SET full_name = %s, phone = %s, dob = %s, headline = %s, location = %s WHERE id = %s",
        (body.fullName, body.phone, body.dob or None, body.headline, body.location, user["id"]),
    )
    if resume_profile_columns_available():
        execute(
            """
            INSERT INTO profiles (
              user_id, about, skills, languages, resume_education, resume_certifications,
              resume_tools, resume_additional_info, profile_strength, updated_at
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            ON CONFLICT (user_id) DO UPDATE
            SET about = EXCLUDED.about, skills = EXCLUDED.skills, languages = EXCLUDED.languages,
                resume_education = EXCLUDED.resume_education,
                resume_certifications = EXCLUDED.resume_certifications,
                resume_tools = EXCLUDED.resume_tools,
                resume_additional_info = EXCLUDED.resume_additional_info,
                profile_strength = EXCLUDED.profile_strength, updated_at = NOW()
            """,
            (
                user["id"], body.about, body.skills, body.languages, body.resumeEducation,
                body.resumeCertifications, body.resumeTools, body.resumeAdditionalInfo,
                calculate_profile_strength(user["id"]),
            ),
        )
    else:
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
        (
            user["id"],
            body.title,
            body.company,
            body.location,
            empty_to_none(body.startDate),
            None if body.isCurrent else empty_to_none(body.endDate),
            body.isCurrent,
            body.description,
        ),
    )
    sync_profile_strength(user["id"])
    return experience


@app.put("/api/account/experience/{experience_id}")
def update_experience(experience_id: UUID, body: ExperienceBody, user: Annotated[dict, Depends(current_user)]):
    experience = execute(
        """
        UPDATE experiences
        SET title = %s, company = %s, location = %s, start_date = %s, end_date = %s, is_current = %s, description = %s
        WHERE id = %s AND user_id = %s
        RETURNING *
        """,
        (
            body.title,
            body.company,
            body.location,
            empty_to_none(body.startDate),
            None if body.isCurrent else empty_to_none(body.endDate),
            body.isCurrent,
            body.description,
            experience_id,
            user["id"],
        ),
    )
    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")
    sync_profile_strength(user["id"])
    return experience


@app.delete("/api/account/experience/{experience_id}")
def delete_experience(experience_id: UUID, user: Annotated[dict, Depends(current_user)]):
    deleted = execute("DELETE FROM experiences WHERE id = %s AND user_id = %s RETURNING id", (experience_id, user["id"]))
    if not deleted:
        raise HTTPException(status_code=404, detail="Experience not found")
    sync_profile_strength(user["id"])
    return {"ok": True}


@app.post("/api/account/education", status_code=201)
def add_education(body: EducationBody, user: Annotated[dict, Depends(current_user)]):
    education = execute(
        """
        INSERT INTO education (user_id, school, degree, field, start_year, end_year)
        VALUES (%s,%s,%s,%s,%s,%s)
        RETURNING *
        """,
        (
            user["id"],
            body.school,
            body.degree,
            empty_to_none(body.field),
            optional_year(body.startYear),
            optional_year(body.endYear),
        ),
    )
    sync_profile_strength(user["id"])
    return education


@app.put("/api/account/education/{education_id}")
def update_education(education_id: UUID, body: EducationBody, user: Annotated[dict, Depends(current_user)]):
    education = execute(
        """
        UPDATE education
        SET school = %s, degree = %s, field = %s, start_year = %s, end_year = %s
        WHERE id = %s AND user_id = %s
        RETURNING *
        """,
        (
            body.school,
            body.degree,
            empty_to_none(body.field),
            optional_year(body.startYear),
            optional_year(body.endYear),
            education_id,
            user["id"],
        ),
    )
    if not education:
        raise HTTPException(status_code=404, detail="Education not found")
    sync_profile_strength(user["id"])
    return education


@app.delete("/api/account/education/{education_id}")
def delete_education(education_id: UUID, user: Annotated[dict, Depends(current_user)]):
    deleted = execute("DELETE FROM education WHERE id = %s AND user_id = %s RETURNING id", (education_id, user["id"]))
    if not deleted:
        raise HTTPException(status_code=404, detail="Education not found")
    sync_profile_strength(user["id"])
    return {"ok": True}


@app.post("/api/account/resume-builder", status_code=201)
def build_resume_pdf(body: ResumeBuilderBody, user: Annotated[dict, Depends(current_user)]):
    if user.get("role") in {"admin", "master_admin", "agent"}:
        raise HTTPException(status_code=403, detail="Smart resume is available for user accounts only")
    resume_profile_columns = resume_profile_select_sql()
    profile = fetch_one(
        f"""
        SELECT about, skills, languages, {resume_profile_columns}
        FROM profiles
        WHERE user_id = %s
        """,
        (user["id"],),
    ) or {}
    body = ResumeBuilderBody(
        summary=body.summary if body.summary is not None else profile.get("about"),
        education=body.education if body.education is not None else profile.get("resume_education"),
        certifications=body.certifications if body.certifications is not None else profile.get("resume_certifications"),
        tools=body.tools if body.tools is not None else profile.get("resume_tools"),
        languages=body.languages if body.languages is not None else "\n".join(profile.get("languages") or []),
        additionalInfo=body.additionalInfo if body.additionalInfo is not None else profile.get("resume_additional_info"),
    )
    experiences = fetch_all(
        """
        SELECT title, company, location, start_date, end_date, is_current, description
        FROM experiences
        WHERE user_id = %s
        ORDER BY start_date DESC NULLS LAST
        LIMIT 8
        """,
        (user["id"],),
    )
    education = fetch_all("SELECT * FROM education WHERE user_id = %s ORDER BY end_year DESC NULLS LAST", (user["id"],))
    courses = fetch_all("SELECT * FROM courses WHERE user_id = %s ORDER BY completion_date DESC NULLS LAST, created_at DESC", (user["id"],))
    try:
        pdf = make_resume_pdf(user, profile, experiences, education, courses, body)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Smart resume PDF dependencies are missing or incomplete: {exc}. Install requirements and Arabic fonts, then restart Rawabet backend.",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Smart resume PDF could not be generated: {exc}",
        )
    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "-", user.get("full_name") or "rawabet").strip("-").lower() or "rawabet"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}-smart-resume.pdf"'},
    )


@app.post("/api/account/documents", status_code=201)
async def upload_document(
    user: Annotated[dict, Depends(current_user)],
    kind: Annotated[str, Form()] = "resume",
    file: UploadFile = File(...),
):
    safe_kind = "certificate" if kind == "certificate" else "resume"
    if safe_kind == "resume":
        if resume_count_for(user["id"]) >= 2:
            raise HTTPException(status_code=400, detail="You can upload up to 2 resumes")
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


@app.delete("/api/account/documents/{document_id}")
def delete_account_document(document_id: UUID, user: Annotated[dict, Depends(current_user)]):
    document = execute(
        """
        DELETE FROM documents
        WHERE id = %s AND user_id = %s AND kind IN ('resume', 'certificate')
        RETURNING user_id, file_path
        """,
        (document_id, user["id"]),
    )
    if not document:
        raise HTTPException(status_code=404, detail="Attachment not found")
    delete_upload_file(document.get("file_path"))
    sync_profile_strength(document["user_id"])
    return {"ok": True}


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


@app.get("/api/agents")
def list_public_agents(user: Annotated[dict, Depends(current_user)], search: str = ""):
    query = f"%{search.strip()}%"
    return fetch_all(
        """
        SELECT u.id, u.full_name, u.email, u.headline, u.location, u.avatar_url,
               p.about, p.agency_name, p.agency_about, p.website,
               (
                 SELECT COUNT(*)::int
                 FROM jobs j
                 WHERE j.status = 'active'
                   AND (
                     j.company_name ILIKE ('%%' || COALESCE(NULLIF(p.agency_name, ''), u.full_name) || '%%')
                     OR j.company_name ILIKE ('%%' || u.full_name || '%%')
                     OR j.id IN (SELECT job_id FROM agent_job_assignments WHERE agent_id = u.id)
                   )
               ) AS open_jobs
        FROM users u
        LEFT JOIN profiles p ON p.user_id = u.id
        WHERE u.role = 'agent'
          AND u.status IN ('active', 'verified')
          AND (%s = '%%' OR u.full_name ILIKE %s OR COALESCE(p.agency_name, '') ILIKE %s)
        ORDER BY open_jobs DESC, u.full_name
        LIMIT 50
        """,
        (query, query, query),
    )


@app.get("/api/agents/{agent_id}")
def get_public_agent(agent_id: UUID, user: Annotated[dict, Depends(current_user)]):
    agent = fetch_one(
        """
        SELECT u.id, u.full_name, u.email, u.headline, u.location, u.avatar_url,
               p.about, p.agency_name, p.agency_about, p.website
        FROM users u
        LEFT JOIN profiles p ON p.user_id = u.id
        WHERE u.id = %s AND u.role = 'agent' AND u.status IN ('active', 'verified')
        """,
        (agent_id,),
    )
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    company_terms = [f"%{agent.get('agency_name') or agent.get('full_name')}%", f"%{agent.get('full_name')}%"]
    jobs = fetch_all(
        """
        SELECT id, job_number, company_name, title, category, location, type, salary_range, description, status, created_at,
               COALESCE(screening_questions, '[]'::jsonb) AS screening_questions
        FROM jobs
        WHERE status = 'active'
          AND (
            company_name ILIKE %s
            OR company_name ILIKE %s
            OR id IN (SELECT job_id FROM agent_job_assignments WHERE agent_id = %s)
          )
        ORDER BY created_at DESC
        """,
        (company_terms[0] or company_terms[1], company_terms[1], agent_id),
    )
    return {"agent": agent, "jobs": jobs}


@app.get("/api/admin/jobs")
def list_admin_jobs(user: Annotated[dict, Depends(admin_user)]):
    return list_jobs_with_number()


@app.post("/api/admin/job-assignments", status_code=201)
def assign_job_to_agent(body: JobAgentBody, user: Annotated[dict, Depends(admin_user)]):
    agent = fetch_one("SELECT id FROM users WHERE id = %s AND role = 'agent'", (body.agentId,))
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    job = fetch_one("SELECT id FROM jobs WHERE id = %s", (body.jobId,))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return execute(
        """
        INSERT INTO agent_job_assignments (agent_id, job_id, assigned_by)
        VALUES (%s,%s,%s)
        ON CONFLICT (agent_id, job_id) DO UPDATE
        SET assigned_by = EXCLUDED.assigned_by, created_at = NOW()
        RETURNING *
        """,
        (body.agentId, body.jobId, user["id"]),
    )


@app.post("/api/jobs/{job_id}/apply", status_code=201)
def apply_to_job(job_id: UUID, body: ApplyBody, user: Annotated[dict, Depends(current_user)]):
    job = fetch_one("SELECT id, COALESCE(screening_questions, '[]'::jsonb) AS screening_questions FROM jobs WHERE id = %s AND status = 'active'", (job_id,))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if body.resumeDocumentId:
        resume = fetch_one("SELECT id FROM documents WHERE id = %s AND user_id = %s AND kind = 'resume'", (body.resumeDocumentId, user["id"]))
        if not resume:
            raise HTTPException(status_code=400, detail="Selected resume was not found")
    questions = job.get("screening_questions") or []
    answers_by_question = {str(item.get("question", "")).strip(): str(item.get("answer", "")).strip() for item in body.answers}
    missing = [question for question in questions if not answers_by_question.get(str(question).strip())]
    if missing:
        raise HTTPException(status_code=400, detail="Please answer all application questions")
    answers = [{"question": str(question), "answer": answers_by_question.get(str(question).strip(), "")} for question in questions]
    execute(
        """
        INSERT INTO applications (job_id, user_id, screening_answers, resume_document_id)
        VALUES (%s,%s,%s::jsonb,%s)
        ON CONFLICT (job_id, user_id) DO UPDATE
        SET screening_answers = EXCLUDED.screening_answers,
            resume_document_id = EXCLUDED.resume_document_id
        """,
        (job_id, user["id"], json.dumps(answers), body.resumeDocumentId),
    )
    return {"ok": True}


@app.get("/api/admin/applications")
def list_admin_applications(user: Annotated[dict, Depends(admin_user)]):
    return fetch_all(
        """
        SELECT
          a.id, a.status, a.created_at, COALESCE(a.screening_answers, '[]'::jsonb) AS screening_answers,
          a.resume_document_id, rd.file_name AS resume_file_name,
          CASE WHEN rd.file_path IS NULL THEN NULL ELSE '/uploads/' || split_part(rd.file_path, '/', array_length(string_to_array(rd.file_path, '/'), 1)) END AS resume_file_url,
          u.id AS user_id, u.full_name, u.email, u.headline, u.avatar_url,
          j.id AS job_id, j.title AS job_title, j.company_name, j.location,
          COALESCE(j.screening_questions, '[]'::jsonb) AS screening_questions
        FROM applications a
        JOIN users u ON u.id = a.user_id
        JOIN jobs j ON j.id = a.job_id
        LEFT JOIN documents rd ON rd.id = a.resume_document_id
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
          a.resume_document_id,
          rd.file_name AS resume_file_name,
          CASE WHEN rd.file_path IS NULL THEN NULL ELSE '/uploads/' || split_part(rd.file_path, '/', array_length(string_to_array(rd.file_path, '/'), 1)) END AS resume_file_url,
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
        LEFT JOIN documents rd ON rd.id = a.resume_document_id
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


@app.put("/api/agent/profile")
def update_agent_profile(body: AgentProfileBody, user: Annotated[dict, Depends(agent_user)]):
    execute(
        "UPDATE users SET headline = COALESCE(%s, headline), location = COALESCE(%s, location) WHERE id = %s",
        (body.headline, body.location, user["id"]),
    )
    current = fetch_one("SELECT about, skills, languages FROM profiles WHERE user_id = %s", (user["id"],)) or {}
    execute(
        """
        INSERT INTO profiles (user_id, about, skills, languages, agency_name, agency_about, website, profile_strength, updated_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW())
        ON CONFLICT (user_id) DO UPDATE
        SET about = EXCLUDED.about,
            skills = EXCLUDED.skills,
            languages = EXCLUDED.languages,
            agency_name = EXCLUDED.agency_name,
            agency_about = EXCLUDED.agency_about,
            website = EXCLUDED.website,
            updated_at = NOW()
        """,
        (
            user["id"],
            body.about if body.about is not None else current.get("about", ""),
            current.get("skills", []),
            current.get("languages", ["English", "Arabic"]),
            body.agencyName,
            body.agencyAbout,
            body.website,
            calculate_profile_strength(user["id"]),
        ),
    )
    return {"ok": True}


@app.get("/api/agent/jobs")
def list_agent_jobs(user: Annotated[dict, Depends(agent_user)]):
    job_number_expr = "j.job_number" if jobs_have_job_number_column() else "NULL::integer AS job_number"
    return fetch_all(
        f"""
        SELECT
          j.id,
          {job_number_expr},
          j.company_name,
          j.title,
          j.category,
          j.location,
          j.type,
          j.salary_range,
          j.description,
          j.status,
          j.created_at,
          COALESCE(j.screening_questions, '[]'::jsonb) AS screening_questions
        FROM jobs j
        JOIN agent_job_assignments aja ON aja.job_id = j.id
        WHERE aja.agent_id = %s AND j.status = 'active'
        ORDER BY j.created_at DESC
        """,
        (user["id"],),
    )


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
    courses = fetch_all("SELECT * FROM courses WHERE user_id = %s ORDER BY completion_date DESC NULLS LAST, created_at DESC", (user_id,))
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
    return {"user": target_user, "profile": profile, "experiences": experiences, "education": education, "courses": courses, "documents": documents}


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
        if resume_count_for(user_id) >= 2:
            raise HTTPException(status_code=400, detail="You can upload up to 2 resumes")
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


@app.post("/api/courses", status_code=201)
def add_course(body: CourseBody, user: Annotated[dict, Depends(current_user)]):
    if user["role"] not in {"admin", "master_admin", "agent"}:
        raise HTTPException(status_code=403, detail="Only admin or agent can add courses")
    if user["role"] == "agent" and not agent_can_access_user_job(user["id"], body.userId):
        raise HTTPException(status_code=403, detail="This user is not shared with this agent")
    if not fetch_one("SELECT id FROM users WHERE id = %s", (body.userId,)):
        raise HTTPException(status_code=404, detail="User not found")
    added_by = user["id"]
    if user["role"] in {"admin", "master_admin"} and body.addedById:
        owner = fetch_one("SELECT id, role FROM users WHERE id = %s", (body.addedById,))
        if not owner or owner["role"] not in {"agent", "admin", "master_admin"}:
            raise HTTPException(status_code=400, detail="Course owner must be an agent or admin")
        added_by = owner["id"]
    return execute(
        """
        INSERT INTO courses (user_id, added_by, title, provider, completion_date, certificate_url, notes)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        RETURNING *
        """,
        (body.userId, added_by, body.title, body.provider, body.completionDate or None, body.certificateUrl, body.notes),
    )


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
    was_live = live_support_requested(target_user_id) if sender_role == "user" else False
    requested_live = is_live_support_request(body.message) if sender_role == "user" else False
    message = execute(
        """
        INSERT INTO support_messages (user_id, sender_role, message)
        VALUES (%s,%s,%s)
        RETURNING *
        """,
        (target_user_id, sender_role, body.message),
    )
    bot_reply = None
    if sender_role == "user" and requested_live:
        bot_reply = execute(
            """
            INSERT INTO support_messages (user_id, sender_role, message)
            VALUES (%s,'bot',%s)
            RETURNING *
            """,
            (target_user_id, LIVE_AGENT_REPLY),
        )
    elif sender_role == "user" and not was_live:
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
