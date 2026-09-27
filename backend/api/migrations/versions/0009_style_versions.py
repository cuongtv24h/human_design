"""Template style versions + report style version stamp (P4)

Revision ID: 0009
Revises: 0008
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0009'
down_revision = '0008'
branch_labels = None
depends_on = None

JSON = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql')


def upgrade() -> None:
    op.create_table(
        'template_style_versions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('template_id', sa.Integer(), sa.ForeignKey('report_templates.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('version_no', sa.Integer(), nullable=False),
        sa.Column('profile', JSON, nullable=False, server_default='{}'),
        sa.Column('source', sa.String(length=16), nullable=False, server_default='manual'),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('template_id', 'version_no', name='uq_style_version_no'),
    )
    with op.batch_alter_table('reports', schema=None) as batch_op:
        batch_op.add_column(sa.Column('style_version', sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('reports', schema=None) as batch_op:
        batch_op.drop_column('style_version')
    op.drop_table('template_style_versions')
