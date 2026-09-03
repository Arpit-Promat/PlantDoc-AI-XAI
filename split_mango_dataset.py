"""
split_mango_dataset.py

Splits the downloaded Mango Leaf Disease Kaggle dataset into
train/ and val/ folders under a SEPARATE "Mango" dataset root
(kept apart from PlantVillage, which is not available on this PC):

    dataset/Mango/train/<ClassName>/*.jpg
    dataset/Mango/val/<ClassName>/*.jpg

USAGE:
    1. Confirm the two paths below match your folders.
    2. Run:  python split_mango_dataset.py
"""

import random
import shutil
from pathlib import Path

# =========================
# EDIT THESE PATHS
# =========================

# Folder where you extracted the Kaggle Mango dataset
# (the one containing "Anthracnose", "Bacterial Canker", etc.)
MANGO_SOURCE_DIR = Path(r"C:\Users\Lenovo\Desktop\Desktopmango-dataset")

# Destination dataset root for the Mango-only model
# (separate from PlantVillage, which is missing on this machine)
PLANTVILLAGE_DIR = Path(
    r"C:\Users\Lenovo\Desktop\plant disease detection\PlantDoc-AI-XAI\dataset\Mango"
)

TRAIN_DIR = PLANTVILLAGE_DIR / "train"
VAL_DIR = PLANTVILLAGE_DIR / "val"

# Fraction of images that go to training (rest goes to validation)
TRAIN_SPLIT = 0.8

# Prefix added to every Mango class name (kept for clarity / future merging)
CLASS_PREFIX = "Mango___"

# Valid image extensions to look for
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}

# Set a seed so the split is reproducible if you re-run this script
random.seed(42)


def main():
    if not MANGO_SOURCE_DIR.exists():
        raise SystemExit(f"ERROR: Mango source folder not found: {MANGO_SOURCE_DIR}")

    TRAIN_DIR.mkdir(parents=True, exist_ok=True)
    VAL_DIR.mkdir(parents=True, exist_ok=True)

    category_dirs = [d for d in MANGO_SOURCE_DIR.iterdir() if d.is_dir()]

    if not category_dirs:
        raise SystemExit(f"ERROR: No category folders found inside {MANGO_SOURCE_DIR}")

    print("==============================")
    print("MANGO DATASET SPLIT")
    print("==============================")
    print(f"Source:      {MANGO_SOURCE_DIR}")
    print(f"Train dest:  {TRAIN_DIR}")
    print(f"Val dest:    {VAL_DIR}")
    print(f"Train split: {TRAIN_SPLIT * 100:.0f}%")
    print("==============================\n")

    total_train = 0
    total_val = 0

    for category_dir in sorted(category_dirs):
        images = [
            f for f in category_dir.iterdir()
            if f.is_file() and f.suffix in IMAGE_EXTENSIONS
        ]

        if not images:
            print(f"[skip] {category_dir.name}: no images found")
            continue

        random.shuffle(images)

        split_index = int(len(images) * TRAIN_SPLIT)
        train_images = images[:split_index]
        val_images = images[split_index:]

        class_name = CLASS_PREFIX + category_dir.name.strip().replace(" ", "_")

        train_class_dir = TRAIN_DIR / class_name
        val_class_dir = VAL_DIR / class_name

        train_class_dir.mkdir(parents=True, exist_ok=True)
        val_class_dir.mkdir(parents=True, exist_ok=True)

        for img in train_images:
            shutil.copy2(img, train_class_dir / img.name)

        for img in val_images:
            shutil.copy2(img, val_class_dir / img.name)

        print(
            f"[{category_dir.name}] "
            f"total={len(images)}  "
            f"train={len(train_images)}  "
            f"val={len(val_images)}  "
            f"-> class name: {class_name}"
        )

        total_train += len(train_images)
        total_val += len(val_images)

    print("\n==============================")
    print("SPLIT COMPLETE")
    print("==============================")
    print(f"Total train images copied: {total_train}")
    print(f"Total val images copied:   {total_val}")
    print("==============================")


if __name__ == "__main__":
    main()