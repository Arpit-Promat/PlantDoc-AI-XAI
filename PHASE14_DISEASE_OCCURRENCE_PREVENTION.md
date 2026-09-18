# Phase 14 — Disease Occurrence & Prevention Guidance

Phase 14 adds educational disease-information guidance to the existing ATHARVADRISHTI scanner.

## User-facing feature

After an accepted prediction, the scanner now shows:

### How does it occur?
A concise explanation of the common causal pathway and conditions associated with the predicted label.

### Prevention
Practical preventive/scouting measures appropriate to the crop-condition category.

The guidance covers the current general PlantDoc labels and Mango labels, with a conservative fallback for any future label that is not yet in the knowledge base.

## Design

- disease_guidance.py contains the curated guidance library.
- pages/1_AI_Scanner.py reads the predicted label and displays the matching guidance.
- Existing model inference and SHAP explanation remain unchanged.
- No pesticide name, dose, spray schedule or treatment prescription is generated.
- Conditions that can resemble one another are presented as model classifications rather than confirmed biological diagnoses.

## Example

For a tomato leaf classified as early blight, the user can see that the condition is associated with fungal infection and that infected crop debris, moisture and leaf wetness can contribute to spread. Prevention guidance emphasizes sanitation, reducing soil splash, improving airflow and avoiding unnecessary leaf wetness.

## Evidence basis

The guidance follows established extension/pathology information such as:
- University of Minnesota Extension guidance on tomato leaf spots, bacterial spot, corn rust and northern corn leaf blight.
- Penn State Extension guidance on grape black rot and apple disease management.

Source-specific crop recommendations should still be verified with local agricultural extension or plant-pathology guidance.