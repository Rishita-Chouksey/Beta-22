"""Admin sign-in and session endpoints."""
import hmac
import secrets
import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from ..admin_auth import (CSRF_COOKIE, SESSION_COOKIE, create_admin_session,
                          is_admin_configured, require_admin, require_admin_csrf, verify_admin_password)
from ..config import settings

router = APIRouter(prefix="/admin/auth", tags=["Admin Authentication"])
_login_attempts: Dict[str, Deque[float]] = defaultdict(deque)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=1024)


def _check_rate_limit(ip: str) -> None:
    now = time.monotonic()
    attempts = _login_attempts[ip]
    while attempts and now - attempts[0] > 900:
        attempts.popleft()
    if len(attempts) >= 8:
        raise HTTPException(status_code=429, detail="Too many login attempts. Try again later.")
    attempts.append(now)


@router.get("/session")
async def session_status(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    if not is_admin_configured():
        return {"configured": False, "authenticated": False}
    try:
        user = require_admin(request)
        csrf = request.cookies.get(CSRF_COOKIE) or secrets.token_urlsafe(32)
        if not request.cookies.get(CSRF_COOKIE):
            response.set_cookie(CSRF_COOKIE, csrf, httponly=True, secure=settings.ADMIN_COOKIE_SECURE,
                                samesite=settings.ADMIN_COOKIE_SAMESITE, path="/api",
                                max_age=settings.ADMIN_SESSION_TTL_SECONDS)
        return {"configured": True, "authenticated": True, "role": user["role"],
                "username": user["sub"], "csrf_token": csrf}
    except HTTPException as exc:
        if exc.status_code in (401, 403):
            return {"configured": True, "authenticated": False}
        raise


@router.post("/login")
async def login(req: LoginRequest, request: Request, response: Response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    if not is_admin_configured():
        raise HTTPException(status_code=503, detail="Admin authentication is not configured. Set ADMIN_USERNAME, ADMIN_PASSWORD_HASH and ADMIN_SESSION_SECRET.")
    _check_rate_limit(request.client.host if request.client else "unknown")
    username_ok = hmac.compare_digest(req.username.encode("utf-8"), settings.ADMIN_USERNAME.encode("utf-8"))
    password_ok = verify_admin_password(req.password, settings.ADMIN_PASSWORD_HASH)
    if not (username_ok and password_ok):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    _login_attempts.pop(request.client.host if request.client else "unknown", None)
    token, csrf = create_admin_session(settings.ADMIN_USERNAME)
    same_site = settings.ADMIN_COOKIE_SAMESITE if settings.ADMIN_COOKIE_SAMESITE in {"strict", "lax", "none"} else "strict"
    if same_site == "none" and not settings.ADMIN_COOKIE_SECURE:
        raise HTTPException(status_code=500, detail="SameSite=None admin cookies require HTTPS.")
    common = {"max_age": settings.ADMIN_SESSION_TTL_SECONDS, "secure": settings.ADMIN_COOKIE_SECURE,
              "httponly": True, "samesite": same_site, "path": "/api"}
    response.set_cookie(SESSION_COOKIE, token, **common)
    response.set_cookie(CSRF_COOKIE, csrf, **common)
    return {"success": True, "role": "admin", "username": settings.ADMIN_USERNAME,
            "expires_in": settings.ADMIN_SESSION_TTL_SECONDS, "csrf_token": csrf}


@router.post("/logout")
async def logout(response: Response, _authorized=Depends(require_admin_csrf)):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    same_site = settings.ADMIN_COOKIE_SAMESITE if settings.ADMIN_COOKIE_SAMESITE in {"strict", "lax", "none"} else "strict"
    common = {"secure": settings.ADMIN_COOKIE_SECURE, "samesite": same_site, "path": "/api"}
    response.delete_cookie(SESSION_COOKIE, httponly=True, **common)
    response.delete_cookie(CSRF_COOKIE, httponly=True, **common)
    return {"success": True}
