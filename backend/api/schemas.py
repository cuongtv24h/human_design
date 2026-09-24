"""Request/response schemas for /api/v1 (source of the generated TypeScript types)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.reporting.contract import ContentMode, DomainName, ReportTemplate, ReportTier, SubjectInput


class Problem(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str


# --- auth -------------------------------------------------------------------

class LoginIn(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: Literal["admin", "coach"]
    is_active: bool
    org_name: str = ""


class UserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    full_name: str = Field(default="", max_length=200)
    password: str = Field(min_length=8, max_length=200)
    role: Literal["admin", "coach"] = "coach"


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: Literal["admin", "coach"] | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=200)


# --- catalog ----------------------------------------------------------------

class CatalogOption(BaseModel):
    value: str
    label: str
    description: str = ""


class CatalogSection(BaseModel):
    id: str
    title: str


class CatalogOut(BaseModel):
    tiers: list[CatalogOption]
    templates: list[CatalogOption]
    content_modes: list[CatalogOption]
    domains: list[CatalogOption]
    sections_by_tier: dict[str, list[CatalogSection]]
    llm_available: bool
    timezone_default: str
    timezone_label: str


# --- clients ----------------------------------------------------------------

class ClientIn(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: str = Field(default="", max_length=320)
    phone: str = Field(default="", max_length=50)
    birth_date: str
    birth_time: str
    birth_time_known: bool = True
    birth_place: str = Field(default="", max_length=200)
    timezone: str = "+07:00"
    notes: str = Field(default="", max_length=5000)
    consent: bool = False

    @field_validator("full_name")
    @classmethod
    def _strip(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Họ tên không được để trống")
        return value

    def subject(self) -> SubjectInput:
        """Validate birth data with the report contract (same rules everywhere)."""
        return SubjectInput(
            name=self.full_name,
            birth_date=self.birth_date,
            birth_time=self.birth_time,
            timezone=self.timezone,
            birth_location=self.birth_place,
        )


class ClientPatch(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=200)
    email: str | None = None
    phone: str | None = None
    birth_date: str | None = None
    birth_time: str | None = None
    birth_time_known: bool | None = None
    birth_place: str | None = None
    timezone: str | None = None
    notes: str | None = None


class ClientOut(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    birth_date: str
    birth_time: str
    birth_time_known: bool
    birth_place: str
    timezone: str
    birth_display: str
    notes: str
    owner_id: int
    owner_name: str
    report_count: int
    consent_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ClientList(BaseModel):
    items: list[ClientOut]
    total: int


# --- reports ----------------------------------------------------------------

class ChartSummary(BaseModel):
    type: str
    type_vn: str
    strategy: str
    authority: str
    profile: str
    definition: str
    incarnation_cross: str
    defined_centers: int


class ReportOptions(BaseModel):
    tier: ReportTier = ReportTier.FREE_BASIC
    template: ReportTemplate = ReportTemplate.SECTIONS
    domains: list[DomainName] = Field(default_factory=list)


class ReportCreate(ReportOptions):
    client_id: int
    content_mode: ContentMode = ContentMode.TEMPLATE


class PreviewIn(ReportOptions):
    client_id: int | None = None
    full_name: str = ""
    birth_date: str | None = None
    birth_time: str | None = None
    birth_place: str = ""
    timezone: str = "+07:00"


class PreviewOut(BaseModel):
    subject_display: str
    summary: ChartSummary
    sections: list[CatalogSection]
    markdown: str
    bodygraph_svg: str


class SectionOut(BaseModel):
    id: str
    title: str
    status: str
    warnings: list[str]


class ReportSummaryOut(BaseModel):
    id: str
    client_id: int
    client_name: str
    tier: str
    template: str
    content_mode: str
    domains: list[str]
    status: Literal["generating", "ready", "failed", "archived"]
    editor: str
    warnings_count: int
    version: int
    error: str
    created_at: datetime
    updated_at: datetime


class ReportList(BaseModel):
    items: list[ReportSummaryOut]
    total: int


class ReportDetailOut(ReportSummaryOut):
    subject_display: str
    summary: ChartSummary | None
    sections: list[SectionOut]
    warnings: list[str]
    markdown: str


# --- dashboard --------------------------------------------------------------

class DashboardOut(BaseModel):
    clients: int
    reports_total: int
    reports_by_status: dict[str, int]
    recent_reports: list[ReportSummaryOut]
