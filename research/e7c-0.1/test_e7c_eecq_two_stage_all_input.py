"""Finite attacks on the external premises of the Lean all-list relation.

The Lean theorem quantifies over lists; these Python tests sample the separate
source/IR implementation link and do not prove that link for every document.
"""

import copy
from fractions import Fraction
import itertools
import unittest

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import joint, marginal
from e7c_b1_canonical import digest
from e7c_eecq_two_stage_b1 import TwoStageAdmission, admit, document, evaluate
from e7_ir_eecq_two_stage_b1 import TwoStageIRAdmission, execute, lower


P = Config(("AB",), None)
Q = Config(("BC",), None)
R = Config(("AC",), None)


def enumerate_rows(source):
    value = {"retained": [], "first_excluded": [], "second_excluded": [],
             "predicate_editions": [source["first"]["predicate_edition"],
                                    source["second_predicate_edition"]]}
    for row in source["first"]["rows"]:
        if "AB" in row["atoms"][0]["edges"]:
            field = "first_excluded"
        elif "BC" in row["atoms"][1]["edges"]:
            field = "second_excluded"
        else:
            field = "retained"
        value[field].append(copy.deepcopy(row))
    return value


def check_observation(source):
    admitted = admit(source)
    assert admitted.arity == 2
    witness = evaluate(source)
    ir = execute(lower(source))
    assert {k: v for k, v in witness.items() if k != "witness"} == ir
    if ir["terminal_outcome"]["tag"] == "success":
        assert ir["terminal_outcome"]["value"] == enumerate_rows(source)
        for field in ("retained", "first_excluded", "second_excluded"):
            for row in ir["terminal_outcome"]["value"][field]:
                c = row["coefficient"]
                assert Fraction(c["numerator"], c["denominator"]) != 0
    else:
        assert "value" not in ir["terminal_outcome"]
    assert ir["resource_progress"]["ledger_prefix"] == ir["ordered_ledger"]
    return ir


class AllInputBridgePremises(unittest.TestCase):
    def test_all_unique_supports_of_size_at_most_two(self):
        # Every subset of size 0, 1 or 2 of the nine correlated graph pairs,
        # with either sign on each coefficient, plus a budget boundary.
        pairs = list(itertools.product((P, Q, R), repeat=2))
        for size in range(3):
            for support in itertools.combinations(pairs, size):
                for signs in itertools.product((-1, 1), repeat=size):
                    value = joint([(Fraction(sign * (i + 1), i + 2), pair)
                                   for i, (sign, pair) in enumerate(zip(signs, support))], arity=2)
                    source = document(value)
                    with self.subTest(support=support, signs=signs):
                        result = check_observation(source)
                        self.assertEqual(result["terminal_outcome"]["tag"], "success")
                        count_first = sum("AB" not in r["atoms"][0]["edges"]
                                          for r in source["first"]["rows"])
                        needed = 2 + len(source["first"]["rows"]) + count_first
                        self.assertEqual(result["resource_progress"]["completed_steps"], needed)
                        bound = document(value, step_bound=needed - 1, ledger_bound=needed)
                        self.assertEqual(check_observation(bound)["terminal_outcome"]["tag"],
                                         "resource_limit")

    def test_correlated_pairs_and_exact_coefficients(self):
        a = joint([(Fraction(-2, 3), (P, P)), (Fraction(-2, 3), (Q, Q))], arity=2)
        b = joint([(Fraction(-2, 3), (P, Q)), (Fraction(-2, 3), (Q, P))], arity=2)
        self.assertEqual(marginal(a, 0), marginal(b, 0))
        self.assertEqual(marginal(a, 1), marginal(b, 1))
        observed = [check_observation(document(x))["terminal_outcome"]["value"] for x in (a, b)]
        self.assertNotEqual(observed[0], observed[1])

    def test_premises_have_counterexamples(self):
        value = joint([(Fraction(-2, 3), (P, Q)), (Fraction(1, 4), (Q, R))], arity=2)
        source = document(value)
        for change in (lambda s: s["first"]["rows"].append(copy.deepcopy(s["first"]["rows"][0])),
                       lambda s: s["first"]["rows"][0]["coefficient"].update(
                           {"numerator": -4, "denominator": 6}),
                       lambda s: s["first"]["rows"][0]["coefficient"].update(
                           {"numerator": 0})):
            invalid = copy.deepcopy(source)
            change(invalid)
            with self.assertRaises(TwoStageAdmission):
                admit(invalid)
        first_bad = document(value, first_capability=False)
        self.assertEqual(check_observation(first_bad)["terminal_outcome"]["tag"], "unsupported")
        second_bad = document(value, second_obligation="unresolved")
        self.assertEqual(check_observation(second_bad)["terminal_outcome"]["tag"], "undetermined")
        exhausted = document(value, step_bound=0)
        self.assertEqual(check_observation(exhausted)["terminal_outcome"]["tag"], "resource_limit")
        forged = lower(source)
        forged["first_ir"]["source_witness"]["claim"]["ordered_ledger"] = []
        child = forged["first_ir"]["source_witness"]
        child["id"] = digest({k: v for k, v in child.items() if k != "id"})
        forged["first_ir"]["id"] = digest({k: v for k, v in forged["first_ir"].items() if k != "id"})
        forged["source_witness"]["first_witness"] = copy.deepcopy(child)
        forged["source_witness"]["id"] = digest({k: v for k, v in forged["source_witness"].items() if k != "id"})
        forged["id"] = digest({k: v for k, v in forged.items() if k != "id"})
        with self.assertRaises(TwoStageIRAdmission):
            execute(forged)


if __name__ == "__main__":
    unittest.main()
