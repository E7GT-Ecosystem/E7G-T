"""Rebuild the finite source/IR to Lean trace bridge exactly."""

import unittest

from e7c_b1_canonical import canonical_bytes
from e7c_eecq_two_stage_lean_bridge import CASES, LEAN, MANIFEST, build


class TwoStageLeanBridge(unittest.TestCase):
    def test_generated_manifest_and_named_lean_vectors(self):
        manifest, code = build()
        self.assertEqual(MANIFEST.read_bytes(), canonical_bytes(manifest) + b"\n")
        self.assertEqual(LEAN.read_text(), code)
        self.assertEqual(tuple(row["case"] for row in manifest["cases"]), CASES)
        self.assertEqual(len(manifest["cases"]), 10)
        for name in CASES:
            self.assertIn(f"theorem vector_{name} :", code)
        self.assertTrue(any(r["target_trace"]["exit"]["tag"] == "success"
                            for r in manifest["cases"]))
        self.assertTrue(any(r["target_trace"]["exit"]["tag"] == "resource_limit"
                            for r in manifest["cases"]))
        self.assertNotEqual(manifest["cases"][0]["target_trace"]["exit"]["value"],
                            manifest["cases"][1]["target_trace"]["exit"]["value"])


if __name__ == "__main__":
    unittest.main()
