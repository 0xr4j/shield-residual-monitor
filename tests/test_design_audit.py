import unittest

from src.design_audit import calibration_resolution, check_clause_masks, check_toy_adapter_support


class DesignAuditTests(unittest.TestCase):
    def test_clause_masks_expose_in_family_overlap(self):
        omitted, masks, other = check_clause_masks()
        self.assertEqual(masks, 15)
        self.assertEqual(omitted, {0: 8, 1: 8, 2: 8, 3: 8})
        self.assertEqual(other, {0: 7, 1: 7, 2: 7, 3: 7})

    def test_partial_adapter_changes_support(self):
        result = check_toy_adapter_support()
        self.assertEqual(result["literal_admitted"], 0)
        self.assertEqual(result["obfuscated_admitted"], 4)

    def test_calibration_resolution(self):
        result = calibration_resolution()
        self.assertFalse(result["rank_supported"]["0.3%"])
        self.assertTrue(result["rank_supported"]["1.0%"])


if __name__ == "__main__":
    unittest.main()
