"""Shared, deterministic prediction utilities for all inference entry points."""

from __future__ import annotations

from typing import Any

import numpy as np

from model_registry import model_identifier


CONFIDENCE_THRESHOLD = 60.0
MARGIN_THRESHOLD = 20.0
HIGH_CONFIDENCE = 85.0
MODERATE_CONFIDENCE = 70.0


def normalize_probabilities(predictions: Any) -> np.ndarray:
    """Return a numerically safe probability vector that sums to one."""
    values = np.asarray(predictions).astype(np.float64).reshape(-1)
    if values.size == 0:
        raise ValueError("Model returned an empty prediction vector")
    if not np.all(np.isfinite(values)):
        raise ValueError("Model returned non-finite prediction values")

    looks_like_probabilities = (
        np.all(values >= 0)
        and np.max(values) <= 1.0
        and np.isclose(np.sum(values), 1.0, atol=0.05)
    )

    if not looks_like_probabilities:
        shifted = values - np.max(values)
        exp_values = np.exp(shifted)
        total = np.sum(exp_values)
        if not np.isfinite(total) or total <= 0:
            raise ValueError("Unable to normalize model output")
        values = exp_values / total
    else:
        total = np.sum(values)
        if total <= 0:
            raise ValueError("Model probability sum is zero")
        values = values / total

    return values


def rank_predictions(predictions: Any, class_names: list[str], top_k: int = 3) -> list[dict[str, Any]]:
    """Return sorted top-k predictions with stable class names and probabilities."""
    values = normalize_probabilities(predictions)
    limit = min(max(1, int(top_k)), len(values))
    indices = np.argsort(values)[::-1][:limit]
    results: list[dict[str, Any]] = []

    for rank, index in enumerate(indices, start=1):
        class_index = int(index)
        class_name = class_names[class_index] if class_index < len(class_names) else f"Class {class_index}"
        results.append(
            {
                "rank": rank,
                "class_index": class_index,
                "class_name": class_name,
                "probability": round(float(values[class_index]), 6),
                "confidence": round(float(values[class_index]) * 100, 2),
            }
        )

    return results


def assess_prediction(predictions: Any, class_names: list[str], model_key: str, top_k: int = 3) -> dict[str, Any]:
    """Create one consistent result object for synchronous and asynchronous inference."""
    values = normalize_probabilities(predictions)
    ranked = rank_predictions(values, class_names, top_k=top_k)

    top1 = ranked[0]
    top2_probability = ranked[1]["probability"] if len(ranked) > 1 else 0.0
    margin = round((top1["probability"] - top2_probability) * 100, 2)
    confidence = float(top1["confidence"])

    if confidence >= HIGH_CONFIDENCE:
        confidence_level = "high"
        confidence_label = "High Confidence"
    elif confidence >= MODERATE_CONFIDENCE:
        confidence_level = "moderate"
        confidence_label = "Moderate Confidence"
    else:
        confidence_level = "low"
        confidence_label = "Low Confidence"

    accepted = confidence >= CONFIDENCE_THRESHOLD and margin >= MARGIN_THRESHOLD

    return {
        "model": model_key,
        "model_version": model_identifier(model_key),
        "prediction": top1["class_name"],
        "predicted_index": top1["class_index"],
        "confidence": round(confidence, 2),
        "margin": margin,
        "confidence_level": confidence_level,
        "confidence_label": confidence_label,
        "accepted": accepted,
        "status": "completed" if accepted else "rejected",
        "top_predictions": ranked,
    }
