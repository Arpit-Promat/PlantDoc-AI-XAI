# Phase 9 — Advanced AI Intelligence & Decision Support

Phase 9 adds a deterministic decision-support layer on top of the existing plant-condition classifier. It does not claim confirmed biological diagnosis and does not prescribe pesticides.

## Included

- `decision_support.py` converts model labels into readable crop/condition information.
- Reliability classification combines prediction status, confidence and prediction margin.
- General next-step guidance is grouped by condition family.
- Clear limitations are returned with every decision-support response.
- `GET /api/scans/<scan_id>/decision-support` returns decision support for an authenticated user's scan.
- `GET /api/crops/<crop_id>/analytics` summarizes scan activity and prediction patterns for an owned crop.
- Crop analytics include scan count, completed/rejected counts, rejection rate, average confidence, healthy/disease prediction counts, and common predictions.
- Phase 9 regression tests are included in CI.
- Existing Streamlit UI and templates are unchanged.

## Why this is safe

The system does not convert an image classification into an automatic treatment prescription. It provides observation-oriented next steps and explicitly tells the user when a prediction is uncertain.

## Example

For `Tomato___Late_blight`, the API can return:

- readable prediction: `Tomato → Late blight`
- crop: `Tomato`
- condition family
- reliability level
- monitoring/inspection suggestions
- limitations about diagnosis and severity

## Important limitation

Phase 9 does not estimate exact disease severity or infected-area percentage. That requires a separate, labeled severity/segmentation dataset and a validated model. Such a model should be added only after the Phase 7 evaluation workflow demonstrates reliable performance.
