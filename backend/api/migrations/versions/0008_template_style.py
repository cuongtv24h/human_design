"""Template style profile + report style rating (P2)

Revision ID: 0008
Revises: 0007
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None

JSON = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql')


def upgrade() -> None:
    with op.batch_alter_table('report_templates', schema=None) as batch_op:
        batch_op.add_column(sa.Column('style_profile', JSON, nullable=False, server_default='{}'))
        batch_op.add_column(sa.Column('style_status', sa.String(length=16), nullable=False, server_default='none'))
    with op.batch_alter_table('reports', schema=None) as batch_op:
        batch_op.add_column(sa.Column('style_rating', sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('reports', schema=None) as batch_op:
        batch_op.drop_column('style_rating')
    with op.batch_alter_table('report_templates', schema=None) as batch_op:
        batch_op.drop_column('style_status')
        batch_op.drop_column('style_profile')
