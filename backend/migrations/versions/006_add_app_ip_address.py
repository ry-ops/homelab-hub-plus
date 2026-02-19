"""add app ip_address

Revision ID: 006
Revises: 005
Create Date: 2026-02-15

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # Add ip_address column to apps table
    op.add_column('apps', sa.Column('ip_address', sa.Text(), nullable=True), if_not_exists=True)


def downgrade():
    # Remove ip_address column from apps table
    op.drop_column('apps', 'ip_address')
