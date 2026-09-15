# Phase 5 — AI & Prediction Upgrade

## Implemented

- Central model registry in `model_registry.py` with explicit versions for the general classifier, Mango classifier, and leaf detector.
- Shared prediction engine in `prediction_engine.py` for probability normalization, top-k ranking, confidence levels, prediction margin, and acceptance/rejection policy.
- Flask inference now uses the shared prediction engine instead of duplicating prediction math.
- Celery background inference now uses the same prediction engine as synchronous Flask inference.
- Scan history records model version, confidence, prediction margin, leaf probability, and top-3 predictions where available.
- Existing confidence policy remains conservative: accept only when confidence is at least 60% and the top-1 vs top-2 margin is at least 20 percentage points.
- Existing Streamlit UI has not been redesigned or modified as part of this phase.

## Current model versions

| Model | Version |
|---|---|
| PlantDoc General Classifier | 1.0.0 |
| Mango Disease Classifier | 1.0.0 |
| Leaf / Non-Leaf Detector | 1.0.0 |

Model versions are intentionally explicit so a future retrained model can be introduced as a new version without losing prediction traceability.

## Not yet claimed

This phase does not claim calibrated probabilities, field-condition accuracy, disease severity measurement, or agricultural treatment recommendations. Those require validation data and/or additional model development.
