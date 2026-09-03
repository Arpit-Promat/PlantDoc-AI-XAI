import json
from pathlib import Path

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# =========================
# DATASET PATH (Leaf vs Not-Leaf)
# =========================
TRAIN_DIR = Path("dataset/LeafDetector/train")
VAL_DIR = Path("dataset/LeafDetector/val")

MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

print("Checking dataset...")

if not TRAIN_DIR.exists():
    raise SystemExit(f"ERROR: Training folder not found: {TRAIN_DIR}")

if not VAL_DIR.exists():
    raise SystemExit(f"ERROR: Validation folder not found: {VAL_DIR}")

print("Training folder:", TRAIN_DIR)
print("Validation folder:", VAL_DIR)

# =========================
# DATA AUGMENTATION
# =========================
train_datagen = ImageDataGenerator(
    rescale=1.0 / 255,
    rotation_range=20,
    width_shift_range=0.15,
    height_shift_range=0.15,
    zoom_range=0.15,
    horizontal_flip=True
)

val_datagen = ImageDataGenerator(
    rescale=1.0 / 255
)

# =========================
# LOAD DATA (binary classification: leaf vs not_leaf)
# =========================
train_data = train_datagen.flow_from_directory(
    str(TRAIN_DIR),
    target_size=(224, 224),
    batch_size=16,
    class_mode="binary",
    shuffle=True
)

val_data = val_datagen.flow_from_directory(
    str(VAL_DIR),
    target_size=(224, 224),
    batch_size=16,
    class_mode="binary",
    shuffle=False
)

print("\n==============================")
print("DATASET LOADED")
print("==============================")
print("Training images:", train_data.samples)
print("Validation images:", val_data.samples)
print("Class indices:", train_data.class_indices)
print("==============================\n")

# =========================
# SAVE CLASS INDEX MAPPING
# (so app.py knows which index means "leaf")
# =========================
with open(MODEL_DIR / "leaf_detector_classes.json", "w") as f:
    json.dump(train_data.class_indices, f, indent=2)

# =========================
# MOBILENETV2 (binary output)
# =========================
print("Loading MobileNetV2...")

base_model = MobileNetV2(
    weights="imagenet",
    include_top=False,
    input_shape=(224, 224, 3)
)

base_model.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dropout(0.3)(x)

# Single output neuron with sigmoid for binary classification
output = Dense(1, activation="sigmoid")(x)

model = Model(
    inputs=base_model.input,
    outputs=output
)

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

# =========================
# CALLBACKS
# =========================
callbacks = [
    EarlyStopping(
        monitor="val_accuracy",
        patience=3,
        restore_best_weights=True
    ),
    ModelCheckpoint(
        "models/leaf_detector_model.keras",
        monitor="val_accuracy",
        save_best_only=True
    )
]

# =========================
# TRAIN
# =========================
print("\nStarting training...\n")

model.fit(
    train_data,
    validation_data=val_data,
    initial_epoch=0,
    epochs=8,
    callbacks=callbacks
)

print("\n==============================")
print("TRAINING COMPLETE")
print("==============================")
print("Model saved in models/leaf_detector_model.keras")
print("Class indices saved in models/leaf_detector_classes.json")
