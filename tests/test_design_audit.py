import unittest
import csv
import json
import tempfile
from pathlib import Path

from src.design_audit import (
    calibration_resolution,
    check_clause_masks,
    check_toy_adapter_support,
    paired_power,
    write_design_audit,
)


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
        self.assertEqual(result["minimum_n_for_target"]["0.3%"], 333)

    def test_planning_power_is_seeded_and_within_reported_range(self):
        first = paired_power(184, 0.30)
        second = paired_power(184, 0.30)
        self.assertEqual(first, second)
        self.assertGreater(first, 0.92)
        self.assertLess(first, 0.97)

    def test_invalid_power_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            paired_power(0, 0.30)
        with self.assertRaises(ValueError):
            paired_power(100, 0.10, effect=0.15)

    def test_design_report_is_machine_readable_and_provenance_labeled(self):
        with tempfile.TemporaryDirectory() as directory:
            path = write_design_audit(Path(directory) / "design_audit.csv")
            with path.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
        self.assertTrue(rows)
        self.assertTrue(all(row["evidence_status"] for row in rows))
        self.assertIn("planning_simulation_independent_episodes", {
            row["evidence_status"] for row in rows
        })
        self.assertIn("finite_sample_arithmetic", {
            row["evidence_status"] for row in rows
        })

    def test_toy_fixture_cannot_be_mistaken_for_benchmark_data(self):
        fixture_path = Path(__file__).parent / "fixtures" / "toy_adapter_cases.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        self.assertEqual(fixture["data_status"], "synthetic_test_fixture_only")
        self.assertEqual(len(fixture["cases"]), 8)
        admitted = [case for case in fixture["cases"] if case["adapter_admits"]]
        self.assertEqual(len(admitted), check_toy_adapter_support()["residual_positive_support"])
        self.assertTrue(all(case["form"] == "obfuscated" for case in admitted))


if __name__ == "__main__":
    unittest.main()
