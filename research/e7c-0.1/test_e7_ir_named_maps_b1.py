"""Selected two-map source/IR differential with output types and replay."""

import copy
import json
from pathlib import Path
import unittest

from e7_ir_named_maps_b1 import MapIRAdmissionError, compare_replay, execute, lower, parse, serialize
from e7c_b1_canonical import canonical_bytes, digest
from test_e7_ir_strict_map_b1 import source_document

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures/wp5_ir/total_graph_map.json"
GRAPH = {"edges": ["AB"], "tag": None}
B = {"id": "b", "valid": False}
C = {"id": "c", "valid": True}


def input_document(name="total_identity", *, binding=None, steps=20, ledger=20,
                   capability=True, obligation="resolved"):
    source = source_document(binding=binding, steps=steps, ledger=ledger,
                             capability=capability, obligation=obligation)
    source["term"]["declaration"] = name
    if name == "total_identity":
        source["interpretation"]["maps"][name]["capability"] = capability
        source["interpretation"]["maps"][name]["obligation"] = obligation
    return source


def conventional(name, binding):
    """Independent finite control outputs; no source or IR evaluator called."""
    if name == "total_identity":
        return {"tag": "success", "value": binding}
    table = [(GRAPH, {"id": "A"}), (B, None), (C, {"id": "C"})]
    for source, output in table:
        if binding == source:
            return ({"tag": "success", "value": output} if output is not None
                    else {"tag": "domain_error", "diagnostic": "outside-domain:strict_normalise"})
    raise ValueError("outside selected carrier")


class NamedMapsDifferential(unittest.TestCase):
    def test_complete_total_fixture_and_typed_output(self):
        ir = json.loads(FIXTURE.read_bytes())
        self.assertEqual(FIXTURE.read_bytes(), canonical_bytes(ir) + b"\n")
        self.assertEqual(lower(input_document()), ir)
        self.assertEqual(parse(serialize(ir)), ir)
        self.assertEqual(compare_replay(ir)["ir_result"], execute(ir))
        self.assertEqual(ir["instruction"]["source_type"], ir["instruction"]["target_type"])
        self.assertEqual(execute(ir)["terminal_outcome"]["value"], GRAPH)
        self.assertEqual([row["static_atom"]["dimension"] for row in execute(ir)["ordered_ledger"]],
                         ["evidence"])

    def test_both_map_policies_guard_and_budget(self):
        for name in ("strict_normalise", "total_identity"):
            for binding in (GRAPH, B, C):
                for steps in (0, 1, 2):
                    for ledger in (0, 1, 2):
                        for capability, obligation in ((True, "resolved"), (False, "resolved"),
                                                       (True, "unresolved")):
                            with self.subTest(name=name, binding=binding, steps=steps,
                                              ledger=ledger, capability=capability,
                                              obligation=obligation):
                                document = input_document(name, binding=binding, steps=steps,
                                                          ledger=ledger, capability=capability,
                                                          obligation=obligation)
                                ir = lower(document)
                                actual = compare_replay(ir)["ir_result"]
                                self.assertEqual(actual, execute(ir))
                                if steps == 2 and ledger >= (2 if name == "strict_normalise" else 1) and capability and obligation == "resolved":
                                    control = conventional(name, binding)
                                    self.assertEqual(actual["terminal_outcome"]["tag"], control["tag"])
                                    self.assertEqual(actual["terminal_outcome"].get("value", actual["terminal_outcome"].get("diagnostic")),
                                                     control.get("value", control.get("diagnostic")))

    def test_edition_output_type_rebinding_and_unsupported_constructor(self):
        ir = json.loads(FIXTURE.read_bytes())
        changed = copy.deepcopy(ir)
        changed["instruction"]["target_type"] = {"tag": "config", "args": ["Sigma-B"]}
        changed["instruction"]["id"] = digest({k: v for k, v in changed["instruction"].items() if k != "id"})
        changed["id"] = digest({k: v for k, v in changed.items() if k != "id"})
        with self.assertRaises(MapIRAdmissionError):
            execute(changed)
        changed = copy.deepcopy(ir)
        changed["ir_edition"] = "unknown"
        changed["id"] = digest({k: v for k, v in changed.items() if k != "id"})
        with self.assertRaises(MapIRAdmissionError):
            execute(changed)
        document = input_document()
        document["term"]["declaration"] = "unknown"
        with self.assertRaises((MapIRAdmissionError, ValueError)):
            lower(document)


if __name__ == "__main__":
    unittest.main()
