"""Restart recovery for background generation (plan option (a): heartbeat + startup sweep)."""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from test_api_v1 import CLIENT, H, PASSWORD, app, login  # noqa: F401  (fixture re-export)

from backend.api import services
from backend.api.jobs import recover_stale_reports
from backend.api.models import AuditLog, Report, ReportRevision


def _llm_report(app, monkeypatch) -> str:
    monkeypatch.delenv("HD_LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = login(app)
    person = client.post("/api/v1/clients", json=CLIENT, headers=H).json()
    return client.post("/api/v1/reports", json={"client_id": person["id"], "tier": "free_basic", "template": "sections",
                                                "content_mode": "llm"}, headers=H).json()["id"]


def _make_stale(app, rid: str, attempts: int = 1, heartbeat_age: float | None = None) -> None:
    """Simulate a process that died mid-generation."""
    with app.state.db.session_factory() as db:
        report = db.get(Report, rid)
        report.status = "generating"
        report.generation_attempts = attempts
        old = datetime.now(timezone.utc) - timedelta(minutes=10)
        report.job_heartbeat_at = None if heartbeat_age is None else datetime.now(timezone.utc) - timedelta(seconds=heartbeat_age)
        db.commit()
        db.query(Report).filter(Report.id == rid).update({"updated_at": old})
        db.commit()


def _sweep(app, **kwargs):
    calls = []

    def submit(fn, *args):
        calls.append(args)
        fn(*args)

    result = recover_stale_reports(app.state.db.session_factory, secret_key=app.state.secret_key,
                                   artifact_dir=None, submit=submit, heartbeat_seconds=0.05, **kwargs)
    return result, calls


def test_stale_report_is_resumed(app, monkeypatch):
    rid = _llm_report(app, monkeypatch)
    _make_stale(app, rid, attempts=1)
    result, calls = _sweep(app)
    assert result == {rid: "resumed"} and len(calls) == 1
    with app.state.db.session_factory() as db:
        report = db.get(Report, rid)
        assert report.status == "ready" and report.generation_attempts == 2 and report.job_heartbeat_at is None
        latest = db.query(ReportRevision).filter_by(report_id=rid).order_by(ReportRevision.version.desc()).first()
        assert latest.author == "system:recovery" and latest.change_type == "regenerate"
        assert db.query(AuditLog).filter_by(action="report.recover", entity_id=rid).count() == 1
    assert _sweep(app)[0] == {}  # nothing left


def test_live_job_is_not_touched(app, monkeypatch):
    rid = _llm_report(app, monkeypatch)
    _make_stale(app, rid, attempts=1, heartbeat_age=10)  # beat 10 s ago: still running elsewhere
    assert _sweep(app, stale_seconds=90)[0] == {}
    with app.state.db.session_factory() as db:
        assert db.get(Report, rid).status == "generating"


def test_gives_up_after_max_attempts(app, monkeypatch):
    rid = _llm_report(app, monkeypatch)
    _make_stale(app, rid, attempts=3, heartbeat_age=600)
    result, calls = _sweep(app, max_attempts=3)
    assert result == {rid: "failed"} and calls == []
    detail = login(app).get(f"/api/v1/reports/{rid}").json()
    assert detail["status"] == "failed" and "Tạo lại" in detail["error"]
    # "Tạo lại" resets the counter and works again.
    client = login(app)
    assert client.post(f"/api/v1/reports/{rid}/regenerate", json={}, headers=H).json()["status"] == "generating"
    assert client.get(f"/api/v1/reports/{rid}").json()["status"] == "ready"  # background task ran
    with app.state.db.session_factory() as db:
        assert db.get(Report, rid).generation_attempts == 1


def test_only_one_claim_per_stale_state(app, monkeypatch):
    rid = _llm_report(app, monkeypatch)
    _make_stale(app, rid, attempts=1)
    parked = []
    first = recover_stale_reports(app.state.db.session_factory, secret_key="x", artifact_dir=None,
                                  submit=lambda fn, *a: parked.append(a))
    second = recover_stale_reports(app.state.db.session_factory, secret_key="x", artifact_dir=None,
                                   submit=lambda fn, *a: parked.append(a))
    assert first == {rid: "resumed"} and second == {} and len(parked) == 1  # claim refreshed the heartbeat


def test_heartbeat_refreshes_while_generating(app, monkeypatch):
    rid = _llm_report(app, monkeypatch)
    _make_stale(app, rid, attempts=0)
    beats = []
    real = services.generate_report

    def slow(request, **kwargs):
        for _ in range(2):
            with app.state.db.session_factory() as db:
                beats.append(db.get(Report, rid).job_heartbeat_at)
            time.sleep(0.25)
        return real(request, **kwargs)

    monkeypatch.setattr(services, "generate_report", slow)
    services.run_llm_generation(app.state.db.session_factory, rid, "t", heartbeat_seconds=0.05)
    assert beats[0] is not None and beats[1] > beats[0]
    with app.state.db.session_factory() as db:
        assert db.get(Report, rid).status == "ready" and db.get(Report, rid).generation_attempts == 1


def test_startup_sweep_runs_in_lifespan(app, monkeypatch):
    rid = _llm_report(app, monkeypatch)
    _make_stale(app, rid, attempts=1)
    with TestClient(app):  # startup → sweeper thread
        deadline = time.time() + 10
        while time.time() < deadline:
            with app.state.db.session_factory() as db:
                if db.get(Report, rid).status == "ready":
                    break
            time.sleep(0.1)
    with app.state.db.session_factory() as db:
        assert db.get(Report, rid).status == "ready"
