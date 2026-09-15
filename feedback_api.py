"""Human-in-the-loop feedback APIs for model improvement."""

from flask import jsonify, request

from database import PredictionFeedback, Scan, db


def register_feedback_routes(app):
    @app.post("/api/feedback")
    def submit_feedback():
        scan_id = request.json.get("scan_id") if request.is_json else None
        if not isinstance(scan_id, int):
            return jsonify({"error": "scan_id is required"}), 400

        scan = Scan.query.filter_by(id=scan_id, user_id=request.current_user.id).first()
        if scan is None:
            return jsonify({"error": "Scan not found"}), 404

        data = request.get_json(silent=True) or {}
        correct = data.get("is_prediction_correct")
        corrected_label = str(data.get("corrected_label", "")).strip()
        notes = str(data.get("notes", "")).strip()

        if correct is not None and not isinstance(correct, bool):
            return jsonify({"error": "is_prediction_correct must be true or false"}), 400
        if len(corrected_label) > 255 or len(notes) > 1000:
            return jsonify({"error": "Feedback field is too long"}), 400
        if correct is False and not corrected_label:
            return jsonify({"error": "corrected_label is required when prediction is incorrect"}), 400

        existing = PredictionFeedback.query.filter_by(
            scan_id=scan.id,
            user_id=request.current_user.id,
        ).first()
        if existing:
            existing.predicted_label = scan.prediction
            existing.corrected_label = corrected_label or None
            existing.is_prediction_correct = correct
            existing.notes = notes or None
            existing.review_status = "updated"
            feedback = existing
        else:
            feedback = PredictionFeedback(
                scan_id=scan.id,
                user_id=request.current_user.id,
                predicted_label=scan.prediction,
                corrected_label=corrected_label or None,
                is_prediction_correct=correct,
                notes=notes or None,
                review_status="submitted",
            )
            db.session.add(feedback)

        db.session.commit()
        return jsonify(feedback.to_dict()), 200

    @app.get("/api/feedback")
    def list_feedback():
        limit = max(1, min(request.args.get("limit", default=50, type=int), 200))
        items = (
            PredictionFeedback.query
            .filter_by(user_id=request.current_user.id)
            .order_by(PredictionFeedback.created_at.desc())
            .limit(limit)
            .all()
        )
        return jsonify({"count": len(items), "feedback": [item.to_dict() for item in items]})

    @app.get("/api/feedback/<int:feedback_id>")
    def get_feedback(feedback_id):
        item = PredictionFeedback.query.filter_by(
            id=feedback_id,
            user_id=request.current_user.id,
        ).first()
        if item is None:
            return jsonify({"error": "Feedback not found"}), 404
        return jsonify(item.to_dict())
