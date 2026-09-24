"""Correlated joint restriction, exact rational baseline and complete replay."""

import copy
from fractions import Fraction
import json
from pathlib import Path
import unittest

from eec_q_fg3_b1 import Config, AdmissionError
from eec_q_fg3_joint_b1 import joint, independent, marginal, joint_signature, restrict_joint_absent
from e7c_b1_canonical import canonical_bytes, digest
from e7c_eecq_joint_restrict_b1 import JointRestrictionAdmission, admit, document, evaluate, rows
from e7_ir_eecq_joint_restrict_b1 import (
    JointRestrictionIRAdmission, compare_replay, execute, lower, parse, serialize,
)

FIXTURE = Path(__file__).resolve().parent / "fixtures/wp5_ir/eecq_correlated_joint_restrict.json"
P, Q = Config(("AB",), None), Config(("BC",), None)


def selected(swapped=False):
    return joint([(Fraction(1), (P, Q if swapped else P)),
                  (Fraction(1), (Q, P if swapped else Q))], arity=2)


def rational_enumeration(source):
    """Plain rational reference: visit tuple rows, never form marginal products."""
    kept, removed = [], []
    for row in source["rows"]:
        c = Fraction(row["coefficient"]["numerator"], row["coefficient"]["denominator"])
        copy_row = {"atoms": row["atoms"], "coefficient": {
            "numerator": c.numerator, "denominator": c.denominator}}
        (removed if "AB" in row["atoms"][0]["edges"] else kept).append(copy_row)
    return {"retained": kept, "excluded": removed,
            "predicate_edition": source["predicate_edition"]}


class JointRestrictIR(unittest.TestCase):
    def test_fixture_and_independent_rational_control(self):
        package = json.loads(FIXTURE.read_bytes())
        self.assertEqual(FIXTURE.read_bytes(), canonical_bytes(package) + b"\n")
        self.assertEqual(package, lower(document(selected())))
        self.assertEqual(parse(serialize(package)), package)
        result = compare_replay(package)["ir_result"]
        self.assertEqual(result, execute(package))
        self.assertEqual(result["terminal_outcome"]["value"],
                         rational_enumeration(package["source_document"]))
        self.assertEqual(result["resource_progress"]["completed_steps"], 3)
        self.assertEqual([e["decision"] for e in result["ordered_ledger"][1:]],
                         ["excluded", "retained"])

    def test_same_marginals_distinct_correlations_and_signed_coefficients(self):
        a, b = selected(), selected(swapped=True)
        self.assertEqual(marginal(a, 0), marginal(b, 0))
        self.assertEqual(marginal(a, 1), marginal(b, 1))
        self.assertNotEqual(joint_signature(a), joint_signature(b))
        result_a, result_b = [], []
        for value, collector in ((a, result_a), (b, result_b)):
            doc = document(value)
            ir = lower(doc)
            terminal = compare_replay(ir)["ir_result"]["terminal_outcome"]
            self.assertEqual(terminal["value"], rational_enumeration(doc))
            kept, removed = restrict_joint_absent("AB", 0, value)
            self.assertEqual(terminal["value"]["retained"], rows(kept))
            self.assertEqual(terminal["value"]["excluded"], rows(removed))
            collector.append(terminal["value"])
        self.assertNotEqual(result_a, result_b)
        product = independent(marginal(a, 0), marginal(a, 1))
        self.assertEqual(len(product.terms), 4)
        product_observation = compare_replay(lower(document(product)))["ir_result"]
        self.assertEqual(product_observation["terminal_outcome"]["value"],
                         rational_enumeration(document(product)))
        self.assertNotEqual(product_observation["terminal_outcome"]["value"], result_a[0])
        signed = joint([(Fraction(-2, 3), (P, Q)), (Fraction(1, 4), (Q, P))])
        s = document(signed)
        self.assertEqual(compare_replay(lower(s))["ir_result"]["terminal_outcome"]["value"],
                         rational_enumeration(s))
        self.assertEqual(compare_replay(lower(document(joint([], arity=2))))["ir_result"]
                         ["terminal_outcome"]["value"]["retained"], [])
        only_excluded = compare_replay(lower(document(joint([(Fraction(1, 3), (P, Q))]))))
        self.assertEqual(only_excluded["ir_result"]["terminal_outcome"]["value"]["retained"], [])
        self.assertEqual(only_excluded["ir_result"]["terminal_outcome"]["value"]["excluded"][0]
                         ["coefficient"], {"numerator": 1, "denominator": 3})

    def test_resource_failure_and_unsupported_remain_distinct(self):
        for steps in range(5):
            for ledger in range(5):
                for cap, obligation in ((True, "resolved"), (False, "resolved"),
                                        (True, "unresolved")):
                    with self.subTest(steps=steps, ledger=ledger, cap=cap,
                                      obligation=obligation):
                        doc = document(selected(), step_bound=steps, ledger_bound=ledger,
                                       capability=cap, obligation=obligation)
                        result = compare_replay(lower(doc))["ir_result"]
                        self.assertLessEqual(result["resource_progress"]["completed_steps"], steps)
                        self.assertLessEqual(len(result["ordered_ledger"]), ledger)
                        if steps >= 3 and ledger >= 3:
                            expected = ("success" if cap and obligation == "resolved" else
                                        "unsupported" if not cap else "undetermined")
                            self.assertEqual(result["terminal_outcome"]["tag"], expected)
                        if result["terminal_outcome"]["tag"] == "resource_limit":
                            self.assertNotIn("value", result["terminal_outcome"])
        self.assertEqual(evaluate(document(selected(), step_bound=0))["ordered_ledger"], [])

    def test_rebound_exclusions_types_and_late_invalid_rows_rejected(self):
        package = json.loads(FIXTURE.read_bytes())
        for mutate in (
                lambda p: p["source_witness"]["claim"]["terminal_outcome"]["value"].update({"excluded": []}),
                lambda p: p["source_witness"]["claim"]["terminal_outcome"].update({"tag": "resource_limit"}),
                lambda p: p["instruction"].update({"input_type": "State[FG3]"}),
        ):
            changed = copy.deepcopy(package)
            mutate(changed)
            changed["source_witness"]["id"] = digest({k: v for k, v in changed["source_witness"].items() if k != "id"})
            changed["id"] = digest({k: v for k, v in changed.items() if k != "id"})
            with self.assertRaises(JointRestrictionIRAdmission):
                compare_replay(changed)
        bad = document(selected(), step_bound=0)
        bad["rows"][-1]["atoms"][1]["edges"] = ["BC", "unknown"]
        with self.assertRaises(JointRestrictionAdmission):
            admit(bad)
        with self.assertRaises(AdmissionError):
            restrict_joint_absent("AB", 2, selected())


if __name__ == "__main__":
    unittest.main()
