# ATHARVADRISHTI — Maximum Dataset Expansion Plan

Updated: 2026-09-29

## Goal

Expand ATHARVADRISHTI from the current baseline into a large, multi-crop, field-robust agricultural vision dataset while keeping provenance, licensing, deduplication, and test-set integrity.

The objective is **maximum usable coverage**, not simply maximum image count.

## Priority dataset pool

### Tier 1 — commercial/product-track candidates

These should be audited for their exact license and source terms before inclusion in a commercial model.

1. **Agri-Foundation-145k**
   - 144,751 images
   - 215 classes
   - aggregates 8 open-access sources: PlantVillage, PlantDoc, New Plant Diseases, Tomato Leaf, Cassava, Wheat, PlantSeg and PlantWild
   - 10.4 GB archive
   - Zenodo record: https://zenodo.org/records/18214758
   - IMPORTANT: this is an aggregate and therefore does not automatically inherit one simple license for every underlying image. Keep source-level provenance and license metadata.

2. **PlantVillage**
   - 54,306 images
   - 14 crop species
   - 38 classes
   - Official source: https://github.com/spMohanty/PlantVillage-Dataset
   - Use official leaf grouping/splits where applicable.

3. **PlantDoc**
   - ~2,598 real-field images
   - complex backgrounds, natural illumination and occlusion
   - Use primarily for field robustness and compatible classes.
   - Do not assume its labels cover the full ATHARVADRISHTI taxonomy.

4. **15-Crop / 45-Disease-and-Healthy leaf datasets**
   - Indian-relevant crops including Cashew, Cassava, Tomato, Potato, Maize, Papaya, Sugarcane, Rice, Chilli, Grapes, Citrus, Groundnut, Cotton, Wheat and Soyabean.
   - Source pages:
     https://data.mendeley.com/datasets/8fr7grr73p/1
     https://data.mendeley.com/datasets/ph9g2cfxwm/1

5. **Fruit + Leaf six-crop dataset**
   - Apple, Banana, Citrus, Guava, Mango, Papaya
   - Use for plant-part expansion and field-style variability.
   - https://data.mendeley.com/datasets/fhbvmpcyy2/1

6. **Additional Mango / Guava datasets**
   - Use to increase field diversity only after deduplication and license verification.

## Tier 2 — research/benchmark track, NOT automatically product training

### PlantWild v1 + v2

- v1: 18,542 images / 89 classes
- v2: 11,488 images / 115 disease-only classes
- real-world/in-the-wild images
- source: https://huggingface.co/datasets/uqtwei2/PlantWild
- License: CC BY-NC-ND 4.0

Because the license is NonCommercial-NoDerivatives, **do not silently place PlantWild images into a commercial/startup training corpus**. Keep it in a research benchmark bucket unless legal/licensing review establishes permitted use.

## Tier 3 — specialized tracks

Add when source terms and labels are verified:

- Cassava disease datasets
- Rice disease datasets
- Wheat disease datasets
- Tomato disease datasets
- Apple Plant Pathology datasets
- pest datasets such as IP102
- crop-pest detection datasets
- segmentation datasets such as PlantSeg
- severity-annotated datasets
- field smartphone datasets
- locally collected India field images

Pest and segmentation data should not be forced into the same image-level disease-classifier labels.

## Target architecture

Do NOT create one giant flat classifier containing every image label.

Use:

IMAGE
→ Plant/Not-Plant Gate
→ Plant Part
→ Crop
→ Condition Family
→ Specific Condition
→ Confidence/Reject
→ Explanation
→ Knowledge Base

### Plant Part

- leaf
- fruit
- flower
- stem
- whole plant
- seed/ear/panicle where supported
- unknown

### Condition Family

- healthy
- fungal
- bacterial
- viral
- pest
- nutrient deficiency
- abiotic stress
- physical damage
- unknown

## Maximum-coverage taxonomy target

The long-term taxonomy should be data-driven.

Instead of fixing a small number of crops, build the master catalog from all verified source datasets:

- crop
- cultivar/variety where available
- plant part
- condition
- pathogen/agent where known
- severity
- field/lab
- geographic region where licensed and available

A class becomes an **active prediction class** only when it has sufficient verified images and a corresponding disease-information record.

## Data buckets

Store datasets separately:

data/
  raw/
    commercial_candidate/
    research_only/
    plantvillage/
    plantdoc/
    mendeley/
    plantwild/
    custom_field/

  processed/
    gate/
    plant_part/
    crop/
    leaf_condition/
    fruit_condition/
    flower_condition/
    pest/
    segmentation/
    severity/

  metadata/
    dataset_sources.json
    class_mapping.json
    image_manifest.parquet
    split_manifest.csv
    license_manifest.csv
    dedup_manifest.csv
    disease_information.json

## Non-negotiable rules

1. Never count duplicates from multiple datasets as independent evidence.
2. Preserve original source label and canonical ATHARVADRISHTI label.
3. Preserve source URL/DOI and license.
4. Use SHA-256 plus perceptual hashing for duplicate detection.
5. Keep plant/capture/session groups together during splitting.
6. Never put augmented copies into validation or test.
7. Keep a locked field test set.
8. Do not manufacture disease labels for crops where the source does not support them.
9. Do not mix pest, disease and nutrient-deficiency labels without condition_type metadata.
10. Do not use research-only/non-commercial data in a commercial training release without checking the license.

## Scale targets

### Phase A — baseline expansion

~70k usable images

### Phase B — maximum public-data research corpus

Potentially **150k+ unique images** after deduplication, depending on source overlap and licensing.

The 144,751-image Agri-Foundation benchmark is a major candidate for this scale, but it is an aggregate of multiple sources and must be audited at source level before being treated as a clean commercial corpus.

### Phase C — product-grade field corpus

Target:

**250k+ images**, but prioritize new field/crop/region/condition diversity over repeated near-identical images.

This phase should include original India field photography with consent/provenance and expert/domain review where possible.

## Quality target

For every active class, record:

- usable image count
- unique plant/subject count
- field vs controlled percentage
- source count
- region count when available
- label verification status
- license status
- duplicate rate
- train/val/test counts

Do not define dataset quality by image count alone.

## Training strategy

1. Build a unified metadata index.
2. Download/source raw datasets.
3. Verify license.
4. Extract labels.
5. Normalize labels.
6. Deduplicate globally.
7. Group by plant/capture/source session.
8. Create train/validation/test splits.
9. Train specialist models.
10. Evaluate cross-dataset and field performance.
11. Activate only validated classes.
12. Link every activated disease to disease_information.json.

## Model families

### Model A
Plant / Not-Plant

### Model B
Plant Part

### Model C
Crop Identification

### Model D
Leaf Condition

### Model E
Fruit Condition

### Model F
Flower Condition

### Model G
Pest Detection

### Model H
Disease/lesion Segmentation

### Model I
Severity Estimation

The existing ATHARVADRISHTI scanner remains the user-facing entry point; model routing can evolve behind it.

## Immediate next step

Do **not** manually download dozens of ZIPs into the repository.

First build a reproducible dataset acquisition/audit pipeline that:

- records every source
- downloads to data/raw
- verifies checksums
- extracts labels
- generates the master manifest
- detects duplicates
- applies license buckets
- produces canonical train/val/test folders

Only after this audit should the new data be used for training.
