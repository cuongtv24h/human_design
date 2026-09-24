"""Service entry point cho mọi "cửa" (MCP, REST, Admin): một hàm tạo báo cáo.

``generate_report`` chạy orchestrator, và nếu ``content_mode="llm"`` thì
build brief → gọi LLM → merge + validate. Mọi lỗi LLM (thiếu key, mạng, JSON
hỏng) đều **fallback về template** kèm cảnh báo — người dùng luôn nhận được
một báo cáo hợp lệ, không bao giờ nhận lỗi trắng.
"""

from __future__ import annotations

import json
from typing import Any, Mapping

from .contract import ContentMode, ReportDocument, ReportRequest
from .export import bodygraph_svg
from .llm_client import LLMConfig, LLMError, Transport, call_llm, parse_llm_json
from .llm_editor import build_llm_brief, merge_llm_draft
from .orchestrator import ReportOrchestrator

LLM_FALLBACK_EDITOR = "template (llm fallback)"


def build_request(payload: Mapping[str, Any]) -> ReportRequest:
    """Validate a flat or nested payload into a ``ReportRequest``."""
    return ReportRequest.model_validate(dict(payload))


def _fallback(document: ReportDocument, reason: str) -> ReportDocument:
    fallback = document.model_copy(deep=True)
    fallback.warnings.append(f"Chế độ LLM không khả dụng, dùng nội dung template: {reason}")
    fallback.provenance.editor = LLM_FALLBACK_EDITOR
    return fallback


def generate_report(
    request: ReportRequest,
    *,
    llm_config: LLMConfig | None = None,
    transport: Transport | None = None,
    orchestrator: ReportOrchestrator | None = None,
) -> ReportDocument:
    """Produce a finished report in the requested content mode."""
    document = (orchestrator or ReportOrchestrator()).run(request)
    if request.content_mode is not ContentMode.LLM:
        return document
    config = llm_config or LLMConfig.from_env()
    if config is None:
        return _fallback(document, "chưa cấu hình HD_LLM_API_KEY")
    try:
        drafts = call_llm(build_llm_brief(document), config, transport=transport)
    except LLMError as exc:
        return _fallback(document, str(exc))
    return merge_llm_draft(document, drafts, editor_model=config.model)


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
    transport: Transport | None = None,
) -> str:
    """Ask the LLM to rewrite one section; returns the proposed markdown (not saved).

    Raises ``LLMError`` when AI is not configured or the call fails, and
    ``KeyError`` for an unknown / omitted section.
    """
    section = next((s for s in document.sections if s.id == section_id and s.status == "included"), None)
    if section is None:
        raise KeyError(section_id)
    config = llm_config or LLMConfig.from_env()
    if config is None:
        raise LLMError("chưa cấu hình HD_LLM_API_KEY")
    drafts = call_llm(build_llm_brief(document, section_ids=[section_id]), config, transport=transport)
    draft = drafts.get(section_id)
    if not draft or not draft.strip():
        raise LLMError("AI không trả về nội dung cho phần này")
    return draft.strip() + "\n"
