import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import APP_ENV
from .routers.core import router as core_router
from .routers.messages import router as messages_router


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


app.include_router(core_router)
app.include_router(messages_router, prefix="/api")
