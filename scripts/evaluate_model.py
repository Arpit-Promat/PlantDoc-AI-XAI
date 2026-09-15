"""CLI benchmark for an ATHARVADRISHTI model on a labeled image directory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tensorflow.keras.models import load_model

from ai_evaluation import discover_labeled_images, evaluate_model, save_evaluation_report
from model_registry import get_model_spec


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate an ATHARVADRISHTI model")
    parser.add_argument("--model", choices=["general", "mango"], default="general")
    parser.add_argument("--data-dir", required=True, help="Labeled directory: data/<class_name>/*.jpg")
    parser.add_argument("--output", default="evaluation_reports/model_evaluation.json")
    args = parser.parse_args()

    spec = get_model_spec(args.model)
    model = load_model(spec.model_path, compile=False)
    class_names = json.loads(Path(spec.class_names_path).read_text(encoding="utf-8"))
    samples = discover_labeled_images(args.data_dir)

    report = evaluate_model(
        model=model,
        class_names=class_names,
        model_key=args.model,
        samples=samples,
        predictor=lambda tensor: model.predict(tensor, verbose=0)[0],
    )
    report["model_version"] = f"{spec.key}@{spec.version}"
    save_evaluation_report(report, args.output)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
