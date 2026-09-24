#!/usr/bin/env bash
# Daily backup: PostgreSQL dump + .env + var/secret_key. Keeps KEEP_DAYS days (default 14).
#   crontab -e:   15 2 * * * $HOME/human_design/deploy/backup.sh >> $HOME/human_design/var/backup.log 2>&1
# Restore: docs/DEPLOY_VPS.md, mục "Sao lưu & khôi phục".
set -euo pipefail
cd "$(dirname "$0")/.."
DEST="${BACKUP_DIR:-$HOME/backups/human_design}"
KEEP="${KEEP_DAYS:-14}"
STAMP="$(date +%Y%m%d-%H%M)"
umask 077
mkdir -p "$DEST"

DB_URL="$(grep -E '^DATABASE_URL=' .env | head -1 | cut -d= -f2- | tr -d '"'"'"'')"
[ -n "$DB_URL" ] || { echo "backup.sh: .env thiếu DATABASE_URL" >&2; exit 1; }
# SQLAlchemy URL → libpq URL (bỏ "+psycopg")
pg_dump --no-owner --format=custom --file "$DEST/db-$STAMP.dump" "${DB_URL/+psycopg/}"

# .env chứa HD_SECRET_KEY (mã hóa khóa AI, ký link) — mất nó thì phải nhập lại khóa AI.
FILES=(.env)
[ -f var/secret_key ] && FILES+=(var/secret_key)
tar -czf "$DEST/config-$STAMP.tgz" "${FILES[@]}"

find "$DEST" -type f \( -name 'db-*.dump' -o -name 'config-*.tgz' \) -mtime +"$KEEP" -delete
echo "backup.sh: OK $STAMP ($(du -sh "$DEST" | cut -f1) tổng)"
