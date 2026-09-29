"""knowledge submissions pipeline (đóng góp → sàng lọc → Admin duyệt → xuất kho)

Revision ID: 0015
Revises: 0014
Create Date: 2026-09-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0015'
down_revision = '0014'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'knowledge_submissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), nullable=False),
        sa.Column('contributor_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('target_file', sa.String(length=200), nullable=False),
        sa.Column('content_md', sa.Text(), nullable=False),
        sa.Column('source_url', sa.String(length=500), nullable=False),
        sa.Column('status', sa.String(length=12), nullable=False),
        sa.Column('dedupe_report',
                  sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'),
                  nullable=False),
        sa.Column('ai_notes', sa.Text(), nullable=True),
        sa.Column('reject_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['contributor_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('knowledge_submissions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_knowledge_submissions_org_id'), ['org_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_knowledge_submissions_contributor_id'),
                              ['contributor_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_knowledge_submissions_status'), ['status'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('knowledge_submissions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_knowledge_submissions_status'))
        batch_op.drop_index(batch_op.f('ix_knowledge_submissions_contributor_id'))
        batch_op.drop_index(batch_op.f('ix_knowledge_submissions_org_id'))
    op.drop_table('knowledge_submissions')
