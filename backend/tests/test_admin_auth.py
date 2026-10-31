from http.cookies import SimpleCookie
from pathlib import Path
import uuid

import pytest
from fastapi import HTTPException, Response
from starlette.requests import Request

from app import admin_auth
from app.admin_auth import revoke_admin_session
from app.config import settings
from app.routes.admin_auth import LoginRequest, login
from app.main import app
from app.routes import agents, admin_monitoring
from app.db import database
from app.main import lifespan


def _request(cookie="", csrf=""):
    headers = []
    if cookie:
        headers.append((b"cookie", cookie.encode()))
    if csrf:
        headers.append((b"x-csrf-token", csrf.encode()))
    return Request({"type": "http", "method": "GET", "path": "/api/admin/auth/session",
                    "headers": headers, "query_string": b"", "server": ("testserver", 80),
                    "client": ("127.0.0.1", 1234), "scheme": "http"})


def _run(coro):
    try:
        coro.send(None)
    except StopIteration as result:
        return result.value
    raise AssertionError("Expected a synchronous endpoint coroutine")


@pytest.fixture
def admin_settings(monkeypatch):
    db_dir = Path(__file__).parent / ".pytest_cache"
    db_dir.mkdir(exist_ok=True)
    db_file = db_dir / f"auth-{uuid.uuid4().hex}.sqlite"
    monkeypatch.setattr(database, "DB_DIR", str(db_dir))
    monkeypatch.setattr(database, "DB_PATH", str(db_file))
    monkeypatch.setattr(database, "_tables_initialized", False)
    database.init_db()
    monkeypatch.setattr(settings, "ADMIN_USERNAME", "reviewer")
    monkeypatch.setattr(settings, "ADMIN_PASSWORD_HASH", admin_auth.hash_admin_password("correct horse battery staple"))
    monkeypatch.setattr(settings, "ADMIN_SESSION_SECRET", "test-session-secret-is-long-enough-for-hmac")
    monkeypatch.setattr(settings, "ADMIN_SESSION_TTL_SECONDS", 1800)
    monkeypatch.setattr(settings, "ADMIN_COOKIE_SECURE", True)
    yield
    for suffix in ("", "-wal", "-shm"):
        Path(f"{db_file}{suffix}").unlink(missing_ok=True)


def test_password_hash_is_one_way_and_verified(admin_settings):
    encoded = settings.ADMIN_PASSWORD_HASH
    assert "correct horse battery staple" not in encoded
    assert admin_auth.verify_admin_password("correct horse battery staple", encoded)
    assert not admin_auth.verify_admin_password("wrong", encoded)


def test_login_creates_secure_role_session_and_csrf_cookie(admin_settings):
    response = Response()
    result = _run(login(LoginRequest(username="reviewer", password="correct horse battery staple"),
                        _request(), response))
    assert result["role"] == "admin"
    assert response.headers["Cache-Control"] == "no-store"
    cookies = SimpleCookie()
    cookies.load("\n".join(value.decode() for key, value in response.raw_headers if key.lower() == b"set-cookie"))
    session = cookies[admin_auth.SESSION_COOKIE]
    csrf = cookies[admin_auth.CSRF_COOKIE]
    assert session["httponly"]
    assert session["secure"]
    assert session["samesite"] == "strict"
    assert csrf.value
    parsed = admin_auth.require_admin(_request(f"{admin_auth.SESSION_COOKIE}={session.value}"))
    assert parsed["sub"] == "reviewer" and parsed["role"] == "admin"
    with pytest.raises(HTTPException) as denied:
        admin_auth.require_admin_csrf(_request(
            f"{admin_auth.SESSION_COOKIE}={session.value}; {admin_auth.CSRF_COOKIE}={csrf.value}", "wrong"))
    assert denied.value.status_code == 403
    assert admin_auth.require_admin_csrf(_request(
        f"{admin_auth.SESSION_COOKIE}={session.value}; {admin_auth.CSRF_COOKIE}={csrf.value}", csrf.value))["role"] == "admin"
    revoke_admin_session(parsed["jti"])
    with pytest.raises(HTTPException) as revoked:
        admin_auth.require_admin(_request(f"{admin_auth.SESSION_COOKIE}={session.value}"))
    assert revoked.value.status_code == 401


def test_bad_password_and_unconfigured_auth_fail_closed(admin_settings, monkeypatch):
    response = Response()
    with pytest.raises(HTTPException) as denied:
        _run(login(LoginRequest(username="reviewer", password="incorrect"), _request(), response))
    assert denied.value.status_code == 401
    with pytest.raises(HTTPException) as regular_user:
        _run(login(LoginRequest(username="citizen", password="correct horse battery staple"), _request(), response))
    assert regular_user.value.status_code == 401
    monkeypatch.setattr(settings, "ADMIN_SESSION_SECRET", "short")
    with pytest.raises(HTTPException) as disabled:
        admin_auth.require_admin(_request())
    assert disabled.value.status_code == 503


def test_admin_and_agent_routes_have_role_and_csrf_dependencies():
    agent_routes = {route.path: route for route in agents.router.routes if hasattr(route, "dependant")}
    monitor_routes = {route.path: route for route in admin_monitoring.router.routes if hasattr(route, "dependant")}
    assert any(dep.dependency is admin_auth.require_admin for dep in agents.router.dependencies)
    for path in ("/agents/status", "/agents/runs", "/sources", "/updates", "/monitoring/status"):
        assert path in agent_routes
    for path in ("/agents/discover", "/agents/crawl", "/agents/monitor", "/updates/{update_id}/approve"):
        route = agent_routes[path]
        assert any(dep.call is admin_auth.require_admin_csrf for dep in route.dependant.dependencies)
    assert admin_monitoring.router.prefix == "/admin/monitoring"
    for path in ("/admin/monitoring/summary", "/admin/monitoring/sources", "/admin/monitoring/changes",
                 "/admin/monitoring/pending-updates", "/admin/monitoring/schemes/{scheme_id}/history"):
        route = monitor_routes[path]
        assert any(dep.call is admin_auth.require_admin for dep in route.dependant.dependencies)
    for path in ("/admin/monitoring/run", "/admin/monitoring/updates/{update_id}/approve",
                 "/admin/monitoring/updates/{update_id}/reject", "/admin/monitoring/schemes/{scheme_id}/rollback"):
        route = monitor_routes[path]
        assert any(dep.call is admin_auth.require_admin_csrf for dep in route.dependant.dependencies)
    assert "/api/admin/auth/login" in app.openapi()["paths"]


def test_application_lifespan_initializes_database_without_demo_rows(monkeypatch):
    db_dir = Path(__file__).parent / ".pytest_cache"
    db_dir.mkdir(exist_ok=True)
    db_file = db_dir / f"startup-{uuid.uuid4().hex}.sqlite"
    monkeypatch.setattr(database, "DB_DIR", str(db_dir))
    monkeypatch.setattr(database, "DB_PATH", str(db_file))
    monkeypatch.setattr(database, "_tables_initialized", False)
    monkeypatch.setattr(settings, "ENABLE_AUTOMATIC_MONITORING", False)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("TESTING", raising=False)

    lifespan_context = app.router.lifespan_context(app)
    _run(lifespan_context.__aenter__())
    conn = database.get_db_connection()
    assert conn.execute("SELECT COUNT(*) FROM schemes").fetchone()[0] >= 5
    assert conn.execute("SELECT COUNT(*) FROM sources WHERE url = ?",
                        ("https://www.myscheme.gov.in/",)).fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM sources WHERE status = 'disabled'").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM pending_scheme_updates WHERE is_demo = 1").fetchone()[0] == 0
    conn.close()
    _run(lifespan_context.__aexit__(None, None, None))
    for suffix in ("", "-wal", "-shm"):
        Path(f"{db_file}{suffix}").unlink(missing_ok=True)
