import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/rawabet")
JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
UPLOAD_DIR = BASE_DIR / os.getenv("UPLOAD_DIR", "uploads")
PORT = int(os.getenv("PORT", "4000"))
