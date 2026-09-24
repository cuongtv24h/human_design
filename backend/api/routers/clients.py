"""/api/v1/clients — people being analyzed. Coaches only see their own clients."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import ValidationError
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..deps import client_ip, current_user, get_db
from ..models import Client, Report, User
from ..schemas import ClientIn, ClientList, ClientOut, ClientPatch, ReportList
from ..services import audit, client_out, get_client_or_404, report_summary, visible_clients

router = APIRouter(prefix="/clients", tags=["clients"])


def _validated(payload: ClientIn) -> ClientIn:
    try:
        subject = payload.subject()
    except ValidationError as exc:
        first = exc.errors()[0]
        field = ".".join(str(p) for p in first.get("loc", ()))
        raise HTTPException(status_code=422, detail=f"Dữ liệu sinh không hợp lệ ({field}): {first.get('msg')}") from exc
    payload.timezone = subject.timezone
    payload.birth_time = subject.birth_time
    return payload


@router.get("", response_model=ClientList)
def list_clients(
    q: str = "", limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0),
    user: User = Depends(current_user), db: Session = Depends(get_db),
) -> ClientList:
    query = visible_clients(user)
    if q.strip():
        like = f"%{q.strip().lower()}%"
        query = query.where(or_(func.lower(Client.full_name).like(like), func.lower(Client.email).like(like),
                                Client.phone.like(like)))
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.scalars(query.order_by(Client.updated_at.desc()).limit(limit).offset(offset)).all()
    return ClientList(items=[client_out(db, c) for c in rows], total=total)


@router.post("", response_model=ClientOut, status_code=201)
def create_client(payload: ClientIn, request: Request, user: User = Depends(current_user),
                  db: Session = Depends(get_db)) -> ClientOut:
    if not payload.consent:
        raise HTTPException(status_code=422, detail="Cần xác nhận khách hàng đã đồng ý cho xử lý dữ liệu cá nhân (ngày, giờ, nơi sinh).")
    payload = _validated(payload)
    client = Client(
        org_id=user.org_id, owner_user_id=user.id, full_name=payload.full_name, email=payload.email.strip(),
        phone=payload.phone.strip(), birth_date=payload.birth_date, birth_time=payload.birth_time,
        birth_time_known=payload.birth_time_known, birth_place=payload.birth_place.strip(),
        timezone=payload.timezone, notes=payload.notes, consent_at=datetime.now(timezone.utc),
    )
    db.add(client)
    db.flush()
    audit(db, user, "client.create", "client", client.id, ip=client_ip(request))
    db.commit()
    return client_out(db, client)


@router.get("/{client_id}", response_model=ClientOut)
def get_client(client_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> ClientOut:
    return client_out(db, get_client_or_404(db, user, client_id))


@router.patch("/{client_id}", response_model=ClientOut)
def update_client(client_id: int, payload: ClientPatch, request: Request, user: User = Depends(current_user),
                  db: Session = Depends(get_db)) -> ClientOut:
    client = get_client_or_404(db, user, client_id)
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    merged = ClientIn(
        full_name=changes.get("full_name", client.full_name), email=changes.get("email", client.email),
        phone=changes.get("phone", client.phone), birth_date=changes.get("birth_date", client.birth_date),
        birth_time=changes.get("birth_time", client.birth_time),
        birth_time_known=changes.get("birth_time_known", client.birth_time_known),
        birth_place=changes.get("birth_place", client.birth_place),
        timezone=changes.get("timezone", client.timezone), notes=changes.get("notes", client.notes), consent=True,
    )
    merged = _validated(merged)
    for field in ("full_name", "email", "phone", "birth_date", "birth_time", "birth_time_known",
                  "birth_place", "timezone", "notes"):
        setattr(client, field, getattr(merged, field))
    audit(db, user, "client.update", "client", client.id, ip=client_ip(request), fields=sorted(changes))
    db.commit()
    return client_out(db, client)


@router.delete("/{client_id}", status_code=204)
def delete_client(client_id: int, request: Request, user: User = Depends(current_user),
                  db: Session = Depends(get_db)) -> None:
    client = get_client_or_404(db, user, client_id)
    client.deleted_at = datetime.now(timezone.utc)
    audit(db, user, "client.delete", "client", client.id, ip=client_ip(request))
    db.commit()


@router.get("/{client_id}/reports", response_model=ReportList)
def client_reports(client_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> ReportList:
    client = get_client_or_404(db, user, client_id)
    rows = db.scalars(select(Report).where(Report.client_id == client.id).order_by(Report.created_at.desc())).all()
    return ReportList(items=[report_summary(r) for r in rows], total=len(rows))
