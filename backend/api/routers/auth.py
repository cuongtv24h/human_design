"""/api/v1/auth — cookie session login."""

from __future__ import annotations

import secrets
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from ..deps import client_ip, current_user, get_db, session_token
from ..models import User, UserSession
from ..schemas import LoginIn, LoginOut, PasswordChange, UserOut
from ..security import SESSION_COOKIE, hash_password, hash_token, new_session_token, verify_password
from ..services import audit

router = APIRouter(prefix="/auth", tags=["auth"])

# Simple in-process brute-force guard: 5 failures / 15 minutes per IP+email.
_FAILURES: dict[str, deque[float]] = defaultdict(deque)
_WINDOW_S = 15 * 60
_MAX_FAILURES = 5
# Chống password-spray: 1 mật khẩu thử trên hàng trăm email cùng IP — mỗi email
# chỉ cộng 1 nên bucket `ip|email` không bao giờ kích hoạt. Cần bucket IP thuần riêng.
_MAX_IP_FAILURES = 20

# Hash Argon2 giả: đăng nhập email KHÔNG tồn tại vẫn chạy đúng một lần verify
# → thời gian phản hồi bằng nhau, không leak "email có tồn tại" qua timing.
_DUMMY_HASH = hash_password(secrets.token_urlsafe(16))


def _prune(key: str) -> deque[float]:
    bucket = _FAILURES[key]
    now = time.monotonic()
    while bucket and now - bucket[0] > _WINDOW_S:
        bucket.popleft()
    return bucket


def _too_many(key: str, limit: int = _MAX_FAILURES) -> bool:
    return len(_prune(key)) >= limit


def _record_failure(*keys: str) -> None:
    now = time.monotonic()
    for key in keys:
        _FAILURES[key].append(now)


def user_out(user: User) -> UserOut:
    out = UserOut.model_validate(user)
    out.org_name = user.organization.name if user.organization else ""
    return out


@router.post("/login", response_model=LoginOut, response_model_exclude_none=True)
def login(payload: LoginIn, request: Request, response: Response, db: Session = Depends(get_db)) -> UserOut:
    email = payload.email.strip().lower()
    ip = client_ip(request)
    key = f"{ip}|{email}"
    if _too_many(key) or _too_many(ip, _MAX_IP_FAILURES):
        raise HTTPException(status_code=429, detail="Đăng nhập sai quá nhiều lần. Vui lòng thử lại sau 15 phút.")
    user = db.scalar(select(User).where(func.lower(User.email) == email))
    # Email không tồn tại → vẫn verify hash giả, cùng chi phí Argon2 (chống timing).
    password_ok = verify_password(_DUMMY_HASH if user is None else user.password_hash, payload.password)
    if user is None or not password_ok:
        _record_failure(key, ip)
        audit(db, user, "auth.login_failed", "user", user.id if user else "", ip=ip, email=email)
        db.commit()
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa.")
    _FAILURES.pop(key, None)
    _FAILURES.pop(ip, None)
    settings = request.app.state.settings
    token, token_hash = new_session_token()
    now = datetime.now(timezone.utc)
    db.add(UserSession(token_hash=token_hash, user_id=user.id, expires_at=now + timedelta(hours=settings.session_hours),
                       ip=ip, user_agent=request.headers.get("user-agent", "")[:300]))
    user.last_login_at = now
    audit(db, user, "auth.login", "user", user.id, ip=ip)
    db.commit()
    _cookie(response, settings, token, settings.session_hours * 3600)
    out = LoginOut(**user_out(user).model_dump())
    if request.headers.get("x-hd-embedded") == "1":
        out.session_token = token
    return out


def _cookie(response: Response, settings, value: str, max_age: int) -> None:
    """Session cookie; adds CHIPS ``Partitioned`` for embedded previews (Starlette only does so on Python 3.14+)."""
    response.set_cookie(SESSION_COOKIE, value, max_age=max_age, httponly=True, path="/", **settings.cookie_options())
    if settings.cookie_partitioned:
        name, header = response.raw_headers[-1]
        response.raw_headers[-1] = (name, header + b"; Partitioned")


@router.post("/logout", status_code=204)
def logout(request: Request, response: Response, db: Session = Depends(get_db)) -> Response:
    token = session_token(request)
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


@router.post("/password", status_code=204)
def change_password(payload: PasswordChange, request: Request, user: User = Depends(current_user),
                    db: Session = Depends(get_db)) -> None:
    """Tự đổi mật khẩu: cần nhập đúng mật khẩu hiện tại; các phiên khác bị đăng xuất."""
    if not verify_password(user.password_hash, payload.current_password):
        raise HTTPException(status_code=401, detail="Mật khẩu hiện tại không đúng.")
    user.password_hash = hash_password(payload.new_password)
    drop = delete(UserSession).where(UserSession.user_id == user.id)
    token = session_token(request)
    if token:
        drop = drop.where(UserSession.token_hash != hash_token(token))
    db.execute(drop)
    audit(db, user, "auth.password_change", "user", user.id, ip=client_ip(request))
    db.commit()
