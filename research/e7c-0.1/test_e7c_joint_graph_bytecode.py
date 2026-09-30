import dis
import itertools
import json
import unittest
from unittest import mock

from e7c_joint_graph_bytecode import (
    GENERATED, ROOT, ModelValue, check, current_program, decode_instructions,
    generated_text, run_model, source,
)
from e7c_joint_serializer_observer import Config


class GraphBytecodeTests(unittest.TestCase):
    def setUp(self):
        self.program, self.manifest = current_program()
        self.instructions = list(dis.get_instructions(source._graph, adaptive=False))

    def test_complete_generated_image_and_cache_record(self):
        self.assertEqual(generated_text(self.program), GENERATED.read_text())
        checked = check()
        self.assertEqual(len(checked["program"]), 10)
        self.assertGreater(len(checked["instructions_with_caches"]), 10)
        self.assertEqual(checked["exception_table_hex"], "")
        self.assertEqual(checked["execution_adequacy"],
                         "unproved; unspecialized instruction model only")

    def test_all_fg3_graphs_tags_against_actual_helper(self):
        for bits in itertools.product((False, True), repeat=3):
            edges = tuple(e for e, present in zip(("AB", "AC", "BC"), bits) if present)
            for tag in (None, "", 'Ω\n"\\\x01'):
                graph = Config(edges, tag)
                snapshot = {"edges": list(graph.edges), "tag": graph.tag}
                modeled = run_model(self.program, snapshot)
                self.assertEqual(modeled, source._graph(graph))
                self.assertEqual(list(modeled), ["edges", "tag"])

    def test_model_preserves_arbitrary_order_and_duplicates(self):
        # WireGraph theorem is all-list; source admission is still narrower.
        for edges in ([], ["BC", "AB", "BC"], ["unregistered"] * 70):
            graph = {"edges": edges, "tag": None}
            self.assertEqual(run_model(self.program, graph), graph)

    def test_null_and_empty_tags_stay_distinct(self):
        null = run_model(self.program, {"edges": [], "tag": None})
        empty = run_model(self.program, {"edges": [], "tag": ""})
        self.assertNotEqual(null, empty)

    def test_decoder_rejects_null_and_method_flag_changes(self):
        for index, arg in ((1, 0), (3, 3), (6, 5)):
            changed = self.instructions.copy()
            changed[index] = changed[index]._replace(arg=arg)
            with self.assertRaises(ValueError):
                decode_instructions(changed)

    def test_decoder_rejects_new_opcode_jump_and_wrong_arity(self):
        changes = [self.instructions[4]._replace(opname="JUMP_FORWARD"),
                   self.instructions[4]._replace(is_jump_target=True),
                   self.instructions[4]._replace(arg=2),
                   self.instructions[4]._replace(opname="CACHE")]
        for replacement in changes:
            changed = self.instructions.copy()
            changed[4] = replacement
            with self.assertRaises(ValueError):
                decode_instructions(changed)

    def test_decoder_rejects_duplicate_or_nonstring_keys(self):
        for keys in (("edges", "edges"), ("edges", None), ("edges",)):
            changed = self.instructions.copy()
            changed[7] = changed[7]._replace(argval=keys)
            with self.assertRaises(ValueError):
                decode_instructions(changed)

    def test_missing_duplicated_and_reordered_instructions_are_not_ignored(self):
        programs = [self.program[:4] + self.program[5:],
                    self.program[:4] + [self.program[4]] + self.program[4:],
                    self.program[:4] + [self.program[5], self.program[4]] + self.program[6:],
                    self.program + [("resume", 0)], self.program[:-1]]
        for changed in programs:
            self.assertNotEqual(generated_text(changed), GENERATED.read_text())
            with self.assertRaises(ValueError):
                run_model(changed, {"edges": ["AB"], "tag": None})

    def test_changed_attribute_reads_falsify_correspondence(self):
        def forged_read(value, name):
            return (ModelValue("sequence", []) if name == "edges"
                    else ModelValue("raw", value.payload["tag"]))
        graph = Config(("AB",), None)
        self.assertNotEqual(run_model(self.program, {"edges": ["AB"], "tag": None},
                                    read=forged_read), source._graph(graph))

    def test_live_source_binding_and_code_changes_are_rejected(self):
        with mock.patch.object(source, "list", tuple, create=True):
            with self.assertRaises(ValueError):
                current_program()
        with mock.patch.object(source, "_graph", lambda g: {}):
            with self.assertRaises(ValueError):
                current_program()

    def test_saved_image_preserves_history_and_matches_portable_program(self):
        saved = json.loads((ROOT / "fixtures/graph-bytecode-image.json").read_text())
        # JSON changes tuples to arrays; compare the portable image separately
        # from the exact original runtime, never relabel a replay as that host.
        self.assertEqual(saved["program"], json.loads(json.dumps(self.program)))
        self.assertEqual(saved["co_code_sha256"], self.manifest["co_code_sha256"])
        self.assertEqual(saved["instructions_with_caches"],
                         json.loads(json.dumps(self.manifest["instructions_with_caches"])))


if __name__ == "__main__":
    unittest.main()
