"""Deterministic, non-prescriptive decision-support helpers for plant predictions."""

from __future__ import annotations

import re
from typing import Any


DISEASE_FAMILIES = {
    "scab": "fungal-like leaf disease pattern",
    "black_rot": "rot / fungal-like lesion pattern",
    "cedar_apple_rust": "rust-like fungal pattern",
    "powdery_mildew": "powdery mildew-like pattern",
    "cercospora": "leaf-spot pattern",
    "gray_leaf_spot": "leaf-spot pattern",
    "common_rust": "rust-like leaf pattern",
    "northern_leaf_blight": "blight-like leaf pattern",
    "bacterial_spot": "bacterial-spot-like pattern",
    "early_blight": "early-blight-like pattern",
    "late_blight": "late-blight-like pattern",
    "leaf_mold": "leaf-mold-like pattern",
    "septoria": "septoria-like leaf-spot pattern",
    "spider_mites": "mite-related visual pattern",
    "target_spot": "target-spot-like pattern",
    "yellow_leaf_curl_virus": "viral-pattern classification",
    "mosaic_virus": "viral mosaic-pattern classification",
    "leaf_blight": "leaf-blight-like pattern",
    "haunglongbing": "citrus greening-like pattern",
    "healthy": "healthy-leaf classification",
}


PRECAUTION_BY_FAMILY = {
    "fungal": [
        "Inspect several leaves instead of relying on one image.",
        "Remove heavily affected plant material where agronomically appropriate.",
        "Avoid prolonged leaf wetness and improve airflow where practical.",
    ],
    "bacterial": [
        "Inspect neighboring plants for similar spotting.",
        "Reduce unnecessary leaf wetness and avoid spreading contaminated plant material.",
        "Use local agricultural guidance before selecting any control product.",
    ],
    "viral": [
        "Check nearby plants and look for a repeating symptom pattern.",
        "Inspect for possible vector or plant-to-plant spread factors.",
        "Seek crop-specific agricultural guidance before taking control action.",
    ],
    "mite": [
        "Inspect the underside of leaves and nearby foliage for additional signs.",
        "Check multiple plants because mite pressure can vary across a field.",
        "Use local integrated pest-management guidance before applying controls.",
    ],
    "rot": [
        "Inspect affected and nearby leaves for expanding lesions or fruit/plant tissue damage.",
        "Remove severely damaged material where appropriate and improve sanitation.",
        "Seek crop-specific guidance before selecting a treatment.",
    ],
    "leaf_spot": [
        "Inspect multiple leaves for the same spot pattern.",
        "Improve airflow and avoid unnecessary leaf wetness where practical.",
        "Seek crop-specific guidance before selecting a treatment.",
    ],
    "blight": [
        "Inspect multiple plants for expanding or coalescing lesions.",
        "Reduce unnecessary leaf wetness and improve airflow where practical.",
        "Seek crop-specific agricultural guidance before treatment decisions.",
    ],
    "rust": [
        "Inspect leaf undersides and nearby plants for additional rust-like structures.",
        "Monitor spread over the next few observations.",
        "Seek crop-specific guidance before selecting a treatment.",
    ],
}


def clean_label(label: str | None) -> str:
    value = str(label or "").strip()
    value = value.replace("___", " → ")
    value = value.replace("__", " ")
    value = value.replace("_", " ")
    return re.sub(r"\s+", " ", value).strip()


def crop_from_label(label: str | None) -> str | None:
    raw = str(label or "").strip()
    if "___" not in raw:
        return None
    return clean_label(raw.split("___", 1)[0])


def condition_family(label: str | None) -> str:
    raw = str(label or "").lower()
    normalized = raw.replace(" ", "_")
    for token, family in DISEASE_FAMILIES.items():
        if token in normalized:
            return family
    return "visual plant-condition classification"


def _family_key(label: str | None) -> str:
    raw = str(label or "").lower().replace(" ", "_")
    if "healthy" in raw:
        return "healthy"
    if any(token in raw for token in ("powdery_mildew", "scab", "rust", "early_blight", "late_blight", "leaf_mold", "septoria", "black_rot", "target_spot", "leaf_blight", "cercospora", "gray_leaf_spot", "northern_leaf_blight")):
        return "fungal"
    if "bacterial_spot" in raw:
        return "bacterial"
    if "virus" in raw or "yellow_leaf_curl" in raw or "mosaic" in raw or "haunglongbing" in raw:
        return "viral"
    if "spider_mite" in raw:
        return "mite"
    if "spot" in raw:
        return "leaf_spot"
    if "blight" in raw:
        return "blight"
    if "rust" in raw:
        return "rust"
    if "rot" in raw:
        return "rot"
    return "leaf_spot"


def build_decision_support(label: str | None, confidence: float | None, margin: float | None, status: str | None = None) -> dict[str, Any]:
    cleaned = clean_label(label)
    is_healthy = "healthy" in cleaned.lower()
    advisory_status = str(status or "").lower()

    if is_healthy:
        next_steps = [
            "Continue routine crop monitoring.",
            "Recheck new growth or visibly changing leaves if symptoms appear.",
        ]
    elif cleaned:
        next_steps = PRECAUTION_BY_FAMILY.get(
            _family_key(label),
            PRECAUTION_BY_FAMILY["leaf_spot"],
        )
    else:
        next_steps = [
            "Upload a clearer leaf image or collect another observation.",
            "Do not make treatment decisions from an uncertain prediction alone.",
        ]

    confidence_value = float(confidence) if confidence is not None else None
    margin_value = float(margin) if margin is not None else None
    reliability = "unknown"
    if advisory_status == "rejected":
        reliability = "uncertain"
    elif confidence_value is not None and margin_value is not None:
        if confidence_value >= 85 and margin_value >= 20:
            reliability = "high"
        elif confidence_value >= 70 and margin_value >= 20:
            reliability = "moderate"
        else:
            reliability = "low"

    return {
        "prediction": cleaned or None,
        "crop": crop_from_label(label),
        "condition_family": condition_family(label) if cleaned else None,
        "reliability": reliability,
        "is_healthy_prediction": is_healthy,
        "recommended_next_steps": next_steps,
        "limitations": [
            "This is visual decision support, not a confirmed biological diagnosis.",
            "The model does not estimate exact disease severity or infected-area percentage.",
            "Treatment or pesticide selection should be based on crop-specific expert or local agricultural guidance.",
        ],
    }
