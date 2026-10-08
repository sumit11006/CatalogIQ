"""Initial migration - create pipeline_runs, catalog_items, validation_items

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # pipeline_runs table
    op.create_table(
        'pipeline_runs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('total_items', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('processed_items', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_items', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(20), nullable=False, server_default='queued'),
        sa.Column('batch_size', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('concurrency', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('stats', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_pipeline_runs_status', 'pipeline_runs', ['status'])

    # catalog_items table
    op.create_table(
        'catalog_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('run_id', sa.String(36), sa.ForeignKey('pipeline_runs.id'), nullable=False),
        sa.Column('row_index', sa.Integer(), nullable=False),
        sa.Column('mfg_part_number', sa.String(120), nullable=False),
        sa.Column('part_desc_raw', sa.Text(), nullable=False, server_default=''),
        sa.Column('e1_brand_raw', sa.String(120), nullable=False, server_default=''),
        sa.Column('unilog_brand_raw', sa.String(120), nullable=False, server_default=''),
        sa.Column('dib_brand_raw', sa.String(120), nullable=False, server_default=''),
        sa.Column('part_manuf_raw', sa.String(160), nullable=False, server_default=''),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('ai_confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('quality_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('needs_review', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('manufacturer_name', sa.String(200), nullable=True),
        sa.Column('brand_name', sa.String(200), nullable=True),
        sa.Column('trade_name', sa.String(200), nullable=True),
        sa.Column('manufacturer_part_number', sa.String(120), nullable=True),
        sa.Column('dept', sa.String(120), nullable=True),
        sa.Column('item_class', sa.String(120), nullable=True),
        sa.Column('fine', sa.String(120), nullable=True),
        sa.Column('classpath', sa.Text(), nullable=True),
        sa.Column('unspsc', sa.String(20), nullable=True),
        sa.Column('product_name', sa.Text(), nullable=True),
        sa.Column('short_desc', sa.Text(), nullable=True),
        sa.Column('invoice_desc', sa.String(60), nullable=True),
        sa.Column('mobile_desc', sa.Text(), nullable=True),
        sa.Column('long_desc', sa.Text(), nullable=True),
        sa.Column('retail_desc', sa.Text(), nullable=True),
        sa.Column('marketing_description', sa.Text(), nullable=True),
        sa.Column('features', sa.JSON(), nullable=True),
        sa.Column('attributes', sa.JSON(), nullable=True),
        sa.Column('applications', sa.Text(), nullable=True),
        sa.Column('includes', sa.Text(), nullable=True),
        sa.Column('standards_approvals', sa.Text(), nullable=True),
        sa.Column('provenance', sa.JSON(), nullable=True),
        sa.Column('delivery_payload', sa.JSON(), nullable=True),
        sa.Column('quality_checks', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_catalog_items_run_id', 'catalog_items', ['run_id'])
    op.create_index('ix_catalog_items_mfg_part_number', 'catalog_items', ['mfg_part_number'])
    op.create_index('ix_catalog_items_status', 'catalog_items', ['status'])
    op.create_index('ix_catalog_items_needs_review', 'catalog_items', ['needs_review'])

    # validation_items table
    op.create_table(
        'validation_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('item_id', sa.String(36), sa.ForeignKey('catalog_items.id'), nullable=False),
        sa.Column('run_id', sa.String(36), nullable=False),
        sa.Column('field_group', sa.String(40), nullable=False),
        sa.Column('field_name', sa.String(80), nullable=False),
        sa.Column('current_value', sa.Text(), nullable=True),
        sa.Column('proposed_value', sa.Text(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('ai_confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('reviewer_note', sa.Text(), nullable=True),
        sa.Column('resolved_by', sa.String(80), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_validation_items_item_id', 'validation_items', ['item_id'])
    op.create_index('ix_validation_items_run_id', 'validation_items', ['run_id'])
    op.create_index('ix_validation_items_status', 'validation_items', ['status'])


def downgrade() -> None:
    op.drop_table('validation_items')
    op.drop_table('catalog_items')
    op.drop_table('pipeline_runs')
