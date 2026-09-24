"""Restart recovery for background report generation — plan option (a), no Redis/arq.

LLM-mode reports are generated in a background task inside ``hd-api``. If the process is
restarted (deploy, crash, pm2 memory limit) the task is lost and the report would stay
"Đang tạo" forever. Each API worker therefore runs a small sweeper — at startup and then
every minute — that finds ``generating`` reports whose heartbeat stopped and:

- resumes them (up to ``job_max_attempts`` attempts in total), or
- marks them ``failed`` with a clear Vietnamese message so the coach can press "Tạo lại".

Claims are atomic (UPDATE … WHERE heartbeat = <value we saw>), so with ``--workers 2``
exactly one worker resumes a given report.
"""

from __future__ import annotations

import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from sqlalchemy import select, update
from sqlalchemy.orm import sessionmaker

from .models import Report
from .services import audit, org_llm_config, run_llm_generation

log = logging.getLogger("hd.jobs")

Submit = Callable[..., Any]


def failed_message(attempts: int) -> str:
    return (f"Máy chủ khởi động lại trong lúc tạo báo cáo và đã thử {attempts} lần chưa thành công. "
            "Bấm “Tạo lại với cùng tùy chọn” để thử lại.")


def _aware(value: datetime | None) -> datetime | None:
    return value if value is None or value.tzinfo else value.replace(tzinfo=timezone.utc)


def recover_stale_reports(session_factory: sessionmaker, *, secret_key: str, artifact_dir: str | None,
                          submit: Submit, stale_seconds: float = 90.0, max_attempts: int = 3,
                          heartbeat_seconds: float = 15.0, now: datetime | None = None) -> dict[str, str]:
    """One sweep. Returns ``{report_id: "resumed" | "failed"}`` for the reports this worker claimed."""
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=stale_seconds)
    with session_factory() as db:
        rows = db.execute(select(Report.id, Report.org_id, Report.version, Report.generation_attempts,
                                 Report.job_heartbeat_at, Report.updated_at)
                          .where(Report.status == "generating")).all()
    results: dict[str, str] = {}
    for row in rows:
        last_seen = _aware(row.job_heartbeat_at) or _aware(row.updated_at)
        if last_seen is not None and last_seen > cutoff:
            continue  # alive (or just queued)
        seen = (Report.job_heartbeat_at.is_(None) if row.job_heartbeat_at is None
                else Report.job_heartbeat_at == row.job_heartbeat_at)
        attempts = row.generation_attempts or 0
        with session_factory() as db:
            claim = update(Report).where(Report.id == row.id, Report.status == "generating", seen)
            if attempts >= max_attempts:
                done = db.execute(claim.values(status="failed", error=failed_message(attempts),
                                               job_heartbeat_at=None))
                if done.rowcount == 1:
                    audit(db, None, "report.recover_failed", "report", row.id, org_id=row.org_id, attempts=attempts)
                    results[row.id] = "failed"
                db.commit()
                continue
            done = db.execute(claim.values(job_heartbeat_at=now, generation_attempts=attempts + 1))
            if done.rowcount != 1:
                db.rollback()
                continue  # another worker got it first
            audit(db, None, "report.recover", "report", row.id, org_id=row.org_id, attempt=attempts + 1)
            db.commit()
            config = org_llm_config(db, row.org_id, secret_key)
        log.warning("resuming stale report %s (attempt %s)", row.id, attempts + 1)
        submit(run_llm_generation, session_factory, row.id, "system:recovery", artifact_dir,
               "regenerate" if row.version else "generate", config, heartbeat_seconds, True)
        results[row.id] = "resumed"
    return results


class RecoverySweeper:
    """Daemon thread: sweep at startup, then every ``job_sweep_seconds``, on a small thread pool."""

    def __init__(self, session_factory: sessionmaker, settings: Any, secret_key: str) -> None:
        self._factory, self._settings, self._secret = session_factory, settings, secret_key
        self._stop = threading.Event()
        self._pool = ThreadPoolExecutor(max_workers=max(1, settings.job_workers), thread_name_prefix="hd-job")
        self._thread = threading.Thread(target=self._loop, name="hd-recovery", daemon=True)

    def _loop(self) -> None:
        while True:
            try:
                found = recover_stale_reports(
                    self._factory, secret_key=self._secret, artifact_dir=self._settings.artifact_dir,
                    submit=self._pool.submit, stale_seconds=self._settings.job_stale_seconds,
                    max_attempts=self._settings.job_max_attempts,
                    heartbeat_seconds=self._settings.job_heartbeat_seconds)
                if found:
                    log.warning("recovery sweep: %s", found)
            except Exception:  # noqa: BLE001 - never kill the sweeper
                log.exception("recovery sweep failed")
            if self._stop.wait(self._settings.job_sweep_seconds):
                return

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._pool.shutdown(wait=False, cancel_futures=True)
