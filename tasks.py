"""Optional background task queue for scalable AI inference."""

import os
from datetime import datetime, timezone

from celery import Celery


def create_celery():
    broker = os.getenv("CELERY_BROKER_URL") or os.getenv("REDIS_URL") or "redis://localhost:6379/0"
    backend = os.getenv("CELERY_RESULT_BACKEND") or broker
    celery = Celery("atharvadrishti", broker=broker, backend=backend)
    celery.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        task_track_started=True,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        task_time_limit=int(os.getenv("CELERY_TASK_TIME_LIMIT", "300")),
        task_soft_time_limit=int(os.getenv("CELERY_TASK_SOFT_TIME_LIMIT", "270")),
        result_expires=int(os.getenv("CELERY_RESULT_EXPIRES", "3600")),
    )
    return celery


celery = create_celery()


@celery.task(bind=True, name="atharvadrishti.predict_scan")
def predict_scan(self, scan_id):
    """Run an existing queued scan through the same model logic as Flask."""
    import numpy as np
    from tensorflow.keras.preprocessing import image
    from app import (
        CONFIDENCE_THRESHOLD,
        MARGIN_THRESHOLD,
        app as flask_app,
        get_model_and_classes,
        is_leaf_image,
    )
    from database import Scan, db

    with flask_app.app_context():
        scan = db.session.get(Scan, int(scan_id))
        if scan is None:
            return {"status": "not_found", "scan_id": scan_id}

        scan.prediction_status = "processing"
        db.session.commit()

        try:
            model, class_names = get_model_and_classes(scan.plant_type)
            if not scan.image_path:
                raise ValueError("Missing scan image path")

            file_path = os.path.join(flask_app.root_path, scan.image_path.lstrip("/"))
            img = image.load_img(file_path, target_size=(224, 224))
            arr = image.img_to_array(img) / 255.0
            input_image = np.expand_dims(arr, axis=0)

            is_leaf, leaf_probability = is_leaf_image(input_image)
            scan.leaf_probability = round(float(leaf_probability) * 100, 2)

            if not is_leaf:
                scan.prediction_status = "rejected"
                scan.error_message = "Image was not classified as a leaf."
            else:
                pred = model.predict(input_image, verbose=0)[0]
                if len(pred) < 2:
                    raise ValueError("Invalid model output")

                idx = int(np.argmax(pred))
                scan.prediction = class_names[idx] if idx < len(class_names) else f"Class {idx}"
                scan.confidence = round(float(pred[idx]) * 100, 2)
                sorted_pred = np.sort(pred)[::-1]
                scan.prediction_margin = round((float(sorted_pred[0]) - float(sorted_pred[1])) * 100, 2)
                scan.model_used = "mango_model" if scan.plant_type == "mango" else "plantdoc_model"

                if scan.confidence < CONFIDENCE_THRESHOLD or scan.prediction_margin < MARGIN_THRESHOLD:
                    scan.prediction_status = "rejected"
                    scan.error_message = "Confidence or prediction margin below threshold."
                else:
                    scan.prediction_status = "completed"
                    scan.error_message = None

            scan.completed_at = datetime.now(timezone.utc)
            db.session.commit()
            return {"status": scan.prediction_status, "scan_id": scan.id, "prediction": scan.prediction}
        except Exception as exc:
            db.session.rollback()
            scan = db.session.get(Scan, int(scan_id))
            if scan is not None:
                scan.prediction_status = "failed"
                scan.error_message = "Background prediction failed."
                scan.completed_at = datetime.now(timezone.utc)
                db.session.commit()
            raise RuntimeError(f"prediction task failed: {exc}") from exc
