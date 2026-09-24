#!/usr/bin/env bash
# Run on the VPS: /srv/human_design/deploy/deploy.sh [branch]
set -euo pipefail
BRANCH="${1:-main}"
cd "$(dirname "$0")/.."
git pull --ff-only origin "$BRANCH"
.venv/bin/pip install -q -r requirements.txt
.venv/bin/alembic upgrade head
(cd web && npm ci && npm run build)
pm2 reload deploy/ecosystem.config.cjs --update-env
pm2 save
echo "deploy.sh: OK"
