"""Game daily streak days (G4)

Revision ID: 0012
Revises: 0011
"""
from alembic import op
import sqlalchemy as sa


revision = '0012'
down_revision = '0011'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'game_streak_days',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('session_id', sa.String(length=64), nullable=False, index=True),
        sa.Column('day', sa.Date(), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.UniqueConstraint('session_id', 'day', name='uq_game_streak_session_day'),
    )


def downgrade() -> None:
    op.drop_table('game_streak_days')
