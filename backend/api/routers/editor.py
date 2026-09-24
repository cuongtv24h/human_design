"""/api/v1/reports/{id} editing (plan P2-1, P2-2, §7.3): sections, facts check, versions, AI per section."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.reporting.contract import ContentMode, ReportDocument, ReportRequest, ReportSection
from backend.reporting.language_vn import (
    AUTHORITY_VN, CENTER_VN, DEFINITION_VN, NOT_SELF_SIGNATURE, STRATEGY_VN, TYPE_VN,
)
from backend.reporting.llm_client import LLMError
from backend.reporting.llm_editor import missing_facts, strip_internal_times
from backend.reporting.orchestrator import ReportOrchestrator
from backend.reporting.service import generate_report, llm_edit_section

from ..deps import client_ip, current_user, get_db
from ..models import Report, ReportRevision, User
from ..schemas import (
    EditorOut, EditorSection, FactCheckIn, FactCheckOut, GlossaryGroup, GlossaryTerm, LlmSectionOut, RegenerateIn,
    ReportDetailOut, RevisionOut, SectionSaveOut, SectionUpdate,
)
from ..services import (
    audit, collect_attempts, get_report_or_404, load_document, org_llm_configs, report_detail, report_summary,
    run_llm_generation, save_llm_usages, store_document,
    warm_artifacts,
)

from hd_time import display_birth  # noqa: E402

router = APIRouter(prefix="/reports", tags=["editor"])

MANUAL_FACT_WARNING = "Chỉnh sửa làm mất sự kiện kỹ thuật của phần: "


def glossary() -> list[GlossaryGroup]:
    """Standard terminology (tools/hd_language.py) for coaches to look up while editing."""
    authority_terms = {}
    for source, term in AUTHORITY_VN.items():
        authority_terms.setdefault(term, source)
    return [
        GlossaryGroup(title="Loại năng lượng (Type)", terms=[GlossaryTerm(source=k, term=v) for k, v in TYPE_VN.items()]),
        GlossaryGroup(title="Chiến lược sống (Strategy)",
                      terms=[GlossaryTerm(source=k, term=v) for k, v in STRATEGY_VN.items()]),
        GlossaryGroup(title="Quyền nội tại (Authority)",
                      terms=[GlossaryTerm(source=src, term=term) for term, src in authority_terms.items()]),
        GlossaryGroup(title="Định nghĩa (Definition)",
                      terms=[GlossaryTerm(source=k, term=v) for k, v in DEFINITION_VN.items()]),
        GlossaryGroup(title="Trung tâm (Centers)", terms=[GlossaryTerm(source=k, term=v) for k, v in CENTER_VN.items()]),
        GlossaryGroup(title="Dấu hiệu sống đúng / sai (Signature · Not-Self)",
                      terms=[GlossaryTerm(source=k, term=f"{sig} · {ns}") for k, (ns, sig) in NOT_SELF_SIGNATURE.items()]),
    ]


def _editor_section(section: ReportSection) -> EditorSection:
    return EditorSection(
        id=section.id, title=section.title, kind=str(section.kind), order=section.order,
        content_markdown=section.content_markdown, data=strip_internal_times(section.data),
        warnings=list(section.warnings), knowledge_refs=list(section.knowledge_refs),
    )


def _editable(db: Session, user: User, report_id: str) -> tuple[Report, ReportDocument]:
    report = get_report_or_404(db, user, report_id)
    if report.status == "generating":
        raise HTTPException(status_code=409, detail="Báo cáo đang được tạo, chưa thể chỉnh sửa.")
    if report.status == "archived":
        raise HTTPException(status_code=409, detail="Báo cáo đã lưu trữ — không chỉnh sửa được.")
    return report, load_document(report)


def _section(document: ReportDocument, section_id: str) -> ReportSection:
    section = next((s for s in document.sections if s.id == section_id and s.status == "included"), None)
    if section is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy phần này trong báo cáo.")
    return section


def _baseline(report: Report, section_id: str) -> str:
    """The deterministic template text of a section (5–8 ms) — reference for the facts check."""
    request = ReportRequest.model_validate({**report.request, "content_mode": "template"})
    document = ReportOrchestrator().run(request)
    section = next((s for s in document.sections if s.id == section_id), None)
    return section.content_markdown if section else ""


@router.get("/{report_id}/editor", response_model=EditorOut)
def editor(report_id: str, request: Request, user: User = Depends(current_user),
           db: Session = Depends(get_db)) -> EditorOut:
    report = get_report_or_404(db, user, report_id)
    document = load_document(report)
    client = report.client
    return EditorOut(
        report=report_summary(report),
        subject_display=display_birth(client.birth_date, client.birth_time, client.timezone),
        sections=[_editor_section(s) for s in sorted(document.sections, key=lambda i: i.order) if s.status == "included"],
        llm_available=bool(org_llm_configs(db, user.org_id, request.app.state.secret_key)),
        glossary=glossary(),
    )


@router.post("/{report_id}/sections/{section_id}/check", response_model=FactCheckOut)
def check_section(report_id: str, section_id: str, payload: FactCheckIn, user: User = Depends(current_user),
                  db: Session = Depends(get_db)) -> FactCheckOut:
    """Live, non-blocking facts check while typing (yellow warning under the editor)."""
    report = get_report_or_404(db, user, report_id)
    document = load_document(report)
    _section(document, section_id)
    return FactCheckOut(missing_facts=missing_facts(document.chart, _baseline(report, section_id), payload.content_markdown))


@router.put("/{report_id}/sections/{section_id}", response_model=SectionSaveOut)
def save_section(report_id: str, section_id: str, payload: SectionUpdate, request: Request,
                 background: BackgroundTasks, user: User = Depends(current_user),
                 db: Session = Depends(get_db)) -> SectionSaveOut:
    report, document = _editable(db, user, report_id)
    if payload.base_version != report.version:
        raise HTTPException(status_code=409, detail=(
            f"Báo cáo vừa được cập nhật lên phiên bản {report.version} (bạn đang sửa bản {payload.base_version}). "
            "Hãy tải lại trang; bản nháp của bạn vẫn được giữ trong trình duyệt."))
    section = _section(document, section_id)
    missing = missing_facts(document.chart, _baseline(report, section_id), payload.content_markdown)
    section.content_markdown = payload.content_markdown.rstrip() + "\n"
    section.warnings = [MANUAL_FACT_WARNING + fact for fact in missing]  # new text supersedes old checks
    prefix = f"{section_id}: "
    document.warnings = [w for w in document.warnings if not w.startswith(prefix)]
    document.warnings += [prefix + w for w in section.warnings]
    store_document(db, report, document, author=user.email, change_type="manual_edit")
    audit(db, user, "report.edit", "report", report.id, ip=client_ip(request), section=section_id,
          version=report.version, missing_facts=missing)
    db.commit()
    state = request.app.state
    background.add_task(warm_artifacts, state.db.session_factory, state.settings.artifact_dir, report.id)
    return SectionSaveOut(version=report.version, section=_editor_section(section), missing_facts=missing)


@router.post("/{report_id}/sections/{section_id}/llm", response_model=LlmSectionOut)
def llm_section(report_id: str, section_id: str, request: Request, user: User = Depends(current_user),
                db: Session = Depends(get_db)) -> LlmSectionOut:
    """Proposal only — the editor shows a diff and the coach accepts or discards it."""
    report, document = _editable(db, user, report_id)
    _section(document, section_id)
    attempts: list = []
    try:
        configs = org_llm_configs(db, user.org_id, request.app.state.secret_key)
        if not configs:
            raise LLMError("chưa cấu hình khóa AI (Cài đặt → AI / LLM hoặc HD_LLM_API_KEY)")
        draft = llm_edit_section(document, section_id, llm_configs=configs,
                                 on_llm_attempt=collect_attempts(attempts))
    except LLMError as exc:
        if attempts:
            save_llm_usages(db, user.org_id, report_id, "section", attempts)
            db.commit()
        raise HTTPException(status_code=503, detail=f"AI chưa biên tập được phần này: {exc}") from exc
    save_llm_usages(db, user.org_id, report_id, "section", attempts)
    audit(db, user, "report.llm_section", "report", report.id, ip=client_ip(request), section=section_id)
    db.commit()
    return LlmSectionOut(draft=draft, missing_facts=missing_facts(document.chart, _baseline(report, section_id), draft))


@router.get("/{report_id}/revisions", response_model=list[RevisionOut])
def revisions(report_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[RevisionOut]:
    report = get_report_or_404(db, user, report_id)
    rows = db.scalars(select(ReportRevision).where(ReportRevision.report_id == report.id)
                      .order_by(ReportRevision.version.desc())).all()
    return [RevisionOut(version=r.version, author=r.author, change_type=r.change_type,
                        warnings_count=len(r.warnings or []), created_at=r.created_at) for r in rows]


@router.post("/{report_id}/revisions/{version}/restore", response_model=ReportDetailOut)
def restore(report_id: str, version: int, request: Request, background: BackgroundTasks,
            user: User = Depends(current_user), db: Session = Depends(get_db)) -> ReportDetailOut:
    """Undo to any version — as a *new* version, so history is never rewritten."""
    report, _ = _editable(db, user, report_id)
    revision = db.scalar(select(ReportRevision).where(ReportRevision.report_id == report.id,
                                                      ReportRevision.version == version))
    if revision is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên bản này.")
    store_document(db, report, ReportDocument.model_validate(revision.document), author=user.email,
                   change_type=f"restore:v{version}")
    audit(db, user, "report.restore", "report", report.id, ip=client_ip(request), from_version=version,
          version=report.version)
    db.commit()
    state = request.app.state
    background.add_task(warm_artifacts, state.db.session_factory, state.settings.artifact_dir, report.id)
    return report_detail(report)


@router.post("/{report_id}/regenerate", response_model=ReportDetailOut)
def regenerate(report_id: str, payload: RegenerateIn, request: Request, background: BackgroundTasks,
               user: User = Depends(current_user), db: Session = Depends(get_db)) -> ReportDetailOut:
    """Re-run generation from the stored request (e.g. after a failure or to switch content mode)."""
    report = get_report_or_404(db, user, report_id)
    if report.status == "generating":
        raise HTTPException(status_code=409, detail="Báo cáo đang được tạo.")
    if report.status == "archived":
        raise HTTPException(status_code=409, detail="Báo cáo đã lưu trữ.")
    if payload.content_mode is not None:
        report.request = {**report.request, "content_mode": payload.content_mode.value}
        report.content_mode = payload.content_mode.value
    request_model = ReportRequest.model_validate(report.request)
    audit(db, user, "report.regenerate", "report", report.id, ip=client_ip(request), content_mode=report.content_mode)
    state = request.app.state
    if request_model.content_mode is ContentMode.LLM:
        report.status, report.error = "generating", ""
        report.generation_attempts, report.job_heartbeat_at = 0, None
        db.commit()
        background.add_task(run_llm_generation, state.db.session_factory, report.id, user.email,
                            state.settings.artifact_dir, "regenerate",
                            llm_configs=org_llm_configs(db, user.org_id, state.secret_key),
                            heartbeat_seconds=state.settings.job_heartbeat_seconds)
    else:
        store_document(db, report, generate_report(request_model), author=user.email, change_type="regenerate")
        db.commit()
        background.add_task(warm_artifacts, state.db.session_factory, state.settings.artifact_dir, report.id)
    return report_detail(report)
