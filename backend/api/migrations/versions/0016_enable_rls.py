"""Enable Row Level Security cho toàn bộ bảng public (Supabase/Postgres)

Bảng trong schema public mà tắt RLS sẽ bị PostgREST cho phép anon/authenticated
CRUD toàn bộ qua Data API (Security Advisor: rls_disabled_in_public).
App của project này chỉ kết nối Postgres trực tiếp bằng role ``postgres``
(qua pooler, SQLAlchemy) — không dùng Supabase client/PostgREST — nên bật RLS
deny-all (không policy) không ảnh hưởng backend: owner không bị RLS áp trừ khi
FORCE, và project không cấp policy nào cho anon.

- Dialect PostgreSQL/Supabase: duyệt ``pg_tables`` (schemaname='public',
  rowsecurity = false) và ``ALTER TABLE ... ENABLE ROW LEVEL SECURITY`` từng bảng.
- Dialect SQLite (dev mặc định): no-op (SQLite không có RLS).

Lưu ý: bảng tạo bởi migration SAU 0016 sẽ không tự bật RLS — migration tạo bảng
mới nên thêm ``ENABLE ROW LEVEL SECURITY`` hoặc chạy lại script này.

Revision ID: 0016
Revises: 0015
Create Date: 2026-09-30
"""
from alembic import op
import sqlalchemy as sa

revision = '0016'
down_revision = '0015'
branch_labels = None
depends_on = None

_ENABLE_RLS_SQL = """
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
  AND NOT rowsecurity
ORDER BY tablename
"""


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != 'postgresql':
        return  # SQLite dev: không có RLS
    rows = bind.execute(sa.text(_ENABLE_RLS_SQL)).fetchall()
    for (tablename,) in rows:
        # owner (postgres) không bị áp RLS khi không FORCE → backend an toàn;
        # anon/authenticated qua PostgREST bị deny toàn bộ vì không có policy.
        bind.execute(
            sa.text('ALTER TABLE public.{} ENABLE ROW LEVEL SECURITY'.format(
                '"' + tablename.replace('"', '""') + '"'))
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != 'postgresql':
        return
    rows = bind.execute(sa.text(
        "SELECT tablename FROM pg_tables "
        "WHERE schemaname = 'public' AND rowsecurity ORDER BY tablename"
    )).fetchall()
    for (tablename,) in rows:
        bind.execute(
            sa.text('ALTER TABLE public.{} DISABLE ROW LEVEL SECURITY'.format(
                '"' + tablename.replace('"', '""') + '"'))
        )
