from .base import db, BaseMixin


class Share(BaseMixin, db.Model):
    __tablename__ = "shares"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    storage_id = db.Column(db.Integer, db.ForeignKey("storage.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.Text, nullable=False)
    hostname = db.Column(db.Text)
    ip = db.Column(db.Text)
    share_type = db.Column(db.Text)  # e.g., NFS, SMB, iSCSI, etc.
    notes = db.Column(db.Text)

    # Relationship back to storage
    storage = db.relationship("Storage", back_populates="shares")

    def to_dict(self):
        return {
            "id": self.id,
            "storage_id": self.storage_id,
            "name": self.name,
            "hostname": self.hostname,
            "ip": self.ip,
            "share_type": self.share_type,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
