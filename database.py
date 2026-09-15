"""Persistent database layer for ATHARVADRISHTI.

SQLite is the zero-configuration default. Set DATABASE_URL to PostgreSQL
(or another SQLAlchemy-supported database) for deployment.
The existing frontend/UI is intentionally not modified by this module.
"""

import json
import os
from datetime import datetime, timezone

from flask import jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, text


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False,
                           default=lambda: datetime.now(timezone.utc))
    farms = db.relationship("Farm", back_populates="user", cascade="all, delete-orphan")
    scans = db.relationship("Scan", back_populates="user", cascade="all, delete-orphan")


class Farm(db.Model):
    __tablename__ = "farms"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    farm_name = db.Column(db.String(160), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False,
                           default=lambda: datetime.now(timezone.utc))
    user = db.relationship("User", back_populates="farms")
    crops = db.relationship("Crop", back_populates="farm", cascade="all, delete-orphan")
    scans = db.relationship("Scan", back_populates="farm")


class Crop(db.Model):
    __tablename__ = "crops"
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id"), nullable=True, index=True)
    crop_name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False,
                           default=lambda: datetime.now(timezone.utc))
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
    created_at = db.Column(db.DateTime(timezone=True), nullable=False,
                           default=lambda: datetime.now(timezone.utc), index=True)
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
            "top_predictions": json.loads(self.top_predictions) if self.top_predictions else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


def _record_scan_from_request(sender, template, context, **extra):
    """Persist UI predictions without changing the existing template contract."""
    if request.method != "POST" or template.name != "index.html":
        return
    if not context.get("prediction") and not context.get("error"):
        return
    try:
        filename = request.files["image"].filename if "image" in request.files else None
        prediction = context.get("prediction")
        confidence = context.get("confidence")
        error = context.get("error")
        plant_type = context.get("selected_plant_type", "general")
        current_user = getattr(request, "current_user", None)
        scan = Scan(
            user_id=current_user.id if current_user else None,
            original_filename=filename,
            image_path=context.get("original_image"),
            plant_type=plant_type,
            model_used=("mango_model" if plant_type == "mango" else "plantdoc_model") if prediction else None,
            prediction=prediction,
            confidence=float(confidence) if confidence is not None else None,
            prediction_status="completed" if prediction else "rejected",
            error_message=error if not prediction else None,
            completed_at=datetime.now(timezone.utc),
        )
        db.session.add(scan)
        db.session.commit()
    except Exception:
        db.session.rollback()


def _register_api_routes(app):
    @app.get("/api/health")
    def database_health():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "ok", "database": "connected"})
        except Exception:
            return jsonify({"status": "error", "database": "unavailable"}), 503

    @app.get("/api/scans")
    def scan_history():
        limit = request.args.get("limit", default=20, type=int)
        limit = max(1, min(limit, 100))
        user_id = request.current_user.id
        scans = (
            Scan.query.filter_by(user_id=user_id)
            .order_by(Scan.created_at.desc())
            .limit(limit)
            .all()
        )
        return jsonify({"count": len(scans), "scans": [scan.to_dict() for scan in scans]})

    @app.get("/api/scans/<int:scan_id>")
    def scan_detail(scan_id):
        scan = Scan.query.filter_by(id=scan_id, user_id=request.current_user.id).first()
        if scan is None:
            return jsonify({"error": "Scan not found"}), 404
        return jsonify(scan.to_dict())


def configure_database(app):
    """Configure SQLAlchemy and initialize the Phase 1 backend."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_sqlite = os.path.join(base_dir, "instance", "atharvadrishti.db")
    os.makedirs(os.path.dirname(default_sqlite), exist_ok=True)
    database_url = os.getenv("DATABASE_URL", f"sqlite:///{default_sqlite}")
    if database_url.startswith("postgres://"):
        database_url = "postgresql://" + database_url[len("postgres://"):]
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", database_url)
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    if database_url.startswith("sqlite"):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            **app.config.get("SQLALCHEMY_ENGINE_OPTIONS", {}),
            "connect_args": {"check_same_thread": False},
        }
    db.init_app(app)
    _register_api_routes(app)
    try:
        from flask import template_rendered
        template_rendered.connect(_record_scan_from_request, app)
    except Exception:
        pass
    with app.app_context():
        db.create_all()
