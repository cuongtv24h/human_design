"""report generation heartbeat + attempts (restart recovery)

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-24
"""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('reports', schema=None) as batch_op:
        batch_op.add_column(sa.Column('generation_attempts', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('job_heartbeat_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('reports', schema=None) as batch_op:
        batch_op.drop_column('job_heartbeat_at')
        batch_op.drop_column('generation_attempts')
