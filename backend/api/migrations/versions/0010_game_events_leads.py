"""Game landing funnel events + leads (G1)

Revision ID: 0010
Revises: 0009
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0010'
down_revision = '0009'
branch_labels = None
depends_on = None

JSON = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql')


def upgrade() -> None:
    op.create_table(
        'game_events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=32), nullable=False, index=True),
        sa.Column('theme', sa.String(length=32), nullable=False, server_default=''),
        sa.Column('session_id', sa.String(length=64), nullable=False, server_default='', index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now(), index=True),
    )
    op.create_table(
        'game_leads',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('contact', sa.String(length=120), nullable=False),
        sa.Column('birth_date', sa.String(length=10), nullable=False, server_default=''),
        sa.Column('birth_time', sa.String(length=8), nullable=False, server_default=''),
        sa.Column('birth_place', sa.String(length=120), nullable=False, server_default=''),
        sa.Column('timezone', sa.String(length=10), nullable=False, server_default='+07:00'),
        sa.Column('theme', sa.String(length=32), nullable=False, server_default=''),
        sa.Column('quiz', JSON, nullable=False, server_default='{}'),
        sa.Column('note', sa.Text(), nullable=False, server_default=''),
        sa.Column('status', sa.String(length=16), nullable=False, server_default='new', index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now(), index=True),
    )


def downgrade() -> None:
    op.drop_table('game_leads')
    op.drop_table('game_events')
