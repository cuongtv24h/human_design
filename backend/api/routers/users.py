"""/api/v1/users — admin manages coach accounts in the organization."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from ..deps import client_ip, get_db, require_admin
from ..models import User, UserSession
from ..schemas import UserCreate, UserOut, UserUpdate
from ..security import hash_password
from ..services import audit
from .auth import user_out

router = APIRouter(prefix="/users", tags=["users"])


def _get(db: Session, admin: User, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None or user.org_id != admin.org_id:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản.")
    return user


@router.get("", response_model=list[UserOut])
def list_users(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> list[UserOut]:
    rows = db.scalars(select(User).where(User.org_id == admin.org_id).order_by(User.created_at)).all()
    return [user_out(u) for u in rows]


@router.post("", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, request: Request, admin: User = Depends(require_admin),
                db: Session = Depends(get_db)) -> UserOut:
    email = payload.email.strip().lower()
    if "@" not in email:
        raise HTTPException(status_code=422, detail="Email không hợp lệ.")
    if db.scalar(select(User).where(func.lower(User.email) == email)):
        raise HTTPException(status_code=409, detail="Email này đã có tài khoản.")
    user = User(org_id=admin.org_id, email=email, full_name=payload.full_name.strip(),
                password_hash=hash_password(payload.password), role=payload.role)
    db.add(user)
    db.flush()
    audit(db, admin, "user.create", "user", user.id, ip=client_ip(request), role=user.role)
    db.commit()
    return user_out(user)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, request: Request, admin: User = Depends(require_admin),
                db: Session = Depends(get_db)) -> UserOut:
    user = _get(db, admin, user_id)
    if user.id == admin.id and (payload.is_active is False or payload.role == "coach"):
        raise HTTPException(status_code=422, detail="Không thể tự khóa hoặc tự hạ quyền tài khoản của chính mình.")
    if payload.full_name is not None:
        user.full_name = payload.full_name.strip()
    if payload.role is not None:
        user.role = payload.role
    if payload.password:
        user.password_hash = hash_password(payload.password)
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.is_active is False or payload.password:
        db.execute(delete(UserSession).where(UserSession.user_id == user.id))
    audit(db, admin, "user.update", "user", user.id, ip=client_ip(request),
          fields=sorted(payload.model_dump(exclude_unset=True, exclude={"password"})) + (["password"] if payload.password else []))
    db.commit()
    return user_out(user)
