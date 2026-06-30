import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/rawabet")
JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
APP_ENV = os.getenv("APP_ENV", "development").lower()
if APP_ENV in {"production", "prod"} and JWT_SECRET == "change-me":
    raise RuntimeError("JWT_SECRET must be set to a strong unique value in production")
UPLOAD_DIR = BASE_DIR / os.getenv("UPLOAD_DIR", "uploads")
PORT = int(os.getenv("PORT", "4000"))
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER or "no-reply@rawabet.local")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MASTER_ADMIN_EMAILS = {
    email.strip().lower()
    for email in os.getenv("MASTER_ADMIN_EMAILS", "loutfi.abouzaid@gmail.com,loutfi.abouzaid@gamil.com").split(",")
    if email.strip()
}
