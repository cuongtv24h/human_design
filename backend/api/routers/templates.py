"""/api/v1/templates — quản trị mẫu báo cáo (Giai đoạn 1).

Mẫu hệ thống (sections/operating_manual) nằm trong code; DB chỉ chứa mẫu tùy chỉnh.
Hàng visibility=shared là bản sao độc lập trên thư viện chung.
Coach: tạo nháp + gửi duyệt. Admin: duyệt/xuất bản/quản lý toàn tổ chức.
"""

from __future__ import annotations

import re
import unicodedata

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.orm import Session

from backend.reporting.blocks import BLOCK_KINDS, BLOCK_VARIABLES, extract_variables
from backend.reporting.catalog import CORE_SECTIONS, DOMAIN_SPECS, NARRATIVE_SECTIONS
from backend.reporting.contract import ReportRequest
from backend.reporting.orchestrator import ReportOrchestrator

from ..deps import client_ip, current_user, get_db
from ..models import Organization, Report, ReportTemplate, TemplateBlock, TemplateSample, User
from ..schemas import (
    BlockCreate,
    BlockOut,
    BlockUpdate,
    BlockVariableOut,
    BuiltinSectionOut,
    FromBuiltinIn,
    OrgVarsIn,
    OrgVarsOut,
    ResolvedSectionOut,
    SampleCreate,
    SampleOut,
    SampleUpdate,
    TemplateCreate,
    TemplateDetailOut,
    TemplatePreviewIn,
    TemplatePreviewOut,
    TemplatePublishIn,
    TemplateSummaryOut,
    TemplateUpdate,
)
from ..services import audit, build_template_snapshot, snapshot_sections

router = APIRouter(prefix="/templates", tags=["templates"])

BUILTIN_SECTIONS: dict[str, dict[str, str]] = {}
for _spec in (*CORE_SECTIONS, *NARRATIVE_SECTIONS):
    BUILTIN_SECTIONS[_spec.id] = {"title": _spec.title, "kind": _spec.kind}
for _name, _dspec in DOMAIN_SPECS.items():
    BUILTIN_SECTIONS[f"domain_{_name.value}"] = {"title": _dspec.title, "kind": "domain"}

_STATUSES = ("draft", "pending", "active", "rejected", "archived")
_COACH_EDITABLE = ("draft", "pending", "rejected")
_COACH_TRANSITIONS = {("draft", "pending"), ("pending", "draft"), ("rejected", "draft"), ("rejected", "pending")}
_MAX_SAMPLES = 10

_DEMO_SUBJECT = {"name": "Khách hàng mẫu", "birth_date": "1990-05-15", "birth_time": "08:30",
                 "timezone": "+07:00", "birth_location": "Hòa Bình"}


# --- helpers ------------------------------------------------------------------

def _slug(name: str) -> str:
    text = unicodedata.normalize("NFKD", (name or "").lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:30] or "mau"


def _unique_key(db: Session, org_id: int | None, visibility: str, base: str) -> str:
    query = select(ReportTemplate.key).where(ReportTemplate.visibility == visibility)
    if visibility == "private":
        query = query.where(ReportTemplate.org_id == org_id)
    taken = set(db.scalars(query).all())
    key, i = base or "mau", 2
    while key in taken:
        key, i = f"{base[:24]}-{i}", i + 1
    return key


def _get(db: Session, user: User, template_id: int) -> ReportTemplate:
    tpl = db.get(ReportTemplate, template_id)
    if tpl is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy mẫu báo cáo.")
    if tpl.visibility == "shared":
        return tpl
    if tpl.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Không tìm thấy mẫu báo cáo.")
    if user.role != "admin" and tpl.created_by != user.id and tpl.status != "active":
        raise HTTPException(status_code=404, detail="Không tìm thấy mẫu báo cáo.")
    return tpl


def _require_owner_private(db: Session, admin: User, template_id: int) -> ReportTemplate:
    tpl = db.get(ReportTemplate, template_id)
    if (tpl is None or tpl.visibility != "private" or tpl.org_id != admin.org_id
            or admin.role != "admin"):
        raise HTTPException(status_code=404, detail="Không tìm thấy mẫu báo cáo.")
    return tpl


def _validate_sections(db: Session, user: User, sections) -> list[dict]:
    out: list[dict] = []
    for entry in sections or []:
        if entry.type == "builtin":
            if not entry.ref or entry.ref not in BUILTIN_SECTIONS:
                raise HTTPException(status_code=422, detail=f"Mục dựng sẵn không tồn tại: {entry.ref!r}.")
            out.append({"type": "builtin", "ref": entry.ref, "title_override": (entry.title_override or "")[:160]})
        else:
            if entry.block_id:
                blk = db.get(TemplateBlock, entry.block_id)
                if blk is None or blk.org_id != user.org_id:
                    raise HTTPException(status_code=422, detail="Khối nội dung không tồn tại.")
                out.append({"type": "block", "block_id": blk.id,
                            "title_override": (entry.title_override or "")[:160]})
                continue
            kind = entry.kind or "core"
            if kind not in BLOCK_KINDS:
                raise HTTPException(status_code=422, detail="Loại khối không hợp lệ.")
            if not (entry.body or "").strip():
                raise HTTPException(status_code=422, detail="Khối viết trực tiếp chưa có nội dung.")
            out.append({"type": "block", "block_id": None,
                        "name": (entry.name or "").strip()[:120] or "Khối nội dung",
                        "kind": kind, "title": (entry.title or "").strip()[:160], "body": entry.body})
    return out


def _resolve_sections(db: Session, tpl: ReportTemplate) -> list[ResolvedSectionOut]:
    out: list[ResolvedSectionOut] = []
    for entry in (tpl.sections or []):
        if entry.get("type") == "builtin":
            meta = BUILTIN_SECTIONS.get(entry.get("ref", ""), {"title": entry.get("ref", ""), "kind": "core"})
            out.append(ResolvedSectionOut(type="builtin", ref=entry.get("ref", ""),
                                          title=entry.get("title_override") or meta["title"],
                                          title_default=meta["title"], kind=meta["kind"]))
        else:
            blk = db.get(TemplateBlock, entry.get("block_id")) if entry.get("block_id") else None
            if blk is not None:
                out.append(ResolvedSectionOut(type="block", block_id=blk.id, name=blk.name,
                                              title=entry.get("title_override") or blk.name,
                                              title_default=blk.name, kind=blk.kind, body=blk.body))
            else:
                out.append(ResolvedSectionOut(type="block", name=entry.get("name", ""),
                                              title=entry.get("title") or "Khối nội dung",
                                              kind=entry.get("kind", "core"), body=entry.get("body", "")))
    return out


def _samples(db: Session, template_id: int) -> list[TemplateSample]:
    return db.scalars(select(TemplateSample).where(TemplateSample.template_id == template_id)
                      .order_by(TemplateSample.sort, TemplateSample.id)).all()


def _reports_count(db: Session, user: User, tpl: ReportTemplate) -> int:
    query = select(func.count()).select_from(Report).where(Report.template == tpl.key)
    if tpl.visibility == "private":
        query = query.where(Report.org_id == user.org_id)
    return db.scalar(query) or 0


def _created_by_name(db: Session, user_id: int) -> str:
    author = db.get(User, user_id)
    return (author.full_name or author.email) if author else ""


def _summary(db: Session, user: User, tpl: ReportTemplate) -> TemplateSummaryOut:
    return TemplateSummaryOut(
        id=tpl.id, key=tpl.key, name=tpl.name, description=tpl.description, badge=tpl.badge,
        visibility=tpl.visibility, status=tpl.status, version=tpl.version,
        sections_count=len(tpl.sections or []),
        samples_count=db.scalar(select(func.count()).select_from(TemplateSample)
                                .where(TemplateSample.template_id == tpl.id)) or 0,
        reports_count=_reports_count(db, user, tpl), origin_label=tpl.origin_label,
        import_count=tpl.import_count, created_by_name=_created_by_name(db, tpl.created_by),
        created_at=tpl.created_at, updated_at=tpl.updated_at,
    )


def _detail(db: Session, user: User, tpl: ReportTemplate) -> TemplateDetailOut:
    base = _summary(db, user, tpl).model_dump()
    return TemplateDetailOut(
        **base, review_note=tpl.review_note or "", sections=_resolve_sections(db, tpl),
        samples=[SampleOut(id=s.id, title=s.title, body=s.body, sort=s.sort) for s in _samples(db, tpl.id)],
    )


def _transition(user: User, tpl: ReportTemplate, new_status: str, note: str) -> None:
    if new_status == tpl.status:
        return
    if new_status not in _STATUSES:
        raise HTTPException(status_code=422, detail="Trạng thái không hợp lệ.")
    if user.role != "admin":
        if tpl.created_by != user.id or tpl.visibility != "private":
            raise HTTPException(status_code=403, detail="Bạn chỉ được gửi duyệt mẫu của chính mình.")
        if new_status in ("active", "archived"):
            raise HTTPException(status_code=403, detail="Chỉ quản trị viên được duyệt/bật mẫu.")
        if (tpl.status, new_status) not in _COACH_TRANSITIONS:
            raise HTTPException(status_code=422, detail="Chuyển trạng thái không hợp lệ.")
    if new_status in ("pending", "active") and not (tpl.sections or []):
        raise HTTPException(status_code=422, detail="Mẫu chưa có nội dung, chưa thể gửi duyệt/bật.")
    if new_status == "rejected" and user.role == "admin" and not (note or "").strip():
        raise HTTPException(status_code=422, detail="Cần ghi lý do từ chối.")
    tpl.status = new_status
    tpl.review_note = (note or "").strip() if new_status == "rejected" else ""


def _block_usage(db: Session, org_id: int) -> dict[int, list[str]]:
    usage: dict[int, list[str]] = {}
    rows = db.scalars(select(ReportTemplate).where(ReportTemplate.org_id == org_id,
                                                   ReportTemplate.visibility == "private")).all()
    for tpl in rows:
        for entry in (tpl.sections or []):
            if entry.get("type") == "block" and entry.get("block_id"):
                usage.setdefault(entry["block_id"], []).append(tpl.name)
    return usage


def _org_var_list(org: Organization | None) -> list[dict]:
    return list(((org.template_vars if org else None) or {}).get("vars", []))


def _copy_samples(db: Session, source_id: int, target: ReportTemplate) -> None:
    for sample in _samples(db, source_id):
        db.add(TemplateSample(template_id=target.id, title=sample.title, body=sample.body, sort=sample.sort))


def _inline_sections(db: Session, tpl: ReportTemplate) -> list[dict]:
    """Chuyển sections (kể cả block tham chiếu) thành bản tự chứa để chia sẻ/sao chép."""
    stored: list[dict] = []
    for entry in (tpl.sections or []):
        if entry.get("type") == "builtin":
            stored.append({"type": "builtin", "ref": entry.get("ref", ""),
                           "title_override": entry.get("title_override", "")})
            continue
        blk = db.get(TemplateBlock, entry.get("block_id")) if entry.get("block_id") else None
        if blk is not None:
            stored.append({"type": "block", "block_id": None, "name": blk.name, "kind": blk.kind,
                           "title": entry.get("title_override") or blk.name, "body": blk.body})
        else:
            stored.append({"type": "block", "block_id": None, "name": entry.get("name", ""),
                           "kind": entry.get("kind", "core"), "title": entry.get("title", ""),
                           "body": entry.get("body", "")})
    return stored


# --- manage -------------------------------------------------------------------

@router.get("", response_model=list[TemplateSummaryOut])
def list_templates(q: str = "", status: str = "",
                   user: User = Depends(current_user), db: Session = Depends(get_db)):
    query = select(ReportTemplate).where(ReportTemplate.org_id == user.org_id)
    if user.role != "admin":
        query = query.where(or_(ReportTemplate.created_by == user.id,
                                and_(ReportTemplate.status == "active",
                                     ReportTemplate.visibility == "private")))
    if q.strip():
        query = query.where(ReportTemplate.name.ilike(f"%{q.strip()}%"))
    if status:
        if status not in _STATUSES:
            raise HTTPException(status_code=422, detail="Trạng thái không hợp lệ.")
        query = query.where(ReportTemplate.status == status)
    rows = db.scalars(query.order_by(ReportTemplate.updated_at.desc())).all()
    return [_summary(db, user, tpl) for tpl in rows]


@router.post("", response_model=TemplateDetailOut, status_code=201)
def create_template(payload: TemplateCreate, request: Request, user: User = Depends(current_user),
                    db: Session = Depends(get_db)) -> TemplateDetailOut:
    sections = _validate_sections(db, user, payload.sections)
    tpl = ReportTemplate(org_id=user.org_id, key=_unique_key(db, user.org_id, "private", _slug(payload.name)),
                         name=payload.name.strip(), description=payload.description.strip(),
                         badge=payload.badge.strip(), visibility="private", status="draft",
                         sections=sections, created_by=user.id)
    db.add(tpl)
    db.flush()
    audit(db, user, "template.create", "template", tpl.id, ip=client_ip(request), key=tpl.key)
    db.commit()
    return _detail(db, user, tpl)


@router.get("/library", response_model=list[TemplateSummaryOut])
def library(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(ReportTemplate).where(ReportTemplate.visibility == "shared",
                                                   ReportTemplate.status == "active")
                      .order_by(ReportTemplate.import_count.desc(), ReportTemplate.updated_at.desc())).all()
    return [_summary(db, user, tpl) for tpl in rows]


@router.post("/library/{key}/import", response_model=TemplateDetailOut, status_code=201)
def import_template(key: str, request: Request, user: User = Depends(current_user),
                    db: Session = Depends(get_db)) -> TemplateDetailOut:
    src = db.scalar(select(ReportTemplate).where(ReportTemplate.visibility == "shared",
                                                 ReportTemplate.key == key,
                                                 ReportTemplate.status == "active"))
    if src is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy mẫu trong thư viện chung.")
    if src.org_id == user.org_id:
        raise HTTPException(status_code=422, detail="Đây là mẫu của tổ chức bạn, không cần lấy về.")
    copy = ReportTemplate(
        org_id=user.org_id, key=_unique_key(db, user.org_id, "private", _slug(src.name)),
        name=src.name, description=src.description, badge="", visibility="private", status="draft",
        sections=_inline_sections(db, src), created_by=user.id, origin_template_id=src.id,
        origin_label=f"Thư viện chung · {src.origin_label or src.name}",
    )
    db.add(copy)
    db.flush()
    _copy_samples(db, src.id, copy)
    src.import_count += 1
    audit(db, user, "template.import", "template", copy.id, ip=client_ip(request), origin=src.id)
    db.commit()
    return _detail(db, user, copy)


@router.patch("/{template_id}", response_model=TemplateDetailOut)
def update_template(template_id: int, payload: TemplateUpdate, request: Request,
                    user: User = Depends(current_user), db: Session = Depends(get_db)) -> TemplateDetailOut:
    tpl = _get(db, user, template_id)
    if payload.visibility == "shared":
        raise HTTPException(status_code=422, detail="Hãy dùng chức năng Chia sẻ ra thư viện chung.")
    if tpl.visibility == "shared":
        if not (user.role == "admin" and tpl.org_id == user.org_id):
            raise HTTPException(status_code=403, detail="Chỉ tổ chức sở hữu được quản lý bản chia sẻ.")
        content = payload.model_dump(exclude_unset=True, exclude={"status", "review_note", "visibility"})
        if content:
            raise HTTPException(status_code=422, detail="Bản chia sẻ chỉ đọc — hãy sửa bản gốc rồi Cập nhật bản chia sẻ.")
        if payload.status is not None and payload.status not in ("active", "archived", tpl.status):
            raise HTTPException(status_code=422, detail="Bản chia sẻ chỉ bật/tắt được.")
    elif user.role != "admin":
        if tpl.created_by != user.id or tpl.status not in _COACH_EDITABLE:
            raise HTTPException(status_code=403, detail="Bạn chỉ được sửa mẫu của chính mình khi còn ở nháp/chờ duyệt.")
    changed = payload.model_dump(exclude_unset=True, exclude={"status", "review_note", "visibility"})
    if changed:
        if payload.name is not None:
            tpl.name = payload.name.strip()
        if payload.description is not None:
            tpl.description = payload.description.strip()
        if payload.badge is not None:
            tpl.badge = payload.badge.strip()
        if payload.sections is not None:
            tpl.sections = _validate_sections(db, user, payload.sections)
        tpl.version += 1
        if user.role != "admin" and tpl.status == "pending":
            tpl.status, tpl.review_note = "draft", ""
    if payload.status is not None:
        _transition(user, tpl, payload.status, payload.review_note or "")
    audit(db, user, "template.update", "template", tpl.id, ip=client_ip(request),
          fields=sorted(changed) + ([f"status->{payload.status}"] if payload.status else []))
    db.commit()
    return _detail(db, user, tpl)


@router.delete("/{template_id}", status_code=204)
def delete_template(template_id: int, request: Request, user: User = Depends(current_user),
                    db: Session = Depends(get_db)) -> None:
    tpl = _get(db, user, template_id)
    if tpl.visibility == "shared":
        if not (user.role == "admin" and tpl.org_id == user.org_id):
            raise HTTPException(status_code=403, detail="Chỉ tổ chức sở hữu được gỡ bản chia sẻ.")
    elif user.role != "admin":
        if tpl.created_by != user.id or tpl.status == "active":
            raise HTTPException(status_code=403, detail="Bạn chỉ được xóa mẫu của chính mình khi chưa bật.")
    else:
        if tpl.org_id != user.org_id:
            raise HTTPException(status_code=404, detail="Không tìm thấy mẫu báo cáo.")
    db.execute(delete(TemplateSample).where(TemplateSample.template_id == tpl.id))
    audit(db, user, "template.delete", "template", tpl.id, ip=client_ip(request), key=tpl.key)
    db.delete(tpl)
    db.commit()


@router.post("/{template_id}/duplicate", response_model=TemplateDetailOut, status_code=201)
def duplicate_template(template_id: int, request: Request, user: User = Depends(current_user),
                       db: Session = Depends(get_db)) -> TemplateDetailOut:
    src = _get(db, user, template_id)
    if src.visibility != "shared" and (src.org_id != user.org_id or (
            user.role != "admin" and src.created_by != user.id and src.status != "active")):
        raise HTTPException(status_code=404, detail="Không tìm thấy mẫu báo cáo.")
    if src.visibility != "shared" and user.role != "admin" and src.created_by != user.id:
        raise HTTPException(status_code=403, detail="Bạn chỉ được sao chép mẫu của chính mình.")
    copy = ReportTemplate(
        org_id=user.org_id, key=_unique_key(db, user.org_id, "private", _slug(src.name)),
        name=src.name, description=src.description, badge="", visibility="private", status="draft",
        sections=_inline_sections(db, src), created_by=user.id, origin_template_id=src.id,
        origin_label=f"Thư viện chung · {src.origin_label or src.name}" if src.visibility == "shared"
        else f"Bản sao của {src.name}",
    )
    db.add(copy)
    db.flush()
    _copy_samples(db, src.id, copy)
    if src.visibility == "shared":
        src.import_count += 1
    audit(db, user, "template.duplicate", "template", copy.id, ip=client_ip(request), origin=src.id)
    db.commit()
    return _detail(db, user, copy)


@router.post("/from-builtin", response_model=TemplateDetailOut, status_code=201)
def from_builtin(payload: FromBuiltinIn, request: Request, user: User = Depends(current_user),
                 db: Session = Depends(get_db)) -> TemplateDetailOut:
    refs = [s.id for s in CORE_SECTIONS] if payload.builtin == "sections" else [s.id for s in NARRATIVE_SECTIONS]
    tpl = ReportTemplate(
        org_id=user.org_id, key=_unique_key(db, user.org_id, "private", _slug(payload.name)),
        name=payload.name.strip(), description="", badge="", visibility="private", status="draft",
        sections=[{"type": "builtin", "ref": ref, "title_override": ""} for ref in refs],
        created_by=user.id, origin_label=f"Từ mẫu hệ thống {payload.builtin}",
    )
    db.add(tpl)
    db.flush()
    audit(db, user, "template.create", "template", tpl.id, ip=client_ip(request), builtin=payload.builtin)
    db.commit()
    return _detail(db, user, tpl)


# --- publish / import -----------------------------------------------------------

@router.post("/{template_id}/publish", response_model=TemplateSummaryOut)
def publish_template(template_id: int, payload: TemplatePublishIn, request: Request,
                     user: User = Depends(current_user),
                     db: Session = Depends(get_db)) -> TemplateSummaryOut:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ quản trị viên được chia sẻ mẫu.")
    tpl = _require_owner_private(db, user, template_id)
    if tpl.status != "active":
        raise HTTPException(status_code=422, detail="Chỉ chia sẻ mẫu đang hoạt động.")
    org = db.get(Organization, user.org_id)
    shared = db.scalar(select(ReportTemplate).where(ReportTemplate.visibility == "shared",
                                                    ReportTemplate.key == tpl.key))
    if shared is not None and shared.org_id != user.org_id:
        raise HTTPException(status_code=409, detail=f"Thư viện đã có mẫu '{tpl.key}' của {shared.origin_label}.")
    badge = payload.badge.strip() or tpl.badge
    origin_label = payload.origin_label.strip() or (org.name if org else "")
    if shared is None:
        shared = ReportTemplate(org_id=user.org_id, key=tpl.key, visibility="shared", status="active",
                                name=tpl.name, description=tpl.description, badge=badge,
                                sections=_inline_sections(db, tpl), version=1,
                                origin_template_id=tpl.id, origin_label=origin_label,
                                created_by=user.id)
        db.add(shared)
        db.flush()
    else:
        shared.name, shared.description, shared.badge = tpl.name, tpl.description, badge
        shared.origin_label = origin_label
        shared.sections = _inline_sections(db, tpl)
        shared.version += 1
        shared.status = "active"
    db.execute(delete(TemplateSample).where(TemplateSample.template_id == shared.id))
    db.flush()
    _copy_samples(db, tpl.id, shared)
    audit(db, user, "template.publish", "template", shared.id, ip=client_ip(request), origin=tpl.id)
    db.commit()
    return _summary(db, user, shared)


@router.post("/{template_id}/unpublish", status_code=204)
def unpublish_template(template_id: int, request: Request, user: User = Depends(current_user),
                       db: Session = Depends(get_db)) -> None:
    tpl = _require_owner_private(db, user, template_id)
    shared = db.scalar(select(ReportTemplate).where(ReportTemplate.visibility == "shared",
                                                    ReportTemplate.key == tpl.key))
    if shared is None:
        raise HTTPException(status_code=404, detail="Mẫu chưa được chia sẻ ra thư viện chung.")
    db.execute(delete(TemplateSample).where(TemplateSample.template_id == shared.id))
    audit(db, user, "template.unpublish", "template", shared.id, ip=client_ip(request), key=tpl.key)
    db.delete(shared)
    db.commit()


# --- samples --------------------------------------------------------------------

@router.post("/{template_id}/samples", response_model=SampleOut, status_code=201)
def add_sample(template_id: int, payload: SampleCreate, request: Request,
               user: User = Depends(current_user), db: Session = Depends(get_db)) -> SampleOut:
    tpl = _get(db, user, template_id)
    _require_editable(user, tpl)
    count = db.scalar(select(func.count()).select_from(TemplateSample)
                      .where(TemplateSample.template_id == tpl.id)) or 0
    if count >= _MAX_SAMPLES:
        raise HTTPException(status_code=422, detail=f"Mỗi mẫu tối đa {_MAX_SAMPLES} bài mẫu.")
    sample = TemplateSample(template_id=tpl.id, title=payload.title.strip(), body=payload.body,
                            sort=payload.sort)
    db.add(sample)
    tpl.version += 1
    db.flush()
    audit(db, user, "template.sample_add", "template", tpl.id, ip=client_ip(request))
    db.commit()
    return SampleOut(id=sample.id, title=sample.title, body=sample.body, sort=sample.sort)


def _require_editable(user: User, tpl: ReportTemplate) -> None:
    if tpl.visibility == "shared":
        raise HTTPException(status_code=422, detail="Bản chia sẻ chỉ đọc.")
    if user.role == "admin":
        if tpl.org_id != user.org_id:
            raise HTTPException(status_code=404, detail="Không tìm thấy mẫu báo cáo.")
        return
    if tpl.created_by != user.id or tpl.status not in _COACH_EDITABLE:
        raise HTTPException(status_code=403, detail="Bạn chỉ được sửa mẫu của chính mình khi còn ở nháp/chờ duyệt.")


@router.patch("/samples/{sample_id}", response_model=SampleOut)
def update_sample(sample_id: int, payload: SampleUpdate, request: Request,
                  user: User = Depends(current_user), db: Session = Depends(get_db)) -> SampleOut:
    sample = db.get(TemplateSample, sample_id)
    if sample is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài mẫu.")
    tpl = _get(db, user, sample.template_id)
    _require_editable(user, tpl)
    if payload.title is not None:
        sample.title = payload.title.strip()
    if payload.body is not None:
        sample.body = payload.body
    if payload.sort is not None:
        sample.sort = payload.sort
    tpl.version += 1
    audit(db, user, "template.sample_update", "template", tpl.id, ip=client_ip(request))
    db.commit()
    return SampleOut(id=sample.id, title=sample.title, body=sample.body, sort=sample.sort)


@router.delete("/samples/{sample_id}", status_code=204)
def delete_sample(sample_id: int, request: Request, user: User = Depends(current_user),
                  db: Session = Depends(get_db)) -> None:
    sample = db.get(TemplateSample, sample_id)
    if sample is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài mẫu.")
    tpl = _get(db, user, sample.template_id)
    _require_editable(user, tpl)
    tpl.version += 1
    audit(db, user, "template.sample_delete", "template", tpl.id, ip=client_ip(request))
    db.delete(sample)
    db.commit()


# --- blocks ---------------------------------------------------------------------

@router.get("/blocks", response_model=list[BlockOut])
def list_blocks(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(TemplateBlock).where(TemplateBlock.org_id == user.org_id)
                      .order_by(TemplateBlock.name)).all()
    usage = _block_usage(db, user.org_id)
    return [BlockOut(id=b.id, name=b.name, kind=b.kind, body=b.body,
                       variables=sorted(extract_variables(b.body or "")),
                       used_in=usage.get(b.id, [])) for b in rows]


@router.post("/blocks", response_model=BlockOut, status_code=201)
def create_block(payload: BlockCreate, request: Request, user: User = Depends(current_user),
                 db: Session = Depends(get_db)) -> BlockOut:
    if payload.kind not in BLOCK_KINDS:
        raise HTTPException(status_code=422, detail="Loại khối không hợp lệ.")
    blk = TemplateBlock(org_id=user.org_id, name=payload.name.strip(), kind=payload.kind,
                        body=payload.body, created_by=user.id)
    db.add(blk)
    db.flush()
    audit(db, user, "template.block_create", "template_block", blk.id, ip=client_ip(request))
    db.commit()
    return BlockOut(id=blk.id, name=blk.name, kind=blk.kind, body=blk.body,
                    variables=sorted(extract_variables(blk.body or "")), used_in=[])


@router.patch("/blocks/{block_id}", response_model=BlockOut)
def update_block(block_id: int, payload: BlockUpdate, request: Request,
                 user: User = Depends(current_user), db: Session = Depends(get_db)) -> BlockOut:
    blk = db.get(TemplateBlock, block_id)
    if blk is None or blk.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Không tìm thấy khối nội dung.")
    if user.role != "admin" and blk.created_by != user.id:
        raise HTTPException(status_code=403, detail="Bạn chỉ được sửa khối của chính mình.")
    if payload.name is not None:
        blk.name = payload.name.strip()
    if payload.kind is not None:
        if payload.kind not in BLOCK_KINDS:
            raise HTTPException(status_code=422, detail="Loại khối không hợp lệ.")
        blk.kind = payload.kind
    if payload.body is not None:
        blk.body = payload.body
    audit(db, user, "template.block_update", "template_block", blk.id, ip=client_ip(request))
    db.commit()
    return BlockOut(id=blk.id, name=blk.name, kind=blk.kind, body=blk.body,
                    variables=sorted(extract_variables(blk.body or "")),
                    used_in=_block_usage(db, user.org_id).get(blk.id, []))


@router.delete("/blocks/{block_id}", status_code=204)
def delete_block(block_id: int, request: Request, user: User = Depends(current_user),
                 db: Session = Depends(get_db)) -> None:
    blk = db.get(TemplateBlock, block_id)
    if blk is None or blk.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Không tìm thấy khối nội dung.")
    if user.role != "admin" and blk.created_by != user.id:
        raise HTTPException(status_code=403, detail="Bạn chỉ được xóa khối của chính mình.")
    used = _block_usage(db, user.org_id).get(blk.id, [])
    if used:
        raise HTTPException(status_code=409, detail=f"Khối đang dùng trong: {', '.join(used[:5])}.")
    audit(db, user, "template.block_delete", "template_block", blk.id, ip=client_ip(request))
    db.delete(blk)
    db.commit()


# --- org vars / variables / preview ----------------------------------------------

@router.get("/variables", response_model=list[BlockVariableOut])
def block_variables(user: User = Depends(current_user)):
    return [BlockVariableOut(**var) for var in BLOCK_VARIABLES]


@router.get("/builtin-sections", response_model=list[BuiltinSectionOut])
def builtin_sections():
    return [BuiltinSectionOut(id=key, title=meta["title"], kind=meta["kind"])
            for key, meta in BUILTIN_SECTIONS.items()]


@router.get("/org-vars", response_model=OrgVarsOut)
def get_org_vars(user: User = Depends(current_user), db: Session = Depends(get_db)) -> OrgVarsOut:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ quản trị viên được xem biến tổ chức.")
    org = db.get(Organization, user.org_id)
    return OrgVarsOut(vars=_org_var_list(org))


@router.put("/org-vars", response_model=OrgVarsOut)
def put_org_vars(payload: OrgVarsIn, request: Request, user: User = Depends(current_user),
                 db: Session = Depends(get_db)) -> OrgVarsOut:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ quản trị viên được sửa biến tổ chức.")
    keys = [var.key for var in payload.vars]
    if len(set(keys)) != len(keys):
        raise HTTPException(status_code=422, detail="Key biến tổ chức bị trùng.")
    org = db.get(Organization, user.org_id)
    org.template_vars = {"vars": [var.model_dump() for var in payload.vars]}
    audit(db, user, "template.org_vars", "organization", org.id, ip=client_ip(request))
    db.commit()
    return OrgVarsOut(vars=_org_var_list(org))


@router.post("/preview", response_model=TemplatePreviewOut)
def preview_template(payload: TemplatePreviewIn, user: User = Depends(current_user),
                     db: Session = Depends(get_db)) -> TemplatePreviewOut:
    from ..services import org_var_map  # tránh import vòng lúc nạp module
    if payload.template_id is not None:
        tpl = _get(db, user, payload.template_id)
        snapshot = build_template_snapshot(db, tpl)
        key = tpl.key
    elif payload.definition is not None:
        sections = _validate_sections(db, user, payload.definition.sections)
        if not sections:
            raise HTTPException(status_code=422, detail="Chưa có nội dung để xem trước.")
        snapshot = {"key": "__preview__", "name": payload.definition.name.strip() or "Xem trước",
                    "description": "", "version": 0, "sections": snapshot_sections(db, sections)}
        key = "__preview__"
    else:
        raise HTTPException(status_code=422, detail="Cần template_id hoặc definition.")
    if not snapshot["sections"]:
        raise HTTPException(status_code=422, detail="Chưa có nội dung để xem trước.")
    org = db.get(Organization, user.org_id)
    request = ReportRequest.model_validate({
        "subject": dict(_DEMO_SUBJECT), "tier": "deep_core", "template": key, "domains": [],
        "options": {"custom_template": snapshot, "org_vars": org_var_map(org)},
    })
    document = ReportOrchestrator().run(request)
    return TemplatePreviewOut(
        title=document.title,
        sections=[{"id": s.id, "title": s.title, "markdown": s.content_markdown}
                  for s in sorted(document.sections, key=lambda item: item.order)],
        warnings=list(document.warnings),
    )


@router.get("/{template_id}", response_model=TemplateDetailOut)
def get_template(template_id: int, user: User = Depends(current_user),
                 db: Session = Depends(get_db)) -> TemplateDetailOut:
    return _detail(db, user, _get(db, user, template_id))
