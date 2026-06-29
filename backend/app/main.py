from pathlib import Path
from uuid import uuid4
from typing import Annotated
from uuid import UUID
from email.message import EmailMessage
import json
import secrets
import smtplib
import urllib.error
import urllib.request

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr

from .auth import admin_user, create_token, current_user, hash_password, public_user, verify_password
from .config import OPENAI_API_KEY, SMTP_FROM, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER, UPLOAD_DIR
from .db import execute, fetch_all, fetch_one


UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Rawabet API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://35.174.9.208:5173",
    "http://35.174.9.208",
    "http://rawabet-sy.com",
    "http://www.rawabet-sy.com",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


def ensure_runtime_schema():
    for sql in (
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS phone TEXT",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS dob DATE",
        "ALTER TABLE pending_registrations ADD COLUMN IF NOT EXISTS phone TEXT",
        "ALTER TABLE pending_registrations ADD COLUMN IF NOT EXISTS dob DATE",
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
    phone: str | None = None
    dob: str | None = None
    headline: str | None = None
    location: str | None = None
    role: str | None = None
    plan: str | None = None
    status: str | None = None


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


class InterviewBody(BaseModel):
    userId: UUID
    jobId: UUID | None = None
    scheduledAt: str
    channel: str = "Video call"
    notes: str | None = None


class ApplicationStatusBody(BaseModel):
    status: str


class SupportMessageBody(BaseModel):
    message: str
    userId: UUID | None = None


class ClearSupportBody(BaseModel):
    userId: UUID | None = None


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
            SELECT id, job_number, company_name, title, category, location, type, salary_range, description, status, created_at
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
            company_name, title, category, location, type, salary_range, description, status, created_at
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
    execute("UPDATE users SET last_active_at = NOW() WHERE id = %s", (user["id"],))
    return {"user": public_user(user), "token": create_token(user)}


@app.get("/api/auth/login")
def login_get_hint():
    return {"detail": "Login requires the Rawabet frontend form. Open http://35.174.9.208:5173 and sign in there."}


@app.get("/api/me")
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
    applications = fetch_all(
        """
        SELECT a.id, a.status, a.created_at, j.id AS job_id, j.company_name, j.title, j.category, j.location, j.type, j.salary_range, j.description, j.status AS job_status
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


@app.put("/api/me/profile")
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


@app.post("/api/me/experience", status_code=201)
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


@app.post("/api/me/documents", status_code=201)
async def upload_document(
    user: Annotated[dict, Depends(current_user)],
    kind: Annotated[str, Form()] = "resume",
    file: UploadFile = File(...),
):
    safe_kind = "certificate" if kind == "certificate" else "resume"
    if safe_kind == "resume":
        old_documents = fetch_all("SELECT id, file_path FROM documents WHERE user_id = %s AND kind = 'resume'", (user["id"],))
        for old_document in old_documents:
            if old_document.get("file_path"):
                Path(old_document["file_path"]).unlink(missing_ok=True)
        execute("DELETE FROM documents WHERE user_id = %s AND kind = 'resume'", (user["id"],))
    else:
        certificate_count = fetch_one("SELECT COUNT(*)::int AS count FROM documents WHERE user_id = %s AND kind = 'certificate'", (user["id"],))["count"]
        if certificate_count >= 5:
            raise HTTPException(status_code=400, detail="You can upload up to 5 certificates")

    original_name = file.filename or safe_kind
    suffix = Path(original_name).suffix
    target = UPLOAD_DIR / f"{user['id']}_{safe_kind}_{uuid4().hex}{suffix}"
    content = await file.read()
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


@app.post("/api/me/avatar")
async def upload_avatar(user: Annotated[dict, Depends(current_user)], file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Profile picture must be an image")
    if user.get("avatar_url"):
        old_avatar = UPLOAD_DIR / Path(user["avatar_url"]).name
        old_avatar.unlink(missing_ok=True)
    suffix = Path(file.filename or "avatar").suffix.lower() or ".jpg"
    target = UPLOAD_DIR / f"{user['id']}_avatar_{uuid4().hex}{suffix}"
    content = await file.read()
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
def apply_to_job(job_id: UUID, user: Annotated[dict, Depends(current_user)]):
    execute("INSERT INTO applications (job_id, user_id) VALUES (%s,%s) ON CONFLICT (job_id, user_id) DO NOTHING", (job_id, user["id"]))
    return {"ok": True}


@app.get("/api/admin/applications")
def list_admin_applications(user: Annotated[dict, Depends(admin_user)]):
    return fetch_all(
        """
        SELECT
          a.id, a.status, a.created_at,
          u.id AS user_id, u.full_name, u.email, u.headline, u.avatar_url,
          j.id AS job_id, j.title AS job_title, j.company_name, j.location
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
    updated = execute(
        """
        UPDATE users
        SET full_name = COALESCE(%s, full_name),
            email = COALESCE(%s, email),
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
        (body.fullName, str(body.email).lower() if body.email else None, body.phone, body.dob or None, body.headline, body.location, body.role, body.plan, body.status, user_id),
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
            if old_document.get("file_path"):
                Path(old_document["file_path"]).unlink(missing_ok=True)
        execute("DELETE FROM documents WHERE user_id = %s AND kind = 'resume'", (user_id,))
    else:
        certificate_count = fetch_one("SELECT COUNT(*)::int AS count FROM documents WHERE user_id = %s AND kind = 'certificate'", (user_id,))["count"]
        if certificate_count >= 5:
            raise HTTPException(status_code=400, detail="You can upload up to 5 certificates")
    original_name = file.filename or safe_kind
    suffix = Path(original_name).suffix
    target = UPLOAD_DIR / f"{user_id}_{safe_kind}_{uuid4().hex}{suffix}"
    content = await file.read()
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
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Profile picture must be an image")
    if target_user.get("avatar_url"):
        (UPLOAD_DIR / Path(target_user["avatar_url"]).name).unlink(missing_ok=True)
    suffix = Path(file.filename or "avatar").suffix.lower() or ".jpg"
    target = UPLOAD_DIR / f"{user_id}_avatar_{uuid4().hex}{suffix}"
    content = await file.read()
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
    if document.get("file_path"):
        Path(document["file_path"]).unlink(missing_ok=True)
    sync_profile_strength(document["user_id"])
    return {"ok": True}


@app.patch("/api/admin/users/{user_id}")
def update_admin_user(user_id: UUID, body: AdminUserPatch, user: Annotated[dict, Depends(admin_user)]):
    updated = execute(
        """
        UPDATE users
        SET full_name = COALESCE(%s, full_name),
            email = COALESCE(%s, email),
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
        (body.fullName, str(body.email).lower() if body.email else None, body.phone, body.dob or None, body.headline, body.location, body.role, body.plan, body.status, user_id),
    )
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


@app.delete("/api/admin/users/{user_id}")
def delete_admin_user(user_id: UUID, user: Annotated[dict, Depends(admin_user)]):
    if str(user_id) == str(user["id"]):
        raise HTTPException(status_code=400, detail="You cannot delete your own admin account")
    target_user = fetch_one("SELECT id, email, avatar_url FROM users WHERE id = %s", (user_id,))
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    documents = fetch_all("SELECT file_path FROM documents WHERE user_id = %s", (user_id,))
    for document in documents:
        if document.get("file_path"):
            Path(document["file_path"]).unlink(missing_ok=True)
    if target_user.get("avatar_url"):
        (UPLOAD_DIR / Path(target_user["avatar_url"]).name).unlink(missing_ok=True)
    deleted = execute("DELETE FROM users WHERE id = %s RETURNING id, email", (user_id,))
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    still_exists = fetch_one("SELECT id FROM users WHERE email = %s", (target_user["email"],))
    return {"ok": True, "deletedEmail": deleted["email"], "emailAvailable": still_exists is None}


@app.post("/api/admin/jobs", status_code=201)
def create_admin_job(body: JobBody, user: Annotated[dict, Depends(admin_user)]):
    return execute(
        """
        INSERT INTO jobs (company_name, title, category, location, type, salary_range, description, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING *
        """,
        (body.companyName, body.title, body.category, body.location, body.type, body.salaryRange, body.description, body.status),
    )


@app.patch("/api/admin/jobs/{job_id}")
def update_admin_job(job_id: UUID, body: JobBody, user: Annotated[dict, Depends(admin_user)]):
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
            status = %s
        WHERE id = %s
        RETURNING *
        """,
        (body.companyName, body.title, body.category, body.location, body.type, body.salaryRange, body.description, body.status, job_id),
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
    target_user_id = user_id if user["role"] == "admin" and user_id else user["id"]
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
    target_user_id = body.userId if user["role"] == "admin" and body.userId else user["id"]
    sender_role = "admin" if user["role"] == "admin" else "user"
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
    target_user_id = user_id if user["role"] == "admin" and user_id else user["id"]
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
