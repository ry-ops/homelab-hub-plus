"""add app https

Revision ID: 007
Revises: 006
Create Date: 2026-02-15

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    # Add https column to apps table
    op.add_column('apps', sa.Column('https', sa.Boolean(), nullable=True, server_default='0'), if_not_exists=True)


def downgrade():
    # Remove https column from apps table
    op.drop_column('apps', 'https')
