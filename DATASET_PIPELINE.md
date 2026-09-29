# ATHARVADRISHTI Dataset Pipeline

This is the implementation layer for the maximum dataset expansion plan.

## Added

- metadata/dataset_sources.json — source registry, expected scale, license status and bucket.
- scripts/dataset_pipeline.py — download, safe ZIP extraction, image validation, SHA-256 and perceptual hashing, audit CSV and manifest.
- Large datasets remain outside Git.

## Run

From the repository root:

    python scripts/dataset_pipeline.py init

Then, for the first large source:

    python scripts/dataset_pipeline.py download agri_foundation_145k
    python scripts/dataset_pipeline.py audit --source agri_foundation_145k

After multiple sources are collected:

    python scripts/dataset_pipeline.py audit
    python scripts/dataset_pipeline.py manifest

## Rules

1. Never commit the image datasets to GitHub.
2. Preserve source labels and original paths.
3. Treat licensing as a gate before training.
4. Deduplicate globally with SHA-256; use perceptual hashes for later visual-similarity review.
5. Do not invent canonical disease labels.
6. Keep research-only data isolated from product training.
7. Split by plant/capture/session where metadata supports it.
8. Apply augmentation only after train/validation/test splitting.
9. Keep a locked field test set.

The source registry is deliberately conservative: sources without a verified direct download endpoint are recorded with their official page and must be downloaded manually into the correct bucket.
