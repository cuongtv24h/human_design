"""Admin: quản lý concept + kho câu hỏi game (Game Manager)."""

from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..deps import current_user, get_db
from ..models import (GameChapter, GameConcept, GameCustomQuestion, GameDisabledQuestion,
                                GameNode, User)
from ..schemas import (GameChapterIn, GameChapterOut, GameChapterPatch, GameConceptAdminOut,
                       GameConceptIn, GameConceptPatch, GameDisabledIn, GameNodeIn, GameNodeOut,
                       GameNodePatch, GameQuestionIn, GameQuestionOut, GameQuestionPatch,
                       GameQuestionsOut)

router = APIRouter(prefix="/game", tags=["game-admin"])

BUILTIN_SLUGS = ("nguoc-dong", "thuong-vu", "linh-thu")
# Game nằm ở URL gốc (/[slug]) nên slug custom không được trùng đường dẫn hệ thống.
RESERVED_SLUGS = frozenset({"admin", "api", "game", "choi", "r", "doi-chieu", "ket-qua", "so-bai"})
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
    if slug in RESERVED_SLUGS:
        raise HTTPException(status_code=422, detail="Slug này trùng đường dẫn hệ thống.")
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

# --- cấu trúc chương/màn (thiếu = client dùng mặc định trong code) ---

NODE_MODES = ("normal", "speed", "boss")

# Copy mặc định (đồng bộ với web/lib/game/stages.ts) — nút "copy mặc định".
DEFAULT_CHAPTERS: dict[str, list[dict]] = {
    "nguoc-dong": [
        {"name": "Thức Tỉnh", "icon": "🌅", "desc": "Nhận ra mình đang sống theo kỳ vọng của người khác."},
        {"name": "Va Chạm", "icon": "💥", "desc": "Những tình huống đầu tiên thử phản xạ thật của bạn."},
        {"name": "Soi Gương", "icon": "🪞", "desc": "Nhìn thẳng vào cách mình ra quyết định mỗi ngày."},
        {"name": "Bứt Phá", "icon": "🚀", "desc": "Trùm cuối: sống đúng thiết kế, hay quay về lối cũ?"},
    ],
    "thuong-vu": [
        {"name": "Nhận Dự Án", "icon": "📋", "desc": "Dự án mới, sếp mới, áp lực mới."},
        {"name": "Deadline Dí", "icon": "⏰", "desc": "Mọi thứ cháy cùng lúc — bạn ưu tiên gì?"},
        {"name": "Đàm Phán", "icon": "🤝", "desc": "Bàn đàm phán là nơi lộ rõ bản chất nhất."},
        {"name": "Chốt Deal", "icon": "🏆", "desc": "Trùm cuối: thương vụ sinh tử quyết định tất cả."},
    ],
    "linh-thu": [
        {"name": "Vào Rừng", "icon": "🌲", "desc": "Bước vào khu rừng nơi linh thú soi thấu lòng người."},
        {"name": "Dấu Vết", "icon": "🐾", "desc": "Mỗi lựa chọn để lại một dấu vết trong rừng."},
        {"name": "Đối Mặt", "icon": "🦁", "desc": "Linh thú hiện thân từ chính phản xạ của bạn."},
        {"name": "Linh Thú Vương", "icon": "👑", "desc": "Trùm cuối: thuần hóa được nó, hay bị nó nuốt?"},
    ],
}
GENERIC_CHAPTERS = [
    {"name": "Chương 1", "icon": "🗺️", "desc": "Bắt đầu hành trình."},
    {"name": "Chương 2", "icon": "🧭", "desc": "Đi sâu hơn vào thế giới này."},
    {"name": "Chương 3", "icon": "⚔️", "desc": "Thử thách tăng dần."},
    {"name": "Chương 4", "icon": "👑", "desc": "Trùm cuối đang chờ."},
]


def _check_node(mode: str, count: int, time_limit: int, ids: list) -> list[str]:
    if mode not in NODE_MODES:
        raise HTTPException(status_code=422, detail="Mode phải là normal, speed hoặc boss.")
    if not 1 <= count <= 25:
        raise HTTPException(status_code=422, detail="Số câu mỗi màn từ 1 đến 25.")
    if not 0 <= time_limit <= 120:
        raise HTTPException(status_code=422, detail="Giới hạn giờ từ 0 (auto) đến 120 giây.")
    clean = [str(q).strip()[:24] for q in ids if str(q).strip()]
    if len(clean) > 25:
        raise HTTPException(status_code=422, detail="Set câu chọn tay tối đa 25 câu.")
    return clean


def _node_out(n: GameNode) -> GameNodeOut:
    ids = list(n.question_ids or [])
    return GameNodeOut(id=n.id, chapter_id=n.chapter_id, idx=n.idx, mode=n.mode,
                       question_count=n.question_count, time_limit=n.time_limit or 0,
                       question_ids=ids, auto=len(ids) == 0)


def _chapter_out(db: Session, c: GameChapter) -> GameChapterOut:
    nodes = db.scalars(select(GameNode).where(GameNode.chapter_id == c.id).order_by(
        GameNode.idx, GameNode.id)).all()
    return GameChapterOut(id=c.id, concept_slug=c.concept_slug, idx=c.idx, name=c.name,
                          icon=c.icon, desc=c.desc, nodes=[_node_out(n) for n in nodes])


def get_structures(db: Session) -> dict[str, list[GameChapterOut]]:
    out: dict[str, list[GameChapterOut]] = {}
    chapters = db.scalars(select(GameChapter).order_by(
        GameChapter.concept_slug, GameChapter.idx, GameChapter.id)).all()
    for c in chapters:
        out.setdefault(c.concept_slug, []).append(_chapter_out(db, c))
    return out


def _delete_chapter(db: Session, c: GameChapter) -> None:
    for n in db.scalars(select(GameNode).where(GameNode.chapter_id == c.id)).all():
        db.delete(n)
    db.delete(c)


@router.get("/chapters", response_model=list[GameChapterOut])
def list_chapters(concept_slug: str = Query(""), user: User = Depends(current_user),
                  db: Session = Depends(get_db)) -> list[GameChapterOut]:
    _admin(user)
    if not concept_slug:
        raise HTTPException(status_code=422, detail="Thiếu concept.")
    _get_concept(db, concept_slug)
    chapters = db.scalars(select(GameChapter).where(
        GameChapter.concept_slug == concept_slug).order_by(GameChapter.idx, GameChapter.id)).all()
    return [_chapter_out(db, c) for c in chapters]


@router.post("/chapters", response_model=GameChapterOut)
def create_chapter(payload: GameChapterIn, user: User = Depends(current_user),
                   db: Session = Depends(get_db)) -> GameChapterOut:
    _admin(user)
    c = _get_concept(db, payload.concept_slug.strip())
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Tên chương không được để trống.")
    top = db.scalar(select(func.max(GameChapter.idx)).where(
        GameChapter.concept_slug == c.slug)) or 0
    row = GameChapter(concept_slug=c.slug, idx=top + 1, name=name[:80],
                      icon=payload.icon.strip()[:16] or "🗺️", desc=payload.desc.strip()[:200])
    db.add(row)
    db.commit()
    return _chapter_out(db, row)


@router.post("/chapters/seed", response_model=list[GameChapterOut])
def seed_chapters(payload: GameChapterIn, user: User = Depends(current_user),
                  db: Session = Depends(get_db)) -> list[GameChapterOut]:
    """Copy cấu trúc mặc định (4 chương × 3 màn) để admin tùy chỉnh tiếp."""
    _admin(user)
    c = _get_concept(db, payload.concept_slug.strip())
    exists = db.scalar(select(func.count()).select_from(GameChapter).where(
        GameChapter.concept_slug == c.slug))
    if exists:
        raise HTTPException(status_code=409, detail="Concept này đã có cấu trúc riêng.")
    copy = DEFAULT_CHAPTERS.get(c.slug, GENERIC_CHAPTERS)
    out = []
    for ci, ch in enumerate(copy):
        row = GameChapter(concept_slug=c.slug, idx=ci, name=ch["name"], icon=ch["icon"],
                          desc=ch["desc"])
        db.add(row)
        db.flush()
        modes = ["normal", "normal", "speed"] if ci < 3 else ["normal", "speed", "boss"]
        for ni, mode in enumerate(modes):
            db.add(GameNode(chapter_id=row.id, idx=ni, mode=mode, question_count=8,
                            time_limit=None, question_ids=[]))
        out.append(row)
    db.commit()
    return [_chapter_out(db, r) for r in out]


@router.delete("/chapters")
def clear_chapters(concept_slug: str = Query(""), user: User = Depends(current_user),
                   db: Session = Depends(get_db)) -> dict:
    """Xóa cấu trúc riêng — client quay về mặc định trong code."""
    _admin(user)
    if not concept_slug:
        raise HTTPException(status_code=422, detail="Thiếu concept.")
    for c in db.scalars(select(GameChapter).where(
            GameChapter.concept_slug == concept_slug.strip())).all():
        _delete_chapter(db, c)
    db.commit()
    return {"ok": True}


@router.patch("/chapters/{chapter_id}", response_model=GameChapterOut)
def update_chapter(chapter_id: int, payload: GameChapterPatch, user: User = Depends(current_user),
                   db: Session = Depends(get_db)) -> GameChapterOut:
    _admin(user)
    row = db.get(GameChapter, chapter_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy chương.")
    if payload.name is not None:
        if not payload.name.strip():
            raise HTTPException(status_code=422, detail="Tên chương không được để trống.")
        row.name = payload.name.strip()[:80]
    if payload.icon is not None:
        row.icon = payload.icon.strip()[:16] or "🗺️"
    if payload.desc is not None:
        row.desc = payload.desc.strip()[:200]
    if payload.idx is not None:
        row.idx = payload.idx
    db.commit()
    return _chapter_out(db, row)


@router.delete("/chapters/{chapter_id}")
def delete_chapter(chapter_id: int, user: User = Depends(current_user),
                   db: Session = Depends(get_db)) -> dict:
    _admin(user)
    row = db.get(GameChapter, chapter_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy chương.")
    _delete_chapter(db, row)
    db.commit()
    return {"ok": True}


@router.post("/nodes", response_model=GameNodeOut)
def create_node(payload: GameNodeIn, user: User = Depends(current_user),
                db: Session = Depends(get_db)) -> GameNodeOut:
    _admin(user)
    chapter = db.get(GameChapter, payload.chapter_id)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy chương.")
    ids = _check_node(payload.mode, payload.question_count, payload.time_limit,
                      payload.question_ids)
    top = db.scalar(select(func.max(GameNode.idx)).where(
        GameNode.chapter_id == chapter.id))
    row = GameNode(chapter_id=chapter.id, idx=(top or -1) + 1, mode=payload.mode,
                   question_count=payload.question_count,
                   time_limit=payload.time_limit or None, question_ids=ids)
    db.add(row)
    db.commit()
    return _node_out(row)


@router.patch("/nodes/{node_id}", response_model=GameNodeOut)
def update_node(node_id: int, payload: GameNodePatch, user: User = Depends(current_user),
                db: Session = Depends(get_db)) -> GameNodeOut:
    _admin(user)
    row = db.get(GameNode, node_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy màn.")
    mode = payload.mode if payload.mode is not None else row.mode
    count = payload.question_count if payload.question_count is not None else row.question_count
    time_limit = payload.time_limit if payload.time_limit is not None else (row.time_limit or 0)
    ids = payload.question_ids if payload.question_ids is not None else list(row.question_ids or [])
    ids = _check_node(mode, count, time_limit, ids)
    row.mode, row.question_count, row.time_limit, row.question_ids = mode, count, time_limit or None, ids
    if payload.idx is not None:
        row.idx = payload.idx
    db.commit()
    return _node_out(row)


@router.delete("/nodes/{node_id}")
def delete_node(node_id: int, user: User = Depends(current_user),
                db: Session = Depends(get_db)) -> dict:
    _admin(user)
    row = db.get(GameNode, node_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy màn.")
    db.delete(row)
    db.commit()
    return {"ok": True}
