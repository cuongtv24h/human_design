"""Application services: permissions, serialization, report generation, audit."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from backend.reporting.contract import ContentMode, ReportDocument, ReportRequest
from backend.reporting.language_vn import TYPE_VN, vn_authority, vn_definition, vn_strategy
from backend.reporting.service import generate_report

from .models import AuditLog, Client, Report, ReportRevision, User
from .schemas import ChartSummary, ClientOut, ReportDetailOut, ReportSummaryOut, SectionOut

from hd_time import display_birth  # noqa: E402  (tools/ on sys.path via backend.reporting)

log = logging.getLogger("hd.api")


def audit(db: Session, user: User | None, action: str, entity: str = "", entity_id: Any = "",
          ip: str = "", **meta: Any) -> None:
    db.add(AuditLog(
        org_id=user.org_id if user else None,
        actor_id=user.id if user else None,
        action=action, entity=entity, entity_id=str(entity_id or ""), meta=meta, ip=ip,
    ))


# --- permissions ------------------------------------------------------------

def visible_clients(user: User):
    query = select(Client).where(Client.org_id == user.org_id, Client.deleted_at.is_(None))
    if user.role != "admin":
        query = query.where(Client.owner_user_id == user.id)
    return query


def get_client_or_404(db: Session, user: User, client_id: int) -> Client:
    client = db.scalar(visible_clients(user).where(Client.id == client_id))
    if client is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng.")
    return client


def visible_reports(user: User):
    query = select(Report).join(Client).where(Report.org_id == user.org_id, Client.deleted_at.is_(None))
    if user.role != "admin":
        query = query.where(Client.owner_user_id == user.id)
    return query


def get_report_or_404(db: Session, user: User, report_id: str) -> Report:
    report = db.scalar(visible_reports(user).where(Report.id == report_id))
    if report is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy báo cáo.")
    return report


# --- serialization ----------------------------------------------------------

def client_out(db: Session, client: Client) -> ClientOut:
    report_count = db.scalar(select(func.count()).select_from(Report).where(
        Report.client_id == client.id, Report.status != "archived")) or 0
    return ClientOut(
        id=client.id, full_name=client.full_name, email=client.email, phone=client.phone,
        birth_date=client.birth_date, birth_time=client.birth_time,
        birth_time_known=client.birth_time_known, birth_place=client.birth_place,
        timezone=client.timezone,
        birth_display=display_birth(client.birth_date, client.birth_time, client.timezone),
        notes=client.notes, owner_id=client.owner_user_id,
        owner_name=client.owner.full_name or client.owner.email,
        report_count=report_count, consent_at=client.consent_at,
        created_at=client.created_at, updated_at=client.updated_at,
    )


def chart_summary(chart: dict[str, Any]) -> ChartSummary:
    chart_type = str(chart.get("type", ""))
    return ChartSummary(
        type=chart_type,
        type_vn=TYPE_VN.get(chart_type, ""),
        strategy=vn_strategy(str(chart.get("strategy", "")), chart_type),
        authority=vn_authority(str(chart.get("authority", ""))),
        profile=str(chart.get("profile", "")),
        definition=vn_definition(str(chart.get("definition", ""))),
        incarnation_cross=str(chart.get("incarnation_cross", "")),
        defined_centers=len(chart.get("defined_centers", []) or []),
    )


def report_summary(report: Report) -> ReportSummaryOut:
    return ReportSummaryOut(
        id=report.id, client_id=report.client_id, client_name=report.client.full_name,
        tier=report.tier, template=report.template, content_mode=report.content_mode,
        domains=list(report.domains or []), status=report.status, editor=report.editor,
        warnings_count=report.warnings_count, version=report.version, error=report.error,
        created_at=report.created_at, updated_at=report.updated_at,
    )


def load_document(report: Report) -> ReportDocument:
    if not report.document:
        raise HTTPException(status_code=409, detail="Báo cáo đang được tạo, vui lòng thử lại sau.")
    return ReportDocument.model_validate(report.document)


def report_detail(report: Report) -> ReportDetailOut:
    base = report_summary(report).model_dump()
    client = report.client
    subject_display = display_birth(client.birth_date, client.birth_time, client.timezone)
    if not report.document:
        return ReportDetailOut(**base, subject_display=subject_display, summary=None,
                               sections=[], warnings=[], markdown="")
    document = load_document(report)
    sections = [
        SectionOut(id=s.id, title=s.title, status=s.status, warnings=list(s.warnings))
        for s in sorted(document.sections, key=lambda item: item.order)
    ]
    return ReportDetailOut(
        **base, subject_display=subject_display, summary=chart_summary(document.chart),
        sections=sections, warnings=list(document.warnings), markdown=document.to_markdown(),
    )


# --- generation -------------------------------------------------------------

def build_request(client: Client, *, tier: str, template: str, content_mode: str,
                  domains: list[str], report_id: str | None = None) -> ReportRequest:
    payload: dict[str, Any] = {
        "subject": {
            "name": client.full_name,
            "birth_date": client.birth_date,
            "birth_time": client.birth_time,
            "timezone": client.timezone,
            "birth_location": client.birth_place,
        },
        "tier": tier, "template": template, "content_mode": content_mode, "domains": domains,
    }
    if report_id:
        payload["report_id"] = report_id
    return ReportRequest.model_validate(payload)


def _store_document(db: Session, report: Report, document: ReportDocument, author: str,
                    change_type: str) -> None:
    report.document = document.model_dump(mode="json")
    report.editor = document.provenance.editor
    report.warnings_count = len(document.warnings)
    report.status = "ready"
    report.error = ""
    report.version = (report.version or 0) + 1
    db.add(ReportRevision(report_id=report.id, version=report.version, author=author,
                          change_type=change_type, document=report.document,
                          warnings=list(document.warnings)))


def create_report(db: Session, user: User, client: Client, *, tier: str, template: str,
                  content_mode: str, domains: list[str]) -> Report:
    report_id = str(uuid4())
    request = build_request(client, tier=tier, template=template, content_mode=content_mode,
                            domains=domains, report_id=report_id)
    report = Report(
        id=report_id, org_id=user.org_id, client_id=client.id, created_by=user.id,
        tier=tier, template=template, content_mode=content_mode, domains=domains,
        status="generating", request=request.model_dump(mode="json"),
    )
    db.add(report)
    if request.content_mode is not ContentMode.LLM:
        # Template mode is deterministic and takes a few milliseconds: generate inline.
        _store_document(db, report, generate_report(request), author=user.email, change_type="generate")
    return report


def run_llm_generation(session_factory: sessionmaker, report_id: str, author: str) -> None:
    """Background job for content_mode=llm (30–120 s). Falls back to template inside service."""
    db = session_factory()
    try:
        report = db.get(Report, report_id)
        if report is None:
            return
        try:
            document = generate_report(ReportRequest.model_validate(report.request))
            _store_document(db, report, document, author=author, change_type="generate")
        except Exception as exc:  # noqa: BLE001 - surface any failure to the UI
            log.exception("report generation failed: %s", report_id)
            report.status = "failed"
            report.error = str(exc)[:1000]
        report.updated_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()
