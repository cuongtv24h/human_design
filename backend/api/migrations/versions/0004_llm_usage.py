"""LLM usage log (fallback chain attempts + token cost tracking)

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-24
"""
from alembic import op
import sqlalchemy as sa

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'llm_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.String(length=36), nullable=True),
        sa.Column('purpose', sa.String(length=20), nullable=False, server_default='report'),
        sa.Column('provider', sa.String(length=120), nullable=False, server_default=''),
        sa.Column('base_url', sa.String(length=300), nullable=False, server_default=''),
        sa.Column('model', sa.String(length=120), nullable=False, server_default=''),
        sa.Column('prompt_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('completion_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('input_price', sa.Float(), nullable=False, server_default='0'),
        sa.Column('output_price', sa.Float(), nullable=False, server_default='0'),
        sa.Column('cost_usd', sa.Float(), nullable=True),
        sa.Column('ok', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('error', sa.String(length=500), nullable=False, server_default=''),
        sa.Column('latency_ms', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_llm_usage_org_id', 'llm_usage', ['org_id'])
    op.create_index('ix_llm_usage_report_id', 'llm_usage', ['report_id'])
    op.create_index('ix_llm_usage_created_at', 'llm_usage', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_llm_usage_created_at', table_name='llm_usage')
    op.drop_index('ix_llm_usage_report_id', table_name='llm_usage')
    op.drop_index('ix_llm_usage_org_id', table_name='llm_usage')
    op.drop_table('llm_usage')
