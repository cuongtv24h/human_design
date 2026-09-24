"""/api/v1/dashboard — counters for the home screen."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..deps import current_user, get_db
from ..models import Report, User
from ..schemas import DashboardOut
from ..services import report_summary, visible_clients, visible_reports

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardOut)
def dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)) -> DashboardOut:
    clients = db.scalar(select(func.count()).select_from(visible_clients(user).subquery())) or 0
    reports = visible_reports(user).subquery()
    by_status = dict(db.execute(select(reports.c.status, func.count()).group_by(reports.c.status)).all())
    recent = db.scalars(visible_reports(user).where(Report.status != "archived")
                        .order_by(Report.created_at.desc()).limit(8)).all()
    return DashboardOut(clients=clients, reports_total=sum(by_status.values()),
                        reports_by_status={str(k): int(v) for k, v in by_status.items()},
                        recent_reports=[report_summary(r) for r in recent])
