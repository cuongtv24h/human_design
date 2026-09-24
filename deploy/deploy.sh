#!/usr/bin/env bash
# Update the running app on the VPS (run as the app user, e.g. `hd`):
#   /srv/human_design/deploy/deploy.sh            # branch main
#   /srv/human_design/deploy/deploy.sh my-branch
# Or via the `git up` shortcut (docs/DEPLOY_VPS.md, §13).
#
# Smart skip: each step is skipped when its inputs did not change since the
# last SUCCESSFUL deploy (tracked in var/.last_deploy). If the previous deploy
# failed midway, everything runs again to be safe.
# First-time installation: docs/DEPLOY_VPS.md
set -euo pipefail
BRANCH="${1:-main}"
cd "$(dirname "$0")/.."

fail() { echo "deploy.sh: $*" >&2; exit 1; }
[ -f .env ] || fail "thiếu file .env (xem docs/DEPLOY_VPS.md, bước 6)"
grep -q '^HD_ENV=production' .env || fail ".env phải có HD_ENV=production"
grep -q '^HD_SECRET_KEY=..' .env || fail ".env phải có HD_SECRET_KEY (chuỗi ngẫu nhiên dài)"
grep -q '^DATABASE_URL=postgresql' .env || echo "deploy.sh: CẢNH BÁO — DATABASE_URL không phải PostgreSQL"

STATE_FILE="var/.last_deploy"   # commit hash của lần deploy THÀNH CÔNG gần nhất
BEFORE=$(git rev-parse HEAD)
LAST_OK=$(cat "$STATE_FILE" 2>/dev/null || true)

echo "==> 1/5 Lấy code ($BRANCH)"
git fetch --prune origin
git checkout -q "$BRANCH"
git pull --ff-only origin "$BRANCH"
AFTER=$(git rev-parse HEAD)

if [ "$LAST_OK" = "$BEFORE" ]; then
  CHANGED=$(git diff --name-only "$BEFORE" "$AFTER" || true)
  TRUST_DIFF=1
else
  echo "deploy.sh: lần deploy trước chưa xong (hoặc lần đầu) — chạy đủ các bước cho chắc."
  CHANGED=""
  TRUST_DIFF=0
fi

need() {  # need <pattern...>: true khi file khớp pattern có đổi, hoặc không chắc chắn
  [ "$TRUST_DIFF" = "0" ] && return 0
  local pattern
  for pattern in "$@"; do
    echo "$CHANGED" | grep -q "^$pattern" && return 0
  done
  return 1
}

echo "==> 2/5 Thư viện Python"
[ -x .venv/bin/pip ] || fail "thiếu .venv — cài lần đầu theo docs/DEPLOY_VPS.md (bước 5)"
if need "requirements.txt"; then
  echo "deploy.sh: requirements.txt có thay đổi — cài lại lib."
  .venv/bin/pip install -q -r requirements.txt
elif .venv/bin/python -c "import fastapi, sqlalchemy, alembic" 2>/dev/null; then
  echo "deploy.sh: requirements.txt không đổi, .venv còn tốt — bỏ qua."
else
  echo "deploy.sh: .venv thiếu lib — cài lại."
  .venv/bin/pip install -q -r requirements.txt
fi

echo "==> 3/5 Nâng cấp CSDL"
if need "backend/api/migrations/"; then
  .venv/bin/alembic upgrade head
else
  echo "deploy.sh: không có migration mới — bỏ qua."
fi

echo "==> 4/5 Build giao diện"
NEED_BUILD=0
NEED_CI=0
if need "web/"; then NEED_BUILD=1; fi
if need "web/package-lock.json" || need "web/package.json"; then NEED_CI=1; NEED_BUILD=1; fi
[ -d web/.next ] || NEED_BUILD=1
[ -d web/node_modules ] || NEED_CI=1
[ "$NEED_CI" = "1" ] && NEED_BUILD=1
if [ "$NEED_BUILD" = "1" ]; then
  if [ "$NEED_CI" = "1" ]; then
    (cd web && npm ci --no-audit --no-fund && npm run build)
  else
    echo "deploy.sh: package-lock không đổi — build lại, bỏ qua npm ci."
    (cd web && npm run build)
  fi
else
  echo "deploy.sh: web/ không đổi — bỏ qua (tiết kiệm 1–3 phút)."
fi

echo "==> 5/5 Khởi động lại (pm2)"
if [ "$BEFORE" = "$AFTER" ] && [ "$TRUST_DIFF" = "1" ]; then
  echo "deploy.sh: code không đổi — kiểm tra app, không restart."
  if curl -fsS http://127.0.0.1:3000/api/v1/health >/dev/null 2>&1; then
    echo "deploy.sh: OK (đã mới nhất, app đang chạy) — $(git log --oneline -1)"
    exit 0
  fi
  echo "deploy.sh: app không trả lời — restart để phục hồi."
fi
pm2 startOrReload deploy/ecosystem.config.cjs --update-env
pm2 save

# Health check (API + web through the same path the browser uses).
for i in $(seq 1 20); do
  if curl -fsS http://127.0.0.1:3000/api/v1/health >/dev/null 2>&1; then
    mkdir -p var
    echo "$AFTER" > "$STATE_FILE"
    echo "deploy.sh: OK — $(git log --oneline -1)"
    exit 0
  fi
  sleep 1
done
fail "sau 20 giây vẫn chưa truy cập được /api/v1/health — xem: pm2 logs hd-api --lines 50"
