"""Central registry for deployed AI models and their versions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    key: str
    display_name: str
    version: str
    model_path: str
    class_names_path: str


MODEL_REGISTRY = {
    "general": ModelSpec(
        key="general",
        display_name="ATHARVADRISHTI General Classifier",
        version="1.0.0",
        model_path="models/plantdoc_model.keras",
        class_names_path="models/class_names.json",
    ),
    "mango": ModelSpec(
        key="mango",
        display_name="Mango Disease Classifier",
        version="1.0.0",
        model_path="models/mango_model.keras",
        class_names_path="models/mango_class_names.json",
    ),
    "leaf_detector": ModelSpec(
        key="leaf_detector",
        display_name="Leaf / Non-Leaf Detector",
        version="1.0.0",
        model_path="models/leaf_detector_model.keras",
        class_names_path="models/leaf_detector_classes.json",
    ),
}


def get_model_spec(key: str) -> ModelSpec:
    try:
        return MODEL_REGISTRY[key]
    except KeyError as exc:
        raise ValueError(f"Unknown model key: {key}") from exc


def model_identifier(key: str) -> str:
    spec = get_model_spec(key)
    return f"{spec.key}@{spec.version}"
