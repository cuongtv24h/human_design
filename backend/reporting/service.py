"""Service entry point cho mọi "cửa" (MCP, REST, Admin): một hàm tạo báo cáo.

``generate_report`` chạy orchestrator, và nếu ``content_mode="llm"`` thì
build brief → gọi LLM → merge + validate. Chế độ LLM thử lần lượt từng nhà
cung cấp trong chuỗi (chính → dự phòng 1 → dự phòng 2); chỉ khi TẤT CẢ đều
lỗi mới **fallback về template** kèm cảnh báo — người dùng luôn nhận được
một báo cáo hợp lệ, không bao giờ nhận lỗi trắng.
"""

from __future__ import annotations

import json
import time
from typing import Any, Callable, Mapping

from .contract import ContentMode, ReportDocument, ReportRequest
from .export import bodygraph_svg
from .llm_client import (
    LLMConfig, LLMError, LLMUsage, Transport, call_llm,
    call_llm_with_usage, display_provider, estimate_cost, parse_llm_json,
)
from .llm_editor import build_llm_brief, merge_llm_draft
from .orchestrator import ReportOrchestrator

LLM_FALLBACK_EDITOR = "template (llm fallback)"

# (config, ok, usage, error, latency_ms) — the Admin API persists one row per attempt.
AttemptCallback = Callable[[LLMConfig, bool, "LLMUsage | None", str, int], None]


def build_request(payload: Mapping[str, Any]) -> ReportRequest:
    """Validate a flat or nested payload into a ``ReportRequest``."""
    return ReportRequest.model_validate(dict(payload))


def _fallback(document: ReportDocument, reason: str) -> ReportDocument:
    fallback = document.model_copy(deep=True)
    fallback.warnings.append(f"Chế độ LLM không khả dụng, dùng nội dung template: {reason}")
    fallback.provenance.editor = LLM_FALLBACK_EDITOR
    return fallback


def _resolve_chain(
    llm_config: LLMConfig | None,
    llm_configs: list[LLMConfig] | tuple[LLMConfig, ...] | None,
) -> list[LLMConfig]:
    """Explicit chain first, legacy single config second, ``HD_LLM_*`` env last."""
    if llm_configs is not None:
        return [c for c in llm_configs if c is not None]
    if llm_config is not None:
        return [llm_config]
    env = LLMConfig.from_env()
    return [env] if env is not None else []


def _run_chain(
    brief: str,
    configs: list[LLMConfig],
    transport: Transport | None,
    on_attempt: AttemptCallback | None,
) -> tuple[dict[str, str], LLMConfig, LLMUsage]:
    """Try each provider in order; return the first success.

    Raises ``LLMError`` listing every provider's error when all fail.
    """
    errors: list[str] = []
    for config in configs:
        started = time.perf_counter()
        try:
            drafts, usage = call_llm_with_usage(brief, config, transport=transport)
        except LLMError as exc:
            latency = int((time.perf_counter() - started) * 1000)
            errors.append(f"{display_provider(config)} ({exc})")
            if on_attempt is not None:
                on_attempt(config, False, None, str(exc)[:500], latency)
            continue
        latency = int((time.perf_counter() - started) * 1000)
        if on_attempt is not None:
            on_attempt(config, True, usage, "", latency)
        return drafts, config, usage
    raise LLMError("; ".join(errors) if errors else "không có nhà cung cấp LLM")


def generate_report(
    request: ReportRequest,
    *,
    llm_config: LLMConfig | None = None,
    llm_configs: list[LLMConfig] | tuple[LLMConfig, ...] | None = None,
    transport: Transport | None = None,
    orchestrator: ReportOrchestrator | None = None,
    on_llm_attempt: AttemptCallback | None = None,
) -> ReportDocument:
    """Produce a finished report in the requested content mode."""
    document = (orchestrator or ReportOrchestrator()).run(request)
    if request.content_mode is not ContentMode.LLM:
        return document
    chain = _resolve_chain(llm_config, llm_configs)
    if not chain:
        return _fallback(document, "chưa cấu hình khóa AI (Cài đặt → AI / LLM hoặc HD_LLM_API_KEY)")
    try:
        drafts, used, usage = _run_chain(build_llm_brief(document), chain, transport, on_llm_attempt)
    except LLMError as exc:
        tried = ", ".join(display_provider(c) for c in chain)
        return _fallback(document, f"đã thử {len(chain)} nhà cung cấp ({tried}) đều lỗi — {exc}")
    merged = merge_llm_draft(document, drafts, editor_model=used.model)
    merged.provenance.llm_provider = display_provider(used)
    merged.provenance.llm_cost_usd = estimate_cost(usage, used.input_price, used.output_price)
    return merged


def apply_draft(
    request: ReportRequest,
    drafts: Mapping[str, str] | str,
    editor_model: str = "",
) -> ReportDocument:
    """Merge a draft produced by an external LLM (e.g. the MCP host itself).

    The chart is recalculated deterministically from the same inputs, so the
    caller does not need to keep document state between brief and merge.
    """
    parsed = parse_llm_json(drafts) if isinstance(drafts, str) else dict(drafts)
    document = ReportOrchestrator().run(request.model_copy(update={"content_mode": ContentMode.LLM}))
    return merge_llm_draft(document, parsed, editor_model=editor_model or "external")


def report_payload(
    document: ReportDocument,
    *,
    include_bodygraph_svg: bool = False,
    bodygraph_path: str | None = None,
) -> dict[str, Any]:
    """Serialize a document for API/MCP responses."""
    payload: dict[str, Any] = {
        "report_id": str(document.report_id),
        "title": document.title,
        "content_mode": document.content_mode.value,
        "editor": document.provenance.editor,
        "tier": document.tier.value,
        "sections": [
            {"id": s.id, "title": s.title, "status": s.status}
            for s in sorted(document.sections, key=lambda item: item.order)
        ],
        "warnings": list(document.warnings),
        "markdown": document.to_markdown(bodygraph_path=bodygraph_path),
    }
    if include_bodygraph_svg:
        payload["bodygraph_svg"] = bodygraph_svg(document)
    return payload


def dumps_payload(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)


__all__ = [
    "LLM_FALLBACK_EDITOR",
    "apply_draft",
    "build_request",
    "generate_report",
    "llm_edit_section",
    "report_payload",
]


def llm_edit_section(
    document: ReportDocument,
    section_id: str,
    *,
    llm_config: LLMConfig | None = None,
    llm_configs: list[LLMConfig] | tuple[LLMConfig, ...] | None = None,
    transport: Transport | None = None,
    on_llm_attempt: AttemptCallback | None = None,
) -> str:
    """Ask the LLM to rewrite one section; returns the proposed markdown (not saved).

    Tries each provider in the fallback chain. Raises ``LLMError`` when AI is
    not configured or every call fails, and ``KeyError`` for an unknown /
    omitted section.
    """
    section = next((s for s in document.sections if s.id == section_id and s.status == "included"), None)
    if section is None:
        raise KeyError(section_id)
    chain = _resolve_chain(llm_config, llm_configs)
    if not chain:
        raise LLMError("chưa cấu hình khóa AI (Cài đặt → AI / LLM hoặc HD_LLM_API_KEY)")
    drafts, _, _ = _run_chain(build_llm_brief(document, section_ids=[section_id]), chain,
                              transport, on_llm_attempt)
    draft = drafts.get(section_id)
    if not draft or not draft.strip():
        raise LLMError("AI không trả về nội dung cho phần này")
    return draft.strip() + "\n"
