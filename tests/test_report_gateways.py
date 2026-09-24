"""Report layer exposed through MCP/REST, and the real LLM mode (fake transport)."""

from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "tools", ROOT / "mcp"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from backend.reporting.contract import ReportRequest  # noqa: E402
from backend.reporting.llm_client import LLMConfig, LLMError, call_llm, parse_llm_json  # noqa: E402
from backend.reporting.orchestrator import ReportOrchestrator  # noqa: E402
from backend.reporting.service import LLM_FALLBACK_EDITOR, apply_draft, generate_report  # noqa: E402

SUBJECT = {
    "name": "Khách thử",
    "birth_date": "1990-05-15",
    "birth_time": "08:30",
    "timezone": "+07:00",
    "birth_location": "Hòa Bình",
}
CONFIG = LLMConfig(api_key="test-key", base_url="https://llm.example/v1", model="fake-model")


def _request(**extra) -> ReportRequest:
    return ReportRequest.model_validate({"subject": SUBJECT, **extra})


def _echo_transport(suffix: str):
    """Fake LLM: returns every template section plus an empathetic closing line."""
    calls: list[dict] = []

    def transport(url, headers, payload, timeout):
        calls.append({"url": url, "headers": dict(headers), "payload": payload})
        document = ReportOrchestrator().run(_request())
        drafts = {s.id: s.content_markdown.rstrip() + suffix for s in document.sections if s.status == "included"}
        return {"choices": [{"message": {"content": "```json\n" + json.dumps(drafts, ensure_ascii=False) + "\n```"}}]}

    return transport, calls


# --- LLM client -------------------------------------------------------------

def test_config_from_env_requires_key_and_reads_overrides():
    assert LLMConfig.from_env({}) is None
    config = LLMConfig.from_env({"HD_LLM_API_KEY": "k", "HD_LLM_BASE_URL": "https://x/v1/", "HD_LLM_MODEL": "m"})
    assert (config.api_key, config.base_url, config.model) == ("k", "https://x/v1", "m")
    assert LLMConfig.from_env({"OPENAI_API_KEY": "k2"}).api_key == "k2"


def test_parse_llm_json_accepts_fenced_and_prose_wrapped_json():
    assert parse_llm_json('{"summary": "A"}') == {"summary": "A"}
    assert parse_llm_json('Đây:\n```json\n{"summary": "B"}\n```') == {"summary": "B"}
    assert parse_llm_json('Kết quả {"summary": "C"} xong') == {"summary": "C"}
    with pytest.raises(LLMError):
        parse_llm_json("không có json")


def test_call_llm_sends_openai_compatible_request():
    transport, calls = _echo_transport(" ♥")
    drafts = call_llm("BRIEF", CONFIG, transport=transport)
    assert "summary" in drafts
    call = calls[0]
    assert call["url"] == "https://llm.example/v1/chat/completions"
    assert call["headers"]["Authorization"] == "Bearer test-key"
    assert call["payload"]["model"] == "fake-model"
    assert call["payload"]["messages"][-1] == {"role": "user", "content": "BRIEF"}


# --- Service ----------------------------------------------------------------

def test_generate_report_llm_mode_merges_edited_sections():
    transport, calls = _echo_transport("\n\nBạn xứng đáng được sống đúng mình.")
    document = generate_report(_request(content_mode="llm"), llm_config=CONFIG, transport=transport)
    assert calls, "LLM must be called in llm mode"
    assert "chuyên gia Human Design" in calls[0]["payload"]["messages"][-1]["content"]
    assert document.provenance.editor == "llm:fake-model"
    assert not document.warnings
    assert all(s.content_markdown.endswith("sống đúng mình.") for s in document.sections if s.status == "included")


def test_generate_report_template_mode_never_calls_llm():
    transport, calls = _echo_transport("x")
    document = generate_report(_request(), llm_config=CONFIG, transport=transport)
    assert not calls
    assert document.provenance.editor == "template"


def test_generate_report_falls_back_without_key(monkeypatch):
    monkeypatch.delenv("HD_LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    document = generate_report(_request(content_mode="llm"))
    assert document.provenance.editor == LLM_FALLBACK_EDITOR
    assert any("HD_LLM_API_KEY" in w for w in document.warnings)
    assert document.sections  # still a full template report


def test_generate_report_falls_back_on_llm_error():
    def broken(url, headers, payload, timeout):
        raise LLMError("LLM HTTP 500")

    document = generate_report(_request(content_mode="llm"), llm_config=CONFIG, transport=broken)
    assert document.provenance.editor == LLM_FALLBACK_EDITOR
    assert any("LLM HTTP 500" in w for w in document.warnings)


def test_apply_draft_accepts_json_string_and_flags_lost_facts():
    document = apply_draft(_request(), '{"summary": "Một đoạn văn không còn số liệu."}', editor_model="host")
    assert document.provenance.editor == "llm:host"
    assert any("summary" in w for w in document.warnings)


# --- MCP tools --------------------------------------------------------------

def test_mcp_report_tools_roundtrip(tmp_path, monkeypatch):
    import server

    monkeypatch.setattr(server, "REPORT_OUTPUT_DIR", str(tmp_path))
    args = dict(birth_date="1990-05-15", birth_time="08:30", name="Khách thử", birth_location="Hòa Bình")

    result = server.generate_hd_report(**args, tier="deep_core")
    assert "error" not in result, result
    assert result["content_mode"] == "template"
    assert "![BodyGraph](" in result["markdown"]
    assert pathlib.Path(result["files"]["bodygraph_svg"]).exists()

    brief = server.build_hd_report_brief(**args)
    assert "summary" in brief["section_ids"]
    assert "Vai trò" in brief["brief"]

    edited = server.generate_hd_report(**args, save_files=False)
    drafts = {"summary": edited["markdown"].split("## ", 2)[1].split("\n", 1)[1] + "\nMột lời động viên."}
    applied = server.apply_hd_report_draft(**args, drafts_json=json.dumps(drafts, ensure_ascii=False))
    assert "error" not in applied, applied
    assert applied["editor"].startswith("llm")
    assert "Một lời động viên." in applied["markdown"]


# --- REST routes ------------------------------------------------------------

def test_rest_report_routes():
    from fastapi.testclient import TestClient

    import openapi_server

    client = TestClient(openapi_server.app)
    body = {"subject": SUBJECT, "tier": "deep_core"}

    generated = client.post("/reports/generate?include_bodygraph_svg=true", json=body)
    assert generated.status_code == 200, generated.text
    data = generated.json()
    assert data["editor"] == "template"
    assert "<svg" in data["bodygraph_svg"]
    assert "Ngày sinh: 1990-05-15" in data["markdown"]

    brief = client.post("/reports/llm-brief", json=body)
    assert brief.status_code == 200 and "channels_gates" in brief.json()["section_ids"]

    svg = client.post("/reports/bodygraph.svg", json=body)
    assert svg.status_code == 200 and svg.headers["content-type"].startswith("image/svg+xml")

    applied = client.post("/reports/apply-draft", json={"request": body, "drafts": {"nope": "x"}})
    assert applied.status_code == 200
    assert any("nope" in w for w in applied.json()["warnings"])

    invalid = client.post("/reports/generate", json={"subject": {**SUBJECT, "birth_date": "15/05/1990"}})
    assert invalid.status_code == 422
