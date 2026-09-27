"""Admin: quản lý concept + kho câu hỏi game (Game Manager)."""

from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..deps import current_user, get_db
from ..models import GameConcept, GameCustomQuestion, GameDisabledQuestion, User
from ..schemas import (GameConceptAdminOut, GameConceptIn, GameConceptPatch, GameDisabledIn,
                       GameQuestionIn, GameQuestionOut, GameQuestionPatch, GameQuestionsOut)

router = APIRouter(prefix="/game", tags=["game-admin"])

BUILTIN_SLUGS = ("nguoc-dong", "thuong-vu", "linh-thu")
BUILTIN_STYLES = ("khoi_xuong", "kien_tao", "dan_duong", "tam_guong")
_SLUG_RE = re.compile(r"^[a-z0-9-]{2,32}$")
_CONTENT_FIELDS = ("name", "entry_label", "entry_desc", "icon", "intro", "bridge")


def _admin(user: User) -> None:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ admin mới quản lý được game.")


def ensure_builtin_concepts(db: Session) -> list[GameConcept]:
    """Đảm bảo 3 concept built-in có dòng settings (kể cả DB tạo bằng create_all)."""
    rows = {c.slug for c in db.scalars(select(GameConcept)).all()}
    changed = False
    for i, slug in enumerate(BUILTIN_SLUGS):
        if slug not in rows:
            db.add(GameConcept(slug=slug, enabled=True, is_builtin=True, sort_order=i * 10))
            changed = True
    if changed:
        db.commit()
    return list(db.scalars(select(GameConcept).order_by(GameConcept.sort_order, GameConcept.slug)).all())


def _get_concept(db: Session, slug: str) -> GameConcept:
    ensure_builtin_concepts(db)
    concept = db.get(GameConcept, slug)
    if concept is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy concept.")
    return concept


def _counts(db: Session) -> tuple[dict[str, int], dict[str, int], dict[str, int]]:
    custom_total: dict[str, int] = {}
    custom_enabled: dict[str, int] = {}
    rows = db.execute(select(GameCustomQuestion.concept_slug, GameCustomQuestion.enabled,
                             func.count()).group_by(GameCustomQuestion.concept_slug,
                                                    GameCustomQuestion.enabled)).all()
    for slug, enabled, n in rows:
        custom_total[slug] = custom_total.get(slug, 0) + n
        if enabled:
            custom_enabled[slug] = custom_enabled.get(slug, 0) + n
    disabled: dict[str, int] = {}
    for slug, n in db.execute(select(GameDisabledQuestion.concept_slug, func.count()).group_by(
            GameDisabledQuestion.concept_slug)).all():
        disabled[slug] = n
    return custom_total, custom_enabled, disabled


def _with_counts(db: Session, c: GameConcept) -> GameConceptAdminOut:
    total, enabled, disabled = _counts(db)
    row = GameConceptAdminOut.model_validate(c, from_attributes=True)
    row.custom_total = total.get(c.slug, 0)
    row.custom_enabled = enabled.get(c.slug, 0)
    row.disabled_builtin = disabled.get(c.slug, 0)
    return row


@router.get("/concepts", response_model=list[GameConceptAdminOut])
def list_concepts(user: User = Depends(current_user),
                  db: Session = Depends(get_db)) -> list[GameConceptAdminOut]:
    _admin(user)
    concepts = ensure_builtin_concepts(db)
    total, enabled, disabled = _counts(db)
    out = []
    for c in concepts:
        row = GameConceptAdminOut.model_validate(c, from_attributes=True)
        row.custom_total = total.get(c.slug, 0)
        row.custom_enabled = enabled.get(c.slug, 0)
        row.disabled_builtin = disabled.get(c.slug, 0)
        out.append(row)
    return out


@router.post("/concepts", response_model=GameConceptAdminOut)
def create_concept(payload: GameConceptIn, user: User = Depends(current_user),
                   db: Session = Depends(get_db)) -> GameConceptAdminOut:
    _admin(user)
    slug = payload.slug.strip()
    if not _SLUG_RE.match(slug):
        raise HTTPException(status_code=422, detail="Slug chỉ gồm chữ thường, số, gạch ngang (2-32 ký tự).")
    if slug in BUILTIN_SLUGS:
        raise HTTPException(status_code=422, detail="Slug này dành cho concept có sẵn.")
    for field in ("name", "entry_label", "entry_desc", "intro", "bridge"):
        if not getattr(payload, field).strip():
            raise HTTPException(status_code=422, detail="Vui lòng nhập đủ tên, nhãn, mô tả, intro và bridge.")
    ensure_builtin_concepts(db)
    if db.get(GameConcept, slug) is not None:
        raise HTTPException(status_code=409, detail="Slug đã tồn tại.")
    top = db.scalar(select(func.max(GameConcept.sort_order))) or 0
    concept = GameConcept(
        slug=slug, name=payload.name.strip(), entry_label=payload.entry_label.strip(),
        entry_desc=payload.entry_desc.strip(), icon=payload.icon.strip() or "🎮",
        intro=payload.intro.strip(), bridge=payload.bridge.strip(),
        enabled=False, is_builtin=False, sort_order=top + 10)
    db.add(concept)
    db.commit()
    return _with_counts(db, concept)


@router.patch("/concepts/{slug}", response_model=GameConceptAdminOut)
def update_concept(slug: str, payload: GameConceptPatch, user: User = Depends(current_user),
                   db: Session = Depends(get_db)) -> GameConceptAdminOut:
    _admin(user)
    c = _get_concept(db, slug)
    content = {k: getattr(payload, k) for k in _CONTENT_FIELDS if getattr(payload, k) is not None}
    if content and c.is_builtin:
        raise HTTPException(status_code=422, detail="Concept có sẵn chỉ đổi được bật/tắt và thứ tự.")
    if payload.enabled is not None:
        c.enabled = payload.enabled
    if payload.sort_order is not None:
        c.sort_order = payload.sort_order
    for k, v in content.items():
        v = v.strip()
        if k in ("name", "entry_label", "intro", "bridge") and not v:
            raise HTTPException(status_code=422, detail="Tên, nhãn, intro và bridge không được để trống.")
        setattr(c, k, v or ("🎮" if k == "icon" else v))
    db.commit()
    return _with_counts(db, c)


@router.delete("/concepts/{slug}")
def delete_concept(slug: str, user: User = Depends(current_user),
                   db: Session = Depends(get_db)) -> dict:
    _admin(user)
    c = _get_concept(db, slug)
    if c.is_builtin:
        raise HTTPException(status_code=422, detail="Không xóa được concept có sẵn.")
    for q in db.scalars(select(GameCustomQuestion).where(GameCustomQuestion.concept_slug == slug)).all():
        db.delete(q)
    for d in db.scalars(select(GameDisabledQuestion).where(GameDisabledQuestion.concept_slug == slug)).all():
        db.delete(d)
    db.delete(c)
    db.commit()
    return {"ok": True}


def _check_options(options: list) -> list[dict]:
    if len(options) != 4:
        raise HTTPException(status_code=422, detail="Mỗi câu hỏi cần đúng 4 đáp án.")
    out = []
    for o in options:
        t = (o.t or "").strip()
        if not t:
            raise HTTPException(status_code=422, detail="Đáp án không được để trống.")
        if o.s not in BUILTIN_STYLES:
            raise HTTPException(status_code=422, detail="Phong cách đáp án không hợp lệ.")
        out.append({"t": t[:500], "s": o.s})
    return out


@router.get("/questions", response_model=GameQuestionsOut)
def list_questions(concept_slug: str = Query(""), user: User = Depends(current_user),
                   db: Session = Depends(get_db)) -> GameQuestionsOut:
    _admin(user)
    if not concept_slug:
        raise HTTPException(status_code=422, detail="Thiếu concept.")
    _get_concept(db, concept_slug)
    custom = db.scalars(select(GameCustomQuestion).where(
        GameCustomQuestion.concept_slug == concept_slug).order_by(GameCustomQuestion.id)).all()
    disabled = db.scalars(select(GameDisabledQuestion.qid).where(
        GameDisabledQuestion.concept_slug == concept_slug)).all()
    return GameQuestionsOut(
        custom=[GameQuestionOut.model_validate(q, from_attributes=True) for q in custom],
        disabled_builtin=list(disabled))


@router.post("/questions", response_model=GameQuestionOut)
def create_question(payload: GameQuestionIn, user: User = Depends(current_user),
                    db: Session = Depends(get_db)) -> GameQuestionOut:
    _admin(user)
    c = _get_concept(db, payload.concept_slug.strip())
    title = payload.title.strip()
    sit = payload.sit.strip()
    if not title or not sit:
        raise HTTPException(status_code=422, detail="Vui lòng nhập tiêu đề và tình huống.")
    opts = _check_options(payload.options)
    row = GameCustomQuestion(concept_slug=c.slug, qid="tmp", title=title[:200], sit=sit[:2000],
                             options=opts, enabled=payload.enabled)
    db.add(row)
    db.flush()
    row.qid = f"cx{row.id:04d}"
    db.commit()
    return GameQuestionOut.model_validate(row, from_attributes=True)


@router.post("/questions/disabled")
def disable_builtin(payload: GameDisabledIn, user: User = Depends(current_user),
                    db: Session = Depends(get_db)) -> dict:
    _admin(user)
    c = _get_concept(db, payload.concept_slug.strip())
    qid = payload.qid.strip()[:24]
    if not qid:
        raise HTTPException(status_code=422, detail="Thiếu mã câu hỏi.")
    exists = db.scalar(select(GameDisabledQuestion).where(
        GameDisabledQuestion.concept_slug == c.slug, GameDisabledQuestion.qid == qid))
    if exists is None:
        db.add(GameDisabledQuestion(concept_slug=c.slug, qid=qid))
        db.commit()
    return {"ok": True}


@router.delete("/questions/disabled")
def enable_builtin(concept_slug: str = Query(""), qid: str = Query(""),
                   user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    _admin(user)
    row = db.scalar(select(GameDisabledQuestion).where(
        GameDisabledQuestion.concept_slug == concept_slug.strip(),
        GameDisabledQuestion.qid == qid.strip()))
    if row is not None:
        db.delete(row)
        db.commit()
    return {"ok": True}


@router.patch("/questions/{question_id}", response_model=GameQuestionOut)
def update_question(question_id: int, payload: GameQuestionPatch, user: User = Depends(current_user),
                    db: Session = Depends(get_db)) -> GameQuestionOut:
    _admin(user)
    row = db.get(GameCustomQuestion, question_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi.")
    if payload.title is not None:
        if not payload.title.strip():
            raise HTTPException(status_code=422, detail="Tiêu đề không được để trống.")
        row.title = payload.title.strip()[:200]
    if payload.sit is not None:
        if not payload.sit.strip():
            raise HTTPException(status_code=422, detail="Tình huống không được để trống.")
        row.sit = payload.sit.strip()[:2000]
    if payload.options is not None:
        row.options = _check_options(payload.options)
    if payload.enabled is not None:
        row.enabled = payload.enabled
    db.commit()
    return GameQuestionOut.model_validate(row, from_attributes=True)


@router.delete("/questions/{question_id}")
def delete_question(question_id: int, user: User = Depends(current_user),
                    db: Session = Depends(get_db)) -> dict:
    _admin(user)
    row = db.get(GameCustomQuestion, question_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi.")
    db.delete(row)
    db.commit()
    return {"ok": True}
