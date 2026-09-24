"""share links (P3-1) + organization LLM settings (P2-6)

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-24
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

JSON = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql')


def upgrade() -> None:
    with op.batch_alter_table('organizations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('llm_settings', JSON, nullable=False, server_default='{}'))

    op.create_table('share_links',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('report_id', sa.String(length=36), nullable=False),
    sa.Column('org_id', sa.Integer(), nullable=False),
    sa.Column('created_by', sa.Integer(), nullable=False),
    sa.Column('token_hash', sa.String(length=64), nullable=False),
    sa.Column('label', sa.String(length=120), nullable=False),
    sa.Column('formats', JSON, nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('view_count', sa.Integer(), nullable=False),
    sa.Column('last_viewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['report_id'], ['reports.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('share_links', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_share_links_org_id'), ['org_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_share_links_report_id'), ['report_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_share_links_token_hash'), ['token_hash'], unique=True)


def downgrade() -> None:
    with op.batch_alter_table('share_links', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_share_links_token_hash'))
        batch_op.drop_index(batch_op.f('ix_share_links_report_id'))
        batch_op.drop_index(batch_op.f('ix_share_links_org_id'))
    op.drop_table('share_links')
    with op.batch_alter_table('organizations', schema=None) as batch_op:
        batch_op.drop_column('llm_settings')
