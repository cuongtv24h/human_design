"""Report generation pipeline for the Admin/Coach application layer.

The orchestrator calculates the chart once, delegates domain analysis to the
existing tools, and normalizes every result into the report contract.  It does
not call an LLM and it never lets prose overwrite calculated chart values.

Two presentation templates are supported (see ``docs/NARRATIVE_STANDARD.md``):
- ``sections`` (default): deterministic structured sections per tier.
- ``operating_manual``: the 5-part narrative standard, rendered by
  ``backend/reporting/narrative.py`` on top of ``language_vn.py``.
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo

# The legacy tool modules use absolute imports such as ``hd_calculator``.
# Expose the tools directory without changing those modules or their public API.
_TOOLS_DIR = str(Path(__file__).resolve().parents[2] / "tools")
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

from hd_calculator import (  # noqa: E402
    CHANNEL_TO_CENTERS,
    GATE_MEANINGS,
    GATE_TO_CENTER,
    calculate_hd_chart,
)
from hd_analyzer import CENTER_ANALYSIS, PROFILE_ANALYSIS, TYPE_ANALYSIS  # noqa: E402

from .catalog import DOMAIN_SPECS, SectionSpec, get_manual_spec, get_plan_definition  # noqa: E402
from .language_vn import (  # noqa: E402
    CROSS_FRAMING,
    CROSS_TYPE_LANGUAGE,
    vn_authority,
    vn_center,
    vn_channel,
    vn_definition,
    vn_strategy,
    vn_type,
)
from .contract import (  # noqa: E402
    DomainName,
    ReportDocument,
    ReportPlan,
    ReportProvenance,
    ReportRequest,
    ReportSection,
    ReportTemplate,
)
from .narrative import render_operating_manual  # noqa: E402

# Domain analyzers are deliberately imported from tools/, rather than copied
# into the application layer.  ``None`` means that a formatter is not needed
# because the adapter creates a small deterministic core section itself.
from hd_decision_analysis import analyze_decision, format_decision_report  # noqa: E402
from hd_deconditioning_analysis import analyze_deconditioning, format_deconditioning_report  # noqa: E402
from hd_health_analysis import analyze_health, format_health_report  # noqa: E402
from hd_money_analysis import analyze_money_map, format_money_report  # noqa: E402
from hd_potential_analysis import analyze_potential_blindspots, format_potential_report  # noqa: E402
from hd_purpose_analysis import analyze_purpose, format_purpose_report  # noqa: E402
from hd_relationship_analysis import analyze_relationship, format_relationship_report  # noqa: E402
from hd_team_analysis import analyze_team, format_team_report  # noqa: E402


ORCHESTRATOR_VERSION = "0.2.0"
CALCULATOR_VERSION = "pyswisseph 2.10.3.2 / Human Design calculator"
KNOWLEDGE_VERSION = "2026-09-24"


def _parse_birth_datetime(date_text: str, time_text: str, timezone_text: str) -> datetime:
    """Convert a subject's local birth time to the naive UTC used by tools."""
    try:
        local_date = date.fromisoformat(date_text)
    except ValueError as exc:
        raise ValueError(f"birth_date must be a valid YYYY-MM-DD date: {date_text}") from exc

    parsed_time: datetime | None = None
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            parsed_time = datetime.strptime(time_text, fmt)
            break
        except ValueError:
            continue
    if parsed_time is None:
        raise ValueError("birth_time must use HH:MM or HH:MM:SS")

    local_naive = datetime.combine(local_date, parsed_time.time())
    try:
        if timezone_text.startswith(("+", "-")):
            sign = 1 if timezone_text[0] == "+" else -1
            clean = timezone_text[1:].replace(":", "")
            if len(clean) not in (2, 4) or not clean.isdigit():
                raise ValueError
            hours = int(clean[:2])
            minutes = int(clean[2:]) if len(clean) == 4 else 0
            if hours > 23 or minutes > 59:
                raise ValueError
            tzinfo = timezone(sign * timedelta(hours=hours, minutes=minutes))
        else:
            tzinfo = ZoneInfo(timezone_text)
    except (ValueError, KeyError) as exc:
        raise ValueError(f"Unsupported timezone: {timezone_text}") from exc

    return local_naive.replace(tzinfo=tzinfo).astimezone(timezone.utc).replace(tzinfo=None)


def _json_safe(value: Any) -> Any:
    """Make legacy analyzer output safe for ReportDocument JSON serialization."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "item"):
        return value.item()
    return value


def _chart_snapshot(chart: dict[str, Any]) -> dict[str, Any]:
    """Keep the calculation result as a complete, serializable source snapshot."""
    return _json_safe(chart)


def _person_summary(chart: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": chart["type"],
        "strategy": chart["strategy"],
        "authority": chart["authority"],
        "profile": chart["profile"],
        "definition": chart["definition"],
        "defined_centers": chart["defined_centers"],
        "defined_channels": [f"{gate1}-{gate2}" for gate1, gate2 in chart["defined_channels"]],
        "incarnation_cross": chart["incarnation_cross"],
    }


def _core_section(spec: SectionSpec, chart: dict[str, Any], subject_name: str) -> tuple[dict[str, Any], str]:
    """Create structured core sections from the already calculated chart."""
    if spec.id == "summary":
        data = {"name": subject_name, **_person_summary(chart)}
        markdown = (
            f"**{subject_name or 'Khách hàng'}** thuộc loại **{vn_type(chart['type'], gloss=True)}**, "
            f"chiến lược sống **{vn_strategy(chart['strategy'], chart['type'])}**, "
            f"quyền nội tại **{vn_authority(chart['authority'])}**, "
            f"nhân cách **{chart['profile']}** và định nghĩa **{vn_definition(chart['definition'])}**."
        )
    elif spec.id == "type_strategy_authority":
        data = {
            "name": subject_name,
            "type": chart["type"],
            "type_analysis": TYPE_ANALYSIS.get(chart["type"], ""),
            "strategy": chart["strategy"],
            "authority": chart["authority"],
        }
        markdown = (
            f"- **Loại năng lượng (Type):** {vn_type(chart['type'], gloss=True)}\n"
            f"- **Chiến lược sống:** {vn_strategy(chart['strategy'], chart['type'])}\n"
            f"- **Quyền nội tại:** {vn_authority(chart['authority'])}\n\n"
            f"{TYPE_ANALYSIS.get(chart['type'], '').strip()}"
        )
    elif spec.id == "profile_definition":
        data = {
            "name": subject_name,
            "profile": chart["profile"],
            "profile_analysis": PROFILE_ANALYSIS.get(chart["profile"], ""),
            "definition": chart["definition"],
            "definition_groups": chart.get("definition_groups", 0),
            "incarnation_cross": chart["incarnation_cross"],
            "cross_type": chart["cross_type"],
            "cross_gates": {
                "personality_sun": chart["p_sun_gate"],
                "personality_earth": chart["p_earth_gate"],
                "design_sun": chart["d_sun_gate"],
                "design_earth": chart["d_earth_gate"],
            },
        }
        markdown = (
            f"- **Nhân cách (Profile):** {chart['profile']}\n"
            f"- **Định nghĩa:** {vn_definition(chart['definition'])}\n"
            f"- **Chữ thập hóa thân:** {chart['incarnation_cross']}\n\n"
            f"{PROFILE_ANALYSIS.get(chart['profile'], '').strip()}"
        )
    elif spec.id == "centers":
        center_names = ["Head", "Ajna", "Throat", "G", "Heart", "Spleen", "Sacral", "Solar Plexus", "Root"]
        defined = set(chart["defined_centers"])
        activated = set(chart["all_activated_gates"])
        centers: dict[str, Any] = {}
        for center in center_names:
            center_gates = sorted(gate for gate, mapped_center in GATE_TO_CENTER.items() if mapped_center == center)
            centers[center] = {
                "status": "defined" if center in defined else "open",
                "gates": center_gates,
                "activated_gates": sorted(set(center_gates) & activated),
                "defined_meaning": CENTER_ANALYSIS.get(center, {}).get("defined", ""),
                "open_meaning": CENTER_ANALYSIS.get(center, {}).get("undefined", ""),
            }
        data = {"name": subject_name, "defined_count": len(defined), "centers": centers}
        markdown = "\n".join(
            f"- **{vn_center(center)}:** {'ĐỊNH NGHĨA (có màu)' if info['status'] == 'defined' else 'MỞ (trắng)'} "
            f"(cổng kích hoạt: {', '.join(map(str, info['activated_gates'])) or 'không có'})"
            for center, info in centers.items()
        )
    elif spec.id == "channels_gates":
        channels = []
        for gate1, gate2 in chart["defined_channels"]:
            centers = CHANNEL_TO_CENTERS.get((gate1, gate2)) or CHANNEL_TO_CENTERS.get((gate2, gate1))
            channels.append({
                "channel": f"{gate1}-{gate2}",
                "gates": [gate1, gate2],
                "centers": centers,
                "gate_meanings": [GATE_MEANINGS.get(gate1), GATE_MEANINGS.get(gate2)],
            })
        connected = {gate for channel in chart["defined_channels"] for gate in channel}
        hanging = sorted(set(chart["all_activated_gates"]) - connected)
        data = {
            "name": subject_name,
            "defined_channels": channels,
            "hanging_activated_gates": hanging,
        }
        lines = [f"**Kênh định nghĩa ({len(channels)})** — tài năng cố định, năng lượng nhất quán của bạn:"]
        for ch in channels:
            lo, hi = sorted(ch["gates"])
            lang = vn_channel(lo, hi)
            center_pair = " ↔ ".join(vn_center(c) for c in ch["centers"])
            if lang:
                lines.append(f"- **Kênh {lo}-{hi} · {lang['name']}** ({center_pair}): {lang['life']}")
            else:
                lines.append(f"- **Kênh {lo}-{hi}** ({center_pair})")
        lines += ["", f"**Cổng treo (Hanging Gates)** — {len(hanging)} cổng kích hoạt chưa thành kênh, chờ 'cầu nối' qua người khác hoặc dòng chảy cuộc sống:"]
        for gate in hanging:
            center = GATE_TO_CENTER.get(gate, "")
            lines.append(f"- Cổng {gate}: {GATE_MEANINGS.get(gate, '')} ({vn_center(center)})")
        markdown = "\n".join(lines)
    elif spec.id == "cross":
        data = {
            "name": subject_name,
            "incarnation_cross": chart["incarnation_cross"],
            "cross_type": chart["cross_type"],
            "gates": {
                "personality_sun": chart["p_sun_gate"],
                "personality_earth": chart["p_earth_gate"],
                "design_sun": chart["d_sun_gate"],
                "design_earth": chart["d_earth_gate"],
            },
            "quarters": chart["quarters"],
        }
        cross_type = chart["cross_type"]
        cross_life = CROSS_TYPE_LANGUAGE.get(cross_type, "")
        quarters = chart.get("quarters") or {}
        lines = [
            f"**{chart['incarnation_cross']}**",
            "",
            f"**{cross_type}** — {cross_life}".rstrip(" —"),
            "",
            CROSS_FRAMING,
            "",
            f"- Mặt Trời nhân cách (Personality Sun): Cổng {chart['p_sun_gate']} — {GATE_MEANINGS.get(chart['p_sun_gate'], '')}",
            f"- Trái Đất nhân cách (Personality Earth): Cổng {chart['p_earth_gate']} — {GATE_MEANINGS.get(chart['p_earth_gate'], '')}",
            f"- Mặt Trời thiết kế (Design Sun): Cổng {chart['d_sun_gate']} — {GATE_MEANINGS.get(chart['d_sun_gate'], '')}",
            f"- Trái Đất thiết kế (Design Earth): Cổng {chart['d_earth_gate']} — {GATE_MEANINGS.get(chart['d_earth_gate'], '')}",
        ]
        if quarters:
            lines += [
                "",
                "Quarters: Personality Sun — "
                f"{quarters.get('p_sun', '')} · Personality Earth — {quarters.get('p_earth', '')} · "
                f"Design Sun — {quarters.get('d_sun', '')} · Design Earth — {quarters.get('d_earth', '')}.",
            ]
        markdown = "\n".join(lines)
    elif spec.id == "practical_actions":
        data = {
            "name": subject_name,
            "first_7_days": [
                "Mỗi ngày, ghi lại một quyết định bạn ra theo chiến lược sống và quyền nội tại của mình.",
                "Đánh dấu khoảnh khắc xuất hiện dấu hiệu sống đúng (Signature) và khi sống sai thiết kế (Not-Self).",
                "Chọn một trung tâm mở để quan sát thay vì cố sửa chữa bản thân.",
            ],
            "strategy": chart["strategy"],
            "authority": chart["authority"],
        }
        markdown = "\n".join(f"- {item}" for item in data["first_7_days"])
    else:
        raise KeyError(f"Unknown core section: {spec.id}")
    return _json_safe(data), markdown


# Each adapter returns raw structured data and a deterministic formatter output.
# A future LLM/editor can work on the markdown while the raw data remains the
# source of truth in ReportSection.data.
_DOMAIN_ADAPTERS: dict[
    DomainName,
    tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any]], str]],
] = {
    DomainName.MONEY: (analyze_money_map, format_money_report),
    DomainName.POTENTIAL: (analyze_potential_blindspots, format_potential_report),
    DomainName.HEALTH: (analyze_health, format_health_report),
    DomainName.RELATIONSHIP: (analyze_relationship, format_relationship_report),
    DomainName.DECISION: (analyze_decision, format_decision_report),
    DomainName.DECONDITIONING: (analyze_deconditioning, format_deconditioning_report),
    DomainName.PURPOSE: (analyze_purpose, format_purpose_report),
    DomainName.TEAM: (analyze_team, format_team_report),
}


class ReportOrchestrator:
    """Build a reproducible ``ReportDocument`` from an Admin report request."""

    def __init__(
        self,
        *,
        orchestrator_version: str = ORCHESTRATOR_VERSION,
        calculator_version: str = CALCULATOR_VERSION,
        knowledge_version: str = KNOWLEDGE_VERSION,
    ) -> None:
        self.orchestrator_version = orchestrator_version
        self.calculator_version = calculator_version
        self.knowledge_version = knowledge_version

    def build_plan(self, request: ReportRequest) -> ReportPlan:
        if request.template is ReportTemplate.OPERATING_MANUAL:
            definition, core_specs = get_manual_spec()
        else:
            definition, core_specs = get_plan_definition(request.tier)
        section_ids = [spec.id for spec in core_specs]
        source_tools: list[str] = []
        knowledge_refs: list[str] = []
        for spec in core_specs:
            source_tools.extend(spec.source_tools)
            knowledge_refs.extend(spec.knowledge_refs)
        for domain in request.domains:
            domain_spec = DOMAIN_SPECS[domain]
            section_ids.append(f"domain_{domain.value}")
            source_tools.extend((domain_spec.analyzer_tool, domain_spec.formatter_tool))
            knowledge_refs.extend(domain_spec.knowledge_refs)
        return ReportPlan(
            definition_key=definition.key,
            tier=request.tier,
            domains=request.domains,
            section_ids=section_ids,
            source_tools=list(dict.fromkeys(source_tools)),
            knowledge_refs=list(dict.fromkeys(knowledge_refs)),
        )

    def _run_narrative_sections(
        self, chart: dict[str, Any], name: str
    ) -> tuple[list[ReportSection], list[str]]:
        """Build the 5 narrative parts; a failing part is auditable, not fatal."""
        sections: list[ReportSection] = []
        warnings: list[str] = []
        for order, part in enumerate(render_operating_manual(chart, name)):
            try:
                sections.append(
                    ReportSection(
                        id=part["id"],
                        title=part["title"],
                        kind=part["kind"],  # type: ignore[arg-type]
                        order=order,
                        data=part["data"],
                        content_markdown=part["markdown"],
                        source_tools=part["source_tools"],
                        knowledge_refs=part["knowledge_refs"],
                    )
                )
            except Exception as exc:  # keep an auditable failed section
                warning = f"Section {part['id']} failed: {exc}"
                warnings.append(warning)
                sections.append(
                    ReportSection(
                        id=part["id"],
                        title=part["title"],
                        kind=part["kind"],  # type: ignore[arg-type]
                        order=order,
                        status="failed",
                        warnings=[warning],
                        source_tools=part["source_tools"],
                        knowledge_refs=part["knowledge_refs"],
                    )
                )
        return sections, warnings

    def run(self, request: ReportRequest) -> ReportDocument:
        """Calculate once and execute the sections selected in ``request``."""
        birth_datetime = _parse_birth_datetime(
            request.subject.birth_date,
            request.subject.birth_time,
            request.subject.timezone,
        )
        chart = calculate_hd_chart(birth_datetime)
        chart_snapshot = _chart_snapshot(chart)
        plan = self.build_plan(request)
        sections: list[ReportSection] = []
        warnings: list[str] = []

        if request.template is ReportTemplate.OPERATING_MANUAL:
            sections, section_warnings = self._run_narrative_sections(chart, request.subject.name)
            warnings.extend(section_warnings)
        else:
            _, core_specs = get_plan_definition(request.tier)
            for order, spec in enumerate(core_specs):
                try:
                    data, markdown = _core_section(spec, chart, request.subject.name)
                    sections.append(
                        ReportSection(
                            id=spec.id,
                            title=spec.title,
                            kind=spec.kind,  # type: ignore[arg-type]
                            order=order,
                            data=data,
                            content_markdown=markdown,
                            source_tools=list(spec.source_tools),
                            knowledge_refs=list(spec.knowledge_refs),
                        )
                    )
                except Exception as exc:  # keep an auditable failed section
                    warning = f"Section {spec.id} failed: {exc}"
                    warnings.append(warning)
                    sections.append(
                        ReportSection(
                            id=spec.id,
                            title=spec.title,
                            kind=spec.kind,  # type: ignore[arg-type]
                            order=order,
                            status="failed",
                            warnings=[warning],
                            source_tools=list(spec.source_tools),
                            knowledge_refs=list(spec.knowledge_refs),
                        )
                    )

        next_order = len(sections)
        for domain in request.domains:
            domain_spec = DOMAIN_SPECS[domain]
            analyzer, formatter = _DOMAIN_ADAPTERS[domain]
            section_id = f"domain_{domain.value}"
            try:
                if domain == DomainName.MONEY or domain == DomainName.POTENTIAL:
                    raw = analyzer(chart, request.subject.name)
                elif domain == DomainName.RELATIONSHIP:
                    partner_datetime = None
                    partner_name = ""
                    if request.partner is not None:
                        partner_datetime = _parse_birth_datetime(
                            request.partner.birth_date,
                            request.partner.birth_time,
                            request.partner.timezone,
                        )
                        partner_name = request.partner.name
                    raw = analyzer(
                        chart,
                        request.subject.name,
                        partner_datetime,
                        partner_name,
                    )
                else:
                    # Domain adapters consume the same calculated chart snapshot;
                    # they do not recalculate the subject's chart.
                    raw = analyzer(chart, request.subject.name)
                data = _json_safe(raw)
                markdown = formatter(raw)
                sections.append(
                    ReportSection(
                        id=section_id,
                        title=domain_spec.title,
                        kind="domain",
                        order=next_order,
                        data=data,
                        content_markdown=markdown,
                        source_tools=[domain_spec.analyzer_tool, domain_spec.formatter_tool],
                        knowledge_refs=list(domain_spec.knowledge_refs),
                    )
                )
            except Exception as exc:
                warning = f"Domain {domain.value} failed: {exc}"
                warnings.append(warning)
                sections.append(
                    ReportSection(
                        id=section_id,
                        title=domain_spec.title,
                        kind="domain",
                        order=next_order,
                        status="failed",
                        warnings=[warning],
                        source_tools=[domain_spec.analyzer_tool, domain_spec.formatter_tool],
                        knowledge_refs=list(domain_spec.knowledge_refs),
                    )
                )
            next_order += 1

        generated_at = datetime.now(timezone.utc)
        provenance = ReportProvenance(
            orchestrator_version=self.orchestrator_version,
            calculator_version=self.calculator_version,
            knowledge_version=self.knowledge_version,
            generated_at=generated_at,
            source_tools=plan.source_tools,
            knowledge_refs=plan.knowledge_refs,
        )
        display_name = request.subject.name or "Customer"
        if request.template is ReportTemplate.OPERATING_MANUAL:
            title = f"Bản Thiết Kế Bản Thân — Cẩm Nang Vận Hành cho {display_name}"
        else:
            title = f"Human Design Report - {display_name}"
        return ReportDocument(
            report_id=request.report_id,
            title=title,
            tier=request.tier,
            content_mode=request.content_mode,
            domains=request.domains,
            subject=request.subject,
            partner=request.partner,
            input_snapshot=_json_safe(request.model_dump(mode="json")),
            chart=chart_snapshot,
            plan=plan,
            sections=sections,
            warnings=warnings,
            provenance=provenance,
        )

    # Friendly aliases for Admin/Coach call sites.
    generate = run
    orchestrate = run


__all__ = ["ReportOrchestrator"]
