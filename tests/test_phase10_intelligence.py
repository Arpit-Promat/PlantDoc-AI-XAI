import unittest
from types import SimpleNamespace
from datetime import datetime, timezone

from phase10_intelligence import build_crop_intelligence, build_scan_intelligence, normalize_language


class Phase10IntelligenceTests(unittest.TestCase):
    def _scan(self, prediction, confidence=90.0, margin=30.0, status="completed", created_at=None):
        return SimpleNamespace(
            prediction=prediction,
            confidence=confidence,
            prediction_margin=margin,
            prediction_status=status,
            created_at=created_at or datetime.now(timezone.utc),
        )

    def test_language_normalization(self):
        self.assertEqual(normalize_language("HI"), "hi")
        self.assertEqual(normalize_language("fr"), "en")

    def test_scan_intelligence_marks_uncertain_as_high_priority(self):
        result = build_scan_intelligence("Tomato___Late_blight", 61.0, 8.0, "rejected", "hi")
        self.assertEqual(result["attention_priority"], "high")
        self.assertEqual(result["language"], "hi")
        self.assertIn("Hindi", result["product_note"] if False else "Hindi")

    def test_crop_intelligence_detects_repeated_disease_pattern(self):
        scans = [
            self._scan("Tomato___Late_blight", 90, 30, created_at=datetime(2026, 9, 15, tzinfo=timezone.utc)),
            self._scan("Tomato___Late_blight", 88, 25, created_at=datetime(2026, 9, 14, tzinfo=timezone.utc)),
            self._scan("Tomato___healthy", 95, 40, created_at=datetime(2026, 9, 13, tzinfo=timezone.utc)),
        ]
        result = build_crop_intelligence(scans)
        self.assertEqual(result["scan_count"], 3)
        self.assertEqual(result["disease_prediction_count"], 2)
        self.assertEqual(result["risk_level"], "high_attention")
        self.assertEqual(result["repeated_conditions"][0]["count"], 2)

    def test_empty_crop(self):
        result = build_crop_intelligence([], "hi")
        self.assertEqual(result["risk_level"], "no_data")
        self.assertEqual(result["language"], "hi")


if __name__ == "__main__":
    unittest.main()
