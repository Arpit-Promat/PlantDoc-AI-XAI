# ATHARVADRISHTI — Curated ~57K Dataset Plan

The first expanded training corpus is capped at approximately **57,000 unique usable images** rather than attempting to train on the full 145K+ aggregate.

## Target composition

| Track | Target |
|---|---:|
| Leaf / condition images | ~45,000 |
| Field-style / robustness images | ~5,000 |
| Fruit images | ~5,000 |
| Hard negatives / non-leaf | ~2,000 |
| **Total** | **~57,000** |

These are targets, not fabricated counts. The actual number is determined after source download, validation, deduplication, label audit, and licensing review.

## Selection rules

1. Remove corrupt/unreadable images.
2. Remove exact duplicates using SHA-256.
3. Review near-duplicates using perceptual hashes.
4. Preserve class coverage instead of taking a random global sample.
5. Preserve field and controlled-condition diversity.
6. Keep healthy examples.
7. Do not invent or silently merge disease labels.
8. Keep train/validation/test groups separated by plant, capture session, field group, or near-duplicate group.
9. Keep research-only/licensing-restricted sources isolated until their terms are cleared.
10. Keep raw source data outside Git.

## Pipeline

After a source has been downloaded and audited:

```bash
python scripts/dataset_pipeline.py curate --source agri_foundation_145k --target-total 57000
```

This creates:

```
data/metadata/curated_manifest.csv
```

The curation step **does not delete raw images**. It creates a reproducible manifest so the selection can be reviewed before training.

## Important

The 57K cap is a first training target. It can later be increased if evaluation shows that additional unique, correctly labelled field data improves coverage.

The existing ATHARVADRISHTI scanner UI and current model artifacts are not changed by this dataset curation step.
