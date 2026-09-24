"""Chat assistant: strict scope, tools, sessions, cost log, admin stats."""

from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "tools", ROOT / "mcp"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from test_api_sharing import _coach  # noqa: F401,E402
from test_api_v1 import H, app, login  # noqa: F401,E402

from backend.reporting.assistant import ASSISTANT_SYSTEM, TOOL_NAMES, parse_agent_step  # noqa: E402


def _provider(i=0, **overrides):
    body = {"name": "Chính", "base_url": "https://llm.example/v1", "model": "m1", "temperature": 0.6,
            "timeout": 60, "enabled": True, "input_price": 1.0, "output_price": 2.0,
            "api_key": "sk-chat-test"}
    body.update(overrides)
    return body


def _scripted_transport(script):
    """Fake chat transport: pop one reply per call, record payloads."""
    calls = []

    def transport(url, headers, payload, timeout):
        calls.append(payload)
        content, usage = script[min(len(calls) - 1, len(script) - 1)]
        return {"choices": [{"message": {"content": content}}], "usage": usage}

    transport.calls = calls
    return transport


def _answer(text, prompt=100, completion=20):
    return json.dumps({"answer": text}, ensure_ascii=False), {"prompt_tokens": prompt, "completion_tokens": completion}


# --- agent core ----------------------------------------------------------------

def test_system_prompt_is_strict():
    for phrase in ("CHỈ trả lời", "Human Design", "TỪ CHỐI", "KHÔNG đoán", "không bịa",
                   "không thay thế tư vấn y tế", "search_knowledge", "calculate_chart",
                   "TRẢ LỜI LUÔN", "càng ít càng tốt"):
        assert phrase in ASSISTANT_SYSTEM
    assert len(TOOL_NAMES) == 7


def test_parse_agent_step():
    assert parse_agent_step('{"answer": "Xin chào"}') == ("answer", "Xin chào")
    kind, (name, args) = parse_agent_step('```json\n{"tool": "read_skill", "args": {"name": "23"}}\n```')
    assert (kind, name, args) == ("tool", "read_skill", {"name": "23"})
    with pytest.raises(ValueError):
        parse_agent_step("không có json")


def test_search_knowledge_ranks_theory_first():
    from backend.api.assistant_tools import search_knowledge

    text, sources = search_knowledge("Generator chiến lược chờ đáp ứng")
    assert "5 LOẠI NĂNG LƯỢNG" in sources and "Wait to Respond" in text
    _, empty = search_knowledge("zxqv wjbk")
    assert empty == ""


def test_read_skill_fuzzy_and_chart_tool():
    from backend.api.assistant_tools import calculate_chart, read_skill

    assert "SKILL 23" in read_skill("23")[1]
    assert read_skill("không-tồn-tại-xyz")[1] == ""
    summary, source = calculate_chart("1990-05-15", "08:30", "+07:00")
    assert "Type:" in summary and "Swiss Ephemeris" in source
    bad, _ = calculate_chart("15/05/1990", "08:30", "+07:00")
    assert "chưa đúng" in bad


# --- API -----------------------------------------------------------------------

def test_models_and_chat_need_ai_configured(app, monkeypatch):
    monkeypatch.delenv("HD_LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    admin = login(app)
    assert admin.get("/api/v1/assistant/models").json() == []
    response = admin.post("/api/v1/assistant/chat", json={"message": "Generator là gì?"}, headers=H)
    assert response.status_code == 503


def test_chat_turn_uses_tools_logs_cost_and_keeps_session(app):
    admin = login(app)
    assert admin.put("/api/v1/settings/llm", json={"providers": [_provider()]}, headers=H).status_code == 200
    app.state.llm_transport = _scripted_transport([
        (json.dumps({"tool": "search_knowledge", "args": {"query": "Generator"}}),
         {"prompt_tokens": 100, "completion_tokens": 20}),
        _answer("Generator chờ để đáp ứng.", prompt=200, completion=30),
    ])
    first = admin.post("/api/v1/assistant/chat", json={"message": "Generator là gì?"}, headers=H)
    assert first.status_code == 200, first.text
    body = first.json()
    assert body["message"]["content"] == "Generator chờ để đáp ứng."
    assert body["message"]["tools_used"] == ["search_knowledge"]
    assert len(body["message"]["sources"]) >= 1  # doc titles cited from the tool result
    assert body["message"]["cost_usd"] == pytest.approx((300 * 1.0 + 50 * 2.0) / 1_000_000)
    assert body["session"]["message_count"] == 2
    assert (body["provider"], body["model"]) == ("Chính", "m1")

    # Follow-up continues the same session; bad model index is rejected.
    second = admin.post("/api/v1/assistant/chat",
                        json={"session_id": body["session"]["id"], "message": "Còn Manifestor?"}, headers=H)
    assert second.json()["session"]["message_count"] == 4
    bad_model = admin.post("/api/v1/assistant/chat", json={"message": "x", "model_index": 5}, headers=H)
    assert bad_model.status_code == 422

    # Every LLM attempt is logged for cost stats.
    stats = admin.get("/api/v1/settings/llm/usage?days=1").json()
    assert stats["totals"]["requests"] == 3  # tool call + 2 answers
    assert all(r["purpose"] == "chat" for r in stats["recent"])
    detail = admin.get(f"/api/v1/assistant/sessions/{body['session']['id']}").json()
    assert [m["role"] for m in detail["messages"]] == ["user", "assistant", "user", "assistant"]


def test_chat_permission_delete_and_rate_limit(app, monkeypatch):
    import backend.api.routers.assistant as router

    admin = login(app)
    admin.put("/api/v1/settings/llm", json={"providers": [_provider(api_key="sk-x")]}, headers=H)
    app.state.llm_transport = _scripted_transport([_answer("OK")])
    coach_a, coach_b = _coach(app, "a@example.com"), _coach(app, "b@example.com")
    sid = coach_a.post("/api/v1/assistant/chat", json={"message": "Type là gì?"}, headers=H).json()["session"]["id"]
    assert coach_b.get(f"/api/v1/assistant/sessions/{sid}").status_code == 404
    assert admin.get(f"/api/v1/assistant/sessions/{sid}").status_code == 200  # admin may audit
    assert coach_a.delete(f"/api/v1/assistant/sessions/{sid}", headers=H).status_code == 204
    assert coach_a.get(f"/api/v1/assistant/sessions/{sid}").status_code == 404

    monkeypatch.setattr(router, "CHAT_HOURLY_LIMIT", 1)
    coach_b.post("/api/v1/assistant/chat", json={"message": "một"}, headers=H)
    limited = coach_b.post("/api/v1/assistant/chat", json={"message": "hai"}, headers=H)
    assert limited.status_code == 429


def test_admin_stats_and_guard(app):
    admin = login(app)
    admin.put("/api/v1/settings/llm", json={"providers": [_provider(api_key="sk-x")]}, headers=H)
    app.state.llm_transport = _scripted_transport([_answer("OK", prompt=10, completion=5)])
    admin.post("/api/v1/assistant/chat", json={"message": "Chào"}, headers=H)
    coach = _coach(app)
    assert coach.get("/api/v1/assistant/admin/stats").status_code == 403
    assert coach.get("/api/v1/assistant/admin/sessions").status_code == 403
    stats = admin.get("/api/v1/assistant/admin/stats?days=7").json()
    assert stats["sessions"] == 1 and stats["messages"] == 1
    assert stats["by_user"][0]["email"] == "admin@example.com"
    sessions = admin.get("/api/v1/assistant/admin/sessions").json()
    assert sessions[0]["user_email"] == "admin@example.com"


# --- streaming / context / rating (v2) ------------------------------------------

def _parse_sse(text):
    events = []
    for block in text.split("\n\n"):
        name, data = None, None
        for line in block.splitlines():
            if line.startswith("event:"):
                name = line[6:].strip()
            elif line.startswith("data:"):
                data = json.loads(line[5:].strip())
        if name is not None:
            events.append((name, data))
    return events


def test_answer_detector_handles_escapes_and_odd_chunks():
    from backend.reporting.assistant import _AnswerDetector

    text = 'Dòng 1\n"Dòng 2" café \U0001f600 cuối'
    raw = json.dumps({"answer": text}, ensure_ascii=False)
    for size in (1, 2, 3, 5, 7, 13, 24):
        detector = _AnswerDetector()
        out = "".join(detector.feed(raw[i:i + size]) for i in range(0, len(raw), size))
        assert detector.completed and out == text, f"chunk={size}"
    tool_mode = _AnswerDetector()
    assert tool_mode.feed('{"tool": "search_knowledge", "args": {}}') == ""
    assert not tool_mode.completed


def test_agent_turn_events_stream_tokens_and_tools():
    from backend.reporting.assistant import agent_turn_events
    from backend.reporting.llm_client import LLMConfig

    script = _scripted_transport([
        (json.dumps({"tool": "search_knowledge", "args": {"query": "x"}}),
         {"prompt_tokens": 10, "completion_tokens": 5}),
        _answer("Chào bạn nhé!", prompt=10, completion=5),
    ])
    config = LLMConfig(api_key="k", base_url="https://llm.example/v1", model="m")
    events = list(agent_turn_events("hi", [], [config], lambda n, a: ("kết quả", "Nguồn X"),
                                    transport=script))
    kinds = [kind for kind, _ in events]
    assert kinds[0] == "tool_start" and kinds[1] == "tool_done"
    assert events[1][1] == {"tool": "search_knowledge", "source": "Nguồn X"}
    assert "".join(p for k, p in events if k == "token") == "Chào bạn nhé!"
    assert events[-1][0] == "result" and events[-1][1].answer == "Chào bạn nhé!"


def test_chat_stream_endpoint_emits_sse(app):
    admin = login(app)
    admin.put("/api/v1/settings/llm", json={"providers": [_provider(api_key="sk-sse")]}, headers=H)
    app.state.llm_transport = _scripted_transport([_answer("Xin chào!", prompt=10, completion=5)])
    response = admin.post("/api/v1/assistant/chat/stream", json={"message": "Chào"}, headers=H)
    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("text/event-stream")
    events = _parse_sse(response.text)
    assert events[0][0] == "meta" and events[0][1]["session_id"]
    assert "".join(p["text"] for k, p in events if k == "token") == "Xin chào!"
    done = [p for k, p in events if k == "done"][0]["message"]
    assert done["content"] == "Xin chào!" and done["cost_usd"] is not None
    detail = admin.get(f"/api/v1/assistant/sessions/{events[0][1]['session_id']}").json()
    assert [m["role"] for m in detail["messages"]] == ["user", "assistant"]


def test_chat_context_sent_to_llm_but_not_stored(app):
    admin = login(app)
    admin.put("/api/v1/settings/llm", json={"providers": [_provider(api_key="sk-ctx")]}, headers=H)
    transport = _scripted_transport([_answer("OK")])
    app.state.llm_transport = transport
    body = admin.post("/api/v1/assistant/chat",
                      json={"message": "Điểm mạnh là gì?", "context_client_id": 7,
                            "context_report_id": "rep-1"}, headers=H).json()
    sent = transport.calls[0]["messages"][-1]["content"]
    assert "[Ngữ cảnh" in sent and "#7" in sent and "rep-1" in sent
    detail = admin.get(f"/api/v1/assistant/sessions/{body['session']['id']}").json()
    assert detail["messages"][0]["content"] == "Điểm mạnh là gì?"


def test_rate_message_and_admin_stats(app):
    admin = login(app)
    admin.put("/api/v1/settings/llm", json={"providers": [_provider(api_key="sk-rate")]}, headers=H)
    app.state.llm_transport = _scripted_transport([_answer("OK")])
    body = admin.post("/api/v1/assistant/chat", json={"message": "Chào"}, headers=H).json()
    mid = body["message"]["id"]
    assert body["message"]["rating"] is None
    url = f"/api/v1/assistant/messages/{mid}/rate"

    assert admin.post(url, json={"rating": 1}, headers=H).json()["rating"] == 1
    stats = admin.get("/api/v1/assistant/admin/stats?days=7").json()
    assert (stats["likes"], stats["dislikes"]) == (1, 0)
    assert admin.post(url, json={"rating": -1}, headers=H).json()["rating"] == -1
    stats = admin.get("/api/v1/assistant/admin/stats?days=7").json()
    assert (stats["likes"], stats["dislikes"]) == (0, 1)
    assert admin.post(url, json={"rating": 0}, headers=H).json()["rating"] is None

    coach = _coach(app)  # cannot rate someone else's answer
    assert coach.post(url, json={"rating": 1}, headers=H).status_code == 404
