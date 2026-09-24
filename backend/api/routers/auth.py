"""/api/v1/auth — cookie session login."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..deps import client_ip, current_user, get_db
from ..models import User, UserSession
from ..schemas import LoginIn, UserOut
from ..security import SESSION_COOKIE, hash_token, new_session_token, verify_password
from ..services import audit

router = APIRouter(prefix="/auth", tags=["auth"])

# Simple in-process brute-force guard: 5 failures / 15 minutes per IP+email.
_FAILURES: dict[str, deque[float]] = defaultdict(deque)
_WINDOW_S = 15 * 60
_MAX_FAILURES = 5


def _too_many(key: str) -> bool:
    bucket = _FAILURES[key]
    now = time.monotonic()
    while bucket and now - bucket[0] > _WINDOW_S:
        bucket.popleft()
    return len(bucket) >= _MAX_FAILURES


def user_out(user: User) -> UserOut:
    out = UserOut.model_validate(user)
    out.org_name = user.organization.name if user.organization else ""
    return out


@router.post("/login", response_model=UserOut)
def login(payload: LoginIn, request: Request, response: Response, db: Session = Depends(get_db)) -> UserOut:
    email = payload.email.strip().lower()
    ip = client_ip(request)
    key = f"{ip}|{email}"
    if _too_many(key):
        raise HTTPException(status_code=429, detail="Đăng nhập sai quá nhiều lần. Vui lòng thử lại sau 15 phút.")
    user = db.scalar(select(User).where(func.lower(User.email) == email))
    if user is None or not verify_password(user.password_hash, payload.password):
        _FAILURES[key].append(time.monotonic())
        audit(db, user, "auth.login_failed", "user", user.id if user else "", ip=ip, email=email)
        db.commit()
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa.")
    _FAILURES.pop(key, None)
    settings = request.app.state.settings
    token, token_hash = new_session_token()
    now = datetime.now(timezone.utc)
    db.add(UserSession(token_hash=token_hash, user_id=user.id, expires_at=now + timedelta(hours=settings.session_hours),
                       ip=ip, user_agent=request.headers.get("user-agent", "")[:300]))
    user.last_login_at = now
    audit(db, user, "auth.login", "user", user.id, ip=ip)
    db.commit()
    _cookie(response, settings, token, settings.session_hours * 3600)
    return user_out(user)


def _cookie(response: Response, settings, value: str, max_age: int) -> None:
    """Session cookie; adds CHIPS ``Partitioned`` for embedded previews (Starlette only does so on Python 3.14+)."""
    response.set_cookie(SESSION_COOKIE, value, max_age=max_age, httponly=True, path="/", **settings.cookie_options())
    if settings.cookie_partitioned:
        name, header = response.raw_headers[-1]
        response.raw_headers[-1] = (name, header + b"; Partitioned")


@router.post("/logout", status_code=204)
def logout(request: Request, response: Response, db: Session = Depends(get_db)) -> Response:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        session = db.get(UserSession, hash_token(token))
        if session is not None:
            audit(db, session.user, "auth.logout", "user", session.user_id, ip=client_ip(request))
            db.delete(session)
            db.commit()
    response.status_code = 204
    _cookie(response, request.app.state.settings, "", 0)
    return response


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)) -> UserOut:
    return user_out(user)
