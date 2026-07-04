from typing import Annotated

import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from .config import JWT_SECRET, MASTER_ADMIN_EMAILS
from .db import fetch_one

security = HTTPBearer()
serializer = URLSafeTimedSerializer(JWT_SECRET, salt="rawabet-session")
TOKEN_MAX_AGE = 60 * 60


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_token(user: dict) -> str:
    return serializer.dumps({"sub": str(user["id"]), "role": user["role"]})


def public_user(user: dict) -> dict:
    role = "master_admin" if is_master_admin(user) else user["role"]
    return {
        "id": str(user["id"]),
        "fullName": user["full_name"],
        "email": user["email"],
        "phone": user.get("phone"),
        "dob": user.get("dob").isoformat() if user.get("dob") else None,
        "role": role,
        "plan": user["plan"],
        "status": user["status"],
        "headline": user.get("headline"),
        "location": user.get("location"),
        "avatarUrl": user.get("avatar_url"),
        "lastActiveAt": user.get("last_active_at").isoformat() if user.get("last_active_at") else None,
    }


def current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> dict:
    try:
        payload = serializer.loads(credentials.credentials, max_age=TOKEN_MAX_AGE)
        user_id = payload.get("sub")
    except (BadSignature, SignatureExpired) as exc:
        raise HTTPException(status_code=401, detail="Invalid session") from exc

    user = fetch_one(
        "SELECT id, full_name, email, phone, dob, role, plan, status, headline, location, avatar_url, last_active_at FROM users WHERE id = %s",
        (user_id,),
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")
    if user.get("status") == "suspended":
        raise HTTPException(status_code=403, detail="This account is suspended")
    return user


def is_master_admin(user: dict) -> bool:
    return user.get("role") == "master_admin" or str(user.get("email", "")).lower() in MASTER_ADMIN_EMAILS


def admin_user(user: Annotated[dict, Depends(current_user)]) -> dict:
    if user["role"] not in {"admin", "master_admin"} and not is_master_admin(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def agent_user(user: Annotated[dict, Depends(current_user)]) -> dict:
    if user["role"] != "agent":
        raise HTTPException(status_code=403, detail="Agent access required")
    return user
