"""Remove hypervisor from VMs and add IP to misc

Revision ID: 003
Revises: 002
Create Date: 2026-02-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove hypervisor column from vms
    op.drop_column("vms", "hypervisor")
    
    # Add ip_address column to misc
    op.add_column("misc", sa.Column("ip_address", sa.Text, nullable=True))


def downgrade() -> None:
    # Remove ip_address from misc
    op.drop_column("misc", "ip_address")
    
    # Add hypervisor back to vms
    op.add_column("vms", sa.Column("hypervisor", sa.Text, nullable=True))
