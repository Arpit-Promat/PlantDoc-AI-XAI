"""Database layer for ATHARVADRISHTI.

The application can run with SQLite by default and can be switched to
PostgreSQL (or another SQLAlchemy-supported database) with DATABASE_URL.
The existing frontend does not depend on this module directly.
"""

import os
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    farms = db.relationship(
        "Farm", back_populates="user", cascade="all, delete-orphan"
    )
    scans = db.relationship(
        "Scan", back_populates="user", cascade="all, delete-orphan"
    )


class Farm(db.Model):
    __tablename__ = "farms"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    farm_name = db.Column(db.String(160), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", back_populates="farms")
    crops = db.relationship(
        "Crop", back_populates="farm", cascade="all, delete-orphan"
    )
    scans = db.relationship("Scan", back_populates="farm")


class Crop(db.Model):
    __tablename__ = "crops"

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id"), nullable=True, index=True)
    crop_name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    farm = db.relationship("Farm", back_populates="crops")
    scans = db.relationship("Scan", back_populates="crop")


class Scan(db.Model):
    __tablename__ = "scans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id"), nullable=True, index=True)
    crop_id = db.Column(db.Integer, db.ForeignKey("crops.id"), nullable=True, index=True)

    image_path = db.Column(db.String(500), nullable=True)
    original_filename = db.Column(db.String(255), nullable=True)
    plant_type = db.Column(db.String(80), nullable=False, default="general")
    model_used = db.Column(db.String(120), nullable=True)
    prediction = db.Column(db.String(255), nullable=True)
    confidence = db.Column(db.Float, nullable=True)
    prediction_margin = db.Column(db.Float, nullable=True)
    leaf_probability = db.Column(db.Float, nullable=True)
    prediction_status = db.Column(db.String(40), nullable=False, default="pending")
    error_message = db.Column(db.Text, nullable=True)
    top_predictions = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    user = db.relationship("User", back_populates="scans")
    farm = db.relationship("Farm", back_populates="scans")
    crop = db.relationship("Crop", back_populates="scans")

    __table_args__ = (
        Index("ix_scans_user_created_at", "user_id", "created_at"),
        Index("ix_scans_status_created_at", "prediction_status", "created_at"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "farm_id": self.farm_id,
            "crop_id": self.crop_id,
            "image_path": self.image_path,
            "original_filename": self.original_filename,
            "plant_type": self.plant_type,
            "model_used": self.model_used,
            "prediction": self.prediction,
            "confidence": self.confidence,
            "prediction_margin": self.prediction_margin,
            "leaf_probability": self.leaf_probability,
            "prediction_status": self.prediction_status,
            "error_message": self.error_message,
            "top_predictions": self.top_predictions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


def configure_database(app):
    """Configure SQLAlchemy without changing the existing UI or routes' contract."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_sqlite = os.path.join(base_dir, "instance", "atharvadrishti.db")
    os.makedirs(os.path.dirname(default_sqlite), exist_ok=True)

    database_url = os.getenv("DATABASE_URL", f"sqlite:///{default_sqlite}")
    # Some cloud providers expose postgres://, while SQLAlchemy expects postgresql://.
    if database_url.startswith("postgres://"):
        database_url = "postgresql://" + database_url[len("postgres://") :]

    app.config.setdefault("SQLALCHEMY_DATABASE_URI", database_url)
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {})

    # SQLite needs this for threaded Flask requests. It is ignored by other DBs.
    if database_url.startswith("sqlite"):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            **app.config["SQLALCHEMY_ENGINE_OPTIONS"],
            "connect_args": {"check_same_thread": False},
        }

    db.init_app(app)

    with app.app_context():
        db.create_all()
