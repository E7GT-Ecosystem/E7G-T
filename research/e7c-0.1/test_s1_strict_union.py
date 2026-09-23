"""Strict joint execution, whole failure and independent replay boundaries."""

import copy
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "adapters"))
from eec_q_fg3_b1 import Config, signature
from eec_q_fg3_joint_b1 import joint, join_union
from e7c_s1_evaluator import evaluate
from e7c_s1_replay_checker import ReplayError, check_witness
from e7c_s1_state_joint_static import EDITION, STRICT_EDITION, STRICT_EXTENSION, check_document
from e7c_s1_values import MODULE, SIGNATURE, RESOURCE_EDITION


def graph(edges=(), tag=None):
    return {"edges": list(edges), "tag": tag}


def row(left, right, n, d=1):
    return {"configs": [left, right], "coefficient": {"numerator": n, "denominator": d}}


def program(rows, term=None, *, edition=STRICT_EDITION):
    state = {"tag": "state", "args": [MODULE, SIGNATURE]}
    document = {"edition": edition, "variables": {"j": {"tag": "joint", "args": [state, state]}},
                "term": term or {"tag": "strict_union", "arg": {"tag": "var", "name": "j"}}}
    return document, {"j": {"kind": "joint", "rows": rows}}


def policy(visits=10):
    return {"edition": RESOURCE_EDITION, "max_steps": 10, "max_pair_visits": visits}


class StrictUnionTests(unittest.TestCase):
    def test_success_matches_pinned_fg3_joint_without_extra_product(self):
        a, b, c = graph(["AB"], "same"), graph(["BC"], "same"), graph(["AC"], "same")
        rows = [row(a, b, 2), row(b, a, -1), row(c, c, 1, 2)]
        doc, values = program(rows)
        self.assertEqual(check_document(doc)["type"],
                         f'Outcome[State["{MODULE}","{SIGNATURE}"],"{STRICT_EXTENSION}"]')
        witness = evaluate(doc, values, policy())
        self.assertTrue(check_witness(witness))
        source = joint([(Fraction(2), (Config(("AB",), "same"), Config(("BC",), "same"))),
                        (Fraction(-1), (Config(("BC",), "same"), Config(("AB",), "same"))),
                        (Fraction(1, 2), (Config(("AC",), "same"), Config(("AC",), "same")))])
        model = join_union(source)
        self.assertEqual(model.tag, "success")
        actual = witness["terminal"]["value"]["rows"]
        self.assertEqual([(tuple(r["configs"][0]["edges"]), r["configs"][0]["tag"],
                           Fraction(r["coefficient"]["numerator"], r["coefficient"]["denominator"])) for r in actual],
                         [(g.edges, g.tag, amount) for g, amount in model.value.terms])
        self.assertEqual(witness["ledger"][-1]["visits"], len(source.terms))

    def test_one_negative_supported_pair_fails_whole(self):
        a, b = graph(["AB"], "same"), graph(["BC"], "same")
        bad = graph(["AC"], "other")
        doc, values = program([row(a, b, 3), row(b, bad, -2)])
        witness = evaluate(doc, values, policy())
        self.assertEqual(witness["terminal"], {"tag": "domain_error", "value": None})
        self.assertEqual(witness["ledger"], [{"rule": "strict_union", "tag": "domain_error",
                                                "visits": 2, "offending_index": 1}])
        self.assertEqual(witness["progress"], {"steps": 2, "pair_visits": 2})
        self.assertTrue(check_witness(witness))
        model = join_union(joint([(Fraction(3), (Config(("AB",), "same"), Config(("BC",), "same"))),
                                  (Fraction(-2), (Config(("BC",), "same"), Config(("AC",), "other")))]))
        self.assertEqual((model.tag, model.value), ("domain_error", None))

    def test_zero_joint_and_cancelled_invalid_pair_succeed(self):
        bad_left, bad_right = graph(["AB"], "x"), graph(["AC"], "y")
        for rows in ([], [row(bad_left, bad_right, 1), row(bad_left, bad_right, -1)]):
            with self.subTest(rows=rows):
                doc, values = program(rows)
                witness = evaluate(doc, values, policy(visits=0))
                self.assertEqual(witness["terminal"], {"tag": "success", "value": {"kind": "state", "rows": []}})
                self.assertEqual(witness["ledger"][-1]["visits"], 0)
                self.assertTrue(check_witness(witness))

    def test_resource_exhaustion_precedes_unexamined_domain_failure(self):
        a, b = graph(["AB"], "same"), graph(["BC"], "same")
        bad = graph(["AC"], "other")
        doc, values = program([row(a, b, 3), row(b, bad, 1)])
        witness = evaluate(doc, values, policy(visits=1))
        self.assertEqual(witness["terminal"], {"tag": "resource_exhausted", "bound": "max_pair_visits", "value": None})
        self.assertEqual(witness["ledger"], [])
        self.assertEqual(witness["progress"]["pair_visits"], 1)
        self.assertTrue(check_witness(witness))

    def test_old_edition_and_consumed_outcome_rejected_statically(self):
        doc, _ = program([], edition=EDITION)
        self.assertEqual(check_document(doc)["status"], "diagnostic")
        doc, _ = program([], term={"tag": "marginal", "coordinate": 0,
                                    "arg": {"tag": "strict_union", "arg": {"tag": "var", "name": "j"}}})
        self.assertEqual(check_document(doc)["diagnostic"]["code"], "E7C-S1-T03")
        state = {"tag": "state", "args": [MODULE, SIGNATURE]}
        doc["variables"]["j"] = {"tag": "joint", "args": [state, state, state]}
        doc["term"] = {"tag": "strict_union", "arg": {"tag": "var", "name": "j"}}
        self.assertEqual(check_document(doc)["diagnostic"]["code"], "E7C-S1-T04")

    def test_replay_rejects_forged_whole_success_and_ledger(self):
        doc, values = program([row(graph(["AB"], "x"), graph(["BC"], "y"), 1)])
        good = evaluate(doc, values, policy())
        for mutate in (lambda w: w.update(terminal={"tag": "success", "value": {"kind": "state", "rows": []}}),
                       lambda w: w.update(ledger=[]),
                       lambda w: w["ledger"][0].update(offending_index=True),
                       lambda w: w.update(calculus_edition=EDITION)):
            forged = copy.deepcopy(good)
            mutate(forged)
            with self.assertRaises(ReplayError):
                check_witness(forged)


if __name__ == "__main__":
    unittest.main()
