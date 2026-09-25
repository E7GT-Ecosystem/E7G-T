"""Exact finite fixture encoding for the Lean MSC Boolean obstruction."""

import copy
import hashlib
import json
from pathlib import Path
import unittest

from test_msc_finite_b1 import ROOT, admit, evaluate, selected, source


FIXTURE = ROOT / "fixtures" / "global_obstruction.json"
FIXTURE_SHA256 = "b1e87b46a57b5c8a52a5c41737dbf96250637e5f49b02854bbe33303c8bd3d2a"


def encode_boolean_obstruction(doc):
    """Reject any diagram whose equations differ from the Lean theorem."""
    if doc.get("schema_version") != "msc-diagram-v1" or doc.get("diagram_id") != "MSC-OBSTRUCTION-01":
        raise ValueError("diagram identity")
    if doc.get("max_combinations") != 20 or set(doc) != {
        "schema_version", "diagram_id", "max_combinations", "carriers", "scopes", "maps", "links"
    }:
        raise ValueError("fixture boundary")
    if doc.get("carriers") != [
        {"carrier_id": name, "values": ["0", "1"]} for name in "RSTV"
    ]:
        raise ValueError("Boolean carriers")
    if doc.get("scopes") != [
        {"scope_id": name.lower(), "edition": "1", "state_carrier": name} for name in "RST"
    ]:
        raise ValueError("scope binding")
    identity = {"0": "0", "1": "1"}
    flip = {"0": "1", "1": "0"}
    expected_maps = [
        {"map_id": name, "source_carrier": domain, "target_carrier": "V",
         "table": flip if name == "p-rt-flip" else identity}
        for name, domain in (("p-rs", "S"), ("c-rs", "R"), ("p-st", "T"),
                             ("c-st", "S"), ("p-rt-flip", "T"), ("c-rt", "R"))
    ]
    if doc.get("maps") != expected_maps:
        raise ValueError("Lean map equations")
    if doc.get("links") != [
        {"link_id": edge, "lower_scope": lower, "upper_scope": upper,
         "projection_map": projection, "comparison_map": comparison,
         "criterion": "exact"}
        for edge, lower, upper, projection, comparison in (
            ("r-s", "r", "s", "p-rs", "c-rs"),
            ("s-t", "s", "t", "p-st", "c-st"),
            ("r-t", "r", "t", "p-rt-flip", "c-rt"))
    ]:
        raise ValueError("Lean link equations")
    return True


class MSCLeanObstruction(unittest.TestCase):
    def test_pinned_fixture_encodes_and_agrees_with_both_executors(self):
        self.assertEqual(hashlib.sha256(FIXTURE.read_bytes()).hexdigest(), FIXTURE_SHA256)
        doc = json.loads(FIXTURE.read_text())
        self.assertTrue(encode_boolean_obstruction(doc))
        reference = source.evaluate(doc)
        independent = evaluate(admit(selected(doc)))
        self.assertEqual((reference["outcome"], independent.outcome),
                         ("incompatible", "incompatible"))
        self.assertEqual((reference["candidate_combinations"], independent.candidate_count), (8, 8))
        self.assertEqual(reference["linkwise_satisfiable"], dict(independent.linkwise))
        self.assertEqual(set(reference["linkwise_satisfiable"].values()), {True})
        self.assertTrue(reference["global_obstruction_despite_linkwise_satisfiability"])
        self.assertTrue(independent.obstruction)
        self.assertEqual(reference["compatible_families"], [])
        self.assertEqual(independent.compatible, ())

    def test_flip_or_relation_mutation_cannot_inherit_proof(self):
        doc = json.loads(FIXTURE.read_text())
        changed = copy.deepcopy(doc)
        changed["maps"][4]["table"] = {"0": "0", "1": "1"}
        with self.assertRaisesRegex(ValueError, "map equations"):
            encode_boolean_obstruction(changed)
        self.assertNotEqual(source.evaluate(changed)["outcome"], "incompatible")
        changed = copy.deepcopy(doc)
        changed["links"][2]["criterion"] = "different"
        with self.assertRaisesRegex(ValueError, "link equations"):
            encode_boolean_obstruction(changed)


if __name__ == "__main__":
    unittest.main()
