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
    SectionSpec("type_strategy_authority", "Type, Strategy và Authority", "core", ("calculate_hd_chart",), ("04_5_loai_va_chien_luoc.md",)),
    SectionSpec("profile_definition", "Profile và Definition", "core", ("calculate_hd_chart",), ("05_profile_cross_definition.md",)),
    SectionSpec("centers", "9 Centers", "core", ("calculate_hd_chart",), ("02_9_trung_tam.md",)),
    SectionSpec("channels_gates", "Channels và Gates", "core", ("calculate_hd_chart",), ("01_mandala_64_cong.md", "03_36_kenh.md")),
    SectionSpec("cross", "Incarnation Cross", "core", ("calculate_hd_chart",), ("08_192_incarnation_crosses_chi_tiet.md",)),
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
}


def get_plan_definition(tier: ReportTier) -> tuple[ReportDefinition, tuple[SectionSpec, ...]]:
    key = "free_basic" if tier == ReportTier.FREE_BASIC else "deep_core"
    definition = REPORT_DEFINITIONS[key]
    specs = tuple(spec for spec in CORE_SECTIONS if spec.id in definition.section_ids)
    return definition, specs
