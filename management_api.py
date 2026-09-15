"""Authenticated user/farm/crop management endpoints for Phase 4.

This module intentionally adds backend routes only. Existing templates and
frontend files are not modified.
"""

from functools import wraps

from flask import jsonify, request

from database import Crop, Farm, Scan, User, db



def _body():
    value = request.get_json(silent=True)
    return value if isinstance(value, dict) else {}


def _owned_farm(farm_id):
    return Farm.query.filter_by(id=farm_id, user_id=request.current_user.id).first()


def _owned_crop(crop_id):
    return (
        Crop.query.join(Farm, Crop.farm_id == Farm.id)
        .filter(Crop.id == crop_id, Farm.user_id == request.current_user.id)
        .first()
    )


def _owned_scan(scan_id):
    return Scan.query.filter_by(id=scan_id, user_id=request.current_user.id).first()


def register_management_routes(app):
    """Register Phase 4 endpoints. Authentication is enforced by security.py."""

    @app.get("/api/profile")
    def profile():
        user = db.session.get(User, request.current_user.id)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        return jsonify({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        })

    @app.patch("/api/profile")
    def update_profile():
        user = db.session.get(User, request.current_user.id)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        data = _body()
        if "name" in data:
            name = str(data.get("name", "")).strip()
            if len(name) > 120:
                return jsonify({"error": "Name is too long"}), 400
            user.name = name or None
        db.session.commit()
        return profile()

    @app.get("/api/farms")
    def list_farms():
        farms = Farm.query.filter_by(user_id=request.current_user.id).order_by(Farm.created_at.desc()).all()
        return jsonify({"count": len(farms), "farms": [
            {"id": f.id, "farm_name": f.farm_name, "location": f.location,
             "crop_count": len(f.crops),
             "created_at": f.created_at.isoformat() if f.created_at else None}
            for f in farms
        ]})

    @app.post("/api/farms")
    def create_farm():
        data = _body()
        name = str(data.get("farm_name", "")).strip()
        location = str(data.get("location", "")).strip() or None
        if not name or len(name) > 160:
            return jsonify({"error": "farm_name is required and must be <= 160 characters"}), 400
        if location and len(location) > 255:
            return jsonify({"error": "location is too long"}), 400
        farm = Farm(user_id=request.current_user.id, farm_name=name, location=location)
        db.session.add(farm)
        db.session.commit()
        return jsonify({"id": farm.id, "farm_name": farm.farm_name, "location": farm.location,
                        "crop_count": 0}), 201

    @app.get("/api/farms/<int:farm_id>")
    def get_farm(farm_id):
        farm = _owned_farm(farm_id)
        if not farm:
            return jsonify({"error": "Farm not found"}), 404
        return jsonify({"id": farm.id, "farm_name": farm.farm_name, "location": farm.location,
                        "crop_count": len(farm.crops)})

    @app.patch("/api/farms/<int:farm_id>")
    def update_farm(farm_id):
        farm = _owned_farm(farm_id)
        if not farm:
            return jsonify({"error": "Farm not found"}), 404
        data = _body()
        if "farm_name" in data:
            name = str(data.get("farm_name", "")).strip()
            if not name or len(name) > 160:
                return jsonify({"error": "farm_name is required and must be <= 160 characters"}), 400
            farm.farm_name = name
        if "location" in data:
            location = str(data.get("location", "")).strip()
            if len(location) > 255:
                return jsonify({"error": "location is too long"}), 400
            farm.location = location or None
        db.session.commit()
        return get_farm(farm_id)

    @app.delete("/api/farms/<int:farm_id>")
    def delete_farm(farm_id):
        farm = _owned_farm(farm_id)
        if not farm:
            return jsonify({"error": "Farm not found"}), 404
        db.session.delete(farm)
        db.session.commit()
        return jsonify({"deleted": True, "farm_id": farm_id})

    @app.get("/api/farms/<int:farm_id>/crops")
    def list_crops(farm_id):
        farm = _owned_farm(farm_id)
        if not farm:
            return jsonify({"error": "Farm not found"}), 404
        return jsonify({"count": len(farm.crops), "crops": [
            {"id": c.id, "farm_id": c.farm_id, "crop_name": c.crop_name,
             "scan_count": len(c.scans),
             "created_at": c.created_at.isoformat() if c.created_at else None}
            for c in sorted(farm.crops, key=lambda x: x.created_at or 0, reverse=True)
        ]})

    @app.post("/api/farms/<int:farm_id>/crops")
    def create_crop(farm_id):
        farm = _owned_farm(farm_id)
        if not farm:
            return jsonify({"error": "Farm not found"}), 404
        data = _body()
        name = str(data.get("crop_name", "")).strip()
        if not name or len(name) > 120:
            return jsonify({"error": "crop_name is required and must be <= 120 characters"}), 400
        crop = Crop(farm_id=farm.id, crop_name=name)
        db.session.add(crop)
        db.session.commit()
        return jsonify({"id": crop.id, "farm_id": crop.farm_id, "crop_name": crop.crop_name,
                        "scan_count": 0}), 201

    @app.get("/api/crops/<int:crop_id>")
    def get_crop(crop_id):
        crop = _owned_crop(crop_id)
        if not crop:
            return jsonify({"error": "Crop not found"}), 404
        return jsonify({"id": crop.id, "farm_id": crop.farm_id, "crop_name": crop.crop_name,
                        "scan_count": len(crop.scans)})

    @app.patch("/api/crops/<int:crop_id>")
    def update_crop(crop_id):
        crop = _owned_crop(crop_id)
        if not crop:
            return jsonify({"error": "Crop not found"}), 404
        data = _body()
        if "crop_name" in data:
            name = str(data.get("crop_name", "")).strip()
            if not name or len(name) > 120:
                return jsonify({"error": "crop_name is required and must be <= 120 characters"}), 400
            crop.crop_name = name
        if "farm_id" in data:
            try:
                target_farm_id = int(data.get("farm_id"))
            except (TypeError, ValueError):
                return jsonify({"error": "farm_id must be an integer"}), 400
            if not _owned_farm(target_farm_id):
                return jsonify({"error": "Target farm not found"}), 404
            crop.farm_id = target_farm_id
        db.session.commit()
        return get_crop(crop_id)

    @app.delete("/api/crops/<int:crop_id>")
    def delete_crop(crop_id):
        crop = _owned_crop(crop_id)
        if not crop:
            return jsonify({"error": "Crop not found"}), 404
        db.session.delete(crop)
        db.session.commit()
        return jsonify({"deleted": True, "crop_id": crop_id})

    @app.get("/api/scans")
    def scan_history_phase4():
        limit = max(1, min(request.args.get("limit", default=20, type=int), 100))
        query = Scan.query.filter_by(user_id=request.current_user.id)
        farm_id = request.args.get("farm_id", type=int)
        crop_id = request.args.get("crop_id", type=int)
        status = request.args.get("status", type=str)
        if farm_id is not None:
            query = query.filter_by(farm_id=farm_id)
        if crop_id is not None:
            query = query.filter_by(crop_id=crop_id)
        if status:
            query = query.filter_by(prediction_status=status.strip().lower())
        scans = query.order_by(Scan.created_at.desc()).limit(limit).all()
        return jsonify({"count": len(scans), "scans": [s.to_dict() for s in scans]})

    @app.post("/api/scans/<int:scan_id>/organize")
    def organize_scan(scan_id):
        scan = _owned_scan(scan_id)
        if not scan:
            return jsonify({"error": "Scan not found"}), 404
        data = _body()
        if "farm_id" in data:
            value = data.get("farm_id")
            if value is None:
                scan.farm_id = None
                scan.crop_id = None
            else:
                try:
                    farm_id = int(value)
                except (TypeError, ValueError):
                    return jsonify({"error": "farm_id must be an integer or null"}), 400
                if not _owned_farm(farm_id):
                    return jsonify({"error": "Farm not found"}), 404
                scan.farm_id = farm_id
        if "crop_id" in data:
            value = data.get("crop_id")
            if value is None:
                scan.crop_id = None
            else:
                try:
                    crop_id = int(value)
                except (TypeError, ValueError):
                    return jsonify({"error": "crop_id must be an integer or null"}), 400
                crop = _owned_crop(crop_id)
                if not crop:
                    return jsonify({"error": "Crop not found"}), 404
                if scan.farm_id is not None and crop.farm_id != scan.farm_id:
                    return jsonify({"error": "Crop does not belong to the selected farm"}), 400
                scan.crop_id = crop_id
        db.session.commit()
        return jsonify(scan.to_dict())
