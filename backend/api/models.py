"""Persistence model (plan §5). Report documents are stored as full JSON."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base, JSONType


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    # D10: auto-generated default theme for now; real branding replaces it later.
    theme: Mapped[dict] = mapped_column(JSONType, default=dict)
    # P2-6, multi-provider: {providers: [{name, base_url, model, temperature, timeout,
    #   api_key_enc (Fernet), enabled, input_price, output_price}], updated_by, updated_at}.
    # Legacy flat keys (base_url/model/api_key_enc/...) are still read as one provider.
    llm_settings: Mapped[dict] = mapped_column(JSONType, default=dict)
    # Biến tổ chức dùng trong khối nội dung: {vars: [{key, label, value}]}.
    template_vars: Mapped[dict] = mapped_column(JSONType, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(200), default="")
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="coach")  # admin | coach
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped[Organization] = relationship()


class UserSession(Base):
    __tablename__ = "sessions"

    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ip: Mapped[str] = mapped_column(String(64), default="")
    user_agent: Mapped[str] = mapped_column(String(300), default="")

    user: Mapped[User] = relationship()


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    full_name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(320), default="")
    phone: Mapped[str] = mapped_column(String(50), default="")
    birth_date: Mapped[str] = mapped_column(String(10))  # YYYY-MM-DD (declared)
    birth_time: Mapped[str] = mapped_column(String(8))  # HH:MM[:SS] declared Vietnam time
    birth_time_known: Mapped[bool] = mapped_column(Boolean, default=True)
    birth_place: Mapped[str] = mapped_column(String(200), default="")  # display only
    timezone: Mapped[str] = mapped_column(String(6), default="+07:00")
    notes: Mapped[str] = mapped_column(Text, default="")
    consent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    owner: Mapped[User] = relationship()


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # = ReportDocument.report_id
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), index=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    tier: Mapped[str] = mapped_column(String(20))
    template: Mapped[str] = mapped_column(String(30))
    content_mode: Mapped[str] = mapped_column(String(20))
    domains: Mapped[list] = mapped_column(JSONType, default=list)
    status: Mapped[str] = mapped_column(String(20), default="generating", index=True)
    request: Mapped[dict] = mapped_column(JSONType, default=dict)
    document: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    editor: Mapped[str] = mapped_column(String(80), default="")
    warnings_count: Mapped[int] = mapped_column(Integer, default=0)
    version: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str] = mapped_column(Text, default="")
    style_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # P2: 1 | -1 | None
    style_version: Mapped[int | None] = mapped_column(Integer, nullable=True)  # P4: dùng văn phong bản mấy
    # Background generation bookkeeping (restart recovery): a running job refreshes the
    # heartbeat; a "generating" report whose heartbeat stopped is resumed or failed.
    generation_attempts: Mapped[int] = mapped_column(Integer, default=0)
    job_heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    client: Mapped[Client] = relationship()


class ReportRevision(Base):
    __tablename__ = "report_revisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_id: Mapped[str] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer)
    author: Mapped[str] = mapped_column(String(120))
    change_type: Mapped[str] = mapped_column(String(30))  # generate | llm_edit | manual_edit | regenerate | apply_style
    document: Mapped[dict] = mapped_column(JSONType)
    warnings: Mapped[list] = mapped_column(JSONType, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ShareLink(Base):
    """Client-facing link /r/{token} (plan P3-1). Only the SHA-256 of the token is stored."""

    __tablename__ = "share_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_id: Mapped[str] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), index=True)
    org_id: Mapped[int] = mapped_column(Integer, index=True)
    created_by: Mapped[int] = mapped_column(Integer)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    label: Mapped[str] = mapped_column(String(120), default="")
    formats: Mapped[list] = mapped_column(JSONType, default=list)  # downloadable: pdf | docx | markdown
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    last_viewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    report: Mapped[Report] = relationship()


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    actor_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    action: Mapped[str] = mapped_column(String(60), index=True)
    entity: Mapped[str] = mapped_column(String(40), default="")
    entity_id: Mapped[str] = mapped_column(String(40), default="")
    meta: Mapped[dict] = mapped_column(JSONType, default=dict)
    ip: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class LLMUsage(Base):
    """One LLM API attempt (every step of the fallback chain, success or not).

    Prices are snapshots (USD per 1M tokens) copied from the provider settings
    at call time, so later price edits never rewrite history.
    """

    __tablename__ = "llm_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    report_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    purpose: Mapped[str] = mapped_column(String(20), default="report")  # report | section | test
    provider: Mapped[str] = mapped_column(String(120), default="")
    base_url: Mapped[str] = mapped_column(String(300), default="")
    model: Mapped[str] = mapped_column(String(120), default="")
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    input_price: Mapped[float] = mapped_column(Float, default=0.0)
    output_price: Mapped[float] = mapped_column(Float, default=0.0)
    cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    ok: Mapped[bool] = mapped_column(Boolean, default=True)
    error: Mapped[str] = mapped_column(String(500), default="")
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class ChatSession(Base):
    """Trợ lý tra cứu: một phiên chat của user (chi phí cộng dồn để liệt kê nhanh)."""

    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(120), default="Cuộc trò chuyện mới")
    provider: Mapped[str] = mapped_column(String(120), default="")
    model: Mapped[str] = mapped_column(String(120), default="")
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    total_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user: Mapped[User] = relationship()


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(10))  # user | assistant
    content: Mapped[str] = mapped_column(Text)
    tools_used: Mapped[list] = mapped_column(JSONType, default=list)
    sources: Mapped[list] = mapped_column(JSONType, default=list)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1 = 👍, -1 = 👎
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

class ReportTemplate(Base):
    """Mẫu báo cáo tùy chỉnh (Giai đoạn 1: quản trị mẫu + khối + bài mẫu).

    Hai mẫu hệ thống (sections/operating_manual) vẫn nằm trong code.
    Hàng ``visibility=shared`` là bản sao độc lập trên thư viện chung.
    """

    __tablename__ = "report_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), nullable=True, index=True)
    key: Mapped[str] = mapped_column(String(30), index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    badge: Mapped[str] = mapped_column(String(40), default="")
    visibility: Mapped[str] = mapped_column(String(10), default="private")  # private | shared
    status: Mapped[str] = mapped_column(String(10), default="draft")  # draft|pending|active|rejected|archived
    review_note: Mapped[str] = mapped_column(Text, default="")
    version: Mapped[int] = mapped_column(Integer, default=1)
    # [{type: "builtin", ref: "<section_id|domain_x>", title_override: ""} |
    #  {type: "block", block_id: <int|null>, title: "", body: "<inline snapshot>"}]
    sections: Mapped[list] = mapped_column(JSONType, default=list)
    # P2: hồ sơ văn phong trích từ bài mẫu + trạng thái none|ready|stale.
    style_profile: Mapped[dict] = mapped_column(JSONType, default=dict)
    style_status: Mapped[str] = mapped_column(String(16), default="none")
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    origin_template_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    origin_label: Mapped[str] = mapped_column(String(200), default="")
    import_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class TemplateBlock(Base):
    """Khối nội dung tái sử dụng trong thư viện khối của tổ chức."""

    __tablename__ = "template_blocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    kind: Mapped[str] = mapped_column(String(20), default="core")  # intro|core|practice|outro|disclaimer
    body: Mapped[str] = mapped_column(Text, default="")
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class TemplateSample(Base):
    """Bài viết mẫu đính kèm mẫu báo cáo (Giai đoạn 1: chỉ để xem)."""

    __tablename__ = "template_samples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("report_templates.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    body: Mapped[str] = mapped_column(Text, default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class TemplateStyleVersion(Base):
    """Lịch sử hồ sơ văn phong: mỗi lần đổi = 1 bản mới (P4)."""

    __tablename__ = "template_style_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("report_templates.id", ondelete="CASCADE"), index=True)
    version_no: Mapped[int] = mapped_column(Integer)
    profile: Mapped[dict] = mapped_column(JSONType, default=dict)
    source: Mapped[str] = mapped_column(String(16), default="manual")
    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class GameEvent(Base):
    """Sự kiện funnel game landing ẩn danh (G1)."""

    __tablename__ = "game_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(32), index=True)
    theme: Mapped[str] = mapped_column(String(32), default="")
    session_id: Mapped[str] = mapped_column(String(64), default="", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class GameLead(Base):
    """Khách tiềm năng từ game (muốn nhận báo cáo đầy đủ)."""

    __tablename__ = "game_leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    contact: Mapped[str] = mapped_column(String(120))
    birth_date: Mapped[str] = mapped_column(String(10), default="")
    birth_time: Mapped[str] = mapped_column(String(8), default="")
    birth_place: Mapped[str] = mapped_column(String(120), default="")
    timezone: Mapped[str] = mapped_column(String(10), default="+07:00")
    theme: Mapped[str] = mapped_column(String(32), default="")
    quiz: Mapped[dict] = mapped_column(JSONType, default=dict)
    note: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(16), default="new", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class GameScore(Base):
    """Điểm ẩn danh trên bảng vàng tuần (G3)."""

    __tablename__ = "game_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    theme: Mapped[str] = mapped_column(String(32), default="", index=True)
    style: Mapped[str] = mapped_column(String(16), default="")
    deviation: Mapped[int] = mapped_column(Integer, default=100)
    session_id: Mapped[str] = mapped_column(String(64), default="", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)