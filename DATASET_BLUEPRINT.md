
# ATHARVADRISHTI — Exact Dataset Blueprint (V1)

**Product:** ATHARVADRISHTI — An Intelligent and Explainable Plant Health Analysis System  
**Repository:** Arpit-Promat/PlantDoc-AI-XAI  
**Purpose:** Define the exact V1 data taxonomy, target image counts, folder structure, annotation schema, source audit rules, and training pipeline before expanding the current leaf-only classifier.

## 1. V1 target in one view

### Target unique image corpus

| Track | Target images | Purpose |
|---|---:|---|
| Leaf condition | **53,200** | 76 leaf condition classes × 700 target images/class |
| Hard negatives / non-leaf | **5,000** | Reject people, objects, food, documents, screenshots, backgrounds, etc. |
| Fruit | **8,000** | Plant-part + crop + healthy/diseased/damaged data; disease subclasses enabled only after label audit |
| Flower | **4,000** | Plant-part recognition first; disease taxonomy added only after verified flower-disease sources are curated |
| **Total** | **70,200** | V1 unique image target |

The plant-part and crop labels are metadata attached to the same images; they are not additional images.

### V1 taxonomy

- 24 crops
- 76 leaf condition labels
  - 24 healthy labels
  - 52 disease / pest / stress labels
- 4 plant-part labels
  - leaf
  - fruit
  - flower
  - whole_plant
- 2 gate labels
  - plant
  - not_plant

The existing repository's general model currently has 38 PlantVillage-style classes and the Mango model has 8 classes. V1 keeps those labels compatible and expands around them rather than renaming the existing model artifacts.

## 2. Crop list — exact V1 crop taxonomy

### Group A — existing PlantVillage coverage

1. Apple
2. Blueberry
3. Cherry
4. Corn
5. Grape
6. Orange / Citrus
7. Peach
8. Bell Pepper
9. Potato
10. Raspberry
11. Soybean
12. Squash
13. Strawberry
14. Tomato

PlantVillage documents 54,306 images, 38 disease/health classes, and 14 crop species. Its current class mapping is the basis for the repository's 38-class general model.

Source:
https://github.com/spMohanty/PlantVillage-Dataset/blob/master/README_HF.md

### Group B — added India-relevant crops

15. Mango
16. Cashew
17. Cassava
18. Chilli
19. Cotton
20. Groundnut
21. Rice
22. Wheat
23. Papaya
24. Sugarcane

The 2026 Mendeley 15-crop / 45-disease-and-healthy dataset explicitly lists Cashew, Cassava, Tomato, Potato, Maize, Papaya, Sugarcane, Rice, Chilli, Grapes, Citrus, Groundnut, Cotton, Wheat and Soyabean.

Source:
https://data.mendeley.com/datasets/8fr7grr73p/1

## 3. Exact V1 leaf class taxonomy

### Naming rule

Every leaf classifier label uses:

    <Crop>__Leaf__<Condition>

Example:

    Tomato__Leaf__Early_Blight

Do not create synonyms such as Tomato-EarlyBlight, Tomato_Early_Blight, or TomatoEarlyBlight.

### Full class table

| # | Crop | Healthy | Disease / pest / stress labels | Target images |
|---:|---|---|---|---:|
| 1 | Apple | Healthy | Apple Scab; Black Rot; Cedar Apple Rust | 2,800 |
| 2 | Blueberry | Healthy | — | 700 |
| 3 | Cherry | Healthy | Powdery Mildew | 1,400 |
| 4 | Corn | Healthy | Cercospora/Gray Leaf Spot; Common Rust; Northern Leaf Blight; Leaf Spot; Maize Streak Virus | 4,200 |
| 5 | Grape | Healthy | Black Rot; Esca/Black Measles; Leaf Blight/Isariopsis Leaf Spot | 2,800 |
| 6 | Orange/Citrus | Healthy | Huanglongbing/Citrus Greening | 1,400 |
| 7 | Peach | Healthy | Bacterial Spot | 1,400 |
| 8 | Bell Pepper | Healthy | Bacterial Spot | 1,400 |
| 9 | Potato | Healthy | Early Blight; Late Blight | 2,100 |
| 10 | Raspberry | Healthy | — | 700 |
| 11 | Soybean | Healthy | Frog Leaf Eye; Mosaic | 2,100 |
| 12 | Squash | Healthy | Powdery Mildew | 1,400 |
| 13 | Strawberry | Healthy | Leaf Scorch | 1,400 |
| 14 | Tomato | Healthy | Bacterial Spot; Early Blight; Late Blight; Leaf Mold; Septoria Leaf Spot; Spider Mites/Two-Spotted Spider Mite; Target Spot; Tomato Yellow Leaf Curl Virus; Tomato Mosaic Virus | 7,000 |
| 15 | Mango | Healthy | Anthracnose; Bacterial Canker; Cutting Weevil; Die Back; Gall Midge; Powdery Mildew; Sooty Mould | 5,600 |
| 16 | Cashew | Healthy | Leaf Miner; Red Rust | 2,100 |
| 17 | Cassava | Healthy | Brown Spot; Mosaic | 2,100 |
| 18 | Chilli | Healthy | Nutrition Deficiency; White Spot | 2,100 |
| 19 | Cotton | Healthy | Bacterial Blight; Curl Virus | 2,100 |
| 20 | Groundnut | Healthy | Late Leaf Spot; Nutrition Deficiency | 2,100 |
| 21 | Rice | Healthy | Brown Spot; Leaf Blast | 2,100 |
| 22 | Wheat | Healthy | Brown Rust; Yellow Rust | 2,100 |
| 23 | Papaya | Healthy | **Disease subclasses pending source/label audit** | 700 |
| 24 | Sugarcane | Healthy | **Disease subclasses pending source/label audit** | 700 |
| | **Total** | **24** | **52 defined disease/pest/stress labels** | **53,200** |

Papaya and Sugarcane are included as crops, but no disease class is to be invented. Their disease labels are activated only after the downloaded source folders are inspected and a source-to-canonical mapping is recorded.

The 38 PlantVillage labels are source-defined. The added crop/condition labels are an ATHARVADRISHTI blueprint taxonomy and must be matched against downloaded source folders before training.

## 4. Source mapping — ready vs needs curation

### Source A — current ATHARVADRISHTI repository

Already aligned with:

- 38 general classes from models/class_names.json
- 8 Mango classes from models/mango_class_names.json

Mango labels:
- Anthracnose
- Bacterial Canker
- Cutting Weevil
- Die Back
- Gall Midge
- Healthy
- Powdery Mildew
- Sooty Mould

### Source B — PlantVillage

Use primarily for leaf disease baseline classes.

PlantVillage reports 54,306 images and 38 class labels over 14 crop species.

Source:
https://github.com/spMohanty/PlantVillage-Dataset

### Source C — Mendeley 15 Crop / 45 Disease and Healthy

Use for expanding India-relevant crop coverage.

The dataset page lists:

- Cashew
- Cassava
- Tomato
- Potato
- Maize
- Papaya
- Sugarcane
- Rice
- Chilli
- Grapes
- Citrus
- Groundnut
- Cotton
- Wheat
- Soyabean

License shown on the dataset page: CC BY 4.0.

Sources:
https://data.mendeley.com/datasets/8fr7grr73p/1
https://data.mendeley.com/datasets/ph9g2cfxwm/1

### Source D — six-crop fruit + leaf dataset

Covers:

- Apple
- Banana
- Citrus
- Guava
- Mango
- Papaya

and includes healthy/diseased fruit and leaf imagery with real-cultivation variation.

License shown on the dataset page: CC BY 4.0.

Source:
https://data.mendeley.com/datasets/fhbvmpcyy2/1

Use this source for the fruit track and field-style robustness, not as an automatic source of canonical disease names without inspecting its downloaded folder/labels.

### Source E — 2026 published label cross-check

A recent Frontiers study reproduces a 33-category subset from public datasets and explicitly shows labels such as:

- Cashew: Healthy, Leaf Miner, Red Rust
- Cassava: Brown Spot, Healthy, Mosaic
- Chilli: Healthy, Nutrition Deficiency, White Spot
- Cotton: Bacterial Blight, Curl Virus, Healthy
- Groundnut: Healthy, Late Leaf Spot, Nutrition Deficiency
- Potato: Early Blight, Healthy, Late Blight
- Soybean: Frog Leaf Eye, Healthy, Mosaic
- Tomato: Healthy, Leaf Mold, Septoria Leaf Spot
- Grape: Black Rot, Esca, Healthy
- Apple: Apple Scab, Cedar Apple Rust, Healthy

Source:
https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2026.1901116/full

This paper is a cross-check for labels, not a replacement for the primary downloaded datasets.

## 5. Exact folder structure

Do not put the full image corpus inside the Git repository.

Use data/raw for downloaded source datasets and data/processed for normalized training data.

    data/
    ├── raw/
    │   ├── plantvillage/
    │   ├── mendeley_15crop/
    │   ├── fruit_leaf_6crop/
    │   ├── plantdoc/
    │   └── custom_field/
    │
    ├── processed/
    │   ├── gate/
    │   │   ├── train/
    │   │   ├── val/
    │   │   └── test/
    │   ├── plant_part/
    │   │   ├── train/
    │   │   ├── val/
    │   │   └── test/
    │   ├── crop/
    │   │   ├── train/
    │   │   ├── val/
    │   │   └── test/
    │   ├── leaf_condition/
    │   │   ├── train/
    │   │   ├── val/
    │   │   └── test/
    │   ├── fruit_condition/
    │   │   ├── train/
    │   │   ├── val/
    │   │   └── test/
    │   └── flower_condition/
    │       ├── train/
    │       ├── val/
    │       └── test/
    │
    └── metadata/
        ├── dataset_sources.json
        ├── class_mapping.json
        ├── disease_information.json
        ├── split_manifest.csv
        └── review_log.csv

## 6. Canonical image ID

Every processed image gets:

    AD_<SOURCE>_<CROP>_<PART>_<CLASS>_<HASH8>

Example:

    AD_PV_TOMATO_LEAF_EARLYBLIGHT_a91c42e8

Required metadata:

    image_id
    source_dataset
    source_license
    source_original_path
    crop
    plant_part
    condition
    condition_type
    canonical_label
    original_label
    healthy_or_not
    field_or_controlled
    capture_session_id
    plant_or_plot_id
    split
    sha256
    review_status
    expert_verified
    notes

## 7. Condition types

Allowed values:

    healthy
    fungal
    bacterial
    viral
    pest
    nutrient_deficiency
    abiotic_stress
    unknown

Example:

    Tomato__Leaf__Early_Blight
    condition_type = fungal
    healthy_or_not = false

Example:

    Tomato__Leaf__Tomato_Yellow_Leaf_Curl_Virus
    condition_type = viral
    healthy_or_not = false

Example:

    Chilli__Leaf__Nutrition_Deficiency
    condition_type = nutrient_deficiency
    healthy_or_not = false

## 8. Plant-part taxonomy

V1:

    leaf
    fruit
    flower
    whole_plant

The same crop can therefore appear as:

    Mango__Leaf__Anthracnose
    Mango__Fruit__<audited-condition>
    Mango__Flower__<audited-condition>

Do not infer that a disease observed on a leaf has the same visual signature on fruit or flower. Fruit and flower receive their own model/evaluation track.

## 9. Fruit track — V1 scope

### Initial fruit crops

1. Apple
2. Banana
3. Citrus
4. Guava
5. Mango
6. Papaya

These six crops are explicitly covered by the 2026 Mendeley fruit + leaf dataset.

### Fruit target

**8,000 images**

Minimum metadata:

    crop
    plant_part = fruit
    health_status
    condition
    severity_stage
    source
    field_or_controlled
    expert_verified

### Fruit disease rule

Do not create disease names from visual guesswork.

Process:

    download source
         ↓
    inspect folders / labels
         ↓
    map original labels
         ↓
    verify disease name
         ↓
    add canonical label
         ↓
    add disease knowledge record
         ↓
    only then include in training

## 10. Flower track — V1 scope

The first flower track is plant-part recognition and image-quality support, not an unrestricted flower-disease classifier.

Target:

**4,000 images**

Labels:

    flower
    not_flower
    uncertain

For crop-specific flower diseases, first create a verified source table and domain review. Do not invent a list of all flower diseases.

## 11. Hard-negative dataset

Target:

**5,000 images**

Include:

    people
    hands
    faces
    documents
    screenshots
    soil only
    sky
    walls
    food
    tables
    bags
    cars
    animals
    random objects
    non-leaf plant parts
    blurred images
    extreme darkness
    extreme glare
    very distant plants

Required behavior:

    non-plant / invalid
            ↓
    "Not a plant image"

and

    plant but unsupported part
            ↓
    "Plant detected, but this plant part is outside the current analysis scope"

## 12. Training split

Default:

- 70% train
- 15% validation
- 15% test

The split must be performed by plant / capture session / field group, not by random image only.

Rule:

> Images originating from the same physical plant, leaf, fruit, flower, capture session, or near-duplicate group must remain in the same split.

### Additional field robustness test

Keep a separate untouched field-style test set where possible:

    field_test/
    ├── leaf/
    ├── fruit/
    └── flower/

Do not use this set for training or hyperparameter tuning.

## 13. Image preprocessing

Canonical stored version:

- RGB
- JPEG
- target storage resolution: 256×256
- JPEG quality: approximately 80–82

Model input remains:

- 224×224
- float32
- normalized to 0–1

The repository's current MobileNetV2 scanner already uses 224×224 input, so V1 does not require changing that interface.

## 14. Quality-control rules

Reject an image when:

- corrupted/unreadable
- duplicate or near-duplicate
- label cannot be verified
- disease is not visually represented in the image when the source claims it is
- image is too blurred for the intended task
- plant part is wrong for the target label
- the image contains a different crop than the folder label
- the image contains only background with no useful target

Flag for review when:

- symptoms are very mild
- multiple conditions may be visible
- disease stage is unclear
- nutrient deficiency vs disease is ambiguous
- pest damage and disease symptoms overlap
- the source label is vague

## 15. Balance target

### Leaf condition classes

**700 usable images/class target**

For classes with fewer public images:

- do not duplicate to pretend the class is larger
- use augmentation only on training data
- label the class as underrepresented
- consider class-weighted loss
- collect additional field images

Healthy classes also target approximately 700 real images/class.

## 16. Disease knowledge base linkage

Every disease/pest/stress label that can appear in the UI must have a corresponding knowledge record.

Required fields:

    canonical_label
    crop
    plant_part
    display_name
    condition_type
    what_it_is
    cause_or_agent
    how_it_occurs
    how_it_spreads
    common_symptoms
    prevention
    management
    cure_status
    warning
    source_name
    source_url
    reviewed_date
    verification_status

Prediction linkage:

    prediction
       ↓
    canonical_label
       ↓
    disease_information.json
       ↓
    display name
    cause
    symptoms
    occurrence
    prevention
    management
    sources

Use Management / Treatment rather than guaranteeing a cure. Some plant diseases, particularly viral diseases, may have no curative treatment; management can instead focus on sanitation, resistant material, vector control and spread reduction according to crop-specific guidance.

## 17. Model pipeline after V1

    IMAGE
      │
      ▼
    Plant / Not-Plant Gate
      │
      ├── Not Plant ─────────► REJECT
      │
      ▼
    Plant-Part Classifier
      │
      ├── Leaf
      ├── Fruit
      ├── Flower
      └── Whole Plant
      │
      ▼
    Crop Classifier
      │
      ▼
    Condition Classifier
      │
      ├── Healthy
      ├── Fungal
      ├── Bacterial
      ├── Viral
      ├── Pest
      ├── Nutrient deficiency
      └── Other supported condition
      │
      ▼
    Confidence + Margin Gate
      │
      ├── Uncertain ───────► Ask for clearer image / expert review
      │
      ▼
    Prediction
      │
      ▼
    SHAP / visual explanation
      │
      ▼
    Disease Knowledge Base
      │
      ▼
    Cause + Occurrence + Symptoms + Prevention + Management + Sources

## 18. Current scanner compatibility

**The existing scanner UI is preserved.**

Current visible flow remains:

    upload / camera
         ↓
    preview
         ↓
    Analyze Image button
         ↓
    leaf validation
         ↓
    current general classifier
         ↓
    confidence
         ↓
    top predictions
         ↓
    SHAP / explanation
         ↓
    disease information

V1 adds backend/model-routing capability around this flow. The visible scanner should not be redesigned just because the dataset becomes larger.

## 19. V1 implementation order

### Step 1 — Freeze current baseline

Keep:

    models/plantdoc_model.keras
    models/class_names.json
    models/mango_model.keras
    models/mango_class_names.json
    models/leaf_detector_model.keras
    models/leaf_detector_classes.json

### Step 2 — Build metadata

Create:

    metadata/class_mapping.json
    metadata/dataset_sources.json
    metadata/split_manifest.csv
    metadata/review_log.csv

### Step 3 — Acquire and audit sources

Start with:

1. PlantVillage
2. Mendeley 15-crop dataset
3. six-crop fruit + leaf dataset
4. PlantDoc / additional field images
5. custom field collection

### Step 4 — Normalize labels

Convert all source labels to the canonical taxonomy in this file.

### Step 5 — Deduplicate

Use SHA-256 plus perceptual-hash review.

### Step 6 — Split by group

Use plant/capture-session/field grouping.

### Step 7 — Train baseline models

Recommended order:

    1. Plant gate
    2. Plant-part classifier
    3. Crop classifier
    4. Leaf-condition classifier
    5. Fruit-condition classifier
    6. Flower-condition classifier

### Step 8 — Evaluate

Report separately:

    overall accuracy
    macro F1
    per-class precision/recall
    confusion matrix
    top-3 accuracy
    rejection rate
    confidence calibration
    field-test performance

Do not publish a single headline accuracy without showing class balance and test-set composition.

## 20. V1 readiness criteria

The dataset is ready for model training only when:

- every active class has an authoritative source record
- every active class has canonical naming
- no known duplicate leakage exists across train/val/test
- each image has crop + plant-part metadata
- disease labels have a corresponding knowledge-base record
- licensing/attribution is recorded
- underrepresented classes are flagged
- the untouched field test set is locked
- the current scanner UI still works with the baseline models

## 21. Important scope rule

This blueprint defines a research/product dataset, not a claim that ATHARVADRISHTI can diagnose every plant disease.

For a label that is not supported by sufficient verified data:

    unsupported
        ↓
    do not predict confidently
        ↓
    return "insufficient evidence / unsupported condition"

The system should never manufacture a disease name, cause, cure, pesticide, or treatment from an uncertain image.

## 22. Dataset roadmap beyond V1

### V1
**24 crops + 76 leaf labels + fruit/flower foundation**

### V2
Add:

- more Indian crops
- more fruit disease classes
- verified flower disease classes
- pest/insect detection
- nutrient-deficiency datasets
- field severity annotations

### V3

Move from classification toward:

    detection
    +
    segmentation
    +
    severity estimation
    +
    temporal monitoring

Only add a new crop/condition when the dataset, labels, disease information, license, and evaluation set are all documented.

## 23. Primary references

1. PlantVillage Dataset — 38-class official class list and dataset description  
https://github.com/spMohanty/PlantVillage-Dataset/blob/master/README_HF.md

2. Mendeley — 15 Crop and 45 Disease and Healthy dataset  
https://data.mendeley.com/datasets/8fr7grr73p/1

3. Mendeley — FC45DHLPD 15 Crop and 45 Disease and Healthy Leaf Plant Disease dataset  
https://data.mendeley.com/datasets/ph9g2cfxwm/1

4. Mendeley — ABCGMP six-crop Fruit and Leaf Disease Dataset  
https://data.mendeley.com/datasets/fhbvmpcyy2/1

5. Frontiers in Plant Science (2026) — public-dataset label cross-check and field/lab sample description  
https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2026.1901116/full
