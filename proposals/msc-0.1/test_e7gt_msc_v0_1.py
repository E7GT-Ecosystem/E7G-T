import copy
import importlib.util
import json
import pathlib
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

    def test_access_quotient_can_hide_distinct_states(self):
        classes = MSC.evaluate(self.unique)["access_quotients"][0]["classes"]
        self.assertEqual(classes, [["L0", "L1"]])

    def test_shared_invariant_preserved_on_compatible_family(self):
        invariant = MSC.evaluate(self.unique)["invariant_tests"][0]
        self.assertEqual(invariant, {"test_id": "shared-k", "outcome": "preserved"})

    def test_pairwise_compatible_global_obstruction(self):
        result = MSC.evaluate(self.obstruction)
        self.assertEqual(result["outcome"], "incompatible")
        self.assertTrue(result["pairwise_all_satisfiable"])
        self.assertTrue(result["global_obstruction_despite_pairwise_compatibility"])

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
        doc["links"].append({"link_id": "reverse", "lower_scope": "global", "upper_scope": "local", "projection_map": "bridge-local", "bridge_map": "project-global", "criterion": "exact"})
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

