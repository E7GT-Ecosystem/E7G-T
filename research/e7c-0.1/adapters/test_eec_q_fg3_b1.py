"""Differential EEC-Q graph-only WP5 fixtures against the pinned FG3 model."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location(
    "eec_q_source_fg3", ROOT / "E7G-T_v0.12_Executable_Examples.py"
)
assert spec is not None and spec.loader is not None
source = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = source
spec.loader.exec_module(source)

from eec_q_fg3_b1 import AdmissionError, Rule, add, push, scale, signature, translate_rows  # noqa: E402


def source_rows(rows):
    result = []
    for row in rows:
        record = row["config"]
        config = source.Graph(tuple(record["edges"]), record["tag"])
        rational = row["coefficient"]
        numerator, denominator = rational["numerator"], rational["denominator"]
        coefficient = numerator if denominator == 1 else Fraction(numerator, denominator)
        result.append((coefficient, config))
    return source.state(*result)


def source_signature(state):
    return tuple((source.key(g), c.numerator, c.denominator) for g, c in state.terms)


class EECQGraphDifferential(unittest.TestCase):
    def test_pinned_profile_and_model_identity(self):
        self.assertEqual((source.PROFILE, source.MODEL), ("EEC-Q/0.1", "FG3/0.1"))

    def test_positive_and_negative_differential_fixtures(self):
        cases = json.loads((HERE / "fixtures/fg3_graph_differential.json").read_text())
        self.assertEqual(len(cases), 11)
        for case in cases:
            with self.subTest(case=case["id"]):
                rows = case["rows"]
                if case["kind"] == "invalid_input":
                    with self.assertRaises(source.InvalidInput):
                        source_rows(rows)
                    with self.assertRaises(AdmissionError):
                        translate_rows(rows)
                    continue
                original = source_rows(rows)
                target = translate_rows(rows)
                self.assertEqual(signature(target), source_signature(original))
                if case["kind"] == "push":
                    declaration = case["rule"]
                    old_rule = source.Rule(declaration["name"], declaration["edge"])
                    new_rule = Rule(declaration["name"], declaration["edge"])
                    self.assertEqual(new_rule.domain_policy,
                                     "strict" if old_rule.name == "require_absent" else "total")
                    try:
                        expected = source.push(old_rule, original)
                    except source.DomainError:
                        self.assertEqual(push(new_rule, target).tag, "domain_error")
                    else:
                        result = push(new_rule, target)
                        self.assertEqual(result.tag, "success")
                        self.assertEqual(signature(result.value), source_signature(expected))

    def test_exact_linear_operations_over_selected_graph_carrier(self):
        rows = [{"config": {"edges": ["AB"], "tag": None},
                 "coefficient": {"numerator": -1, "denominator": 3}}]
        target = translate_rows(rows)
        original = source_rows(rows)
        factor = {"numerator": 2, "denominator": 5}
        self.assertEqual(signature(scale(factor, target)),
                         source_signature(source.scale(Fraction(2, 5), original)))
        self.assertEqual(signature(add(target, target)),
                         source_signature(source.add(original, original)))

    def test_no_probabilistic_coercion_or_implicit_branch_filtering(self):
        rows = [{"config": {"edges": ["AB"], "tag": None},
                 "coefficient": {"numerator": -1, "denominator": 3}}]
        target = translate_rows(rows)
        self.assertEqual(signature(target)[0][1:], (-1, 3))
        self.assertEqual(push(Rule("require_absent", "AB"), target).tag, "domain_error")


if __name__ == "__main__":
    unittest.main()
