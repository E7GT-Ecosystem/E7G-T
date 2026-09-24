import copy
import json
from pathlib import Path
import unittest

from e7_ir_conformance_b1 import EDITION, build_manifest
from e7c_b1_canonical import canonical_bytes

MANIFEST = Path(__file__).resolve().parent / "fixtures/wp5_ir/ir_conformance_manifest.json"


class CrossSliceConformance(unittest.TestCase):
    def test_all_pinned_packages_replay_and_match_manifest(self):
        recorded = json.loads(MANIFEST.read_bytes())
        self.assertEqual(MANIFEST.read_bytes(), canonical_bytes(recorded) + b"\n")
        self.assertEqual(recorded, build_manifest())
        self.assertEqual(recorded["edition"], EDITION)
        self.assertEqual(len(recorded["cases"]), 5)

    def test_source_view_and_projection_remain_distinct(self):
        rows = {row["slice"]: row for row in build_manifest()["cases"]}
        self.assertEqual(rows["var"]["ledger_dimensions"], [])
        self.assertEqual(rows["strict_map"]["ledger_dimensions"], ["evidence", "partiality"])
        self.assertEqual(rows["named_total"]["ledger_dimensions"], ["evidence"])
        self.assertEqual(rows["source_view"]["ledger_dimensions"], ["inquiry", "alternatives"])
        self.assertEqual(rows["lossy_projection"]["ledger_dimensions"],
                         ["inquiry", "loss", "alternatives"])
        self.assertNotEqual(rows["source_view"]["static_type"],
                            rows["lossy_projection"]["static_type"])
        self.assertEqual({row["terminal_tag"] for row in rows.values()}, {"success"})
        self.assertEqual({row["completed_steps"] for row in rows.values()}, {1, 2})

    def test_changed_manifest_claim_is_not_accepted(self):
        modified = copy.deepcopy(json.loads(MANIFEST.read_bytes()))
        modified["cases"][0]["source_document_digest"] = "0" * 64
        self.assertNotEqual(modified, build_manifest())


if __name__ == "__main__":
    unittest.main()
