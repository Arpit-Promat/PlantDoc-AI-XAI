"""Phase 10 agricultural intelligence APIs."""

from flask import jsonify, request

from database import Crop, Farm, Scan
from phase10_intelligence import build_crop_intelligence, build_scan_intelligence


def _owned_crop(crop_id):
    return (
        Crop.query.join(Farm, Crop.farm_id == Farm.id)
        .filter(Crop.id == crop_id, Farm.user_id == request.current_user.id)
        .first()
    )


def _owned_scan(scan_id):
    return Scan.query.filter_by(id=scan_id, user_id=request.current_user.id).first()


def _language():
    return request.args.get("language", "en").strip().lower()


def register_phase10_routes(app):
    @app.get("/api/scans/<int:scan_id>/intelligence")
    def scan_intelligence(scan_id):
        scan = _owned_scan(scan_id)
        if scan is None:
            return jsonify({"error": "Scan not found"}), 404

        return jsonify(
            build_scan_intelligence(
                scan.prediction,
                scan.confidence,
                scan.prediction_margin,
                scan.prediction_status,
                _language(),
            )
        )

    @app.get("/api/crops/<int:crop_id>/intelligence")
    def crop_intelligence(crop_id):
        crop = _owned_crop(crop_id)
        if crop is None:
            return jsonify({"error": "Crop not found"}), 404

        return jsonify(build_crop_intelligence(crop.scans, _language()))
