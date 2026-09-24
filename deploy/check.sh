#!/usr/bin/env bash
# Run on the dev machine before deploying (replaces CI).
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHONPATH=tools:mcp .venv/bin/pytest -q
DATABASE_URL=sqlite:///"$(mktemp -d)"/check.sqlite3 sh -c '.venv/bin/alembic upgrade head >/dev/null && .venv/bin/alembic check'
(cd web && npm run typecheck && npm run build)
echo "check.sh: OK"
