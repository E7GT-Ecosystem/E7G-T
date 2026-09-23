"""Differential tests against MSC-B1/0.1's finite reference and fixtures."""

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

from msc_finite_b1 import (AdmissionError, access_classes, admit, evaluate,
                           observation_fibre, scope_fibre)

ROOT = Path(__file__).resolve().parents[3] / "proposals" / "msc-0.1"
spec = importlib.util.spec_from_file_location("msc_source", ROOT / "e7gt_msc_v0_1.py")
source = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = source
spec.loader.exec_module(source)


def selected(doc):
    """Project source fixture to the declared, closed core module input."""
    return {key: copy.deepcopy(value) for key, value in doc.items()
            if key in {"schema_version", "diagram_id", "max_combinations",
                       "carriers", "scopes", "maps", "links"}}


class MSCDifferential(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.unique = json.loads((ROOT / "fixtures" / "unique_closure.json").read_text())
        cls.obstruction = json.loads((ROOT / "fixtures" / "global_obstruction.json").read_text())

    def compare(self, doc):
        result, reference = evaluate(admit(selected(doc))), source.evaluate(doc)
        self.assertEqual(result.outcome, reference["outcome"])
        if result.outcome in {"unsupported", "resource_limit"}:
            if result.outcome == "resource_limit":
                self.assertEqual(result.candidate_count, reference["candidate_combinations"])
            return result
        self.assertEqual(result.candidate_count, reference["candidate_combinations"])
        self.assertEqual([dict(family) for family in result.compatible],
                         reference["compatible_families"])
        self.assertEqual(dict(result.linkwise), reference["linkwise_satisfiable"])
        self.assertEqual(result.obstruction,
                         reference["global_obstruction_despite_linkwise_satisfiability"])
        return result

    def test_unique_ambiguous_and_global_obstruction(self):
        self.assertEqual(self.compare(self.unique).outcome, "unique")
        self.assertEqual(self.compare(self.obstruction).outcome, "incompatible")
        self.assertTrue(self.compare(self.obstruction).obstruction)
        ambiguous = copy.deepcopy(self.unique)
        ambiguous["carriers"][1]["values"].append("G1")
        ambiguous["maps"][0]["table"]["G1"] = "1"
        ambiguous["maps"][4]["table"]["G1"] = "k1"
        self.assertEqual(self.compare(ambiguous).outcome, "ambiguous")

    def test_scope_and_observation_fibres_differ(self):
        doc = copy.deepcopy(self.unique)
        doc["carriers"][1]["values"].append("G1")
        doc["maps"][0]["table"]["G1"] = "1"
        doc["maps"][4]["table"]["G1"] = "k1"
        diagram, result, reference = admit(selected(doc)), self.compare(doc), source.evaluate(doc)
        self.assertEqual(len(scope_fibre(diagram, result, "local", "L0")),
                         reference["reconstruction_queries"][0]["compatible_count"])
        self.assertEqual(len(observation_fibre(diagram, result, "local", "observe-local", "same")),
                         reference["reconstruction_queries"][1]["compatible_count"])
        self.assertEqual(len(scope_fibre(diagram, result, "local", "L0")), 1)
        self.assertEqual(len(observation_fibre(diagram, result, "local", "observe-local", "same")), 2)
        with self.assertRaisesRegex(AdmissionError, "scope_state_sort_mismatch"):
            scope_fibre(diagram, result, "local", "G1")
        with self.assertRaisesRegex(AdmissionError, "observation_sort_mismatch"):
            observation_fibre(diagram, result, "local", "project-global", "0")
        with self.assertRaisesRegex(AdmissionError, "result_diagram_mismatch"):
            scope_fibre(admit(selected(self.obstruction)), result, "r", "0")

    def test_access_quotient_and_missingness_policy(self):
        diagram = admit(selected(self.unique))
        source_classes = source.evaluate(self.unique)["access_quotients"][0]["classes"]
        self.assertEqual(access_classes(diagram, "local", ("observe-local",)),
                         tuple(tuple(group) for group in source_classes))
        empty = copy.deepcopy(self.unique)
        empty["access_profiles"].append({"profile_id": "sealed", "scope": "local",
                                          "context": "sealed", "observation_maps": []})
        expected = source.evaluate(empty)["access_quotients"][1]["classes"]
        self.assertEqual(access_classes(admit(selected(empty)), "local", ()),
                         tuple(tuple(group) for group in expected))

    def test_resource_and_partial_map_are_not_negative_coherence(self):
        limited = copy.deepcopy(self.obstruction)
        limited["max_combinations"] = 7
        result = self.compare(limited)
        self.assertEqual(result.outcome, "resource_limit")
        with self.assertRaisesRegex(AdmissionError, "incomplete_carrier"):
            scope_fibre(admit(selected(limited)), result, "r", "0")
        partial = copy.deepcopy(self.unique)
        del partial["maps"][1]["table"]["L1"]
        self.assertEqual(self.compare(partial).outcome, "unsupported")

    def test_common_carrier_edition_and_cycle_are_checked(self):
        wrong = copy.deepcopy(self.unique)
        wrong["maps"][1]["target_carrier"] = "visible"
        wrong["maps"][1]["table"] = {"L0": "same", "L1": "same"}
        with self.assertRaisesRegex(AdmissionError, "common_comparison_carrier"):
            admit(selected(wrong))
        with self.assertRaisesRegex(source.MSCError, "common comparison carrier"):
            source.evaluate(wrong)
        cycle = copy.deepcopy(self.unique)
        cycle["links"].append({"link_id": "reverse", "lower_scope": "global",
                               "upper_scope": "local", "projection_map": "compare-local",
                               "comparison_map": "project-global", "criterion": "exact"})
        with self.assertRaisesRegex(AdmissionError, "scope_cycle"):
            admit(selected(cycle))
        with self.assertRaisesRegex(source.MSCError, "cycle"):
            source.evaluate(cycle)
        wrong = copy.deepcopy(self.unique)
        wrong["schema_version"] = "future"
        with self.assertRaisesRegex(AdmissionError, "unsupported_diagram_edition"):
            admit(selected(wrong))
        with self.assertRaisesRegex(AdmissionError, "unsupported_diagram_shape"):
            admit(self.unique)  # Optional source tests cannot be silently accepted.


if __name__ == "__main__":
    unittest.main()
