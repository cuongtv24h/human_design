"""Report templates: custom templates + blocks + samples + org vars (Giai doan 1)

Revision ID: 0007
Revises: 0006
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None

JSON = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql')


def upgrade() -> None:
    with op.batch_alter_table('organizations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('template_vars', JSON, nullable=False, server_default='{}'))

    op.create_table('report_templates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('org_id', sa.Integer(), nullable=True),
    sa.Column('key', sa.String(length=30), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('description', sa.Text(), nullable=False, server_default=''),
    sa.Column('badge', sa.String(length=40), nullable=False, server_default=''),
    sa.Column('visibility', sa.String(length=10), nullable=False, server_default='private'),
    sa.Column('status', sa.String(length=10), nullable=False, server_default='draft'),
    sa.Column('review_note', sa.Text(), nullable=False, server_default=''),
    sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
    sa.Column('sections', JSON, nullable=False, server_default='[]'),
    sa.Column('created_by', sa.Integer(), nullable=False),
    sa.Column('origin_template_id', sa.Integer(), nullable=True),
    sa.Column('origin_label', sa.String(length=200), nullable=False, server_default=''),
    sa.Column('import_count', sa.Integer(), nullable=False, server_default='0'),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('report_templates', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_report_templates_key'), ['key'], unique=False)
        batch_op.create_index(batch_op.f('ix_report_templates_org_id'), ['org_id'], unique=False)

    op.create_table('template_blocks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('org_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('kind', sa.String(length=20), nullable=False, server_default='core'),
    sa.Column('body', sa.Text(), nullable=False, server_default=''),
    sa.Column('created_by', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('template_blocks', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_template_blocks_org_id'), ['org_id'], unique=False)

    op.create_table('template_samples',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('template_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=160), nullable=False),
    sa.Column('body', sa.Text(), nullable=False, server_default=''),
    sa.Column('sort', sa.Integer(), nullable=False, server_default='0'),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['template_id'], ['report_templates.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('template_samples', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_template_samples_template_id'), ['template_id'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('template_samples', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_template_samples_template_id'))
    op.drop_table('template_samples')
    with op.batch_alter_table('template_blocks', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_template_blocks_org_id'))
    op.drop_table('template_blocks')
    with op.batch_alter_table('report_templates', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_report_templates_org_id'))
        batch_op.drop_index(batch_op.f('ix_report_templates_key'))
    op.drop_table('report_templates')
    with op.batch_alter_table('organizations', schema=None) as batch_op:
        batch_op.drop_column('template_vars')
