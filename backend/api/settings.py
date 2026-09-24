"""Runtime settings read from environment variables (and an optional ``.env``).

No extra dependency: a tiny ``.env`` loader fills variables that are not already
set in the process environment (pm2/systemd values always win).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_dotenv(path: Path | None = None) -> None:
    env_path = path or Path(os.environ.get("HD_ENV_FILE", ROOT / ".env"))
    if not env_path.is_file():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)


def _bool(value: str | None, default: bool) -> bool:
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    database_url: str = f"sqlite:///{ROOT / 'var' / 'hd_dev.sqlite3'}"
    cors_origins: tuple[str, ...] = field(default_factory=tuple)
    cookie_secure: bool = False
    session_hours: int = 12
    auto_create_tables: bool = True
    environment: str = "development"

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        origins = tuple(o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip())
        environment = os.environ.get("HD_ENV", "development")
        return cls(
            database_url=os.environ.get("DATABASE_URL") or cls.database_url,
            cors_origins=origins,
            cookie_secure=_bool(os.environ.get("COOKIE_SECURE"), environment == "production"),
            session_hours=int(os.environ.get("SESSION_HOURS") or cls.session_hours),
            auto_create_tables=_bool(os.environ.get("AUTO_CREATE_TABLES"), environment != "production"),
            environment=environment,
        )
