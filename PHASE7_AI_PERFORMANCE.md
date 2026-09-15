# Phase 7 — Real-World AI Performance & Model Improvement

Phase 7 adds a repeatable evaluation layer so model improvements are measured rather than assumed.

## What is included

- Consistent RGB → 224×224 → [0, 1] image preprocessing for evaluation.
- Labeled-dataset discovery using `data/<class_name>/*.{jpg,jpeg,png,webp}`.
- Top-1 accuracy and Top-3 accuracy measurement.
- Average model confidence and prediction margin measurement.
- Production rejection-rate measurement using the current confidence/margin policy.
- Field-robustness checks across horizontal flip and mild brightness changes.
- JSON evaluation reports for model/version comparison.
- CLI benchmark at `scripts/evaluate_model.py`.
- Regression tests included in CI.

## Run an evaluation

Place a validation set in class-named folders, for example:

```text
field_validation/
├── Apple_Scab/
│   ├── leaf_001.jpg
│   └── leaf_002.jpg
├── Apple_healthy/
│   └── leaf_003.jpg
└── ...
```

Then run:

```bash
python scripts/evaluate_model.py \
  --model general \
  --data-dir field_validation \
  --output evaluation_reports/general.json
```

For the Mango model:

```bash
python scripts/evaluate_model.py \
  --model mango \
  --data-dir mango_validation \
  --output evaluation_reports/mango.json
```

## Interpreting results

Do not treat confidence as accuracy. Compare Top-1 and Top-3 accuracy on labeled images, and separately monitor the production rejection rate and field-robustness consistency.

A model update should only be promoted after comparing it against a fixed validation set and recording the model version in the evaluation report.

## Current limitation

The repository does not include the large PlantDoc image dataset. Phase 7 therefore adds the evaluation infrastructure, but it does not claim a new accuracy percentage until a labeled validation set is actually run through the benchmark.
