"""Add cost tracking tables

Revision ID: add_cost_tracking
Revises: 
Create Date: 2024-01-10 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_cost_tracking'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create cost_entries table
    op.create_table('cost_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('service', sa.String(length=100), nullable=False),
        sa.Column('operation', sa.String(length=100), nullable=False),
        sa.Column('cost_amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('requests_count', sa.Integer(), nullable=True),
        sa.Column('data_processed_mb', sa.Float(), nullable=True),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('extra_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cost_entries_service'), 'cost_entries', ['service'], unique=False)
    op.create_index(op.f('ix_cost_entries_job_id'), 'cost_entries', ['job_id'], unique=False)

    # Create cost_summaries table
    op.create_table('cost_summaries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('period_type', sa.String(length=20), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_cost', sa.Float(), nullable=False),
        sa.Column('service_breakdown', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('cost_summaries')
    op.drop_index(op.f('ix_cost_entries_job_id'), table_name='cost_entries')
    op.drop_index(op.f('ix_cost_entries_service'), table_name='cost_entries')
    op.drop_table('cost_entries')
