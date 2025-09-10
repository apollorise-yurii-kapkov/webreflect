"""Add is_shared column to analysis_jobs

Revision ID: add_is_shared_column
Revises: 
Create Date: 2024-01-10 18:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_is_shared_column'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_shared column to analysis_jobs table
    op.add_column('analysis_jobs', sa.Column('is_shared', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Remove is_shared column from analysis_jobs table
    op.drop_column('analysis_jobs', 'is_shared')
