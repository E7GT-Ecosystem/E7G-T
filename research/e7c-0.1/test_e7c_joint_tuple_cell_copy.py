import copy
import json
import unittest

from e7c_joint_tuple_cell_copy import FIXTURE, check_source_packet, copy_cells


class TupleCellCopyTests(unittest.TestCase):
    def test_source_pins(self):
        check_source_packet(json.loads(FIXTURE.read_text()))

    def test_changed_copy_operation_rejected(self):
        packet = json.loads(FIXTURE.read_text())
        packet["sources"][0]["copy_loop"] = packet["sources"][0]["copy_loop"].replace(
            "src[i]", "src[n - i - 1]")
        with self.assertRaises(ValueError):
            check_source_packet(packet)

    def test_changed_allocation_or_guard_rejected(self):
        packet = json.loads(FIXTURE.read_text())
        for original, forged in [("n == 0", "n == 1"), ("dest[i]", "dest[0]"),
                                 ("PyTuple_CheckExact", "PyTuple_Check"),
                                 ("list_preallocate_exact", "list_resize")]:
            changed = copy.deepcopy(packet)
            changed["sources"][0]["selected_fast_path"] = changed["sources"][0][
                "selected_fast_path"].replace(original, forged)
            with self.subTest(original=original), self.assertRaises(ValueError):
                check_source_packet(changed)

    def test_mismatched_source_pin_rejected(self):
        packet = json.loads(FIXTURE.read_text())
        packet["sources"][1]["git_blob"] = "0" * 40
        with self.assertRaises(ValueError):
            check_source_packet(packet)

    def test_native_order_and_identity(self):
        repeated = object()
        for cells in [(), (repeated,), (repeated, None, "", repeated),
                      tuple(range(64))]:
            output, events = copy_cells(cells)
            native = list(cells)
            self.assertEqual(len(output), len(native))
            self.assertTrue(all(a is b for a, b in zip(output, native)))
            self.assertEqual(len(events), 3 * len(cells))
            for index, pointer in enumerate(cells):
                self.assertEqual(events[3 * index:3 * index + 3],
                                 [("read", index, pointer),
                                  ("newRef", pointer, pointer),
                                  ("write", index, pointer)])

    def test_forged_reference_falsifies_correspondence(self):
        pointer = object()
        output, _ = copy_cells((pointer,), lambda _: object())
        self.assertIsNot(output[0], list((pointer,))[0])

    def test_generic_iterables_outside_selected_domain(self):
        for cells in [[], iter([1]), "abc"]:
            with self.assertRaises(ValueError):
                copy_cells(cells)


if __name__ == "__main__":
    unittest.main()
