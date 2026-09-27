"""Application services: permissions, serialization, report generation, audit."""

from __future__ import annotations

import hashlib
import logging
import os
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, sessionmaker

from backend.reporting.contract import ContentMode, ReportDocument, ReportRequest
from backend.reporting.render_common import Theme
from backend.reporting.render_docx import render_docx
from backend.reporting.render_pdf import render_pdf
from backend.reporting.language_vn import TYPE_VN, vn_authority, vn_definition, vn_strategy
from backend.reporting.llm_client import (LLMConfig, LLMError, LLMUsage as TokenUsage, call_llm_with_usage,
    display_provider, estimate_cost)
from backend.reporting.style import (ANALYSIS_SYSTEM, DEFAULT_PREVIEW_TOPIC, PREVIEW_SYSTEM,
                                     build_style_analysis_brief, build_style_preview_brief, parse_style_preview,
                                     parse_style_profile)
from backend.reporting.service import AttemptCallback, generate_report

from .models import (AuditLog, Client, LLMUsage, Organization, Report, ReportRevision, ReportTemplate,
                     TemplateBlock, TemplateSample, User)
from .security import decrypt_value
from .schemas import ChartSummary, ClientOut, ReportDetailOut, ReportSummaryOut, SectionOut

from hd_time import display_birth  # noqa: E402  (tools/ on sys.path via backend.reporting)

log = logging.getLogger("hd.api")


def audit(db: Session, user: User | None, action: str, entity: str = "", entity_id: Any = "",
          ip: str = "", org_id: int | None = None, **meta: Any) -> None:
    """``user=None`` for public events (share page views, signed links) — pass ``org_id``."""
    db.add(AuditLog(
        org_id=user.org_id if user else org_id,
        actor_id=user.id if user else None,
        action=action, entity=entity, entity_id=str(entity_id or ""), meta=meta, ip=ip,
    ))


# --- permissions ------------------------------------------------------------

def visible_clients(user: User):
    query = select(Client).where(Client.org_id == user.org_id, Client.deleted_at.is_(None))
    if user.role != "admin":
        query = query.where(Client.owner_user_id == user.id)
    return query


def get_client_or_404(db: Session, user: User, client_id: int) -> Client:
    client = db.scalar(visible_clients(user).where(Client.id == client_id))
    if client is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng.")
    return client


def visible_reports(user: User):
    query = select(Report).join(Client).where(Report.org_id == user.org_id, Client.deleted_at.is_(None))
    if user.role != "admin":
        query = query.where(Client.owner_user_id == user.id)
    return query


def get_report_or_404(db: Session, user: User, report_id: str) -> Report:
    report = db.scalar(visible_reports(user).where(Report.id == report_id))
    if report is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy báo cáo.")
    return report


# --- serialization ----------------------------------------------------------

def client_out(db: Session, client: Client) -> ClientOut:
    report_count = db.scalar(select(func.count()).select_from(Report).where(
        Report.client_id == client.id, Report.status != "archived")) or 0
    return ClientOut(
        id=client.id, full_name=client.full_name, email=client.email, phone=client.phone,
        birth_date=client.birth_date, birth_time=client.birth_time,
        birth_time_known=client.birth_time_known, birth_place=client.birth_place,
        timezone=client.timezone,
        birth_display=display_birth(client.birth_date, client.birth_time, client.timezone),
        notes=client.notes, owner_id=client.owner_user_id,
        owner_name=client.owner.full_name or client.owner.email,
        report_count=report_count, consent_at=client.consent_at,
        created_at=client.created_at, updated_at=client.updated_at,
    )


def chart_summary(chart: dict[str, Any]) -> ChartSummary:
    chart_type = str(chart.get("type", ""))
    return ChartSummary(
        type=chart_type,
        type_vn=TYPE_VN.get(chart_type, ""),
        strategy=vn_strategy(str(chart.get("strategy", "")), chart_type),
        authority=vn_authority(str(chart.get("authority", ""))),
        profile=str(chart.get("profile", "")),
        definition=vn_definition(str(chart.get("definition", ""))),
        incarnation_cross=str(chart.get("incarnation_cross", "")),
        defined_centers=len(chart.get("defined_centers", []) or []),
    )


def report_summary(report: Report) -> ReportSummaryOut:
    return ReportSummaryOut(
        id=report.id, client_id=report.client_id, client_name=report.client.full_name,
        tier=report.tier, template=report.template, template_name=template_display_name(report),
        content_mode=report.content_mode,
        domains=list(report.domains or []), status=report.status, editor=report.editor,
        warnings_count=report.warnings_count, version=report.version, error=report.error,
        created_at=report.created_at, updated_at=report.updated_at,
    )


def load_document(report: Report) -> ReportDocument:
    if not report.document:
        raise HTTPException(status_code=409, detail="Báo cáo đang được tạo, vui lòng thử lại sau.")
    return ReportDocument.model_validate(report.document)


def report_detail(report: Report) -> ReportDetailOut:
    base = report_summary(report).model_dump()
    client = report.client
    style_used = bool(((report.request or {}).get("options") or {}).get("style_profile"))
    subject_display = display_birth(client.birth_date, client.birth_time, client.timezone)
    if not report.document:
        return ReportDetailOut(**base, subject_display=subject_display, summary=None,
                               sections=[], warnings=[], markdown="",
                               style_used=style_used, style_rating=report.style_rating)
    document = load_document(report)
    sections = [
        SectionOut(id=s.id, title=s.title, status=s.status, warnings=list(s.warnings))
        for s in sorted(document.sections, key=lambda item: item.order)
    ]
    return ReportDetailOut(
        **base, subject_display=subject_display, summary=chart_summary(document.chart),
        sections=sections, warnings=list(document.warnings), markdown=document.to_markdown(),
        llm_provider=document.provenance.llm_provider, llm_cost_usd=document.provenance.llm_cost_usd,
        style_used=style_used, style_rating=report.style_rating,
    )


# --- generation -------------------------------------------------------------

def build_request(client: Client, *, tier: str, template: str, content_mode: str,
                  domains: list[str], report_id: str | None = None) -> ReportRequest:
    payload: dict[str, Any] = {
        "subject": {
            "name": client.full_name,
            "birth_date": client.birth_date,
            "birth_time": client.birth_time,
            "timezone": client.timezone,
            "birth_location": client.birth_place,
        },
        "tier": tier, "template": template, "content_mode": content_mode, "domains": domains,
    }
    if report_id:
        payload["report_id"] = report_id
    return ReportRequest.model_validate(payload)


def store_document(db: Session, report: Report, document: ReportDocument, author: str,
                   change_type: str) -> None:
    """Save ``document`` as the report's next version (+ full revision snapshot)."""
    report.document = document.model_dump(mode="json")
    report.editor = document.provenance.editor
    report.warnings_count = len(document.warnings)
    report.status = "ready"
    report.error = ""
    report.version = (report.version or 0) + 1
    db.add(ReportRevision(report_id=report.id, version=report.version, author=author,
                          change_type=change_type, document=report.document,
                          warnings=list(document.warnings)))


def create_report(db: Session, user: User, client: Client, *, tier: str, template: str,
                  content_mode: str, domains: list[str], custom_template: dict | None = None,
                  org_vars: dict | None = None, style_profile: dict | None = None) -> Report:
    report_id = str(uuid4())
    request = build_request(client, tier=tier, template=template, content_mode=content_mode,
                            domains=domains, report_id=report_id)
    if custom_template is not None:
        request.options = {**(request.options or {}), "custom_template": custom_template,
                           "org_vars": org_vars or {}}
    if style_profile is not None:
        request.options = {**(request.options or {}), "style_profile": style_profile}
    report = Report(
        id=report_id, org_id=user.org_id, client_id=client.id, created_by=user.id,
        tier=tier, template=template, content_mode=content_mode, domains=domains,
        status="generating", request=request.model_dump(mode="json"),
    )
    db.add(report)
    if request.content_mode is not ContentMode.LLM:
        # Template mode is deterministic and takes a few milliseconds: generate inline.
        store_document(db, report, generate_report(request), author=user.email, change_type="generate")
    return report


# --- LLM configuration: fallback chain of providers (P2-6) ------------------------

MAX_LLM_PROVIDERS = 3


def env_llm_defaults() -> LLMConfig:
    """Non-secret defaults from HD_LLM_* env vars (key left empty)."""
    config = LLMConfig.from_env({**os.environ, "HD_LLM_API_KEY": "-"})
    assert config is not None  # "-" key guarantees a config
    return LLMConfig(api_key="", base_url=config.base_url, model=config.model, timeout=config.timeout,
                     temperature=config.temperature)


def stored_providers(org: Organization | None) -> list[dict[str, Any]]:
    """Provider dicts from the DB: the ``providers`` list, else legacy flat keys as one entry."""
    stored = (org.llm_settings or {}) if org else {}
    providers = stored.get("providers")
    if isinstance(providers, list) and providers:
        return [p for p in providers if isinstance(p, dict)]
    if not any(k in stored for k in ("base_url", "model", "api_key_enc")):
        return []
    return [{
        "name": "Chính",
        "base_url": stored.get("base_url") or "",
        "model": stored.get("model") or "",
        "temperature": stored.get("temperature"),
        "timeout": stored.get("timeout"),
        "api_key_enc": stored.get("api_key_enc") or "",
        "enabled": True,
        "input_price": 0.0,
        "output_price": 0.0,
    }]


def decrypt_provider_key(entry: dict[str, Any], secret: str) -> tuple[str, bool]:
    """``(key, unreadable)`` for one stored provider entry."""
    encrypted = entry.get("api_key_enc") or ""
    if not encrypted:
        return "", False
    key = decrypt_value(secret, encrypted)
    return (key or "", key is None)


def _num(value: Any, default: float) -> float:
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def provider_config(entry: dict[str, Any], key: str, defaults: LLMConfig) -> LLMConfig:
    return LLMConfig(
        api_key=key,
        base_url=(entry.get("base_url") or defaults.base_url).rstrip("/"),
        model=(entry.get("model") or defaults.model).strip(),
        timeout=_num(entry.get("timeout"), defaults.timeout),
        temperature=_num(entry.get("temperature"), defaults.temperature),
        name=(entry.get("name") or "").strip(),
        input_price=max(0.0, _num(entry.get("input_price"), 0.0)),
        output_price=max(0.0, _num(entry.get("output_price"), 0.0)),
    )


def org_llm_configs(db: Session, org_id: int, secret: str) -> list[LLMConfig]:
    """Enabled providers with a readable key, in fallback order.

    Explicit DB providers win completely: the ``HD_LLM_*`` env fallback applies
    only when the organization has no usable stored provider.
    """
    org = db.get(Organization, org_id)
    defaults = env_llm_defaults()
    configs = []
    for entry in stored_providers(org):
        if entry.get("enabled", True) is False:
            continue
        key = decrypt_provider_key(entry, secret)[0]
        if not key:
            continue  # missing, or encrypted with another server secret
        configs.append(provider_config(entry, key, defaults))
    if configs:
        return configs
    env = LLMConfig.from_env()
    return [env] if env is not None else []


def org_llm_config(db: Session, org_id: int, secret: str) -> LLMConfig | None:
    """First provider of the fallback chain (``None`` = AI off)."""
    configs = org_llm_configs(db, org_id, secret)
    return configs[0] if configs else None


# --- LLM usage + cost tracking -------------------------------------------------

def collect_attempts(entries: list[dict[str, Any]]) -> AttemptCallback:
    def _collect(config: LLMConfig, ok: bool, usage: TokenUsage | None, error: str, latency_ms: int) -> None:
        entries.append({"config": config, "ok": ok, "usage": usage, "error": error, "latency_ms": latency_ms})

    return _collect


def save_llm_usages(db: Session, org_id: int, report_id: str | None, purpose: str,
                    entries: list[dict[str, Any]]) -> None:
    """Persist one ``llm_usage`` row per collected attempt (success or failure)."""
    for entry in entries:
        config = entry["config"]
        usage: TokenUsage | None = entry["usage"]
        cost = estimate_cost(usage, config.input_price, config.output_price) if usage is not None else None
        db.add(LLMUsage(
            org_id=org_id, report_id=report_id, purpose=purpose,
            provider=display_provider(config), base_url=config.base_url, model=config.model,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            input_price=config.input_price, output_price=config.output_price,
            cost_usd=cost, ok=entry["ok"], error=entry["error"][:500], latency_ms=entry["latency_ms"],
        ))


def _naive_utc(value: datetime) -> datetime:
    return value if value.tzinfo is None else value.astimezone(timezone.utc).replace(tzinfo=None)


def llm_usage_stats(db: Session, org_id: int, days: int) -> dict[str, Any]:
    """Totals + per-provider breakdown + recent attempts for the last ``days`` days."""
    days = min(max(int(days), 1), 365)
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
    rows = db.scalars(select(LLMUsage).where(LLMUsage.org_id == org_id)
                      .order_by(LLMUsage.created_at.desc()).limit(5000)).all()
    rows = [r for r in rows if _naive_utc(r.created_at) >= cutoff]

    def blank() -> dict[str, Any]:
        return {"requests": 0, "errors": 0, "prompt_tokens": 0, "completion_tokens": 0,
                "cost_usd": 0.0, "unpriced_requests": 0}

    totals = blank()
    by_provider: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        for agg in (totals, by_provider.setdefault((row.provider, row.model), blank())):
            agg["requests"] += 1
            if not row.ok:
                agg["errors"] += 1
            agg["prompt_tokens"] += row.prompt_tokens or 0
            agg["completion_tokens"] += row.completion_tokens or 0
            if row.cost_usd is None:
                agg["unpriced_requests"] += 1
            else:
                agg["cost_usd"] += row.cost_usd
    providers = [{"provider": provider, "model": model, **agg}
                 for (provider, model), agg in sorted(by_provider.items(), key=lambda kv: -kv[1]["requests"])]
    recent = [{
        "id": r.id, "created_at": r.created_at, "report_id": r.report_id, "purpose": r.purpose,
        "provider": r.provider, "model": r.model, "prompt_tokens": r.prompt_tokens,
        "completion_tokens": r.completion_tokens, "cost_usd": r.cost_usd, "ok": r.ok,
        "error": r.error, "latency_ms": r.latency_ms,
    } for r in rows[:100]]
    return {"days": days, "totals": totals, "by_provider": providers, "recent": recent}


class Heartbeat:
    """Refresh ``reports.job_heartbeat_at`` every few seconds while a job runs (own DB session)."""

    def __init__(self, session_factory: sessionmaker, report_id: str, interval: float) -> None:
        self._factory, self._id, self._interval = session_factory, report_id, interval
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, name=f"hb-{report_id[:8]}", daemon=True)

    def _run(self) -> None:
        while not self._stop.wait(self._interval):
            try:
                with self._factory() as db:
                    db.execute(update(Report).where(Report.id == self._id, Report.status == "generating")
                               .values(job_heartbeat_at=datetime.now(timezone.utc)))
                    db.commit()
            except Exception:  # noqa: BLE001 - a missed beat only delays recovery
                log.warning("heartbeat failed for %s", self._id, exc_info=True)

    def __enter__(self) -> "Heartbeat":
        self._thread.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self._stop.set()
        self._thread.join(timeout=5)


def run_llm_generation(session_factory: sessionmaker, report_id: str, author: str,
                       artifact_dir: str | None = None, change_type: str = "generate",
                       llm_config: LLMConfig | None = None, heartbeat_seconds: float = 15.0,
                       claimed: bool = False, llm_configs: list[LLMConfig] | None = None) -> None:
    """Background job for content_mode=llm (30-120 s). Falls back to template inside service.

    No DB session is held during the LLM call; a heartbeat thread proves the job is alive so
    ``jobs.recover_stale_reports`` can resume it if the process dies (restart / deploy / crash).
    ``claimed=True`` when the recovery sweep already counted this attempt.
    Every provider attempt is logged to ``llm_usage`` (tokens + cost).
    """
    if llm_configs is None and llm_config is not None:
        llm_configs = [llm_config]
    with session_factory() as db:
        report = db.get(Report, report_id)
        if report is None or report.status != "generating":
            return
        if not claimed:
            report.generation_attempts = (report.generation_attempts or 0) + 1
        report.job_heartbeat_at = datetime.now(timezone.utc)
        request = ReportRequest.model_validate(report.request)
        db.commit()

    attempts: list[dict[str, Any]] = []
    document: ReportDocument | None = None
    error = ""
    with Heartbeat(session_factory, report_id, heartbeat_seconds):
        try:
            document = generate_report(request, llm_configs=llm_configs or None,
                                       on_llm_attempt=collect_attempts(attempts))
        except Exception as exc:  # noqa: BLE001 - surface any failure to the UI
            log.exception("report generation failed: %s", report_id)
            error = str(exc)[:1000] or exc.__class__.__name__

    ready = False
    with session_factory() as db:
        report = db.get(Report, report_id)
        if report is None:
            return
        if attempts:
            save_llm_usages(db, report.org_id, report_id, "report", attempts)
        if report.status != "generating":
            db.commit()
            return  # archived / superseded meanwhile
        if document is not None:
            store_document(db, report, document, author=author, change_type=change_type)
        else:
            report.status, report.error = "failed", error
        report.job_heartbeat_at = None
        report.updated_at = datetime.now(timezone.utc)
        db.commit()
        ready = report.status == "ready"
    if artifact_dir and ready:
        warm_artifacts(session_factory, artifact_dir, report_id)


# --- file exports (PDF / DOCX) ----------------------------------------------

ARTIFACT_FORMATS = {
    "pdf": ("application/pdf", ".pdf"),
    "docx": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx"),
}


def report_theme(db: Session, report: Report) -> Theme:
    org = db.get(Organization, report.org_id)
    return Theme.from_mapping(org.theme if org else None)


def _artifact_path(artifact_dir: str, report: Report, fmt: str, theme: Theme) -> Path:
    theme_key = hashlib.sha256(repr(theme).encode("utf-8")).hexdigest()[:8]
    return Path(artifact_dir) / report.id / f"v{report.version}-{theme_key}{ARTIFACT_FORMATS[fmt][1]}"


def render_artifact(artifact_dir: str, report: Report, fmt: str, theme: Theme) -> bytes:
    """PDF/DOCX bytes, cached on disk per report version (plan P0-10).

    A new version (regenerate / edit) gets a new file name, so cached files never go stale.
    """
    path = _artifact_path(artifact_dir, report, fmt, theme)
    if path.is_file():
        return path.read_bytes()
    document = load_document(report)
    data = render_pdf(document, theme) if fmt == "pdf" else render_docx(document, theme)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".{uuid4().hex}.tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)  # atomic: concurrent workers never read half-written files
    return data


def warm_artifacts(session_factory: sessionmaker, artifact_dir: str, report_id: str) -> None:
    """Pre-render PDF + DOCX right after generation so the first download is instant."""
    db = session_factory()
    try:
        report = db.get(Report, report_id)
        if report is None or not report.document:
            return
        theme = report_theme(db, report)
        for fmt in ARTIFACT_FORMATS:
            try:
                render_artifact(artifact_dir, report, fmt, theme)
            except Exception:  # noqa: BLE001 - downloads will retry and surface the error
                log.exception("pre-render %s failed for %s", fmt, report_id)
        prune_artifacts(artifact_dir, report_id, keep_version=report.version)
    finally:
        db.close()


def prune_artifacts(artifact_dir: str, report_id: str, keep_version: int) -> int:
    """Delete cached files of older versions (any version can be re-rendered from its revision)."""
    folder = Path(artifact_dir) / report_id
    removed = 0
    if not folder.is_dir():
        return 0
    for path in folder.iterdir():
        if path.is_file() and not path.name.startswith(f"v{keep_version}-") and not path.name.startswith("."):
            try:
                path.unlink()
                removed += 1
            except OSError:  # concurrent download / already gone
                pass
    return removed

# --- report templates (Giai đoạn 1) -------------------------------------------

BUILTIN_TEMPLATE_KEYS = ("sections", "operating_manual")
BUILTIN_TEMPLATE_NAMES = {"sections": "Theo mục", "operating_manual": "Cẩm nang vận hành"}


def org_var_map(org: Organization | None) -> dict[str, str]:
    try:
        items = ((org.template_vars if org else None) or {}).get("vars", [])
    except AttributeError:
        items = []
    return {v["key"]: v.get("value", "") for v in items if isinstance(v, dict) and v.get("key")}


def snapshot_sections(db: Session, sections) -> list[dict]:
    """Chuyển sections đã validate thành snapshot tự chứa cho orchestrator."""
    out: list[dict] = []
    for i, entry in enumerate(sections or []):
        if entry.get("type") == "builtin":
            out.append({"id": entry.get("ref", f"custom_{i}"), "type": "builtin",
                        "ref": entry.get("ref", ""), "title_override": entry.get("title_override", "")})
            continue
        blk = db.get(TemplateBlock, entry.get("block_id")) if entry.get("block_id") else None
        if blk is not None:
            out.append({"id": f"custom_{i}", "type": "block", "name": blk.name, "kind": blk.kind,
                        "title": entry.get("title_override") or blk.name, "body": blk.body})
        else:
            out.append({"id": f"custom_{i}", "type": "block", "name": entry.get("name", ""),
                        "kind": entry.get("kind", "core") or "core",
                        "title": entry.get("title", "") or "Khối nội dung",
                        "body": entry.get("body", "")})
    return out


def build_template_snapshot(db: Session, tpl: ReportTemplate) -> dict:
    return {"key": tpl.key, "name": tpl.name, "description": tpl.description or "",
            "version": tpl.version, "sections": snapshot_sections(db, tpl.sections)}


def resolve_custom_template(db: Session, user: User, key: str) -> dict | None:
    """Snapshot mẫu tùy chỉnh đang hoạt động, hoặc None nếu là mẫu hệ thống/không có."""
    if key in BUILTIN_TEMPLATE_KEYS:
        return None
    tpl = db.scalar(select(ReportTemplate).where(
        ReportTemplate.org_id == user.org_id, ReportTemplate.key == key,
        ReportTemplate.status == "active"))
    if tpl is None:
        tpl = db.scalar(select(ReportTemplate).where(
            ReportTemplate.visibility == "shared", ReportTemplate.key == key,
            ReportTemplate.status == "active"))
    return build_template_snapshot(db, tpl) if tpl is not None else None


def template_display_name(report: Report) -> str:
    key = report.template or "sections"
    if key in BUILTIN_TEMPLATE_NAMES:
        return BUILTIN_TEMPLATE_NAMES[key]
    try:
        snap = ((report.request or {}).get("options") or {}).get("custom_template") or {}
        if snap.get("name"):
            return str(snap["name"])
    except (AttributeError, TypeError):
        pass
    return key


# --- template style (P2) ------------------------------------------------------

STYLE_MIN_SAMPLES = 2


def analyze_template_style(db: Session, user: User, tpl: ReportTemplate, secret: str) -> dict:
    """Trích hồ sơ văn phong từ bài mẫu qua LLM của tổ chức (P2-B)."""
    samples = db.scalars(select(TemplateSample).where(TemplateSample.template_id == tpl.id)
                         .order_by(TemplateSample.sort, TemplateSample.id)).all()
    if len(samples) < STYLE_MIN_SAMPLES:
        raise HTTPException(status_code=422, detail=(
            f"Cần ít nhất {STYLE_MIN_SAMPLES} bài mẫu để phân tích văn phong (hiện có {len(samples)})."))
    configs = org_llm_configs(db, user.org_id, secret)
    if not configs:
        raise HTTPException(status_code=422, detail="Chưa cấu hình AI cho tổ chức (Cài đặt → AI / LLM).")
    brief = build_style_analysis_brief(tpl.name, [(s.title, s.body) for s in samples])
    attempts: list[dict[str, Any]] = []
    errors: list[str] = []
    for config in configs:
        started = time.perf_counter()
        try:
            drafts, usage = call_llm_with_usage(brief, config, system=ANALYSIS_SYSTEM)
        except LLMError as exc:
            latency = int((time.perf_counter() - started) * 1000)
            errors.append(f"{display_provider(config)} ({exc})")
            attempts.append({"config": config, "ok": False, "usage": None,
                             "error": str(exc)[:500], "latency_ms": latency})
            continue
        latency = int((time.perf_counter() - started) * 1000)
        attempts.append({"config": config, "ok": True, "usage": usage, "error": "", "latency_ms": latency})
        save_llm_usages(db, user.org_id, None, "template_style", attempts)
        try:
            return parse_style_profile(drafts, len(samples))
        except ValueError as exc:
            db.commit()
            raise HTTPException(status_code=502, detail=f"{exc} Thử phân tích lại.") from exc
    save_llm_usages(db, user.org_id, None, "template_style", attempts)
    db.commit()
    raise HTTPException(status_code=503, detail=f"AI đang bận, thử lại sau ({'; '.join(errors)}).")


def resolve_template_style(db: Session, user: User, key: str) -> dict | None:
    """Snapshot hồ sơ văn phong (ready) của mẫu custom, hoặc None."""
    if key in BUILTIN_TEMPLATE_KEYS:
        return None
    tpl = db.scalar(select(ReportTemplate).where(
        ReportTemplate.org_id == user.org_id, ReportTemplate.key == key,
        ReportTemplate.status == "active"))
    if tpl is None:
        tpl = db.scalar(select(ReportTemplate).where(
            ReportTemplate.visibility == "shared", ReportTemplate.key == key,
            ReportTemplate.status == "active"))
    if tpl is None or tpl.style_status != "ready":
        return None
    return {"template_key": tpl.key, "template_name": tpl.name, "template_version": tpl.version,
            "profile": tpl.style_profile or {}}

# --- văn phong mẫu: viết thử / so sánh / thống kê (P3) -------------------------

def _style_llm_text(db: Session, user: User, secret: str, brief: str, purpose: str,
                    ) -> tuple[str, LLMConfig]:
    """Gọi LLM lấy đoạn văn thô qua fallback-chain. Trả về (text, config đã dùng)."""
    configs = org_llm_configs(db, user.org_id, secret)
    if not configs:
        raise HTTPException(status_code=422, detail="Chưa cấu hình AI cho tổ chức (Cài đặt → AI / LLM).")
    attempts: list[dict[str, Any]] = []
    errors: list[str] = []
    for config in configs:
        started = time.perf_counter()
        try:
            drafts, usage = call_llm_with_usage(brief, config, system=PREVIEW_SYSTEM)
        except LLMError as exc:
            latency = int((time.perf_counter() - started) * 1000)
            errors.append(f"{display_provider(config)} ({exc})")
            attempts.append({"config": config, "ok": False, "usage": None,
                             "error": str(exc)[:500], "latency_ms": latency})
            continue
        latency = int((time.perf_counter() - started) * 1000)
        attempts.append({"config": config, "ok": True, "usage": usage, "error": "", "latency_ms": latency})
        save_llm_usages(db, user.org_id, None, purpose, attempts)
        try:
            return parse_style_preview(drafts), config
        except ValueError as exc:
            db.commit()
            raise HTTPException(status_code=502, detail=f"{exc} Thử lại.") from exc
    save_llm_usages(db, user.org_id, None, purpose, attempts)
    db.commit()
    raise HTTPException(status_code=503, detail=f"AI đang bận, thử lại sau ({'; '.join(errors)}).")


def _preview_topic(tpl: ReportTemplate, topic: str | None) -> tuple[dict, str]:
    profile = tpl.style_profile or {}
    if not str(profile.get("tone", "") or "").strip():
        raise HTTPException(status_code=422, detail="Mẫu chưa có hồ sơ văn phong. Phân tích văn phong trước.")
    clean = (topic or "").strip() or DEFAULT_PREVIEW_TOPIC
    if len(clean) > 300:
        raise HTTPException(status_code=422, detail="Chủ đề viết thử tối đa 300 ký tự.")
    return profile, clean


def preview_template_style(db: Session, user: User, tpl: ReportTemplate, secret: str,
                           topic: str | None) -> tuple[str, str, str]:
    """Viết thử 1 đoạn theo văn phong mẫu (P3.1). Trả về (text, topic, provider)."""
    profile, clean = _preview_topic(tpl, topic)
    text, config = _style_llm_text(db, user, secret,
                                   build_style_preview_brief(clean, profile, styled=True),
                                   "template_style_preview")
    return text, clean, display_provider(config)


def compare_template_style(db: Session, user: User, tpl: ReportTemplate, secret: str,
                           topic: str | None) -> tuple[str, str, str, str]:
    """So sánh giọng mặc định vs giọng mẫu (P3.2). Trả về (default, styled, topic, provider)."""
    profile, clean = _preview_topic(tpl, topic)
    default_text, first = _style_llm_text(db, user, secret,
                                          build_style_preview_brief(clean, profile, styled=False),
                                          "template_style_compare")
    styled_text, second = _style_llm_text(db, user, secret,
                                         build_style_preview_brief(clean, profile, styled=True),
                                         "template_style_compare")
    providers = [display_provider(first), display_provider(second)]
    provider = providers[0] if providers[0] == providers[1] else " / ".join(providers)
    return default_text, styled_text, clean, provider


def template_style_stats(db: Session, user: User, tpl: ReportTemplate) -> dict:
    """Thống kê 👍/👎 từ các báo cáo đã dùng văn phong mẫu (P3.3)."""
    rated = visible_reports(user).where(Report.template == tpl.key,
                                        Report.style_rating.is_not(None))
    up = db.scalar(select(func.count()).select_from(rated.where(Report.style_rating == 1).subquery())) or 0
    down = db.scalar(select(func.count()).select_from(rated.where(Report.style_rating == -1).subquery())) or 0
    recent = db.scalars(rated.order_by(Report.created_at.desc()).limit(10)).all()
    return {"up": up, "down": down, "reports": [
        {"report_id": r.id, "client_name": r.client.full_name,
         "rating": r.style_rating, "created_at": r.created_at} for r in recent]}