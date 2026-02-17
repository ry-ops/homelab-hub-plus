from .base import db, BaseMixin


class Network(BaseMixin, db.Model):
    __tablename__ = "networks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    vlan_id = db.Column(db.Integer)
    subnet = db.Column(db.Text)
    gateway = db.Column(db.Text)
    dns_servers = db.Column(db.Text)
    color = db.Column(db.Text)
    notes = db.Column(db.Text)

    members = db.relationship("NetworkMember", backref="network", lazy="select", cascade="all, delete-orphan")


class NetworkMember(BaseMixin, db.Model):
    __tablename__ = "network_members"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    network_id = db.Column(db.Integer, db.ForeignKey("networks.id", ondelete="CASCADE"), nullable=False)
    member_type = db.Column(db.Text, nullable=False)
    member_id = db.Column(db.Integer, nullable=False)
    ip_on_network = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint("network_id", "member_type", "member_id", name="uq_network_member"),
    )
