"""Finite differential against the pinned FG3 source, not the S1 adapter."""

import importlib.util
import itertools
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path

from e7c_s1_evaluator import evaluate
from e7c_s1_replay_checker import check_witness
from e7c_s1_state_joint_static import STRICT_EDITION
from e7c_s1_values import CANONICAL_BLOB, FG3_BLOB, MODULE, RESOURCE_EDITION, SIGNATURE


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "E7G-T_v0.12_Executable_Examples.py"


def source_model():
    spec = importlib.util.spec_from_file_location("pinned_fg3_source", SOURCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclass resolves its defining module
    spec.loader.exec_module(module)
    return module


def row(left, right, coefficient):
    return {"configs": [{"edges": list(left.edges), "tag": left.tag},
                         {"edges": list(right.edges), "tag": right.tag}],
            "coefficient": {"numerator": coefficient.numerator, "denominator": coefficient.denominator}}


def document():
    state = {"tag": "state", "args": [MODULE, SIGNATURE]}
    return {"edition": STRICT_EDITION,
            "variables": {"joint": {"tag": "joint", "args": [state, state]}},
            "term": {"tag": "strict_union", "arg": {"tag": "var", "name": "joint"}}}


def result_signature(witness):
    terminal = witness["terminal"]
    if terminal["tag"] != "success":
        return terminal["tag"], None
    return "success", tuple((tuple(record["configs"][0]["edges"]),
                              record["configs"][0]["tag"],
                              Fraction(record["coefficient"]["numerator"],
                                       record["coefficient"]["denominator"]))
                             for record in terminal["value"]["rows"])


class SourceCorrespondence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for path, expected in ((SOURCE, FG3_BLOB),
                               (ROOT / "E7G-T_Kernel_v0.12.1_Experimental_Canonical_Reference.md", CANONICAL_BLOB)):
            actual = subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()
            if actual != expected:
                raise AssertionError(f"source pin changed: {path.name}")
        cls.src = source_model()
        cls.graphs = tuple(cls.src.Graph(tuple(e for e, bit in zip(("AB", "AC", "BC"), mask) if bit), tag)
                           for tag in (None, "marked")
                           for mask in itertools.product((False, True), repeat=3))
        cls.doc = document()
        cls.policy = {"edition": RESOURCE_EDITION, "max_steps": 8, "max_pair_visits": 8}

    def compare_rows(self, rows):
        source_rows = self.src.joint(*rows)
        try:
            source_value = self.src.join(source_rows, "union")
            expected = "success", tuple((g.edges, g.tag, c) for g, c in source_value.terms)
        except self.src.DomainError:
            expected = "domain_error", None
        value = {"joint": {"kind": "joint", "rows": [row(left, right, coefficient)
                                                   for coefficient, (left, right) in rows]}}
        witness = evaluate(self.doc, value, self.policy)
        self.assertEqual((witness["canonical_blob"], witness["fg3_blob"]),
                         (CANONICAL_BLOB, FG3_BLOB))
        self.assertTrue(check_witness(witness))
        self.assertEqual(witness["static"]["effects"], [
            {"dimension": "partiality", "payload": "E7C-S1-FG3-STRICT/0.1-provisional"},
            {"dimension": "resources", "payload": "finite_strict_union"},
        ])
        self.assertEqual(result_signature(witness), expected)
        first_bad = next((i for i, ((left, right), _) in enumerate(source_rows)
                          if left.tag != right.tag), None)
        self.assertEqual(witness["progress"]["pair_visits"],
                         len(source_rows) if first_bad is None else first_bad + 1)
        if expected[0] == "domain_error":
            self.assertIsNone(witness["terminal"]["value"])
            self.assertEqual(witness["ledger"], [{"rule": "strict_union", "tag": "domain_error",
                                                    "visits": first_bad + 1, "offending_index": first_bad}])
        else:
            self.assertEqual(witness["ledger"][-1]["tag"], "success")

    def test_all_signed_singleton_graph_pairs(self):
        # 16 graphs, 256 ordered pairs, two signs: 512 exact source comparisons.
        for left, right in itertools.product(self.graphs, repeat=2):
            for coefficient in (Fraction(-1), Fraction(1)):
                with self.subTest(left=left, right=right, coefficient=coefficient):
                    self.compare_rows(((coefficient, (left, right)),))

    def test_two_row_cancellation_and_order(self):
        # Four representative edge/tag configurations yield 16 pair identities.
        # Every ordered pair of rows and both signs on row two: 512 comparisons.
        sample = (self.graphs[0], self.graphs[3], self.graphs[8], self.graphs[15])
        pairs = tuple(itertools.product(sample, repeat=2))
        for first, second in itertools.product(pairs, repeat=2):
            for second_sign in (Fraction(-1), Fraction(1)):
                with self.subTest(first=first, second=second, sign=second_sign):
                    self.compare_rows(((Fraction(1), first), (second_sign, second)))

    def test_zero_joint_matches_formal_zero(self):
        # The source uses an empty tuple; S1 retains the declared binary arity.
        self.compare_rows(())


if __name__ == "__main__":
    unittest.main()
