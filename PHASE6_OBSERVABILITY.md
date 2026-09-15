# Phase 6 — Observability & Production Reliability

Phase 6 improves operational reliability without changing the existing Streamlit UI.

## Runtime observability

`observability.py` provides lightweight structured logging with:

- event names
- elapsed operation time
- model identifiers
- prediction status
- safe error types

Sensitive image contents and credentials are not written to logs.

## Flask health diagnostics

Two public diagnostic endpoints were added:

- `GET /api/system/health` — database connectivity and loaded model status.
- `GET /api/system/models` — model names and registry identifiers without filesystem paths.

`/api/system/health` returns HTTP 200 when the database and all three configured models are loaded, otherwise HTTP 503 with `degraded` status.

## CI regression checks

GitHub Actions now runs `tests/test_prediction_engine.py` for pushes and pull requests targeting `main`.

The tests verify probability normalization, Top-3 ranking, confidence/margin rejection, and model registry identifiers.

## Deployment verification

After deployment, verify:

1. The Streamlit app opens successfully.
2. A normal leaf image still produces the same UI flow.
3. Existing SHAP/attention output still works.
4. Flask deployments can report `/api/system/health` as `ok`.
5. GitHub Actions shows the prediction-engine test job passing.

The Streamlit UI and its visual structure were intentionally left unchanged in Phase 6.
