import unittest

from decision_support import build_decision_support, clean_label, crop_from_label


class DecisionSupportTests(unittest.TestCase):
    def test_clean_label(self):
        self.assertEqual(clean_label("Tomato___Late_blight"), "Tomato → Late blight")

    def test_crop_from_label(self):
        self.assertEqual(crop_from_label("Apple___Apple_scab"), "Apple")
        self.assertIsNone(crop_from_label("unknown label"))

    def test_healthy_prediction(self):
        result = build_decision_support("Tomato___healthy", 92.0, 35.0, "completed")
        self.assertTrue(result["is_healthy_prediction"])
        self.assertEqual(result["reliability"], "high")
        self.assertGreaterEqual(len(result["recommended_next_steps"]), 1)

    def test_uncertain_prediction(self):
        result = build_decision_support("Potato___Late_blight", 61.0, 8.0, "rejected")
        self.assertEqual(result["reliability"], "uncertain")
        self.assertIn("exact disease severity", " ".join(result["limitations"]))


if __name__ == "__main__":
    unittest.main()
