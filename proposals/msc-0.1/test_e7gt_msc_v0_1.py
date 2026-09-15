import copy
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("msc", ROOT / "e7gt_msc_v0_1.py")
MSC = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MSC)


class MSCReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.unique = json.loads((ROOT / "fixtures" / "unique_closure.json").read_text())
        cls.obstruction = json.loads((ROOT / "fixtures" / "global_obstruction.json").read_text())

    def test_unique_closure(self):
        result = MSC.evaluate(self.unique)
        self.assertEqual(result["outcome"], "unique")
        self.assertEqual(result["compatible_families"], [{"global": "G0", "local": "L0"}])
        self.assertEqual(result["scope_order_reflexive_transitive_closure"], [["global", "global"], ["local", "global"], ["local", "local"]])

    def test_access_quotient_can_hide_distinct_states(self):
        classes = MSC.evaluate(self.unique)["access_quotients"][0]["classes"]
        self.assertEqual(classes, [["L0", "L1"]])

    def test_shared_invariant_preserved_on_compatible_family(self):
        invariant = MSC.evaluate(self.unique)["invariant_tests"][0]
        self.assertEqual(invariant, {"test_id": "shared-k", "outcome": "preserved"})

    def test_linkwise_satisfiable_global_obstruction(self):
        result = MSC.evaluate(self.obstruction)
        self.assertEqual(result["outcome"], "incompatible")
        self.assertTrue(result["all_links_individually_satisfiable"])
        self.assertTrue(result["global_obstruction_despite_linkwise_satisfiability"])

    def test_ambiguous_closure(self):
        doc = copy.deepcopy(self.unique)
        doc["carriers"][1]["values"].append("G1")
        doc["maps"][0]["table"]["G1"] = "1"
        doc["maps"][4]["table"]["G1"] = "k1"
        self.assertEqual(MSC.evaluate(doc)["outcome"], "ambiguous")

    def test_partial_required_map_is_unsupported(self):
        doc = copy.deepcopy(self.unique)
        del doc["maps"][1]["table"]["L1"]
        self.assertEqual(MSC.evaluate(doc)["outcome"], "unsupported")

    def test_non_object_roots_are_controlled_validation_errors(self):
        for value in ([], None, "text", 3):
            with self.subTest(value=value), self.assertRaisesRegex(MSC.MSCError, "document must be an object"):
                MSC.evaluate(value)

    def test_cli_non_object_roots_exit_two_without_traceback(self):
        for value in ([], None, "text", 3):
            with self.subTest(value=value), tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8") as handle:
                json.dump(value, handle)
                handle.flush()
                completed = subprocess.run([sys.executable, str(ROOT / "e7gt_msc_v0_1.py"), handle.name], capture_output=True, text=True, check=False)
                self.assertEqual(completed.returncode, 2)
                self.assertIn("document must be an object", completed.stderr)
                self.assertNotIn("Traceback", completed.stderr)

    def test_reconstruction_query_membership_values_are_type_checked(self):
        for field, value, message in (
            ("kind", [], "kind invalid"),
            ("kind", {}, "kind invalid"),
            ("observation_map", [], "observation map invalid"),
            ("observation_map", {}, "observation map invalid"),
        ):
            with self.subTest(field=field, value=value):
                doc = copy.deepcopy(self.unique)
                doc["reconstruction_queries"][1][field] = value
                with self.assertRaisesRegex(MSC.MSCError, message):
                    MSC.evaluate(doc)

    def test_cli_reconstruction_query_type_errors_exit_two_without_traceback(self):
        for field, value, message in (
            ("kind", [], "kind invalid"),
            ("kind", {}, "kind invalid"),
            ("observation_map", [], "observation map invalid"),
            ("observation_map", {}, "observation map invalid"),
        ):
            with self.subTest(field=field, value=value), tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8") as handle:
                doc = copy.deepcopy(self.unique)
                doc["reconstruction_queries"][1][field] = value
                json.dump(doc, handle)
                handle.flush()
                completed = subprocess.run([sys.executable, str(ROOT / "e7gt_msc_v0_1.py"), handle.name], capture_output=True, text=True, check=False)
                self.assertEqual(completed.returncode, 2)
                self.assertIn(message, completed.stderr)
                self.assertNotIn("Traceback", completed.stderr)

    def test_invalid_access_reference_not_hidden_by_resource_limit(self):
        doc = copy.deepcopy(self.unique)
        doc["max_combinations"] = 1
        doc["access_profiles"][0]["observation_maps"] = ["missing"]
        with self.assertRaisesRegex(MSC.MSCError, "unknown observation map"):
            MSC.evaluate(doc)

    def test_invalid_invariant_reference_not_hidden_by_resource_limit(self):
        doc = copy.deepcopy(self.unique)
        doc["max_combinations"] = 1
        doc["invariant_tests"][0]["maps_by_scope"]["local"] = "missing"
        with self.assertRaisesRegex(MSC.MSCError, "unknown reference"):
            MSC.evaluate(doc)

    def test_unknown_commutation_reference_is_malformed(self):
        doc = copy.deepcopy(self.unique)
        doc["commutation_tests"] = [{"test_id": "bad", "direct_map": "missing", "path": ["project-global"]}]
        with self.assertRaisesRegex(MSC.MSCError, "unknown direct map"):
            MSC.evaluate(doc)

    def test_duplicate_optional_identifiers_rejected(self):
        doc = copy.deepcopy(self.unique)
        doc["access_profiles"].append(copy.deepcopy(doc["access_profiles"][0]))
        with self.assertRaisesRegex(MSC.MSCError, "duplicate access_profiles"):
            MSC.evaluate(doc)
        doc = copy.deepcopy(self.unique)
        doc["commutation_tests"] = [{"test_id": "shared", "direct_map": "project-global", "path": ["project-global"]}]
        doc["invariant_tests"][0]["test_id"] = "shared"
        with self.assertRaisesRegex(MSC.MSCError, "duplicate test_id"):
            MSC.evaluate(doc)

    def test_partial_invariant_undefined_outside_closure_is_allowed(self):
        doc = copy.deepcopy(self.unique)
        del doc["maps"][3]["table"]["L1"]
        self.assertEqual(MSC.evaluate(doc)["invariant_tests"][0]["outcome"], "preserved")

    def test_partial_invariant_undefined_on_closure_is_unsupported(self):
        doc = copy.deepcopy(self.unique)
        del doc["maps"][3]["table"]["L0"]
        self.assertEqual(MSC.evaluate(doc)["invariant_tests"][0]["outcome"], "unsupported")

    def test_empty_observation_family_is_universal_quotient(self):
        doc = copy.deepcopy(self.unique)
        doc["access_profiles"].append({"profile_id": "no-access", "scope": "local", "context": "sealed", "observation_maps": []})
        quotient = MSC.evaluate(doc)["access_quotients"][1]
        self.assertTrue(quotient["empty_observation_family"])
        self.assertEqual(quotient["classes"], [["L0", "L1"]])
        self.assertEqual(quotient["missingness_rule"], "co_undefined_equal")

    def test_scope_state_and_observation_fibres_are_distinct(self):
        doc = copy.deepcopy(self.unique)
        doc["carriers"][1]["values"].append("G1")
        doc["maps"][0]["table"]["G1"] = "1"
        doc["maps"][4]["table"]["G1"] = "k1"
        queries = MSC.evaluate(doc)["reconstruction_queries"]
        self.assertEqual(queries[0]["compatible_count"], 1)
        self.assertEqual(queries[1]["compatible_count"], 2)

    def test_invariant_on_incompatible_family_is_not_applicable(self):
        doc = copy.deepcopy(self.obstruction)
        doc["invariant_tests"] = [{"test_id": "no-family", "maps_by_scope": {"r": "c-rs", "s": "p-rs", "t": "p-st"}}]
        outcome = MSC.evaluate(doc)["invariant_tests"][0]["outcome"]
        self.assertEqual(outcome, "not_applicable_incompatible")

    def test_additional_schema_field_rejected_at_runtime(self):
        doc = copy.deepcopy(self.unique)
        doc["unexpected"] = True
        with self.assertRaisesRegex(MSC.MSCError, "additional fields"):
            MSC.evaluate(doc)

    def test_resource_limit_is_distinct(self):
        doc = copy.deepcopy(self.obstruction)
        doc["max_combinations"] = 7
        self.assertEqual(MSC.evaluate(doc)["outcome"], "resource_limit")

    def test_no_common_comparison_carrier_rejected(self):
        doc = copy.deepcopy(self.unique)
        doc["maps"][1]["target_carrier"] = "visible"
        doc["maps"][1]["table"] = {"L0": "same", "L1": "same"}
        with self.assertRaisesRegex(MSC.MSCError, "common comparison carrier"):
            MSC.validate_diagram(doc)

    def test_scope_cycle_rejected(self):
        doc = copy.deepcopy(self.unique)
        doc["links"].append({"link_id": "reverse", "lower_scope": "global", "upper_scope": "local", "projection_map": "compare-local", "comparison_map": "project-global", "criterion": "exact"})
        with self.assertRaisesRegex(MSC.MSCError, "cycle"):
            MSC.validate_diagram(doc)

    def test_commuting_and_non_commuting_maps(self):
        doc = {
            "schema_version": "msc-diagram-v1", "diagram_id": "maps", "max_combinations": 10,
            "carriers": [
                {"carrier_id": "A", "values": ["0", "1"]},
                {"carrier_id": "B", "values": ["0", "1"]},
                {"carrier_id": "C", "values": ["0", "1"]}],
            "scopes": [{"scope_id": "only", "edition": "1", "state_carrier": "A"}],
            "maps": [
                {"map_id": "ab", "source_carrier": "A", "target_carrier": "B", "table": {"0": "0", "1": "1"}},
                {"map_id": "bc", "source_carrier": "B", "target_carrier": "C", "table": {"0": "0", "1": "1"}},
                {"map_id": "direct", "source_carrier": "A", "target_carrier": "C", "table": {"0": "0", "1": "1"}},
                {"map_id": "flipped", "source_carrier": "A", "target_carrier": "C", "table": {"0": "1", "1": "0"}}],
            "links": [],
            "commutation_tests": [
                {"test_id": "yes", "direct_map": "direct", "path": ["ab", "bc"]},
                {"test_id": "no", "direct_map": "flipped", "path": ["ab", "bc"]}]
        }
        results = MSC.evaluate(doc)["commutation_tests"]
        self.assertEqual(results[0]["outcome"], "commuting")
        self.assertEqual(results[1]["outcome"], "non_commuting")

    def test_output_carries_non_ontological_boundary(self):
        boundary = MSC.evaluate(self.unique)["interpretation_boundary"]
        self.assertIn("no external existence", boundary)


if __name__ == "__main__":
    unittest.main()
