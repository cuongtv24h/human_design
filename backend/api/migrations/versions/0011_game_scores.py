"""Game leaderboard scores (G3)

Revision ID: 0011
Revises: 0010
"""
from alembic import op
import sqlalchemy as sa


revision = '0011'
down_revision = '0010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'game_scores',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('theme', sa.String(length=32), nullable=False, server_default='', index=True),
        sa.Column('style', sa.String(length=16), nullable=False, server_default=''),
        sa.Column('deviation', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('session_id', sa.String(length=64), nullable=False, server_default='', index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now(), index=True),
    )


def downgrade() -> None:
    op.drop_table('game_scores')
