from pathlib import Path
from uuid import uuid4
from typing import Annotated
from uuid import UUID
from email.message import EmailMessage
import secrets
import smtplib

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr

from .auth import admin_user, create_token, current_user, hash_password, public_user, verify_password
from .config import SMTP_FROM, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER, UPLOAD_DIR
from .db import execute, fetch_all, fetch_one

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Rawabet API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


class RegisterBody(BaseModel):
    fullName: str
    email: EmailStr
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


@app.get("/api/health")
def health():
    return {"ok": True, "service": "rawabet-python-api"}


def send_verification_email(email: str, otp: str) -> tuple[bool, str | None]:
    if not SMTP_HOST or not SMTP_PASSWORD or SMTP_PASSWORD == "PUT_GMAIL_APP_PASSWORD_HERE":
        return False, "SMTP is not configured."
    message = EmailMessage()
    message["Subject"] = "Rawabet verification code"
    message["From"] = SMTP_FROM
    message["To"] = email
    message.set_content(f"Your Rawabet verification code is: {otp}\n\nThis code expires in 15 minutes.")
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
        (body.fullName, body.email.lower(), hash_password(body.password), body.role, hash_password(otp)),
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
    if not pending or not verify_password(body.otp, pending["otp_hash"]):
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    if fetch_one("SELECT id FROM users WHERE email = %s", (pending["email"],)):
        execute("DELETE FROM pending_registrations WHERE id = %s", (pending["id"],))
        raise HTTPException(status_code=409, detail="Email already registered")
    verified_user = execute(
        """
        INSERT INTO users (full_name, email, password_hash, role, status, email_verified)
        VALUES (%s,%s,%s,%s,'active',true)
        RETURNING id, full_name, email, role, plan, status, headline, location, avatar_url
        """,
        (pending["full_name"], pending["email"], pending["password_hash"], pending["role"]),
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
    return {"user": public_user(user), "profile": profile, "experiences": experiences, "education": education, "documents": documents, "applications": applications, "stats": stats}


@app.put("/api/me/profile")
def update_profile(body: ProfileBody, user: Annotated[dict, Depends(current_user)]):
    execute("UPDATE users SET full_name = %s, headline = %s, location = %s WHERE id = %s", (body.fullName, body.headline, body.location, user["id"]))
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
    return fetch_all("SELECT * FROM jobs WHERE status = 'active' ORDER BY created_at DESC")


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
    updated = execute("UPDATE applications SET status = %s WHERE id = %s RETURNING id", (body.status, application_id))
    if not updated:
        raise HTTPException(status_code=404, detail="Application not found")
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
          u.id, u.full_name, u.email, u.role, u.plan, u.status, u.headline, u.location, u.avatar_url, u.created_at, u.last_active_at,
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
        "SELECT id, full_name, email, role, plan, status, headline, location, avatar_url, created_at, last_active_at FROM users WHERE id = %s",
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
            headline = COALESCE(%s, headline),
            location = COALESCE(%s, location),
            role = COALESCE(%s, role),
            plan = COALESCE(%s, plan),
            status = COALESCE(%s, status)
        WHERE id = %s
        RETURNING id
        """,
        (body.fullName, str(body.email).lower() if body.email else None, body.headline, body.location, body.role, body.plan, body.status, user_id),
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
            headline = COALESCE(%s, headline),
            location = COALESCE(%s, location),
            role = COALESCE(%s, role),
            plan = COALESCE(%s, plan),
            status = COALESCE(%s, status)
        WHERE id = %s
        RETURNING id, full_name, email, role, plan, status, headline, location, created_at, last_active_at
        """,
        (body.fullName, str(body.email).lower() if body.email else None, body.headline, body.location, body.role, body.plan, body.status, user_id),
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
        SELECT i.*, u.full_name, u.email, j.title AS job_title
        FROM interviews i
        JOIN users u ON u.id = i.user_id
        LEFT JOIN jobs j ON j.id = i.job_id
        ORDER BY i.scheduled_at DESC
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
    return execute(
        """
        INSERT INTO interviews (user_id, admin_id, job_id, scheduled_at, channel, notes)
        VALUES (%s,%s,%s,%s,%s,%s)
        RETURNING *
        """,
        (body.userId, user["id"], body.jobId, body.scheduledAt, body.channel, body.notes),
    )


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
            (target_user_id, "Thanks for contacting Rawabet support. I received your message and an admin can follow up from the dashboard."),
        )
    return {"message": message, "botReply": bot_reply}
