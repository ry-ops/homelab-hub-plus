"""Add hostname to misc

Revision ID: 004
Revises: 003
Create Date: 2026-02-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add hostname column to misc
    op.add_column("misc", sa.Column("hostname", sa.Text, nullable=True))


def downgrade() -> None:
    # Remove hostname from misc
    op.drop_column("misc", "hostname")
