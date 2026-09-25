"""All fields of the bounded source/IR observations against staged rule."""
import copy
from fractions import Fraction
import itertools
import unittest

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import joint
from eec_q_fg3_joint_b1 import marginal
from e7c_eecq_two_stage_b1 import document, evaluate
from e7_ir_eecq_two_stage_b1 import execute, lower
from e7c_eecq_two_stage_exact_codec import (
    CodecAdmission, LeanGraph, LeanRow, decode_row, graph, observation, partition,
    row, rows, staged_spec,
)


def selected():
    null = Config(("AB",), None)
    empty = Config(("AC",), "")
    opaque = Config(("BC",), "α \" 🧭\n")
    return joint([(Fraction(-2, 3), (null, empty)),
                  (Fraction(5, 7), (empty, opaque)),
                  (Fraction(-19, 11), (opaque, null))], arity=2)


class ExactCodec(unittest.TestCase):
    def test_arbitrary_strings_and_null_are_distinct(self):
        source = document(selected())
        encoded = rows(source)
        self.assertEqual([decode_row(r) for r in encoded], source["first"]["rows"])
        self.assertNotEqual(graph({"edges": [], "tag": ""}),
                            graph({"edges": [], "tag": None}))
        self.assertEqual([e for r in encoded for e in (r.left.tag, r.right.tag)
                          if e is not None].count(""), 2)
        self.assertEqual([r.coefficient for r in encoded],
                         [Fraction(-2, 3), Fraction(5, 7), Fraction(-19, 11)])
        self.assertEqual(sum(len(p) for p in partition(encoded)), len(encoded))

    def test_unrepresentable_or_noncanonical_wire_rejected(self):
        for graph_record in ({"edges": ["BC", "AB"], "tag": None},
                             {"edges": ["AB", "AB"], "tag": None},
                             {"edges": [], "tag": 3},
                             {"edges": [], "tag": "\ud800"},
                             {"edges": ["AX"], "tag": None}):
            with self.subTest(graph=graph_record), self.assertRaises(CodecAdmission):
                graph(graph_record)
        bad = {"atoms": [{"edges": [], "tag": None}] * 2,
               "coefficient": {"numerator": 2, "denominator": 4}}
        with self.assertRaises(CodecAdmission):
            row(bad)

    def test_inverse_rejects_constructed_surrogate_tag(self):
        good = LeanGraph(True, False, False, None)
        invalid = LeanGraph(False, True, False, "\ud800")
        for candidate in (LeanRow(invalid, good, Fraction(1, 3)),
                          LeanRow(good, invalid, Fraction(-2, 5))):
            with self.subTest(candidate=candidate), self.assertRaises(CodecAdmission):
                decode_row(candidate)

    def test_event_metadata_checked_before_projection(self):
        source = document(selected(), step_bound=20, ledger_bound=20)
        result = evaluate(source)
        self.assertEqual(observation(source, result), staged_spec(source))
        tamperings = (
            (0, "effect", "wrong_first_attempt_effect"),
            (0, "predicate_edition", "wrong_first_predicate"),
            (1, "effect", "wrong_first_row_effect"),
            (4, "effect", "wrong_second_attempt_effect"),
            (4, "predicate_edition", "wrong_second_predicate"),
            (5, "effect", "wrong_second_row_effect"),
        )
        for index, key, replacement in tamperings:
            altered = copy.deepcopy(result)
            altered["ordered_ledger"][index][key] = replacement
            altered["resource_progress"]["ledger_prefix"][index][key] = replacement
            with self.subTest(index=index, field=key), self.assertRaises(CodecAdmission):
                observation(source, altered)

    def test_all_policy_budget_boundaries_source_ir_and_step_rule(self):
        supports = (joint([], arity=2), selected())
        for value, steps, ledger, first_cap, first_obl, second_cap, second_obl in itertools.product(
                supports, range(7), range(7), (False, True),
                ("resolved", "unresolved"), (False, True), ("resolved", "unresolved")):
            source = document(value, step_bound=steps, ledger_bound=ledger,
                              first_capability=first_cap, first_obligation=first_obl,
                              second_capability=second_cap, second_obligation=second_obl)
            with self.subTest(size=len(value.terms), step=steps, ledger=ledger,
                              first=(first_cap, first_obl), second=(second_cap, second_obl)):
                spec = staged_spec(source)
                self.assertEqual(observation(source, evaluate(source)), spec)
                self.assertEqual(observation(source, execute(lower(source))), spec)

    def test_second_attempt_charged_without_append(self):
        only = joint([(Fraction(-2, 1), (Config(("BC",), None),
                                          Config(("AC",), "")))], arity=2)
        source = document(only, step_bound=4, ledger_bound=2)
        spec = staged_spec(source)
        self.assertEqual(spec["terminal"], "resource_limit")
        self.assertEqual(spec["completedSteps"], 3)
        self.assertTrue(spec["secondStarted"])
        self.assertEqual([(e.stage, e.index) for e in spec["orderedLedger"]],
                         [("first", None), ("first", 0)])
        self.assertEqual(observation(source, evaluate(source)), spec)
        self.assertEqual(observation(source, execute(lower(source))), spec)

    def test_same_marginals_keep_distinct_correlated_rows(self):
        a, b = Config(("AB",), None), Config(("BC",), None)
        left = joint([(Fraction(1, 3), (a, a)), (Fraction(1, 3), (b, b))], arity=2)
        right = joint([(Fraction(1, 3), (a, b)), (Fraction(1, 3), (b, a))], arity=2)
        for coordinate in (0, 1):
            self.assertEqual(marginal(left, coordinate), marginal(right, coordinate))
        results = []
        for value in (left, right):
            source = document(value)
            spec = staged_spec(source)
            self.assertEqual(observation(source, evaluate(source)), spec)
            self.assertEqual(observation(source, execute(lower(source))), spec)
            results.append(spec["partition"])
        self.assertNotEqual(results[0], results[1])


if __name__ == "__main__":
    unittest.main()
