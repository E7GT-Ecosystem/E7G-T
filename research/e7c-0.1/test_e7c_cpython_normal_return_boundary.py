"""Regression evidence for CPython dict equality in the pinned admit path."""

from __future__ import annotations

import copy
import unittest

from e7c_eecq_joint_restrict_b1 import admit
from test_e7c_joint_raw_json_admission import one_row_document


class CPythonNormalReturnEqualityBoundary(unittest.TestCase):
    def test_row_and_nested_object_key_order_is_ignored_by_final_guard(self):
        source = one_row_document()
        original = source["rows"][0]

        # Reinsert every object with reversed field insertion order. Python's
        # dict equality ignores that order, and the pinned helper admits it.
        source["rows"] = [{
            "coefficient": dict(reversed(list(original["coefficient"].items()))),
            "atoms": [
                {"tag": atom["tag"], "edges": atom["edges"]}
                for atom in original["atoms"]
            ],
        }]
        admitted = admit(source)
        self.assertEqual(len(admitted.terms), 1)

    def test_object_order_is_ignored_at_multiple_nested_levels(self):
        source = one_row_document()
        row = source["rows"][0]
        row["atoms"] = [
            {"tag": atom["tag"], "edges": atom["edges"]}
            for atom in reversed(row["atoms"])
        ]
        # Coordinate order is data, so a swapped pair is admitted as that
        # different pair. It is not treated as a dictionary-key permutation.
        admitted = admit(source)
        self.assertEqual(admitted.terms[0][0][0].edges, ("BC",))
        self.assertEqual(admitted.terms[0][0][0].tag, "")
        self.assertEqual(admitted.terms[0][0][1].edges, ("AB",))
        self.assertIsNone(admitted.terms[0][0][1].tag)


if __name__ == "__main__":
    unittest.main()
