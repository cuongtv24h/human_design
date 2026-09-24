"""Admin CLI.

    python -m backend.api.cli init-db
    python -m backend.api.cli create-admin --email admin@example.com --name "Quản trị" [--org "Tên tổ chức"]
    (password is read from HD_ADMIN_PASSWORD or prompted)
"""

from __future__ import annotations

import argparse
import getpass
import os
import sys

from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError, ProgrammingError

from .db import Database
from .models import Organization, User
from .security import hash_password
from .settings import Settings

DEFAULT_THEME = {  # D10: auto-generated sample theme, replaced by real branding later.
    "brand_name": "Human Design Studio",
    "primary": "#3565A8",
    "accent": "#C8963E",
    "paper": "#FBF8F1",
}


def ensure_admin(db: Database, email: str, password: str, name: str = "", org_name: str = "Human Design Studio") -> User:
    with db.session_factory() as session:
        org = session.scalar(select(Organization).order_by(Organization.id))
        if org is None:
            org = Organization(name=org_name, theme=DEFAULT_THEME)
            session.add(org)
            session.flush()
        user = session.scalar(select(User).where(func.lower(User.email) == email.lower()))
        if user is None:
            user = User(org_id=org.id, email=email.lower(), full_name=name, role="admin",
                        password_hash=hash_password(password))
            session.add(user)
        else:
            user.role, user.is_active = "admin", True
            user.password_hash = hash_password(password)
            if name:
                user.full_name = name
        session.commit()
        session.refresh(user)
        return user


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="backend.api.cli")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init-db", help="Create tables (dev/SQLite). Production: alembic upgrade head.")
    admin = sub.add_parser("create-admin", help="Create or reset an admin account")
    admin.add_argument("--email", required=True)
    admin.add_argument("--name", default="")
    admin.add_argument("--org", default="Human Design Studio")
    args = parser.parse_args(argv)

    settings = Settings.from_env()
    db = Database(settings.database_url)
    if args.command == "init-db" or settings.auto_create_tables:
        db.create_all()  # dev convenience; production schema comes only from `alembic upgrade head`
    if args.command == "init-db":
        print(f"OK: tables ready at {settings.database_url.split('@')[-1]}")
        return 0
    password = os.environ.get("HD_ADMIN_PASSWORD") or getpass.getpass("Mật khẩu admin (≥ 8 ký tự): ")
    if len(password) < 8:
        print("Mật khẩu phải có ít nhất 8 ký tự.", file=sys.stderr)
        return 2
    try:
        user = ensure_admin(db, args.email, password, args.name, args.org)
    except (OperationalError, ProgrammingError):
        print("Chưa có bảng dữ liệu. Chạy trước: .venv/bin/alembic upgrade head", file=sys.stderr)
        return 3
    print(f"OK: admin {user.email} (id={user.id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
