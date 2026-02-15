from .base import db, BaseMixin


class Misc(BaseMixin, db.Model):
    __tablename__ = "misc"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text)
    description = db.Column(db.Text)
    properties = db.Column(db.Text)  # JSON blob for arbitrary key-value pairs
    notes = db.Column(db.Text)
