"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-02-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "hardware",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("hostname", sa.Text),
        sa.Column("ip_address", sa.Text),
        sa.Column("cpu", sa.Text),
        sa.Column("cpu_cores", sa.Integer),
        sa.Column("ram_gb", sa.Float),
        sa.Column("os", sa.Text),
        sa.Column("make", sa.Text),
        sa.Column("model", sa.Text),
        sa.Column("serial_number", sa.Text),
        sa.Column("location", sa.Text),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "vms",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("hardware_id", sa.Integer, sa.ForeignKey("hardware.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("hostname", sa.Text),
        sa.Column("ip_address", sa.Text),
        sa.Column("cpu_cores", sa.Integer),
        sa.Column("ram_gb", sa.Float),
        sa.Column("disk_gb", sa.Float),
        sa.Column("os", sa.Text),
        sa.Column("hypervisor", sa.Text),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "apps",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("hardware_id", sa.Integer, sa.ForeignKey("hardware.id", ondelete="SET NULL"), nullable=True),
        sa.Column("vm_id", sa.Integer, sa.ForeignKey("vms.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("hostname", sa.Text),
        sa.Column("external_hostname", sa.Text),
        sa.Column("port", sa.Integer),
        sa.Column("url", sa.Text),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.CheckConstraint(
            "NOT (hardware_id IS NOT NULL AND vm_id IS NOT NULL)",
            name="ck_apps_single_parent",
        ),
    )

    op.create_table(
        "storage",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("hardware_id", sa.Integer, sa.ForeignKey("hardware.id", ondelete="SET NULL"), nullable=True),
        sa.Column("vm_id", sa.Integer, sa.ForeignKey("vms.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("storage_type", sa.Text),
        sa.Column("raid_type", sa.Text),
        sa.Column("drive_count", sa.Integer),
        sa.Column("raw_space_gb", sa.Float),
        sa.Column("usable_space_gb", sa.Float),
        sa.Column("filesystem", sa.Text),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.CheckConstraint(
            "NOT (hardware_id IS NOT NULL AND vm_id IS NOT NULL)",
            name="ck_storage_single_parent",
        ),
    )

    op.create_table(
        "networks",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("vlan_id", sa.Integer),
        sa.Column("subnet", sa.Text),
        sa.Column("gateway", sa.Text),
        sa.Column("dns_servers", sa.Text),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "network_members",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("network_id", sa.Integer, sa.ForeignKey("networks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("member_type", sa.Text, nullable=False),
        sa.Column("member_id", sa.Integer, nullable=False),
        sa.Column("ip_on_network", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.UniqueConstraint("network_id", "member_type", "member_id", name="uq_network_member"),
    )

    op.create_table(
        "misc",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("category", sa.Text),
        sa.Column("description", sa.Text),
        sa.Column("properties", sa.Text),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("parent_id", sa.Integer, sa.ForeignKey("documents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.Text, nullable=False, server_default="Untitled"),
        sa.Column("content", sa.Text, nullable=False, server_default=""),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "map_layout",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("node_type", sa.Text, nullable=False),
        sa.Column("node_id", sa.Integer, nullable=False),
        sa.Column("x", sa.Float, nullable=False, server_default="0"),
        sa.Column("y", sa.Float, nullable=False, server_default="0"),
        sa.Column("pinned", sa.Boolean, nullable=False, server_default="0"),
        sa.UniqueConstraint("node_type", "node_id", name="uq_map_node"),
    )

    op.create_table(
        "map_edges",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("source_type", sa.Text, nullable=False),
        sa.Column("source_id", sa.Integer, nullable=False),
        sa.Column("target_type", sa.Text, nullable=False),
        sa.Column("target_id", sa.Integer, nullable=False),
        sa.Column("label", sa.Text),
        sa.Column("style", sa.Text),
    )

    op.create_table(
        "relationships",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("source_type", sa.Text, nullable=False),
        sa.Column("source_id", sa.Integer, nullable=False),
        sa.Column("target_type", sa.Text, nullable=False),
        sa.Column("target_id", sa.Integer, nullable=False),
        sa.Column("label", sa.Text),
        sa.UniqueConstraint("source_type", "source_id", "target_type", "target_id", name="uq_relationship"),
    )


def downgrade() -> None:
    op.drop_table("relationships")
    op.drop_table("map_edges")
    op.drop_table("map_layout")
    op.drop_table("documents")
    op.drop_table("misc")
    op.drop_table("network_members")
    op.drop_table("networks")
    op.drop_table("storage")
    op.drop_table("apps")
    op.drop_table("vms")
    op.drop_table("hardware")
