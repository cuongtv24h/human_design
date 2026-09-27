"""Game stages: chapters + nodes (cau truc chuong/man tuy chinh)

Revision ID: 0014
Revises: 0013
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0014'
down_revision = '0013'
branch_labels = None
depends_on = None

JSON = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql')


def upgrade() -> None:
    op.create_table(
        'game_chapters',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('concept_slug', sa.String(length=32),
                  sa.ForeignKey('game_concepts.slug', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('idx', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('name', sa.String(length=80), nullable=False, server_default=''),
        sa.Column('icon', sa.String(length=16), nullable=False, server_default=''),
        sa.Column('desc', sa.String(length=200), nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_table(
        'game_nodes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('chapter_id', sa.Integer(),
                  sa.ForeignKey('game_chapters.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('idx', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('mode', sa.String(length=8), nullable=False, server_default='normal'),
        sa.Column('question_count', sa.Integer(), nullable=False, server_default='8'),
        sa.Column('time_limit', sa.Integer(), nullable=True),
        sa.Column('question_ids', JSON, nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('game_nodes')
    op.drop_table('game_chapters')
