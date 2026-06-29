import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import psycopg

from app.config import DATABASE_URL, UPLOAD_DIR


def newest_matching_file(user_id: str, kind: str) -> Path | None:
    matches = sorted(
        UPLOAD_DIR.glob(f"{user_id}_{kind}_*"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return matches[0] if matches else None


def path_exists(value: str | None) -> bool:
    if not value:
        return False
    return (UPLOAD_DIR / Path(value).name).exists()


def repair_upload_links():
    repaired_avatars = 0
    repaired_documents = 0
    inserted_documents = 0
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, avatar_url FROM users WHERE avatar_url IS NOT NULL")
            for user_id, avatar_url in cur.fetchall():
                if path_exists(avatar_url):
                    continue
                replacement = newest_matching_file(str(user_id), "avatar")
                if replacement:
                    cur.execute("UPDATE users SET avatar_url = %s WHERE id = %s", (f"/uploads/{replacement.name}", user_id))
                    repaired_avatars += 1

            cur.execute("SELECT id, user_id, kind, file_path FROM documents")
            for document_id, user_id, kind, file_path in cur.fetchall():
                if path_exists(file_path):
                    continue
                replacement = newest_matching_file(str(user_id), kind)
                if replacement:
                    cur.execute("UPDATE documents SET file_path = %s WHERE id = %s", (str(replacement), document_id))
                    repaired_documents += 1

            cur.execute("SELECT id FROM users")
            user_ids = {str(row[0]) for row in cur.fetchall()}
            cur.execute("SELECT file_path FROM documents")
            known_document_files = {Path(row[0]).name for row in cur.fetchall() if row[0]}
            for file_path in UPLOAD_DIR.glob("*"):
                if not file_path.is_file():
                    continue
                name = file_path.name
                if name in known_document_files:
                    continue
                parts = name.split("_", 2)
                if len(parts) < 3:
                    continue
                user_id, kind = parts[0], parts[1]
                if user_id not in user_ids or kind not in {"resume", "certificate"}:
                    continue
                cur.execute(
                    """
                    INSERT INTO documents (user_id, kind, file_name, file_path, mime_type, file_size, verification_status)
                    VALUES (%s,%s,%s,%s,%s,%s,'approved')
                    """,
                    (user_id, kind, name, str(file_path), "application/octet-stream", file_path.stat().st_size),
                )
                inserted_documents += 1

    print(f"Repaired {repaired_avatars} avatars, repaired {repaired_documents} document paths, inserted {inserted_documents} missing document rows")


if __name__ == "__main__":
    repair_upload_links()
