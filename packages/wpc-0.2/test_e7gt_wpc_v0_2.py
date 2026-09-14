"""First-party tests for the bounded WPC/0.2 allocation model."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest


MODEL_PATH = Path(__file__).with_name("E7G-T_WPC_v0.2_Reference_Model.py")
SPEC = spec_from_file_location("e7gt_wpc_v0_2", MODEL_PATH)
assert SPEC is not None and SPEC.loader is not None
MODEL = module_from_spec(SPEC)
SPEC.loader.exec_module(MODEL)


class WPCReferenceModelTests(unittest.TestCase):
    def test_recorded_reference_run(self):
        report = MODEL.run()
        self.assertEqual(report["checks_passed"], 34)
        self.assertEqual(report["finite_initial_wholes"], 10)
        self.assertEqual(report["portion_round_trips"], 30)
        self.assertEqual(len(report["checks"]), 34)

    def test_profile_pin_is_draft_specific(self):
        self.assertEqual(
            MODEL.PROFILE,
            "E7G-T-v0.13-draft:WPC/0.2-proposed:allocation-example/0.1",
        )

    def test_canonical_round_trip_rejects_local_payload_conflict(self):
        whole = MODEL.Whole(0, MODEL.IDS, (0, 0, 0))
        assembly = MODEL.alpha(whole)
        changed = MODEL.replace(
            assembly,
            rows=(("A", 1, MODEL.encode(whole)),) + assembly.rows[1:],
        )
        with self.assertRaisesRegex(MODEL.Reject, "^source_conflict$"):
            MODEL.beta(changed)

    def test_constitution_does_not_require_payload_operation(self):
        whole = MODEL.Whole(0, ("A", "B"), (1, 1))
        self.assertEqual(whole.values, (1, 1))
        self.assertLessEqual(sum(whole.values), whole.budget)


if __name__ == "__main__":
    unittest.main()
