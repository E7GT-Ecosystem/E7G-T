"""Bounded WP5 to IR integration and independent source witness replay."""

import copy
import json
from pathlib import Path
import unittest

from e7_ir_var_b1 import IRAdmissionError, execute, lower, parse, serialize
from e7c_b1_canonical import canonical_bytes, digest
from e7c_b1_evaluator import evaluate
from e7c_b1_replay_checker import check_witness
from wp5_ir_finite_case import build_case, conventional_baseline

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "wp5_ir" / "finite_graph_var.json"


class FiniteIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = json.loads(FIXTURE.read_bytes())

    def test_reproducible_full_package_and_three_paths(self):
        case = self.case
        self.assertEqual(case, build_case())
        self.assertEqual(FIXTURE.read_bytes(), canonical_bytes(case) + b"\n")
        self.assertEqual(conventional_baseline(case["profile_rows"])["config"], case["selected_config"])
        self.assertEqual(evaluate(case["source_document"]), case["source_result"])
        self.assertEqual(lower(case["source_document"]), case["ir"])
        self.assertEqual(parse(serialize(case["ir"])), case["ir"])
        self.assertEqual(execute(case["ir"]), case["ir_result"])
        self.assertEqual(check_witness(case["source_result"]["witness"])["status"], "accepted")

    def test_source_rebinding_and_ir_detachment_boundaries(self):
        case = self.case
        witness = copy.deepcopy(case["source_result"]["witness"])
        witness["runtime_inputs"]["values"]["source_config"] = {"edges": ["AC"], "tag": None}
        self.assertEqual(check_witness(witness)["status"], "rejected")
        ir = copy.deepcopy(case["ir"])
        ir["binding"] = {"edges": ["AC"], "tag": None}
        ir["id"] = digest({k: v for k, v in ir.items() if k != "id"})
        with self.assertRaises(IRAdmissionError):
            execute(ir)
        # A different, separately admitted package is possible: IDs do not
        # authenticate the source or prove any general WP5 correspondence.
        ir["binding_carriers"][next(iter(ir["binding_carriers"]))].append(ir["binding"])
        ir["binding_carriers"][next(iter(ir["binding_carriers"]))].sort(key=lambda x: json.dumps(x, sort_keys=True, separators=(",", ":")))
        ir["id"] = digest({k: v for k, v in ir.items() if k != "id"})
        self.assertEqual(execute(ir)["terminal_outcome"]["value"], ir["binding"])
        self.assertNotEqual(execute(ir)["terminal_outcome"]["value"], case["selected_config"])


if __name__ == "__main__":
    unittest.main()
