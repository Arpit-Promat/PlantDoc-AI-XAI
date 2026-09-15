"""Evaluation and field-robustness utilities for ATHARVADRISHTI models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import numpy as np
from PIL import Image, ImageEnhance

from prediction_engine import assess_prediction


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def load_image_tensor(path: str | Path, image_size: int = 224) -> np.ndarray:
    """Load an image using the same RGB/224/0-1 preprocessing contract."""
    with Image.open(path) as image:
        rgb = image.convert("RGB").resize((image_size, image_size))
        array = np.asarray(rgb, dtype=np.float32) / 255.0
    return np.expand_dims(array, axis=0)


def discover_labeled_images(data_dir: str | Path) -> list[tuple[Path, str]]:
    """Discover images from class-named subdirectories."""
    root = Path(data_dir)
    if not root.exists():
        raise FileNotFoundError(f"Dataset directory not found: {root}")

    samples: list[tuple[Path, str]] = []
    for class_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        for image_path in sorted(class_dir.rglob("*")):
            if image_path.is_file() and image_path.suffix.lower() in IMAGE_EXTENSIONS:
                samples.append((image_path, class_dir.name))
    if not samples:
        raise ValueError("No labeled images found. Expected data_dir/<class_name>/*.jpg|png")
    return samples


def evaluate_model(
    model: Any,
    class_names: list[str],
    model_key: str,
    samples: list[tuple[Path, str]],
    predictor: Callable[[np.ndarray], np.ndarray],
) -> dict[str, Any]:
    """Evaluate Top-1/Top-3 accuracy and production rejection behavior."""
    class_to_index = {str(name): index for index, name in enumerate(class_names)}
    total = len(samples)
    top1_correct = 0
    top3_correct = 0
    rejected = 0
    confidence_sum = 0.0
    margin_sum = 0.0
    unknown_labels = 0

    for image_path, true_label in samples:
        if true_label not in class_to_index:
            unknown_labels += 1
            continue

        tensor = load_image_tensor(image_path)
        raw_prediction = predictor(tensor)
        result = assess_prediction(raw_prediction, class_names, model_key, top_k=3)

        predicted_label = result["prediction"]
        top3_labels = [item["class_name"] for item in result["top_predictions"]]
        top1_correct += int(predicted_label == true_label)
        top3_correct += int(true_label in top3_labels)
        rejected += int(not result["accepted"])
        confidence_sum += float(result["confidence"])
        margin_sum += float(result["margin"])

    evaluated = total - unknown_labels
    if evaluated <= 0:
        raise ValueError("No dataset labels matched the model class names")

    return {
        "model": model_key,
        "samples_discovered": total,
        "samples_evaluated": evaluated,
        "unknown_labels": unknown_labels,
        "top1_accuracy": round(top1_correct / evaluated, 6),
        "top3_accuracy": round(top3_correct / evaluated, 6),
        "average_confidence": round(confidence_sum / evaluated, 4),
        "average_margin": round(margin_sum / evaluated, 4),
        "production_rejection_rate": round(rejected / evaluated, 6),
    }


def field_robustness_check(
    model_predict: Callable[[np.ndarray], np.ndarray],
    image_tensor: np.ndarray,
) -> dict[str, Any]:
    """Measure prediction consistency under mild, non-geometric image changes."""
    base = image_tensor[0]
    variants = {
        "original": base,
        "horizontal_flip": np.flip(base, axis=1),
        "brightness_up": np.asarray(
            ImageEnhance.Brightness(
                Image.fromarray(np.uint8(np.clip(base * 255.0, 0, 255)))
            ).enhance(1.10),
            dtype=np.float32,
        ) / 255.0,
        "brightness_down": np.asarray(
            ImageEnhance.Brightness(
                Image.fromarray(np.uint8(np.clip(base * 255.0, 0, 255)))
            ).enhance(0.90),
            dtype=np.float32,
        ) / 255.0,
    }

    predictions: dict[str, np.ndarray] = {}
    for name, variant in variants.items():
        predictions[name] = np.asarray(model_predict(np.expand_dims(variant, axis=0))).reshape(-1)

    top_indices = [int(np.argmax(values)) for values in predictions.values()]
    base_index = top_indices[0]
    consistent = sum(index == base_index for index in top_indices[1:])

    return {
        "variants_tested": list(variants.keys()),
        "base_predicted_index": base_index,
        "consistent_variants": consistent,
        "consistency_rate": round(consistent / max(1, len(top_indices) - 1), 4),
    }


def save_evaluation_report(report: dict[str, Any], output_path: str | Path) -> None:
    """Persist a JSON evaluation report."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
