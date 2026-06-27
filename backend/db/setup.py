from pathlib import Path
import sys

import psycopg
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.config import DATABASE_URL

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def admin_url() -> str:
    return DATABASE_URL.rsplit("/", 1)[0] + "/postgres"


def create_database():
    with psycopg.connect(admin_url(), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = 'rawabet'")
            if cur.fetchone():
                print("Database rawabet already exists")
                return
            cur.execute("CREATE DATABASE rawabet")
            print("Created database rawabet")


def apply_schema():
    schema = Path(__file__).with_name("schema.sql").read_text()
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(schema)
    print("Applied schema")


if __name__ == "__main__":
    create_database()
    apply_schema()
    import seed
