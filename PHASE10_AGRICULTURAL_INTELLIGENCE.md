# Phase 10 — Agricultural Intelligence & Productization

Phase 10 upgrades ATHARVADRISHTI from prediction-only output toward a reusable agricultural intelligence layer while keeping the existing UI unchanged.

## What was added

### 1. Scan-level intelligence
`GET /api/scans/<scan_id>/intelligence`

Returns:
- the existing decision-support interpretation
- `attention_priority`: `routine`, `moderate`, or `high`
- a concise headline and rationale
- bilingual English/Hindi wording
- conservative next-step guidance
- product limitations

Use `?language=en` or `?language=hi`.

### 2. Crop-level intelligence
`GET /api/crops/<crop_id>/intelligence`

Aggregates the crop's scan history and reports:
- total/completed/rejected scans
- rejection rate
- average model confidence
- disease-prediction count
- disease rate across the most recent 10 completed scans
- repeated prediction patterns
- a monitoring priority: `routine`, `monitor`, `high_attention`, or `no_data`
- bilingual monitoring recommendation

### 3. Productization-safe design
The intelligence layer deliberately does **not**:
- claim a confirmed biological diagnosis
- estimate exact disease severity or infected area
- prescribe pesticides, doses, or treatment chemicals
- infer weather, soil, crop stage, cultivar, or field-wide prevalence from images alone

These constraints keep the new layer appropriate for decision support and future expert-review workflows.

## Example responses

### Scan intelligence
`GET /api/scans/42/intelligence?language=hi`

```json
{
  "prediction": "Tomato → Late blight",
  "reliability": "high",
  "attention_priority": "moderate",
  "headline": "निगरानी बढ़ाएँ"
}
```

### Crop intelligence
`GET /api/crops/7/intelligence?language=en`

```json
{
  "scan_count": 12,
  "disease_prediction_count": 7,
  "recent_10_disease_rate": 70.0,
  "risk_level": "high_attention"
}
```

## Architecture

`scan prediction -> decision support -> phase10 intelligence -> REST API`

The existing `templates/index.html`, `static/style.css`, and Streamlit interface are not modified by Phase 10.

## Next production step

For a production agricultural platform, the next layer should connect this deterministic intelligence to curated expert-reviewed evidence, field context, validated severity/segmentation models, and eventually mobile/cloud workflows. Any agronomic recommendation should remain traceable to its evidence and local/crop-specific validation.
