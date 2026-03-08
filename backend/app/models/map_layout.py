from .base import db


class MapLayout(db.Model):
    __tablename__ = "map_layout"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    node_type = db.Column(db.Text, nullable=False)
    node_id = db.Column(db.Integer, nullable=False)
    x = db.Column(db.Float, nullable=False, default=0)
    y = db.Column(db.Float, nullable=False, default=0)
    pinned = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        db.UniqueConstraint("node_type", "node_id", name="uq_map_node"),
    )


class MapEdge(db.Model):
    __tablename__ = "map_edges"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source_type = db.Column(db.Text, nullable=False)
    source_id = db.Column(db.Integer, nullable=False)
    target_type = db.Column(db.Text, nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    label = db.Column(db.Text)
    style = db.Column(db.Text)  # JSON


class Relationship(db.Model):
    __tablename__ = "relationships"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source_type = db.Column(db.Text, nullable=False)
    source_id = db.Column(db.Integer, nullable=False)
    target_type = db.Column(db.Text, nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    label = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint("source_type", "source_id", "target_type", "target_id", name="uq_relationship"),
    )
