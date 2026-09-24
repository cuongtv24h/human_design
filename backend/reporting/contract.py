"""Stable data contracts for admin report generation.

The contract deliberately separates report selection from the implementation of
individual analyzers.  A future API or frontend can therefore submit a
``ReportRequest`` without knowing which Python module produces each section.
"""

from __future__ import annotations

import sys
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

_TOOLS_DIR = str(Path(__file__).resolve().parents[2] / "tools")
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

from hd_time import VN_UTC_OFFSET, format_local, normalize_offset, zone_label  # noqa: E402


class ReportTier(str, Enum):
    """Base report level; domains are add-ons to either level."""

    FREE_BASIC = "free_basic"
    DEEP_CORE = "deep_core"


class ReportFormat(str, Enum):
    STRUCTURED = "structured"
    MARKDOWN = "markdown"


class ReportTemplate(str, Enum):
    """Presentation template for the report document.

    The template is independent from ``tier`` and ``domains``: a base report
    level selects how much chart data is analyzed, while the template selects
    how that data is written.  ``operating_manual`` is the natural-Vietnamese
    narrative standard documented in ``docs/NARRATIVE_STANDARD.md``.
    """

    SECTIONS = "sections"
    OPERATING_MANUAL = "operating_manual"


class ContentMode(str, Enum):
    """Who writes the report body.

    Every report starts from the same calculated data and always carries the
    subject information plus the auto-generated BodyGraph.  The content itself
    then follows one of two modes:

    - ``TEMPLATE``: deterministic renderer (default).
    - ``LLM``: an LLM rewrites the content from the calculated source data,
      bound to the expert/consultant persona and the hard rules defined in
      ``backend/reporting/llm_editor.py`` (see ``docs/NARRATIVE_STANDARD.md``).
      The LLM never recalculates — it only narrates.
    """

    TEMPLATE = "template"
    LLM = "llm"


class DomainName(str, Enum):
    MONEY = "money"
    POTENTIAL = "potential"
    HEALTH = "health"
    RELATIONSHIP = "relationship"
    DECISION = "decision"
    DECONDITIONING = "deconditioning"
    PURPOSE = "purpose"
    TEAM = "team"


def _validate_birth_date(value: str) -> str:
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("birth_date must be a valid YYYY-MM-DD date") from exc
    return value


def _validate_birth_time(value: str) -> str:
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            datetime.strptime(value, fmt)
            return value
        except ValueError:
            continue
    raise ValueError("birth_time must use HH:MM or HH:MM:SS")


def _validate_timezone(value: str) -> str:
    """Canonical fixed offset; Vietnam aliases/empty → +07:00 (tools/hd_time.py)."""
    return normalize_offset(value)


def _birth_display(birth_date: str, birth_time: str, tz: str) -> tuple[str, str]:
    """(``15/05/1990``, ``08:30 (giờ Việt Nam)``) — exactly the declared time."""
    local = format_local(birth_date, birth_time)
    day, clock = local.split(" ", 1)
    return day, f"{clock} ({zone_label(tz)})"


class SubjectInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = ""
    birth_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    birth_time: str = Field(..., pattern=r"^\d{2}:\d{2}(:\d{2})?$")
    timezone: str = Field(
        VN_UTC_OFFSET,
        description="Offset cố định của giờ khai báo; mặc định giờ Việt Nam +07:00 (không áp offset lịch sử).",
    )
    birth_location: str = ""

    _date_validator = field_validator("birth_date")(_validate_birth_date)
    _time_validator = field_validator("birth_time")(_validate_birth_time)
    _tz_validator = field_validator("timezone")(_validate_timezone)


class PartnerInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = ""
    birth_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    birth_time: str = Field(..., pattern=r"^\d{2}:\d{2}(:\d{2})?$")
    timezone: str = VN_UTC_OFFSET

    _date_validator = field_validator("birth_date")(_validate_birth_date)
    _time_validator = field_validator("birth_time")(_validate_birth_time)
    _tz_validator = field_validator("timezone")(_validate_timezone)


class ReportRequest(BaseModel):
    """Input accepted by the report orchestrator.

    ``domains`` is intentionally independent from ``tier``.  This allows the
    product layer to sell a deep core report plus one or more domain modules
    without creating a new hard-coded report type for every combination.
    """

    model_config = ConfigDict(extra="forbid")

    report_id: UUID = Field(default_factory=uuid4)
    subject: SubjectInput
    tier: ReportTier = ReportTier.FREE_BASIC
    template: ReportTemplate = ReportTemplate.SECTIONS
    content_mode: ContentMode = ContentMode.TEMPLATE
    domains: list[DomainName] = Field(default_factory=list)
    partner: PartnerInput | None = None
    output_format: ReportFormat = ReportFormat.STRUCTURED
    locale: str = "vi-VN"
    requested_by: str | None = None
    include_bodygraph: bool = True
    options: dict[str, Any] = Field(default_factory=dict)

    @field_validator("domains")
    @classmethod
    def deduplicate_domains(cls, value: list[DomainName]) -> list[DomainName]:
        return list(dict.fromkeys(value))


SectionKind = Literal[
    "summary",
    "core",
    "domain",
    "practice",
    "appendix",
]
SectionStatus = Literal["included", "skipped", "failed"]


class ReportSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    kind: SectionKind
    order: int
    status: SectionStatus = "included"
    content_markdown: str = ""
    data: dict[str, Any] = Field(default_factory=dict)
    source_tools: list[str] = Field(default_factory=list)
    knowledge_refs: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ReportDefinition(BaseModel):
    """Catalog entry for a reusable base report definition."""

    model_config = ConfigDict(extra="forbid")

    key: str
    title: str
    tier: ReportTier
    section_ids: list[str]
    description: str = ""


class ReportPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    definition_key: str
    tier: ReportTier
    domains: list[DomainName] = Field(default_factory=list)
    section_ids: list[str]
    source_tools: list[str] = Field(default_factory=list)
    knowledge_refs: list[str] = Field(default_factory=list)


class ReportProvenance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    orchestrator_version: str = "0.1.0"
    calculator_version: str = "pyswisseph / Human Design calculator"
    knowledge_version: str = "2026-09-24"
    generated_at: datetime
    source_tools: list[str] = Field(default_factory=list)
    knowledge_refs: list[str] = Field(default_factory=list)
    editor: str = "template"
    # Which provider of the fallback chain wrote the content ("<name> · <model>"); "" for template.
    llm_provider: str = ""
    # Estimated USD cost of the successful LLM call (None when the price is unknown).
    llm_cost_usd: float | None = None


class ReportDocument(BaseModel):
    """Versioned, serializable result consumed by Admin/report renderers."""

    model_config = ConfigDict(extra="forbid")

    schema_name: str = "human_design.report"
    schema_version: str = "1.0.0"
    report_id: UUID
    title: str
    tier: ReportTier
    content_mode: ContentMode = ContentMode.TEMPLATE
    domains: list[DomainName] = Field(default_factory=list)
    subject: SubjectInput
    partner: PartnerInput | None = None
    input_snapshot: dict[str, Any] = Field(default_factory=dict)
    chart: dict[str, Any]
    plan: ReportPlan
    sections: list[ReportSection]
    warnings: list[str] = Field(default_factory=list)
    provenance: ReportProvenance

    def to_markdown(self, bodygraph_path: str | None = None) -> str:
        """Render a deterministic Markdown document without invoking an LLM."""
        lines = [f"# {self.title}", ""]
        day, clock = _birth_display(
            self.subject.birth_date, self.subject.birth_time, self.subject.timezone
        )
        info_bits = [f"Ngày sinh: {day}", f"Giờ sinh: {clock}"]
        if self.subject.birth_location:
            info_bits.append(f"Nơi sinh: {self.subject.birth_location}")
        if self.partner:
            info_bits.append(
                f"Đối tác: {self.partner.name or '—'} "
                f"({' '.join(_birth_display(self.partner.birth_date, self.partner.birth_time, self.partner.timezone))})"
            )
        lines += ["> " + " · ".join(info_bits), ""]
        if bodygraph_path:
            lines += [f"![BodyGraph]({bodygraph_path})", ""]
        for section in sorted(self.sections, key=lambda item: item.order):
            if section.status != "included":
                continue
            lines.extend([f"## {section.title}", ""])
            if section.content_markdown:
                lines.extend([section.content_markdown.rstrip(), ""])
        if self.warnings:
            lines.extend(["## Lưu ý", ""])
            lines.extend(f"- {warning}" for warning in self.warnings)
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"
