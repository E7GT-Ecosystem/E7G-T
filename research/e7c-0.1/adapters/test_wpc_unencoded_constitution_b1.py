"""WPC/0.2 constitution without SR4 representation for both draft kernels."""

import importlib.util
from pathlib import Path
import sys
import unittest

from wpc_allocation_b1 import (AdmissionError, constitute as strict_reconstruct,
                               represent as legacy_represent)
from wpc_unencoded_constitution_b1 import constitute, presentation, source_pin

MODEL = Path(__file__).resolve().parents[3] / \
    "packages/wpc-0.2/E7G-T_WPC_v0.2_Reference_Model.py"
spec = importlib.util.spec_from_file_location("wpc_unencoded_source", MODEL)
source = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = source
spec.loader.exec_module(source)


class UnencodedConstitution(unittest.TestCase):
    def test_semantic_constitution_without_any_representation(self):
        for kernel in ("0.13-experimental-draft", "0.14-experimental-draft"):
            with self.subTest(kernel=kernel):
                given = presentation(kernel, 0, ("A", "B", "C"),
                                     (("A", 1), ("B", 1), ("C", 0)))
                actual = constitute(given, 3)
                conventional = source.Whole(0, source.IDS, (1, 1, 0))
                self.assertEqual(actual.tag, "unique")
                self.assertEqual(actual.visited, 3)
                self.assertEqual((actual.value.members, actual.value.values),
                                 (conventional.members, conventional.values))
                self.assertEqual(actual.source.kernel, kernel)
                self.assertEqual(actual.value.kernel, kernel)
                self.assertEqual(actual.source.source_digest, source_pin(kernel))
                self.assertTrue(all(len(row) == 2 for row in given.rows))
                with self.assertRaisesRegex(AdmissionError, "presentation_required"):
                    strict_reconstruct(given)
                with self.assertRaisesRegex(AdmissionError, "whole_required"):
                    legacy_represent(actual.value)

    def test_resource_and_incompatible_do_not_return_partial_whole(self):
        given = presentation("0.13-experimental-draft", 0, ("A", "B", "C"),
                             (("A", 1), ("B", 1), ("C", 1)))
        for bound in (0, 1, 2):
            out = constitute(given, bound)
            self.assertEqual((out.tag, out.visited, out.value),
                             ("resource_limit", bound, None))
        out = constitute(given, 3)
        self.assertEqual((out.tag, out.visited, out.value),
                         ("incompatible", 3, None))
        with self.assertRaisesRegex(source.Reject, "global_incompatibility"):
            source.Whole(0, source.IDS, (1, 1, 1))

    def test_coverage_and_edition_boundaries(self):
        for kernel in ("0.13-experimental-draft", "0.14-experimental-draft"):
            with self.subTest(kernel=kernel):
                reversed_row = presentation(kernel, 0, ("A", "B"),
                                            (("B", 0), ("A", 0)))
                with self.assertRaisesRegex(AdmissionError, "coverage_incomplete"):
                    constitute(reversed_row, 2)
                empty = presentation(kernel, 0, (), ())
                with self.assertRaises(AdmissionError):
                    constitute(empty, 2)
                tampered = presentation(kernel, 0, ("A",), (("A", 0),))
                from dataclasses import replace
                with self.assertRaisesRegex(AdmissionError, "typed edition-bound"):
                    constitute(replace(tampered, source_digest="forged"), 1)


if __name__ == "__main__":
    unittest.main()
