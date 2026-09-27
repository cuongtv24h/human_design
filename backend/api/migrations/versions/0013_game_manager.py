"""Game manager: concepts, custom questions, disabled built-in questions

Revision ID: 0013
Revises: 0012
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0013'
down_revision = '0012'
branch_labels = None
depends_on = None

JSON = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql')


def upgrade() -> None:
    op.create_table(
        'game_concepts',
        sa.Column('slug', sa.String(length=32), primary_key=True),
        sa.Column('name', sa.String(length=80), nullable=False, server_default=''),
        sa.Column('entry_label', sa.String(length=120), nullable=False, server_default=''),
        sa.Column('entry_desc', sa.String(length=200), nullable=False, server_default=''),
        sa.Column('icon', sa.String(length=16), nullable=False, server_default=''),
        sa.Column('intro', sa.Text(), nullable=False, server_default=''),
        sa.Column('bridge', sa.Text(), nullable=False, server_default=''),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('is_builtin', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_table(
        'game_custom_questions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('concept_slug', sa.String(length=32),
                  sa.ForeignKey('game_concepts.slug', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('qid', sa.String(length=24), nullable=False, unique=True, index=True),
        sa.Column('title', sa.String(length=200), nullable=False, server_default=''),
        sa.Column('sit', sa.String(length=2000), nullable=False, server_default=''),
        sa.Column('options', JSON, nullable=False, server_default='[]'),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_table(
        'game_disabled_questions',
        sa.Column('concept_slug', sa.String(length=32), primary_key=True),
        sa.Column('qid', sa.String(length=24), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    concepts = sa.table(
        'game_concepts',
        sa.column('slug', sa.String), sa.column('enabled', sa.Boolean),
        sa.column('is_builtin', sa.Boolean), sa.column('sort_order', sa.Integer),
    )
    op.bulk_insert(concepts, [
        {'slug': 'nguoc-dong', 'enabled': True, 'is_builtin': True, 'sort_order': 0},
        {'slug': 'thuong-vu', 'enabled': True, 'is_builtin': True, 'sort_order': 10},
        {'slug': 'linh-thu', 'enabled': True, 'is_builtin': True, 'sort_order': 20},
    ])


def downgrade() -> None:
    op.drop_table('game_disabled_questions')
    op.drop_table('game_custom_questions')
    op.drop_table('game_concepts')
