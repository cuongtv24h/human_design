"""/api/v1/catalog — options for the report wizard."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from backend.reporting.catalog import CORE_SECTIONS, FREE_BASIC_SECTION_SPECS, NARRATIVE_SECTIONS

from ..deps import current_user, get_db
from ..models import User
from ..schemas import CatalogLlmProvider, CatalogOption, CatalogOut, CatalogSection
from ..services import org_llm_configs

from hd_time import VN_UTC_OFFSET, zone_label  # noqa: E402

router = APIRouter(tags=["catalog"])

TIERS = [
    CatalogOption(value="free_basic", label="Cơ bản (Free Basic)",
                  description="Tóm tắt chart và những bước thực hành đầu tiên."),
    CatalogOption(value="deep_core", label="Chuyên sâu (Deep Core)",
                  description="Phân tích đầy đủ 9 trung tâm, kênh, cổng và Chữ thập hóa thân."),
]
TEMPLATES = [
    CatalogOption(value="sections", label="Theo mục (Sections)",
                  description="Trình bày theo từng khối kiến thức: Type, Profile, Centers…"),
    CatalogOption(value="operating_manual", label="Cẩm nang vận hành (Operating Manual)",
                  description="5 phần kể chuyện bằng tiếng Việt đời thường — dễ đọc cho người mới."),
]
CONTENT_MODES = [
    CatalogOption(value="template", label="Nội dung chuẩn (Template)",
                  description="Tạo ngay trong vài giây, nội dung ổn định, kiểm soát được."),
    CatalogOption(value="llm", label="Biên tập bởi AI (LLM)",
                  description="AI viết lại như chuyên gia tham vấn, giàu thấu cảm. Mất khoảng 1–2 phút."),
]
DOMAINS = [
    CatalogOption(value="money", label="Tiền bạc & Thịnh vượng (Money)"),
    CatalogOption(value="potential", label="Tiềm năng & Điểm mù (Potential)"),
    CatalogOption(value="health", label="Sức khỏe Thân–Tâm–Trí (Health)"),
    CatalogOption(value="relationship", label="Tình cảm & Gắn kết (Relationship)"),
    CatalogOption(value="decision", label="Ra quyết định (Decision)"),
    CatalogOption(value="deconditioning", label="Gỡ bỏ điều kiện hóa (Deconditioning)"),
    CatalogOption(value="purpose", label="Sứ mệnh & Mục đích (Purpose)"),
    CatalogOption(value="team", label="Đội nhóm & Lãnh đạo (Team)"),
]


def _sections(specs) -> list[CatalogSection]:
    return [CatalogSection(id=spec.id, title=spec.title) for spec in specs]


@router.get("/catalog", response_model=CatalogOut)
def catalog(request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)) -> CatalogOut:
    chain = org_llm_configs(db, user.org_id, request.app.state.secret_key)
    return CatalogOut(
        tiers=TIERS, templates=TEMPLATES, content_modes=CONTENT_MODES, domains=DOMAINS,
        sections_by_tier={
            "free_basic": _sections(FREE_BASIC_SECTION_SPECS),
            "deep_core": _sections(CORE_SECTIONS),
            "operating_manual": _sections(NARRATIVE_SECTIONS),
        },
        llm_available=bool(chain),
        llm_providers=[CatalogLlmProvider(name=c.name or f"Nhà cung cấp {i + 1}", model=c.model)
                       for i, c in enumerate(chain)],
        timezone_default=VN_UTC_OFFSET,
        timezone_label=zone_label(VN_UTC_OFFSET),
    )
