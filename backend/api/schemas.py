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


class LoginOut(UserOut):
    # Only for embedded previews (request header X-HD-Embedded: 1) where cookies are blocked.
    session_token: str | None = None


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


class CatalogLlmProvider(BaseModel):
    name: str
    model: str


class CatalogOut(BaseModel):
    tiers: list[CatalogOption]
    templates: list[CatalogOption]
    content_modes: list[CatalogOption]
    domains: list[CatalogOption]
    sections_by_tier: dict[str, list[CatalogSection]]
    llm_available: bool
    # Fallback chain in order (primary first) for the wizard to display.
    llm_providers: list[CatalogLlmProvider] = Field(default_factory=list)
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
    # Which fallback-chain provider wrote the content ("<name> · <model>"); "" for template.
    llm_provider: str = ""
    llm_cost_usd: float | None = None


# --- dashboard --------------------------------------------------------------

class DashboardOut(BaseModel):
    clients: int
    reports_total: int
    reports_by_status: dict[str, int]
    recent_reports: list[ReportSummaryOut]


# --- editor (P2) ------------------------------------------------------------

class GlossaryTerm(BaseModel):
    source: str
    term: str


class GlossaryGroup(BaseModel):
    title: str
    terms: list[GlossaryTerm]


class EditorSection(BaseModel):
    id: str
    title: str
    kind: str
    order: int
    content_markdown: str
    data: dict
    warnings: list[str]
    knowledge_refs: list[str]


class EditorOut(BaseModel):
    report: ReportSummaryOut
    subject_display: str
    sections: list[EditorSection]
    llm_available: bool
    glossary: list[GlossaryGroup]


class SectionUpdate(BaseModel):
    content_markdown: str = Field(max_length=100_000)
    base_version: int


class FactCheckIn(BaseModel):
    content_markdown: str = Field(max_length=100_000)


class FactCheckOut(BaseModel):
    missing_facts: list[str]


class SectionSaveOut(BaseModel):
    version: int
    section: EditorSection
    missing_facts: list[str]


class RevisionOut(BaseModel):
    version: int
    author: str
    change_type: str
    warnings_count: int
    created_at: datetime


class LlmSectionOut(BaseModel):
    draft: str
    missing_facts: list[str]


class RegenerateIn(BaseModel):
    content_mode: ContentMode | None = None


# --- signed download links (P0-10) ------------------------------------------

class DownloadLinkIn(BaseModel):
    format: Literal["pdf", "docx", "markdown", "infographic", "bodygraph_svg"]


class DownloadLinkOut(BaseModel):
    url: str
    expires_at: datetime


# --- LLM settings: fallback chain + cost tracking (P2-6) ---------------------------

class LlmProviderIn(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    base_url: str = Field(min_length=8, max_length=300)
    model: str = Field(min_length=1, max_length=120)
    temperature: float = Field(ge=0, le=2)
    timeout: float = Field(ge=10, le=600)
    # None = keep the stored key; "" = delete it.
    api_key: str | None = Field(default=None, max_length=500)
    enabled: bool = True
    # USD per 1M tokens (0 = unknown → cost is not computed for this provider).
    input_price: float = Field(default=0.0, ge=0, le=10000)
    output_price: float = Field(default=0.0, ge=0, le=10000)

    @field_validator("name")
    @classmethod
    def _name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Tên nhà cung cấp không được để trống")
        return value

    @field_validator("base_url")
    @classmethod
    def _url(cls, value: str) -> str:
        value = value.strip().rstrip("/")
        if not value.startswith(("https://", "http://")):
            raise ValueError("phải bắt đầu bằng https:// hoặc http://")
        return value

    @field_validator("model")
    @classmethod
    def _model(cls, value: str) -> str:
        return value.strip()


class LlmSettingsIn(BaseModel):
    providers: list[LlmProviderIn] = Field(min_length=1, max_length=3)


class LlmProviderOut(BaseModel):
    index: int
    name: str
    base_url: str
    model: str
    temperature: float
    timeout: float
    enabled: bool
    has_key: bool
    key_hint: str = ""
    key_unreadable: bool = False  # stored with another HD_SECRET_KEY
    input_price: float = 0.0
    output_price: float = 0.0


class LlmSettingsOut(BaseModel):
    providers: list[LlmProviderOut]
    key_source: Literal["database", "environment", "none"]
    updated_by: str = ""
    updated_at: datetime | None = None


class LlmTestIn(BaseModel):
    # Which provider to test; None = all enabled providers with a key.
    provider_index: int | None = Field(default=None, ge=0, le=2)


class LlmTestItem(BaseModel):
    index: int
    name: str
    model: str
    ok: bool
    latency_ms: int
    detail: str


class LlmTestOut(BaseModel):
    results: list[LlmTestItem]


class LlmUsageTotals(BaseModel):
    requests: int = 0
    errors: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    unpriced_requests: int = 0


class LlmProviderStat(LlmUsageTotals):
    provider: str
    model: str


class LlmUsageRow(BaseModel):
    id: int
    created_at: datetime
    report_id: str | None
    purpose: str
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float | None
    ok: bool
    error: str = ""
    latency_ms: int


class LlmUsageOut(BaseModel):
    days: int
    totals: LlmUsageTotals
    by_provider: list[LlmProviderStat]
    recent: list[LlmUsageRow]


# --- chat assistant (lookup widget) --------------------------------------------

class AssistantModelOut(BaseModel):
    index: int
    name: str
    model: str


class ChatSendIn(BaseModel):
    session_id: str | None = Field(default=None, max_length=36)
    model_index: int = Field(default=0, ge=0, le=2)
    message: str = Field(min_length=1, max_length=2000)
    context_client_id: int | None = Field(default=None, ge=1)
    context_report_id: str | None = Field(default=None, max_length=36)

    @field_validator("message")
    @classmethod
    def _strip(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Tin nhắn không được để trống")
        return value


class ChatSessionOut(BaseModel):
    id: str
    title: str
    provider: str
    model: str
    message_count: int
    total_cost_usd: float
    created_at: datetime
    updated_at: datetime


class ChatMessageOut(BaseModel):
    id: int
    role: str
    content: str
    tools_used: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float | None = None
    latency_ms: int = 0
    rating: int | None = None
    created_at: datetime


class ChatRateIn(BaseModel):
    rating: int = Field(ge=-1, le=1)  # 1 = 👍, -1 = 👎, 0 = gỡ đánh giá


class ChatSendOut(BaseModel):
    session: ChatSessionOut
    message: ChatMessageOut
    provider: str
    model: str


class ChatSessionDetailOut(BaseModel):
    session: ChatSessionOut
    messages: list[ChatMessageOut]


class ChatAdminSessionOut(ChatSessionOut):
    user_email: str = ""
    user_name: str = ""


class ChatUserStat(BaseModel):
    user_id: int
    email: str
    full_name: str
    sessions: int
    messages: int
    cost_usd: float


class ChatAdminStatsOut(BaseModel):
    days: int
    sessions: int
    messages: int
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    likes: int = 0
    dislikes: int = 0
    by_user: list[ChatUserStat]


# --- share links (P3) ---------------------------------------------------------

ShareFormat = Literal["pdf", "docx", "markdown"]


class ShareCreate(BaseModel):
    formats: list[ShareFormat] = Field(default_factory=lambda: ["pdf"], max_length=3)
    expires_days: int = Field(default=30, ge=1, le=365)
    label: str = Field(default="", max_length=120)


class ShareOut(BaseModel):
    id: int
    report_id: str
    label: str
    formats: list[str]
    expires_at: datetime
    revoked_at: datetime | None
    view_count: int
    last_viewed_at: datetime | None
    created_at: datetime
    status: Literal["active", "expired", "revoked"]


class ShareCreated(BaseModel):
    share: ShareOut
    # Shown exactly once — only its hash is stored.
    url: str


class PublicSection(BaseModel):
    id: str
    title: str
    content_markdown: str


class PublicReportOut(BaseModel):
    client_name: str
    subject_display: str
    title: str
    generated_at: datetime
    summary: "ChartSummary"
    formats: list[str]
    sections: list[PublicSection]
    org_name: str
