"""FastAPI dependencies: DB session, current user, role checks."""

from __future__ import annotations

import re
from collections.abc import Iterator
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .models import User, UserSession
from .security import SESSION_COOKIE, hash_token

# ``GET ?access_token=`` chỉ dành cho nạp file trình duyệt tự tải (<img>/<iframe>/link tải
# trong iframe preview nhúng) — không bao giờ cho endpoint dữ liệu API, để token phiên
# không thể rơi vào access log/lịch sử trình duyệt qua URL tùy ý.
_FILE_EXPORT = re.compile(r"^/api/v1/reports/[^/]+/(markdown|infographic\.html|bodygraph\.svg|pdf|docx)/?$")


def get_db(request: Request) -> Iterator[Session]:
    yield from request.app.state.db.session()


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def session_token(request: Request) -> str:
    """Session token from the httpOnly cookie (normal) or — for embedded previews where the
    browser blocks third-party cookies — ``Authorization: Bearer`` (any request) /
    ``?access_token=`` (GET/HEAD on report file-export routes only, used by
    <img>/<iframe>/download links)."""
    token = request.cookies.get(SESSION_COOKIE, "")
    if token:
        return token
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    if request.method in {"GET", "HEAD"} and _FILE_EXPORT.match(request.url.path):
        return request.query_params.get("access_token", "")
    return ""


def current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = session_token(request)
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
    """IP thật sau nginx: ``X-Real-IP`` (nginx set từ ``$remote_addr`` — không giả mạo được)
    trước; nếu thiếu thì lấy **giá trị CUỐI** ``X-Forwarded-For`` (do proxy gần nhất thêm).
    Không bao giờ lấy phần tử đầu tiên — client gửi lên được giá trị đó, nên rate-limit
    và audit log sẽ bị giả mạo (kiểm thử: xoay XFF bypass 429)."""
    real = request.headers.get("x-real-ip", "").strip()
    if real:
        return real[:64]
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[-1].strip()[:64]
    return (request.client.host if request.client else "")[:64]
