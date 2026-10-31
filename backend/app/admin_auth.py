"""Signed, short-lived admin sessions and CSRF protection."""
import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any, Dict

from fastapi import HTTPException, Request

from .config import settings
from .db.database import get_db_connection

SESSION_COOKIE = "ys_admin_session"
CSRF_COOKIE = "ys_admin_csrf"


def hash_admin_password(password: str, iterations: int = 310_000) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    enc = lambda value: base64.urlsafe_b64encode(value).decode().rstrip("=")
    return f"pbkdf2_sha256${iterations}${enc(salt)}${enc(digest)}"


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def verify_admin_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt, expected = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256" or int(iterations) < 100_000:
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), _decode(salt), int(iterations))
        return hmac.compare_digest(actual, _decode(expected))
    except (ValueError, TypeError):
        return False


def is_admin_configured() -> bool:
    try:
        algorithm, iterations, salt, digest = settings.ADMIN_PASSWORD_HASH.split("$", 3)
        valid_hash = (algorithm == "pbkdf2_sha256" and int(iterations) >= 100_000
                      and len(_decode(salt)) >= 16 and len(_decode(digest)) == 32)
    except (ValueError, TypeError):
        valid_hash = False
    return bool(settings.ADMIN_USERNAME and valid_hash and len(settings.ADMIN_SESSION_SECRET) >= 32
                and 60 <= settings.ADMIN_SESSION_TTL_SECONDS <= 86_400)


def _sign(payload: Dict[str, Any]) -> str:
    body = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
    signature = hmac.new(settings.ADMIN_SESSION_SECRET.encode(), body.encode(), hashlib.sha256).digest()
    sig = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return f"{body}.{sig}"


def _read(token: str) -> Dict[str, Any]:
    try:
        body, supplied = token.split(".", 1)
        expected = base64.urlsafe_b64encode(
            hmac.new(settings.ADMIN_SESSION_SECRET.encode(), body.encode(), hashlib.sha256).digest()
        ).decode().rstrip("=")
        if not hmac.compare_digest(supplied, expected):
            raise ValueError("signature")
        payload = json.loads(_decode(body))
        if payload.get("role") != "admin" or int(payload.get("exp", 0)) <= int(time.time()):
            raise ValueError("expired or invalid role")
        return payload
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Admin session is missing or expired.") from exc


def create_admin_session(username: str) -> tuple[str, str]:
    now = int(time.time())
    session_id = secrets.token_urlsafe(16)
    token = _sign({"sub": username, "role": "admin", "iat": now,
                   "exp": now + settings.ADMIN_SESSION_TTL_SECONDS, "jti": session_id})
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM admin_sessions WHERE expires_at < ? OR revoked_at IS NOT NULL", (now - 86_400,))
        conn.execute("INSERT INTO admin_sessions (session_id, username, expires_at) VALUES (?, ?, ?)",
                     (session_id, username, now + settings.ADMIN_SESSION_TTL_SECONDS))
        conn.commit()
    finally:
        conn.close()
    return token, secrets.token_urlsafe(32)


def require_admin(request: Request) -> Dict[str, Any]:
    if not is_admin_configured():
        raise HTTPException(status_code=503, detail="Admin authentication is not configured.")
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=401, detail="Admin login required.")
    payload = _read(token)
    if payload.get("sub") != settings.ADMIN_USERNAME:
        raise HTTPException(status_code=403, detail="Admin role is not authorized.")
    try:
        conn = get_db_connection()
        try:
            row = conn.execute("SELECT 1 FROM admin_sessions WHERE session_id = ? AND username = ? AND expires_at > ? AND revoked_at IS NULL",
                               (payload.get("jti"), payload["sub"], int(time.time()))).fetchone()
        finally:
            conn.close()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Admin session storage is unavailable.") from exc
    if not row:
        raise HTTPException(status_code=401, detail="Admin session has been revoked or expired.")
    return payload


def require_admin_csrf(request: Request) -> Dict[str, Any]:
    payload = require_admin(request)
    cookie = request.cookies.get(CSRF_COOKIE, "")
    header = request.headers.get("X-CSRF-Token", "")
    if not cookie or not header or not hmac.compare_digest(cookie, header):
        raise HTTPException(status_code=403, detail="CSRF validation failed.")
    return payload


def revoke_admin_session(session_id: str) -> None:
    conn = get_db_connection()
    try:
        conn.execute("UPDATE admin_sessions SET revoked_at = ? WHERE session_id = ? AND revoked_at IS NULL",
                     (int(time.time()), session_id))
        conn.commit()
    finally:
        conn.close()
