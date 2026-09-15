import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from ai_evaluation import discover_labeled_images, evaluate_model, field_robustness_check


class TestAIEvaluation(unittest.TestCase):
    def test_discover_labeled_images(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            class_dir = root / "Apple_Scab"
            class_dir.mkdir()
            Image.new("RGB", (16, 16), "white").save(class_dir / "sample.jpg")

            samples = discover_labeled_images(root)
            self.assertEqual(len(samples), 1)
            self.assertEqual(samples[0][1], "Apple_Scab")

    def test_evaluate_model_metrics(self):
        samples = [(Path("a.jpg"), "Healthy")]
        class_names = ["Healthy", "Disease"]

        def predictor(_tensor):
            return np.array([0.9, 0.1], dtype=np.float32)

        report = evaluate_model(
            model=None,
            class_names=class_names,
            model_key="general",
            samples=samples,
            predictor=predictor,
        )

        self.assertEqual(report["top1_accuracy"], 1.0)
        self.assertEqual(report["top3_accuracy"], 1.0)
        self.assertEqual(report["production_rejection_rate"], 0.0)

    def test_field_robustness_check(self):
        tensor = np.zeros((1, 8, 8, 3), dtype=np.float32)

        def predictor(_tensor):
            return np.array([0.8, 0.2], dtype=np.float32)

        result = field_robustness_check(predictor, tensor)
        self.assertEqual(result["consistency_rate"], 1.0)
        self.assertEqual(result["variants_tested"][0], "original")


if __name__ == "__main__":
    unittest.main()
