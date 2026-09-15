import copy
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("score_rec_eval", ROOT / "score_rec_eval.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class RecEvalScorerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads((ROOT / "fixtures" / "synthetic_scoring_fixture.json").read_text())
        cls.case_set = json.loads((ROOT / "fixtures" / "synthetic_case_set.json").read_text())

    def test_fixture_validates(self):
        MODULE.validate_run(self.fixture)

    def test_all_arms_are_scored(self):
        score = MODULE.score_run(self.fixture)
        self.assertEqual(set(score["arms"]), set(MODULE.ARMS))
        self.assertTrue(all(v["observations"] == 2 for v in score["arms"].values()))

    def test_fixture_matches_golden_score(self):
        expected = json.loads((ROOT / "fixtures" / "synthetic_expected_scores.json").read_text())
        self.assertEqual(MODULE.score_run(self.fixture), expected)

    def test_case_set_cross_check_accepts_matching_labels(self):
        MODULE.validate_run_against_case_set(self.fixture, self.case_set)

    def test_case_set_cross_check_rejects_gold_drift(self):
        case_set = copy.deepcopy(self.case_set)
        case_set["cases"][0]["gold"]["expected_action"] = "assert"
        with self.assertRaisesRegex(MODULE.ValidationError, "expected_action mismatch"):
            MODULE.validate_run_against_case_set(self.fixture, case_set)

    def test_primary_delta_is_paired_not_aggregate_subtraction(self):
        delta = MODULE.score_run(self.fixture)["primary_paired_delta_retrieval_rec_minus_retrieval"]
        self.assertEqual(delta["unsupported_rate"], {"mean": -0.416667, "paired_cells": 2})
        self.assertEqual(delta["decision_accuracy"], {"mean": 0.5, "paired_cells": 2})

    def test_zero_denominator_is_null(self):
        doc = copy.deepcopy(self.fixture)
        for row in doc["observations"]:
            if row["arm"] == "ordinary":
                row["gold_units"] = 0
                row["asserted_units"] = 0
                row["correct_units"] = 0
                row["unsupported_units"] = 0
        metrics = MODULE.score_run(doc)["arms"]["ordinary"]
        self.assertIsNone(metrics["factual_recall"])
        self.assertIsNone(metrics["asserted_precision"])

    def test_missing_arm_rejected(self):
        doc = copy.deepcopy(self.fixture)
        doc["observations"].pop()
        with self.assertRaisesRegex(MODULE.ValidationError, "incomplete matched cell"):
            MODULE.validate_run(doc)

    def test_duplicate_cell_rejected(self):
        doc = copy.deepcopy(self.fixture)
        doc["observations"].append(copy.deepcopy(doc["observations"][0]))
        with self.assertRaisesRegex(MODULE.ValidationError, "duplicate observation"):
            MODULE.validate_run(doc)

    def test_wrong_arm_trace_shape_rejected(self):
        doc = copy.deepcopy(self.fixture)
        doc["observations"][0]["rec_trace_valid"] = True
        with self.assertRaisesRegex(MODULE.ValidationError, "rec_trace_valid inconsistent"):
            MODULE.validate_run(doc)

    def test_missing_conflict_label_rejected(self):
        doc = copy.deepcopy(self.fixture)
        doc["observations"][0]["conflict_retained"] = None
        with self.assertRaisesRegex(MODULE.ValidationError, "conflict_retained inconsistent"):
            MODULE.validate_run(doc)

    def test_impossible_unit_count_rejected(self):
        doc = copy.deepcopy(self.fixture)
        doc["observations"][0]["correct_units"] = 3
        with self.assertRaisesRegex(MODULE.ValidationError, "correct exceeds asserted"):
            MODULE.validate_run(doc)

    def test_score_never_claims_promotion(self):
        score = MODULE.score_run(self.fixture)
        self.assertFalse(score["promotion_evidence"])
        self.assertEqual(score["data_class"], "synthetic")

    def test_promotion_label_enforces_minimum_design(self):
        doc = copy.deepcopy(self.fixture)
        doc["data_class"] = "promotion"
        doc["adjudication_blinded"] = True
        with self.assertRaisesRegex(MODULE.ValidationError, "at least 100 cases"):
            MODULE.validate_run(doc)

    def test_execution_failures_are_visible(self):
        doc = copy.deepcopy(self.fixture)
        doc["observations"][0]["execution_status"] = "timeout"
        metrics = MODULE.score_run(doc)["arms"]["ordinary"]
        self.assertEqual(metrics["execution_failure_rate"], 0.5)


if __name__ == "__main__":
    unittest.main()
