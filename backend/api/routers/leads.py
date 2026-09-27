"""Admin: khách tiềm năng từ game landing (G1)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..deps import current_user, get_db
from ..models import GameLead, User
from ..schemas import GameLeadOut, GameLeadStatusIn

router = APIRouter(prefix="/game/leads", tags=["leads"])

LEAD_STATUSES = ("new", "contacted", "converted", "spam")


def _admin(user: User) -> None:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới xem được danh sách này.")


@router.get("", response_model=list[GameLeadOut])
def list_leads(status: str = "", limit: int = Query(50, ge=1, le=200),
               offset: int = Query(0, ge=0), user: User = Depends(current_user),
               db: Session = Depends(get_db)) -> list[GameLeadOut]:
    _admin(user)
    query = select(GameLead).order_by(GameLead.created_at.desc())
    if status:
        if status not in LEAD_STATUSES:
            raise HTTPException(status_code=422, detail="Trạng thái không hợp lệ.")
        query = query.where(GameLead.status == status)
    rows = db.scalars(query.limit(limit).offset(offset)).all()
    return [GameLeadOut.model_validate(r, from_attributes=True) for r in rows]


@router.patch("/{lead_id}", response_model=GameLeadOut)
def update_lead(lead_id: int, payload: GameLeadStatusIn, user: User = Depends(current_user),
                db: Session = Depends(get_db)) -> GameLeadOut:
    _admin(user)
    lead = db.get(GameLead, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách tiềm năng.")
    lead.status = payload.status
    db.commit()
    return GameLeadOut.model_validate(lead, from_attributes=True)
