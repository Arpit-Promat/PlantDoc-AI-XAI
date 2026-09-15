"""Phase 9 decision-support and crop analytics APIs."""

from collections import Counter

from flask import jsonify, request

from database import Crop, Farm, Scan
from decision_support import build_decision_support


def _owned_crop(crop_id):
    return (
        Crop.query.join(Farm, Crop.farm_id == Farm.id)
        .filter(Crop.id == crop_id, Farm.user_id == request.current_user.id)
        .first()
    )


def _owned_scan(scan_id):
    return Scan.query.filter_by(id=scan_id, user_id=request.current_user.id).first()


def register_phase9_routes(app):
    @app.get("/api/scans/<int:scan_id>/decision-support")
    def scan_decision_support(scan_id):
        scan = _owned_scan(scan_id)
        if scan is None:
            return jsonify({"error": "Scan not found"}), 404
        return jsonify(
            build_decision_support(
                scan.prediction,
                scan.confidence,
                scan.prediction_margin,
                scan.prediction_status,
            )
        )

    @app.get("/api/crops/<int:crop_id>/analytics")
    def crop_analytics(crop_id):
        crop = _owned_crop(crop_id)
        if crop is None:
            return jsonify({"error": "Crop not found"}), 404

        scans = list(crop.scans)
        completed = [s for s in scans if s.prediction_status == "completed"]
        rejected = [s for s in scans if s.prediction_status == "rejected"]
        predictions = [s.prediction for s in completed if s.prediction]
        disease_predictions = [p for p in predictions if "healthy" not in p.lower()]
        average_confidence = (
            round(sum(float(s.confidence) for s in completed if s.confidence is not None) / len(completed), 2)
            if any(s.confidence is not None for s in completed)
            else None
        )

        return jsonify({
            "crop_id": crop.id,
            "crop_name": crop.crop_name,
            "farm_id": crop.farm_id,
            "scan_count": len(scans),
            "completed_scans": len(completed),
            "rejected_scans": len(rejected),
            "rejection_rate": round((len(rejected) / len(scans)) * 100, 2) if scans else 0.0,
            "average_confidence": average_confidence,
            "healthy_prediction_count": len(predictions) - len(disease_predictions),
            "disease_prediction_count": len(disease_predictions),
            "most_common_predictions": [
                {"prediction": name, "count": count}
                for name, count in Counter(predictions).most_common(5)
            ],
        })
