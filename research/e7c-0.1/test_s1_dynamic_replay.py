"""Executable S1 scope, source-model differential and adversarial replay."""

import copy
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "adapters"))
from eec_q_fg3_b1 import Config, collect
from eec_q_fg3_joint_b1 import independent, marginal
from e7c_s1_evaluator import evaluate
from e7c_s1_replay_checker import ReplayError, check_witness
from e7c_s1_state_joint_static import EDITION
from e7c_s1_values import (CANONICAL_BLOB, FG3_BLOB, MODULE, SIGNATURE,
                           RESOURCE_EDITION, RuntimeAdmissionError)


def state_type():
    return {"tag": "state", "args": [MODULE, SIGNATURE]}


def var(name):
    return {"tag": "var", "name": name}


def config(edges=(), tag=None):
    return {"edges": list(edges), "tag": tag}


def row(configs, n, d=1):
    return {"configs": configs, "coefficient": {"numerator": n, "denominator": d}}


def value(kind, rows):
    return {"kind": kind, "rows": rows}


def doc(term, variables=None):
    return {"edition": EDITION, "variables": variables or {"a": state_type(), "b": state_type()}, "term": term}


def policy(steps=12, pairs=40):
    return {"edition": RESOURCE_EDITION, "max_steps": steps, "max_pair_visits": pairs}


class S1DynamicTests(unittest.TestCase):
    def setUp(self):
        self.a = value("state", [row([config(["AB"])], 2), row([config(["BC"])], -1)])
        self.b = value("state", [row([config(["AC"])], 1, 2)])
        self.values = {"a": self.a, "b": self.b}
        self.product = {"tag": "independent", "left": var("a"), "right": var("b")}

    def test_exact_product_and_marginals_match_separate_fg3_model(self):
        left = collect([(Config(("AB",), None), Fraction(2)), (Config(("BC",), None), Fraction(-1))])
        right = collect([(Config(("AC",), None), Fraction(1, 2))])
        model_joint = independent(left, right)
        witness = evaluate(doc(self.product), self.values, policy())
        self.assertTrue(check_witness(witness))
        got = witness["terminal"]["value"]["rows"]
        self.assertEqual([(tuple(tuple(c["edges"]) for c in r["configs"]), Fraction(**{
            "numerator": r["coefficient"]["numerator"], "denominator": r["coefficient"]["denominator"]})) for r in got],
            [(tuple(a.edges for a in atoms), n) for atoms, n in model_joint.terms])
        for i in (0, 1):
            term = {"tag": "marginal", "coordinate": i, "arg": self.product}
            witness = evaluate(doc(term), self.values, policy())
            self.assertTrue(check_witness(witness))
            actual = witness["terminal"]["value"]["rows"]
            self.assertEqual([(tuple(r["configs"][0]["edges"]), Fraction(r["coefficient"]["numerator"], r["coefficient"]["denominator"])) for r in actual],
                             [(g.edges, n) for g, n in marginal(model_joint, i).terms])

    def test_pinned_repository_sources(self):
        root = Path(__file__).resolve().parents[2]
        for path, expected in (("E7G-T_Kernel_v0.12.1_Experimental_Canonical_Reference.md", CANONICAL_BLOB),
                               ("E7G-T_v0.12_Executable_Examples.py", FG3_BLOB)):
            self.assertEqual(subprocess.check_output(["git", "hash-object", path], cwd=root, text=True).strip(), expected)

    def test_correlated_input_and_cancellation_preserve_joint_choice(self):
        p, q = config(["AB"]), config(["BC"])
        joint = value("joint", [row([p, q], 1), row([p, q], -1), row([p, p], 3), row([q, q], 2)])
        joint_type = {"tag": "joint", "args": [state_type(), state_type()]}
        w = evaluate(doc({"tag": "marginal", "coordinate": 0, "arg": var("j")}, {"j": joint_type}), {"j": joint}, policy())
        self.assertTrue(check_witness(w))
        self.assertEqual([r["coefficient"]["numerator"] for r in w["terminal"]["value"]["rows"]], [3, 2])

    def test_bad_zero_rows_fail_before_cancellation(self):
        malformed = value("state", [row([config(["bad"])], 0)])
        with self.assertRaises(RuntimeAdmissionError):
            evaluate(doc(var("a")), {"a": malformed, "b": self.b}, policy())
        forged = value("state", [row([config(["AB"])], 1), row([config(["AB"])], -1), row([config(["bad"])], 0)])
        with self.assertRaises(RuntimeAdmissionError):
            evaluate(doc(var("a")), {"a": forged, "b": self.b}, policy())

    def test_bound_failure_is_whole_and_replayable(self):
        for steps, pairs, bound in ((2, 40, "max_steps"), (12, 1, "max_pair_visits")):
            witness = evaluate(doc(self.product), self.values, policy(steps, pairs))
            self.assertEqual(witness["terminal"], {"tag": "resource_exhausted", "bound": bound, "value": None})
            self.assertTrue(check_witness(witness))
        nested = {"tag": "marginal", "coordinate": 0, "arg": self.product}
        witness = evaluate(doc(nested), self.values, policy(pairs=3))
        self.assertEqual(witness["terminal"]["tag"], "resource_exhausted")
        self.assertIsNone(witness["terminal"]["value"])
        self.assertEqual([event["rule"] for event in witness["ledger"]], ["independent"])
        self.assertEqual(witness["progress"]["pair_visits"], 3)
        self.assertTrue(check_witness(witness))

    def test_input_rejects_bool_coefficient_and_wrong_arity(self):
        bad_bool = value("state", [row([config()], True)])
        with self.assertRaises(RuntimeAdmissionError):
            evaluate(doc(var("a")), {"a": bad_bool, "b": self.b}, policy())
        wrong = value("joint", [row([config()], 1)])
        jtype = {"tag": "joint", "args": [state_type(), state_type()]}
        with self.assertRaises(RuntimeAdmissionError):
            evaluate(doc(var("j"), {"j": jtype}), {"j": wrong}, policy())

    def test_forged_result_ledger_progress_and_pins_are_rejected(self):
        witness = evaluate(doc(self.product), self.values, policy())
        for path, replacement in (("terminal", {"tag": "success", "value": self.a}),
                                  ("ledger", []), ("progress", {"steps": 0, "pair_visits": 0}),
                                  ("fg3_blob", "wrong")):
            forged = copy.deepcopy(witness)
            forged[path] = replacement
            with self.subTest(path=path), self.assertRaises(ReplayError):
                check_witness(forged)
        forged = copy.deepcopy(witness)
        forged["terminal"]["value"]["rows"][0]["coefficient"]["numerator"] = True
        with self.assertRaises(ReplayError):
            check_witness(forged)


if __name__ == "__main__":
    unittest.main()
