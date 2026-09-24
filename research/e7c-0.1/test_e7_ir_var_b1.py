"""Selected var source/IR differential including terminal and resource paths."""

import copy
import unittest

from e7_ir_var_b1 import IRAdmissionError, execute, lower, parse, serialize
from e7c_b1_canonical import digest
from e7c_b1_evaluator import evaluate
from test_wp3_i import VAR, document


class IRVarDifferential(unittest.TestCase):
    @staticmethod
    def rebound(ir):
        ir["id"] = digest({k: v for k, v in ir.items() if k != "id"})
        return ir

    def test_typed_variable_and_precharge_limit_correspondence(self):
        for term in (VAR, {"tag": "var", "name": "terminal_result"}):
            for steps in (0, 1, 2):
                with self.subTest(term=term, steps=steps):
                    source = document(term, steps=steps)
                    ir = lower(source)
                    self.assertEqual(parse(serialize(ir)), ir)
                    self.assertEqual(serialize(parse(serialize(ir))), serialize(ir))
                    actual = execute(ir)
                    expected = evaluate(source)
                    for field in ("terminal_outcome", "ordered_ledger", "resource_progress"):
                        if field == "terminal_outcome" and actual[field]["tag"] == "success":
                            self.assertIsNone(actual[field]["optional_witness"])
                            self.assertIsInstance(expected[field]["optional_witness"], str)
                            self.assertEqual(actual[field]["value"], expected[field]["value"])
                        else:
                            self.assertEqual(actual[field], expected[field])
                    self.assertEqual(ir["instruction"]["source_location"],
                                     {"document": digest(source), "path": "$.term"})

    def test_unknown_capability_and_rebound_id_rejected(self):
        ir = lower(document(VAR))
        changed = copy.deepcopy(ir)
        changed["required_capabilities"].append("future.mandatory")
        changed["id"] = digest({k: v for k, v in changed.items() if k != "id"})
        with self.assertRaises( IRAdmissionError):
            parse(serialize(changed))
        changed = copy.deepcopy(ir)
        changed["binding"] = {"id": "b", "valid": False}
        with self.assertRaises(IRAdmissionError):
            execute(changed)
        for bad in ({"id": "unlisted", "valid": True},
                    {"id": "a", "valid": False, "extra": "different"}):
            with self.subTest(rebound=bad):
                changed = self.rebound(copy.deepcopy(ir))
                changed["binding"] = bad
                self.rebound(changed)
                with self.assertRaises(IRAdmissionError):
                    execute(changed)
        changed = copy.deepcopy(ir)
        changed["binding_carriers"] = {}
        self.rebound(changed)
        with self.assertRaises(IRAdmissionError):
            execute(changed)
        terminal = lower(document({"tag": "var", "name": "terminal_result"}))
        for malformed in ({"tag": "success", "value": {"id": "unlisted"},
                           "optional_witness": None},
                          {"tag": "success", "value": {"id": "a", "valid": True},
                           "optional_witness": "forged"},
                          {"tag": "domain_error", "diagnostic": "x", "extra": True}):
            with self.subTest(malformed=malformed):
                changed = copy.deepcopy(terminal)
                changed["binding"] = malformed
                self.rebound(changed)
                with self.assertRaises(IRAdmissionError):
                    execute(changed)
        changed = copy.deepcopy(ir)
        changed["instruction"]["type"] = {"tag": "unknown", "args": []}
        changed["instruction"]["id"] = digest({k: v for k, v in changed["instruction"].items() if k != "id"})
        changed["id"] = digest({k: v for k, v in changed.items() if k != "id"})
        with self.assertRaises(IRAdmissionError):
            parse(serialize(changed))

    def test_selected_operator_boundary(self):
        with self.assertRaises(IRAdmissionError):
            lower(document({"tag": "apply", "declaration": "total_identity", "arg": VAR}))


if __name__ == "__main__":
    unittest.main()
