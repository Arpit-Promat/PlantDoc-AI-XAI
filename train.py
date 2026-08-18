import json
from pathlib import Path

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# =========================
# DATASET PATH
# =========================
TRAIN_DIR = Path("dataset/PlantVillage/train")
VAL_DIR = Path("dataset/PlantVillage/val")

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
# LOAD DATA
# =========================
train_data = train_datagen.flow_from_directory(
    str(TRAIN_DIR),
    target_size=(224, 224),
    batch_size=8,
    class_mode="categorical",
    shuffle=True
)

val_data = val_datagen.flow_from_directory(
    str(VAL_DIR),
    target_size=(224, 224),
    batch_size=8,
    class_mode="categorical",
    shuffle=False
)

print("\n==============================")
print("DATASET LOADED")
print("==============================")
print("Training images:", train_data.samples)
print("Validation images:", val_data.samples)
print("Number of classes:", train_data.num_classes)
print("==============================\n")

# =========================
# SAVE CLASS NAMES
# =========================
class_names = [
    name
    for name, index in sorted(
        train_data.class_indices.items(),
        key=lambda x: x[1]
    )
]

with open(MODEL_DIR / "class_names.json", "w") as f:
    json.dump(class_names, f, indent=2)

# =========================
# MOBILENETV2
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

output = Dense(
    train_data.num_classes,
    activation="softmax"
)(x)

model = Model(
    inputs=base_model.input,
    outputs=output
)

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# =========================
# CALLBACKS
# =========================
callbacks = [
    EarlyStopping(
        monitor="val_accuracy",
        patience=2,
        restore_best_weights=True
    ),
    ModelCheckpoint(
        "models/plantdoc_model.keras",
        monitor="val_accuracy",
        save_best_only=True
    )
]

# =========================
# TRAIN
# =========================
import os
from tensorflow.keras.models import load_model

checkpoint_path = "models/plantdoc_model.keras"

if os.path.exists(checkpoint_path):
    print("Saved model found!")
    print("Loading previous model...")
    model = load_model(checkpoint_path)
    print("Previous model loaded successfully!")
print("\nStarting training...\n")

model.fit(
    train_data,
    validation_data=val_data,
    initial_epoch=1,
    epochs=5,
    callbacks=callbacks
)

print("\n==============================")
print("TRAINING COMPLETE")
print("==============================")
print("Model saved in models/plantdoc_model.keras")