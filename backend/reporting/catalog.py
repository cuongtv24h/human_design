"""Report definitions and domain metadata.

This file is the product-facing catalog.  It contains no calculation logic;
that belongs to the orchestrator adapters.
"""

from __future__ import annotations

from dataclasses import dataclass

from .contract import DomainName, ReportDefinition, ReportTier


@dataclass(frozen=True)
class SectionSpec:
    id: str
    title: str
    kind: str
    source_tools: tuple[str, ...] = ()
    knowledge_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class DomainSpec:
    name: DomainName
    title: str
    analyzer_tool: str
    formatter_tool: str
    knowledge_refs: tuple[str, ...]


CORE_SECTIONS: tuple[SectionSpec, ...] = (
    SectionSpec("summary", "Tóm tắt chart", "summary", ("calculate_hd_chart",), ("00_tong_quan_he_thong.md",)),
    SectionSpec("type_strategy_authority", "Loại năng lượng · Chiến lược · Quyền nội tại (Type · Strategy · Authority)", "core", ("calculate_hd_chart",), ("04_5_loai_va_chien_luoc.md",)),
    SectionSpec("profile_definition", "Nhân cách & Định nghĩa (Profile · Definition)", "core", ("calculate_hd_chart",), ("05_profile_cross_definition.md",)),
    SectionSpec("centers", "9 trung tâm năng lượng (9 Centers)", "core", ("calculate_hd_chart",), ("02_9_trung_tam.md",)),
    SectionSpec("channels_gates", "Kênh & Cổng (Channels & Gates)", "core", ("calculate_hd_chart",), ("01_mandala_64_cong.md", "03_36_kenh.md")),
    SectionSpec("cross", "Chữ thập hóa thân (Incarnation Cross)", "core", ("calculate_hd_chart",), ("08_192_incarnation_crosses_chi_tiet.md",)),
    SectionSpec("practical_actions", "Ứng dụng thực tiễn", "practice", ("calculate_hd_chart",), ("07_ung_dung_thuc_tien.md",)),
)

DOMAIN_SPECS: dict[DomainName, DomainSpec] = {
    DomainName.MONEY: DomainSpec(DomainName.MONEY, "Money & Wealth", "analyze_money_map", "format_money_report", ("13_money_wealth_full_map.md",)),
    DomainName.POTENTIAL: DomainSpec(DomainName.POTENTIAL, "Potential & Blind Spots", "analyze_potential_blindspots", "format_potential_report", ("14_potential_blindspots.md",)),
    DomainName.HEALTH: DomainSpec(DomainName.HEALTH, "Health Thân-Tâm-Trí", "analyze_health", "format_health_report", ("15_health_than_tam_tri.md",)),
    DomainName.RELATIONSHIP: DomainSpec(DomainName.RELATIONSHIP, "Relationship & Intimacy", "analyze_relationship", "format_relationship_report", ("16_relationship_intimacy_deep.md",)),
    DomainName.DECISION: DomainSpec(DomainName.DECISION, "Decision & Authority", "analyze_decision", "format_decision_report", ("17_decision_authority.md",)),
    DomainName.DECONDITIONING: DomainSpec(DomainName.DECONDITIONING, "Deconditioning & Not-Self", "analyze_deconditioning", "format_deconditioning_report", ("18_deconditioning_notsel.md",)),
    DomainName.PURPOSE: DomainSpec(DomainName.PURPOSE, "Purpose & Mission", "analyze_purpose", "format_purpose_report", ("19_purpose_mission_practical.md",)),
    DomainName.TEAM: DomainSpec(DomainName.TEAM, "Team & Leadership", "analyze_team", "format_team_report", ("20_team_leadership_dynamics.md",)),
}

FREE_BASIC_SECTION_SPECS = (CORE_SECTIONS[0], CORE_SECTIONS[1], CORE_SECTIONS[2], CORE_SECTIONS[3], CORE_SECTIONS[6])

# Narrative template — "Bản Thiết Kế Bản Thân — Cẩm Nang Vận Hành".
# The 5 parts follow the standard in docs/NARRATIVE_STANDARD.md:
# (1) identity, (2) decision compass, (3) burden release, (4) role/profile,
# (5) field application.  Content is rendered by backend/reporting/narrative.py
# on top of the language layer backend/reporting/language_vn.py.
NARRATIVE_SECTIONS: tuple[SectionSpec, ...] = (
    SectionSpec(
        "part1_identity",
        "Phần 1 — Bức tranh toàn cảnh: Bạn thực sự là ai khi bỏ qua mọi kỳ vọng?",
        "summary",
        ("calculate_hd_chart", "language_vn"),
        ("00_tong_quan_he_thong.md", "04_5_loai_va_chien_luoc.md"),
    ),
    SectionSpec(
        "part2_decision_compass",
        "Phần 2 — La bàn ra quyết định: Làm sao để ngừng hối hận sau mỗi lựa chọn?",
        "core",
        ("calculate_hd_chart", "language_vn"),
        ("04_5_loai_va_chien_luoc.md", "17_decision_authority.md"),
    ),
    SectionSpec(
        "part3_burden_release",
        "Phần 3 — Tháo gỡ gánh nặng: Những điều bạn đang gánh mà vốn không phải của bạn",
        "core",
        ("calculate_hd_chart", "language_vn"),
        ("02_9_trung_tam.md", "18_deconditioning_notsel.md"),
    ),
    SectionSpec(
        "part4_role_profile",
        "Phần 4 — Phong cách sống & vai diễn cuộc đời: Người bên trong và hình ảnh bên ngoài",
        "core",
        ("calculate_hd_chart", "language_vn"),
        ("05_profile_cross_definition.md", "08_192_incarnation_crosses_chi_tiet.md"),
    ),
    SectionSpec(
        "part5_field_application",
        "Phần 5 — Ứng dụng thực chiến: Đưa thiết kế vào đời sống 24/7",
        "practice",
        ("calculate_hd_chart", "language_vn"),
        ("07_ung_dung_thuc_tien.md", "20_team_leadership_dynamics.md"),
    ),
)

REPORT_DEFINITIONS: dict[str, ReportDefinition] = {
    "free_basic": ReportDefinition(
        key="free_basic",
        title="Free Basic Human Design Report",
        tier=ReportTier.FREE_BASIC,
        section_ids=[spec.id for spec in FREE_BASIC_SECTION_SPECS],
        description="Core chart summary and first practical steps.",
    ),
    "deep_core": ReportDefinition(
        key="deep_core",
        title="Deep Core Human Design Report",
        tier=ReportTier.DEEP_CORE,
        section_ids=[spec.id for spec in CORE_SECTIONS],
        description="Complete core chart analysis before optional domain modules.",
    ),
    "operating_manual": ReportDefinition(
        key="operating_manual",
        title="Bản Thiết Kế Bản Thân — Cẩm Nang Vận Hành",
        tier=ReportTier.DEEP_CORE,
        section_ids=[spec.id for spec in NARRATIVE_SECTIONS],
        description=(
            "Narrative report in natural Vietnamese, styled as a personal operating "
            "manual: 5 parts (identity, decision compass, burden release, role/profile, "
            "field application) rendered from the language layer."
        ),
    ),
}


def get_plan_definition(tier: ReportTier) -> tuple[ReportDefinition, tuple[SectionSpec, ...]]:
    key = "free_basic" if tier == ReportTier.FREE_BASIC else "deep_core"
    definition = REPORT_DEFINITIONS[key]
    specs = tuple(spec for spec in CORE_SECTIONS if spec.id in definition.section_ids)
    return definition, specs


def get_manual_spec() -> tuple[ReportDefinition, tuple[SectionSpec, ...]]:
    """Definition and part specs for the ``operating_manual`` narrative template."""
    return REPORT_DEFINITIONS["operating_manual"], NARRATIVE_SECTIONS
