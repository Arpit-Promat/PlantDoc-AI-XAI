# Phase 8 — Human-in-the-Loop & Continuous Learning

Phase 8 adds a controlled feedback loop so real-world prediction mistakes can be captured and later used for dataset curation and model improvement.

## Included

- `PredictionFeedback` database model linked to a scan and user.
- Authenticated feedback API:
  - `POST /api/feedback`
  - `GET /api/feedback`
  - `GET /api/feedback/<feedback_id>`
- Ownership checks prevent a user from submitting feedback against another user's scan.
- Corrected labels are required when a prediction is marked incorrect.
- Feedback records keep the original predicted label, optional corrected label, notes and review status.
- Existing Streamlit UI/templates are unchanged.

## Submit feedback

Use a valid Bearer token from `/api/auth/login` and send JSON:

```json
{
  "scan_id": 123,
  "is_prediction_correct": false,
  "corrected_label": "Tomato Late blight",
  "notes": "Visible dark lesions with yellow margins"
}
```

## Continuous-learning policy

Feedback is **evidence for review**, not automatic retraining. A corrected label should be treated as a candidate annotation until it has passed an appropriate review/label-quality process.

Before a new model is promoted:

1. Curate reviewed feedback into a fixed training/validation dataset.
2. Train a new candidate model with a new registry version.
3. Run the Phase 7 benchmark and compare Top-1/Top-3 accuracy, rejection rate and robustness.
4. Promote the new model only when the evaluation evidence supports the change.

This avoids silently learning from noisy or incorrect user feedback.
