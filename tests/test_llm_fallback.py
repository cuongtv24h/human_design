"""LLM fallback chain (primary + 2 backups), token usage and cost tracking."""

from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "tools", ROOT / "mcp"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from test_api_v1 import CLIENT, H, app, login  # noqa: F401,E402  (fixture re-export)

from backend.api.security import encrypt_value  # noqa: E402
from backend.reporting.contract import ReportRequest  # noqa: E402
from backend.reporting.llm_client import LLMConfig, LLMError, LLMUsage, estimate_cost  # noqa: E402
from backend.reporting.service import LLM_FALLBACK_EDITOR, generate_report  # noqa: E402


def _request() -> ReportRequest:
    return ReportRequest.model_validate(
        {"subject": {"birth_date": "1990-05-15", "birth_time": "08:30"}, "content_mode": "llm"})


def _chain(*names: str) -> list[LLMConfig]:
    return [LLMConfig(api_key=f"sk-{name}", name=f"NCC {name}", model=f"m-{name}",
                       input_price=1.0, output_price=2.0) for name in names]


# --- reporting layer: the chain ------------------------------------------------

def test_chain_uses_first_working_provider_and_records_cost(monkeypatch):
    from backend.reporting import service as svc

    def transport(brief, config, transport=None):
        if config.api_key == "sk-mot":
            raise LLMError("LLM HTTP 500: boom")
        return ({"summary": "AI viết lại."}, LLMUsage(prompt_tokens=100, completion_tokens=50))

    monkeypatch.setattr(svc, "call_llm_with_usage", transport)
    attempts = []
    document = generate_report(_request(), llm_configs=_chain("mot", "hai"),
                               on_llm_attempt=lambda *args: attempts.append(args))
    assert document.provenance.editor == "llm:m-hai"
    assert document.provenance.llm_provider == "NCC hai · m-hai"
    assert document.provenance.llm_cost_usd == pytest.approx((100 * 1.0 + 50 * 2.0) / 1_000_000)
    assert [ok for (_, ok, _, _, _) in attempts] == [False, True]


def test_chain_falls_back_to_template_only_when_everything_fails(monkeypatch):
    from backend.reporting import service as svc

    def broken(brief, config, transport=None):
        raise LLMError("timeout")

    monkeypatch.setattr(svc, "call_llm_with_usage", broken)
    document = generate_report(_request(), llm_configs=_chain("mot", "hai"))
    assert document.provenance.editor == LLM_FALLBACK_EDITOR
    assert document.provenance.llm_provider == ""
    warning = " ".join(document.warnings)
    assert "NCC mot" in warning and "NCC hai" in warning and "timeout" in warning


def test_usage_parsing_and_cost_math():
    assert LLMUsage.from_response({}).total_tokens == 0
    assert LLMUsage.from_response({"usage": {"prompt_tokens": 5}}).completion_tokens == 0
    assert estimate_cost(LLMUsage(10, 10), 0.0, 0.0) is None  # unknown price
    assert estimate_cost(LLMUsage(1_000_000, 500_000), 2.0, 4.0) == pytest.approx(4.0)


# --- API layer ----------------------------------------------------------------

def _save_chain(admin, second_enabled=True):
    return admin.put("/api/v1/settings/llm", json={"providers": [
        {"name": "Chính", "base_url": "https://one.test/v1", "model": "m1", "temperature": 0.6,
         "timeout": 60, "enabled": True, "input_price": 1.0, "output_price": 2.0, "api_key": "sk-first"},
        {"name": "Dự phòng", "base_url": "https://two.test/v1", "model": "m2", "temperature": 0.6,
         "timeout": 60, "enabled": second_enabled, "input_price": 1.0, "output_price": 2.0,
         "api_key": "sk-second"},
    ]}, headers=H)


def test_catalog_shows_chain_and_skips_disabled(app):
    admin = login(app)
    assert admin.get("/api/v1/catalog").json()["llm_providers"] == []
    _save_chain(admin, second_enabled=False)
    catalog = admin.get("/api/v1/catalog").json()
    assert catalog["llm_available"] is True
    assert catalog["llm_providers"] == [{"name": "Chính", "model": "m1"}]


def test_report_falls_through_and_logs_usage_with_cost(app, monkeypatch):
    from backend.reporting import service as svc

    monkeypatch.delenv("HD_LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    admin = login(app)
    assert _save_chain(admin).status_code == 200

    def transport(brief, config, transport=None):
        if config.api_key == "sk-first":
            raise LLMError("LLM HTTP 500: boom")
        return ({"summary": "AI viết lại, vẫn nhắc Projector và các sự kiện kỹ thuật."},
                LLMUsage(prompt_tokens=10_000, completion_tokens=2_000))

    monkeypatch.setattr(svc, "call_llm_with_usage", transport)
    person = admin.post("/api/v1/clients", json=CLIENT, headers=H).json()
    created = admin.post("/api/v1/reports", json={"client_id": person["id"], "content_mode": "llm"},
                         headers=H).json()
    detail = admin.get(f"/api/v1/reports/{created['id']}").json()
    assert detail["status"] == "ready"
    assert detail["llm_provider"] == "Dự phòng · m2"
    assert detail["llm_cost_usd"] == pytest.approx((10_000 * 1.0 + 2_000 * 2.0) / 1_000_000)

    stats = admin.get("/api/v1/settings/llm/usage?days=30").json()
    assert stats["totals"]["requests"] == 2 and stats["totals"]["errors"] == 1
    assert stats["totals"]["prompt_tokens"] == 10_000
    assert stats["totals"]["cost_usd"] == pytest.approx(0.014)
    assert {p["provider"] for p in stats["by_provider"]} == {"Chính · m1", "Dự phòng · m2"}
    assert len(stats["recent"]) == 2


def test_legacy_flat_settings_still_work_as_single_provider(app, monkeypatch):
    from backend.api.models import Organization

    monkeypatch.delenv("HD_LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with app.state.db.session_factory() as db:
        org = db.get(Organization, 1)
        org.llm_settings = {"base_url": "https://old.test/v1", "model": "legacy-m", "temperature": 0.5,
                            "timeout": 60, "api_key_enc": encrypt_value("test-secret", "sk-legacy")}
        db.commit()
    catalog = login(app).get("/api/v1/catalog").json()
    assert catalog["llm_available"] is True
    assert catalog["llm_providers"] == [{"name": "Chính", "model": "legacy-m"}]
