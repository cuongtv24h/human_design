"""FastAPI dependencies: DB session, current user, role checks."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .models import User, UserSession
from .security import SESSION_COOKIE, hash_token


def get_db(request: Request) -> Iterator[Session]:
    yield from request.app.state.db.session()


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=401, detail="Bạn cần đăng nhập.")
    session = db.get(UserSession, hash_token(token))
    if session is None or _aware(session.expires_at) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại.")
    user = session.user
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa.")
    return user


def require_admin(user: User = Depends(current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ quản trị viên được thực hiện thao tác này.")
    return user


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    return (forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else ""))[:64]
