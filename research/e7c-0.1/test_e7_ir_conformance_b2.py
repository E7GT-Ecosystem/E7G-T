import copy
import json
from pathlib import Path
import unittest

from e7_ir_conformance_b2 import EDITION, build_manifest
from e7c_b1_canonical import canonical_bytes

MANIFEST = Path(__file__).resolve().parent / "fixtures/wp5_ir/ir_conformance_b2_manifest.json"


class B2CrossEditionConformance(unittest.TestCase):
    def test_pinned_outcomes_and_failure_short_circuit(self):
        recorded = json.loads(MANIFEST.read_bytes())
        self.assertEqual(MANIFEST.read_bytes(), canonical_bytes(recorded) + b"\n")
        self.assertEqual(recorded, build_manifest())
        self.assertEqual(recorded["edition"], EDITION)
        rows = {item["case"]: item for item in recorded["b2_cases"]}
        self.assertEqual(len(rows), 6)
        self.assertEqual({key: value["terminal_tag"] for key, value in rows.items()}, {
            "success": "success", "first_unsupported": "unsupported",
            "first_undetermined": "undetermined", "continuation_domain_error": "domain_error",
            "step_limit": "resource_limit", "ledger_limit": "resource_limit"})
        for key in ("first_unsupported", "first_undetermined"):
            self.assertEqual(rows[key]["ledger_dimensions"], ["evidence"])
        self.assertEqual(rows["success"]["ledger_dimensions"],
                         ["evidence", "evidence", "partiality"])

    def test_changed_record_is_detected(self):
        modified = copy.deepcopy(json.loads(MANIFEST.read_bytes()))
        modified["b2_cases"][1]["terminal_tag"] = "success"
        self.assertNotEqual(modified, build_manifest())


if __name__ == "__main__":
    unittest.main()
