"""Request/response schemas for /api/v1 (source of the generated TypeScript types)."""

from __future__ import annotations

import re

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.reporting.contract import ContentMode, DomainName, ReportTier, SubjectInput


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
    created_at: datetime | None = None
    last_login_at: datetime | None = None


class LoginOut(UserOut):
    # Only for embedded previews (request header X-HD-Embedded: 1) where cookies are blocked.
    session_token: str | None = None


class UserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    full_name: str = Field(default="", max_length=200)
    password: str = Field(min_length=8, max_length=200)
    role: Literal["admin", "coach"] = "coach"


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=200)
    role: Literal["admin", "coach"] | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=200)


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=8, max_length=200)


# --- catalog ----------------------------------------------------------------

class CatalogOption(BaseModel):
    value: str
    label: str
    description: str = ""
    badge: str = ""
    meta: str = ""
    has_style: bool = False


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
    # Mẫu hệ thống ("sections"/"operating_manual") hoặc key mẫu tùy chỉnh.
    template: str = "sections"
    domains: list[DomainName] = Field(default_factory=list)

    @field_validator("template")
    @classmethod
    def _check_template(cls, value: str) -> str:
        value = (value or "").strip()
        if value in ("sections", "operating_manual"):
            return value
        if re.fullmatch(r"[a-z0-9-]{1,30}", value or ""):
            return value
        raise ValueError("Mẫu báo cáo không hợp lệ.")


class PartnerIn(BaseModel):
    name: str = ""
    birth_date: str
    birth_time: str
    timezone: str = "+07:00"


class ReportCreate(ReportOptions):
    client_id: int
    content_mode: ContentMode = ContentMode.TEMPLATE
    use_style: bool = True
    partner: PartnerIn | None = None


class PreviewIn(ReportOptions):
    client_id: int | None = None
    full_name: str = ""
    birth_date: str | None = None
    birth_time: str | None = None
    birth_place: str = ""
    timezone: str = "+07:00"
    partner: PartnerIn | None = None


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
    template_name: str = ""
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
    style_used: bool = False
    style_rating: int | None = None
    style_version: int | None = None


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


# --- report templates (Giai đoạn 1) -------------------------------------------

TemplateSectionType = Literal["builtin", "block"]
TemplateStatus = Literal["draft", "pending", "active", "rejected", "archived"]
BlockKind = Literal["intro", "core", "practice", "outro", "disclaimer"]


# --- văn phong mẫu (P2) ----------------------------------------------------------


class StyleProfile(BaseModel):
    tone: str = ""
    rhythm: str = ""
    vocabulary: str = ""
    structure: str = ""
    do: list[str] = Field(default_factory=list)
    dont: list[str] = Field(default_factory=list)
    excerpt: str = ""
    sample_count: int = 0


class StylePreviewIn(BaseModel):
    topic: str | None = None


class StylePreviewOut(BaseModel):
    preview: str
    topic: str
    style_status: str
    provider: str


class StyleCompareOut(BaseModel):
    topic: str
    default_text: str
    styled_text: str
    style_status: str
    provider: str


class StyleRatedReport(BaseModel):
    report_id: str
    client_name: str
    rating: int
    created_at: datetime


class StyleVersionStat(BaseModel):
    version: int
    up: int
    down: int


class StyleStatsOut(BaseModel):
    up: int
    down: int
    reports: list[StyleRatedReport]
    by_version: list[StyleVersionStat] = []


class StyleHistoryOut(BaseModel):
    version_no: int
    source: str
    created_by_name: str
    created_at: datetime
    tone: str
    excerpt: str
    sample_count: int


class StyleCopyIn(BaseModel):
    from_template_id: int


class ApplyStyleIn(BaseModel):
    template_key: str | None = None

class StyleRatingIn(BaseModel):
    rating: int = Field(ge=-1, le=1)  # 1 = 👍, -1 = 👎, 0 = gỡ đánh giá


class TemplateSectionIn(BaseModel):
    type: TemplateSectionType
    ref: str = ""
    block_id: int | None = None
    title_override: str = Field(default="", max_length=160)
    name: str = Field(default="", max_length=120)
    kind: str = "core"
    title: str = Field(default="", max_length=160)
    body: str = Field(default="", max_length=20000)


class TemplateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    badge: str = Field(default="", max_length=40)
    sections: list[TemplateSectionIn] = Field(default_factory=list, min_length=1, max_length=30)


class TemplateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    badge: str | None = Field(default=None, max_length=40)
    sections: list[TemplateSectionIn] | None = Field(default=None, min_length=1, max_length=30)
    status: TemplateStatus | None = None
    review_note: str | None = Field(default=None, max_length=2000)
    visibility: str | None = None
    style_profile: StyleProfile | None = None


class ResolvedSectionOut(BaseModel):
    type: str
    ref: str = ""
    block_id: int | None = None
    title: str
    title_default: str = ""
    kind: str = ""
    name: str = ""
    body: str = ""


class TemplateSummaryOut(BaseModel):
    id: int
    key: str
    name: str
    description: str = ""
    badge: str = ""
    visibility: str
    status: str
    version: int
    sections_count: int
    samples_count: int
    reports_count: int = 0
    origin_label: str = ""
    import_count: int = 0
    created_by_name: str = ""
    style_status: str = "none"
    created_at: datetime
    updated_at: datetime


class SampleOut(BaseModel):
    id: int
    title: str
    body: str
    sort: int


class TemplateDetailOut(TemplateSummaryOut):
    review_note: str = ""
    style_profile: StyleProfile = Field(default_factory=StyleProfile)
    style_status: str = "none"
    sections: list[ResolvedSectionOut] = Field(default_factory=list)
    samples: list[SampleOut] = Field(default_factory=list)


class SampleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    body: str = Field(default="", max_length=50000)
    sort: int = 0


class SampleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    body: str | None = Field(default=None, max_length=50000)
    sort: int | None = None


class BlockCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    kind: BlockKind = "core"
    body: str = Field(default="", max_length=20000)


class BlockUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    kind: BlockKind | None = None
    body: str | None = Field(default=None, max_length=20000)


class BlockOut(BaseModel):
    id: int
    name: str
    kind: str
    body: str
    variables: list[str] = Field(default_factory=list)
    used_in: list[str] = Field(default_factory=list)


class OrgVarIn(BaseModel):
    key: str = Field(pattern=r"^[a-z][a-z0-9_]{0,29}$")
    label: str = Field(default="", max_length=60)
    value: str = Field(default="", max_length=500)


class OrgVarsIn(BaseModel):
    vars: list[OrgVarIn] = Field(default_factory=list, max_length=50)


class OrgVarsOut(BaseModel):
    vars: list[OrgVarIn] = Field(default_factory=list)


class BlockVariableOut(BaseModel):
    path: str
    label: str
    example: str


class TemplateDefinitionIn(BaseModel):
    name: str = Field(default="", max_length=120)
    sections: list[TemplateSectionIn] = Field(default_factory=list, min_length=1, max_length=30)


class TemplatePreviewIn(BaseModel):
    template_id: int | None = None
    definition: TemplateDefinitionIn | None = None


class PreviewSectionOut(BaseModel):
    id: str
    title: str
    markdown: str


class TemplatePreviewOut(BaseModel):
    title: str
    sections: list[PreviewSectionOut]
    warnings: list[str] = Field(default_factory=list)


class FromBuiltinIn(BaseModel):
    builtin: Literal["sections", "operating_manual"]
    name: str = Field(min_length=1, max_length=120)


class TemplatePublishIn(BaseModel):
    badge: str = ""
    origin_label: str = ""


class BuiltinSectionOut(BaseModel):
    id: str
    title: str
    kind: str

class GameChartIn(BaseModel):
    birth_date: str
    birth_time: str
    timezone: str = "+07:00"
    birth_place: str = ""


class GameChartOut(BaseModel):
    summary: ChartSummary
    centers: list[str]
    subject_display: str


class GameEventIn(BaseModel):
    name: str
    theme: str = ""
    session_id: str = ""


class GameLeadIn(BaseModel):
    name: str = Field("", max_length=80)
    contact: str = Field("", max_length=120)
    birth_date: str = ""
    birth_time: str = ""
    birth_place: str = Field("", max_length=120)
    timezone: str = "+07:00"
    theme: str = Field("", max_length=32)
    quiz: dict = {}
    note: str = Field("", max_length=500)


class GameLeadStatusIn(BaseModel):
    status: Literal["new", "contacted", "converted", "spam"]


class GameLeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    contact: str
    birth_date: str
    birth_time: str
    birth_place: str
    timezone: str
    theme: str
    quiz: dict
    note: str
    status: str
    created_at: datetime

class GameFunnelStat(BaseModel):
    theme: str
    name: str
    count: int


class GameScoreIn(BaseModel):
    theme: str = ""
    style: str = ""
    deviation: int = -1
    session_id: str = ""


class GameScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    theme: str
    style: str
    deviation: int
    created_at: datetime


class GameStreakIn(BaseModel):
    session_id: str = ""


class GameStreakOut(BaseModel):
    streak: int
    today_done: bool

class GameConceptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    name: str
    entry_label: str
    entry_desc: str
    icon: str
    intro: str
    bridge: str
    enabled: bool
    is_builtin: bool
    sort_order: int


class GameConceptAdminOut(GameConceptOut):
    custom_total: int = 0
    custom_enabled: int = 0
    disabled_builtin: int = 0


class GameConceptIn(BaseModel):
    slug: str = Field("", max_length=32)
    name: str = Field("", max_length=80)
    entry_label: str = Field("", max_length=120)
    entry_desc: str = Field("", max_length=200)
    icon: str = Field("", max_length=16)
    intro: str = Field("", max_length=2000)
    bridge: str = Field("", max_length=2000)


class GameConceptPatch(BaseModel):
    enabled: bool | None = None
    sort_order: int | None = None
    name: str | None = Field(None, max_length=80)
    entry_label: str | None = Field(None, max_length=120)
    entry_desc: str | None = Field(None, max_length=200)
    icon: str | None = Field(None, max_length=16)
    intro: str | None = Field(None, max_length=2000)
    bridge: str | None = Field(None, max_length=2000)


class GameQuestionOption(BaseModel):
    t: str = Field("", max_length=500)
    s: str = ""


class GameQuestionIn(BaseModel):
    concept_slug: str = ""
    title: str = Field("", max_length=200)
    sit: str = Field("", max_length=2000)
    options: list[GameQuestionOption] = []
    enabled: bool = True


class GameQuestionPatch(BaseModel):
    title: str | None = Field(None, max_length=200)
    sit: str | None = Field(None, max_length=2000)
    options: list[GameQuestionOption] | None = None
    enabled: bool | None = None


class GameQuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    concept_slug: str
    qid: str
    title: str = ""
    sit: str = ""
    options: list
    enabled: bool
    created_at: datetime


class GameQuestionsOut(BaseModel):
    custom: list[GameQuestionOut]
    disabled_builtin: list[str]


class GameDisabledIn(BaseModel):
    concept_slug: str = ""
    qid: str = ""


class GamePublicConfig(BaseModel):
    concepts: list[GameConceptOut]
    custom_questions: dict[str, list[GameQuestionOut]]
    disabled_builtin: dict[str, list[str]]
    structures: dict[str, list[GameChapterOut]] = {}

class GameNodeIn(BaseModel):
    chapter_id: int = 0
    mode: str = "normal"
    question_count: int = 8
    time_limit: int = 0
    question_ids: list[str] = []


class GameNodePatch(BaseModel):
    mode: str | None = None
    question_count: int | None = None
    time_limit: int | None = None
    question_ids: list[str] | None = None
    idx: int | None = None


class GameNodeOut(BaseModel):
    id: int
    chapter_id: int
    idx: int
    mode: str
    question_count: int
    time_limit: int
    question_ids: list[str]
    auto: bool = True


class GameChapterIn(BaseModel):
    concept_slug: str = ""
    name: str = Field("", max_length=80)
    icon: str = Field("", max_length=16)
    desc: str = Field("", max_length=200)


class GameChapterPatch(BaseModel):
    name: str | None = Field(None, max_length=80)
    icon: str | None = Field(None, max_length=16)
    desc: str | None = Field(None, max_length=200)
    idx: int | None = None


class GameChapterOut(BaseModel):
    id: int
    concept_slug: str
    idx: int
    name: str
    icon: str
    desc: str
    nodes: list[GameNodeOut] = []
