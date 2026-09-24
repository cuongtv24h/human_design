#!/usr/bin/env bash
# Update the running app on the VPS (run as the app user, e.g. `hd`):
#   /srv/human_design/deploy/deploy.sh            # branch main
#   /srv/human_design/deploy/deploy.sh my-branch
# First-time installation: docs/DEPLOY_VPS.md
set -euo pipefail
BRANCH="${1:-main}"
cd "$(dirname "$0")/.."

fail() { echo "deploy.sh: $*" >&2; exit 1; }
[ -f .env ] || fail "thiếu file .env (xem docs/DEPLOY_VPS.md, bước 6)"
grep -q '^HD_ENV=production' .env || fail ".env phải có HD_ENV=production"
grep -q '^HD_SECRET_KEY=..' .env || fail ".env phải có HD_SECRET_KEY (chuỗi ngẫu nhiên dài)"
grep -q '^DATABASE_URL=postgresql' .env || echo "deploy.sh: CẢNH BÁO — DATABASE_URL không phải PostgreSQL"

echo "==> 1/5 Lấy code ($BRANCH)"
git fetch --prune origin
git checkout -q "$BRANCH"
git pull --ff-only origin "$BRANCH"

echo "==> 2/5 Thư viện Python"
.venv/bin/pip install -q -r requirements.txt

echo "==> 3/5 Nâng cấp CSDL"
.venv/bin/alembic upgrade head

echo "==> 4/5 Build giao diện"
(cd web && npm ci --no-audit --no-fund && npm run build)

echo "==> 5/5 Khởi động lại (pm2)"
pm2 startOrReload deploy/ecosystem.config.cjs --update-env
pm2 save

# Health check (API + web through the same path the browser uses).
for i in $(seq 1 20); do
  if curl -fsS http://127.0.0.1:3000/api/v1/health >/dev/null 2>&1; then
    echo "deploy.sh: OK — $(git log --oneline -1)"
    exit 0
  fi
  sleep 1
done
fail "sau 20 giây vẫn chưa truy cập được /api/v1/health — xem: pm2 logs hd-api --lines 50"
