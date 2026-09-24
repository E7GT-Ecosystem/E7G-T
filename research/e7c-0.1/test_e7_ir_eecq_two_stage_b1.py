"""Two-stage correlated restriction and a plain exact-rational control."""

import copy
from fractions import Fraction
import json
from pathlib import Path
import unittest

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import joint, marginal
from e7c_b1_canonical import canonical_bytes, canonical_key, digest
from e7c_eecq_two_stage_b1 import (
    SECOND_PREDICATE, TwoStageAdmission, admit, conserves, document, evaluate,
)
from e7_ir_eecq_two_stage_b1 import (
    TwoStageIRAdmission, compare_replay, execute, lower, parse, serialize,
)

FIXTURE = Path(__file__).resolve().parent / "fixtures/wp5_ir/eecq_two_stage_joint.json"
P, Q, R = Config(("AB",), None), Config(("BC",), None), Config(("AC",), None)


def selected(swapped=False):
    return joint([(Fraction(-2, 3), (P, Q if swapped else P)),
                  (Fraction(-2, 3), (Q, P if swapped else Q)),
                  (Fraction(1, 4), (R, R))], arity=2)


def enumeration(source):
    """Independent finite Fraction partition directly over original tuples."""
    final, first_out, second_out = [], [], []
    for row in source["first"]["rows"]:
        coefficient = Fraction(row["coefficient"]["numerator"],
                               row["coefficient"]["denominator"])
        exact = {"atoms": copy.deepcopy(row["atoms"]), "coefficient": {
            "numerator": coefficient.numerator, "denominator": coefficient.denominator}}
        if "AB" in row["atoms"][0]["edges"]:
            first_out.append(exact)
        elif "BC" in row["atoms"][1]["edges"]:
            second_out.append(exact)
        else:
            final.append(exact)
    return {"retained": final, "first_excluded": first_out,
            "second_excluded": second_out,
            "predicate_editions": [source["first"]["predicate_edition"], SECOND_PREDICATE]}


class TwoStageJoint(unittest.TestCase):
    def test_complete_fixture_and_conservation(self):
        package = json.loads(FIXTURE.read_bytes())
        self.assertEqual(FIXTURE.read_bytes(), canonical_bytes(package) + b"\n")
        self.assertEqual(package, lower(document(selected())))
        self.assertEqual(parse(serialize(package)), package)
        actual = compare_replay(package)["ir_result"]
        self.assertEqual(actual, execute(package))
        value = actual["terminal_outcome"]["value"]
        self.assertEqual(value, enumeration(package["source_document"]))
        self.assertTrue(conserves(package["source_document"]["first"]["rows"],
                                  value["retained"], value["first_excluded"],
                                  value["second_excluded"]))
        self.assertEqual([len(value[k]) for k in ("retained", "first_excluded", "second_excluded")],
                         [1, 1, 1])
        self.assertEqual(actual["resource_progress"]["completed_steps"], 7)
        self.assertEqual(len(actual["ordered_ledger"]), 7)

    def test_identical_marginals_distinct_joint_partition(self):
        a, b = selected(), selected(swapped=True)
        self.assertEqual(marginal(a, 0), marginal(b, 0))
        self.assertEqual(marginal(a, 1), marginal(b, 1))
        observations = []
        for value in (a, b):
            source = document(value)
            result = compare_replay(lower(source))["ir_result"]["terminal_outcome"]["value"]
            self.assertEqual(result, enumeration(source))
            observations.append(result)
        self.assertNotEqual(observations[0], observations[1])
        self.assertEqual([len(observations[1][k]) for k in
                          ("retained", "first_excluded", "second_excluded")], [2, 1, 0])

    def test_stage_specific_failures_and_resource_prefixes(self):
        for steps in range(9):
            for ledger in range(9):
                for first_cap, second_cap, second_obligation in (
                        (True, True, "resolved"), (False, True, "resolved"),
                        (True, False, "resolved"), (True, True, "unresolved")):
                    with self.subTest(steps=steps, ledger=ledger,
                                      first_cap=first_cap, second_cap=second_cap,
                                      second_obligation=second_obligation):
                        source = document(selected(), step_bound=steps, ledger_bound=ledger,
                                          first_capability=first_cap,
                                          second_capability=second_cap,
                                          second_obligation=second_obligation)
                        package = lower(source)
                        result = compare_replay(package)["ir_result"]
                        self.assertLessEqual(result["resource_progress"]["completed_steps"], steps)
                        self.assertLessEqual(len(result["ordered_ledger"]), ledger)
                        self.assertEqual(result["resource_progress"]["ledger_prefix"],
                                         result["ordered_ledger"])
                        if result["terminal_outcome"]["tag"] == "resource_limit":
                            self.assertNotIn("value", result["terminal_outcome"])
                        if not first_cap:
                            self.assertFalse(package["source_witness"]["second_started"])
                        if steps >= 7 and ledger >= 7:
                            expected = ("unsupported" if not first_cap or not second_cap
                                        else "undetermined" if second_obligation == "unresolved"
                                        else "success")
                            self.assertEqual(result["terminal_outcome"]["tag"], expected)
                            if not second_cap and first_cap:
                                self.assertEqual(len(result["resource_progress"]["first_excluded"]), 1)
                                self.assertEqual(result["resource_progress"]["second_excluded_prefix"], [])
        midway = compare_replay(lower(document(selected(), step_bound=6)))["ir_result"]
        self.assertEqual(midway["terminal_outcome"]["tag"], "resource_limit")
        self.assertEqual(len(midway["resource_progress"]["first_excluded"]), 1)
        self.assertLessEqual(len(midway["resource_progress"]["second_excluded_prefix"]), 1)
        first_unknown = compare_replay(lower(document(
            selected(), first_obligation="unresolved")))["ir_result"]
        self.assertEqual(first_unknown["terminal_outcome"]["tag"], "undetermined")
        self.assertIsNone(first_unknown["resource_progress"]["first_excluded"])
        second_unknown = compare_replay(lower(document(
            selected(), second_obligation="unresolved")))["ir_result"]
        self.assertEqual(second_unknown["terminal_outcome"]["tag"], "undetermined")
        self.assertEqual(len(second_unknown["resource_progress"]["first_excluded"]), 1)

    def test_adversarial_rebound_and_forged_partition(self):
        package = json.loads(FIXTURE.read_bytes())
        for mutation in (
                lambda p: p["source_witness"]["claim"]["terminal_outcome"]["value"].update(
                    {"first_excluded": []}),
                lambda p: p["source_witness"]["claim"]["terminal_outcome"]["value"].update(
                    {"second_excluded": []}),
                lambda p: p["source_witness"]["claim"]["terminal_outcome"].update(
                    {"tag": "resource_limit"}),
                lambda p: p["instruction"].update({"fields": ["retained"]}),
        ):
            altered = copy.deepcopy(package)
            mutation(altered)
            altered["source_witness"]["id"] = digest({k: v for k, v in altered["source_witness"].items() if k != "id"})
            altered["id"] = digest({k: v for k, v in altered.items() if k != "id"})
            with self.assertRaises(TwoStageIRAdmission):
                compare_replay(altered)
        original = package["source_document"]["first"]["rows"]
        result = enumeration(package["source_document"])
        changed = copy.deepcopy(result["retained"])
        changed[0]["coefficient"] = {"numerator": 9, "denominator": 1}
        self.assertFalse(conserves(original, changed, result["first_excluded"],
                                   result["second_excluded"]))
        self.assertFalse(conserves(original, result["retained"] + result["retained"],
                                   result["first_excluded"], result["second_excluded"]))
        malformed = document(selected(), step_bound=0)
        malformed["first"]["rows"][-1]["atoms"][0]["edges"] = ["invalid"]
        with self.assertRaises(TwoStageAdmission):
            admit(malformed)


if __name__ == "__main__":
    unittest.main()
