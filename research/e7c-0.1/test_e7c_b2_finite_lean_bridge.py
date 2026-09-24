import json
from pathlib import Path
import unittest

from e7c_b2_finite_lean_bridge import EDITION, NAMES, build
from e7c_b1_canonical import canonical_bytes

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "fixtures/wp5_ir/b2_lean_finite_bridge.json"
LEAN = HERE / "proof-packages/lean-core/E7CB2FiniteBridge.lean"


class FiniteLeanBridge(unittest.TestCase):
    def test_full_source_b1_ir_relation_and_exact_generated_vectors(self):
        recorded = json.loads(MANIFEST.read_bytes())
        self.assertEqual(MANIFEST.read_bytes(), canonical_bytes(recorded) + b"\n")
        regenerated, lean = build()
        self.assertEqual(recorded, regenerated)
        self.assertEqual(LEAN.read_text(), lean)
        self.assertEqual(recorded["edition"], EDITION)
        self.assertEqual([row["case"] for row in recorded["cases"]], list(NAMES))
        tags = {row["source_claim"]["terminal_outcome"]["tag"]
                for row in recorded["cases"]}
        self.assertEqual(tags, {"success", "unsupported", "undetermined",
                                "domain_error", "resource_limit"})


if __name__ == "__main__":
    unittest.main()
