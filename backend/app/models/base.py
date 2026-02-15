from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class BaseMixin:
    """Mixin that adds created_at/updated_at and a to_dict helper."""

    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Subclasses should set this to a list of column names for serialization
    _serializable_fields: list[str] = []

    def to_dict(self) -> dict:
        result = {}
        for col in self.__table__.columns:
            val = getattr(self, col.name)
            if isinstance(val, datetime):
                val = val.isoformat()
            result[col.name] = val
        return result

    def update_from_dict(self, data: dict) -> None:
        for key, value in data.items():
            if hasattr(self, key) and key not in ("id", "created_at", "updated_at"):
                setattr(self, key, value)
