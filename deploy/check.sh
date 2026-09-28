#!/usr/bin/env bash
# Run on the dev machine before deploying (replaces CI).
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHONPATH=tools:mcp .venv/bin/pytest -q
DATABASE_URL=sqlite:///$(mktemp -d)/check.sqlite3 sh -c '.venv/bin/alembic upgrade head >/dev/null && .venv/bin/alembic check'
(cd web && npm run typecheck && npm run build)
# Quét lỗ hổng dependency runtime của frontend — CHẶN deploy khi có high/critical.
# next@16.3.6 (issue #4) đã xử lý hết postcss GHSA → 0 lỗ hổng, bật fail-on-high.
# Nếu npm audit báo high trở lại, deploy dừng tại đây cho tới khi nâng/cập nhật xong.
(cd web && npm audit --omit=dev --audit-level=high) \
  || { echo "check.sh: npm audit phát hiện HIGH/CRITICAL — không deploy (xem issue nâng dependency)."; exit 1; }
echo "check.sh: OK"
