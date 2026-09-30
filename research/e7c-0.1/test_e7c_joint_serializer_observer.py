"""Actual execution and observer boundaries; not all-input CPython adequacy."""
import copy
import json
import sys
import unittest
from fractions import Fraction
from unittest.mock import patch

from eec_q_fg3_b1 import Config
from eec_q_fg3_joint_b1 import Joint, joint
import e7c_eecq_joint_restrict_b1 as source
from e7c_joint_serializer_observer import (
    ROOT, certificate_text, freeze_manifest, lean_string, observe,
)


def fixture_values():
    left, right = Config(("AB",), None), Config(("BC",), "")
    return [Joint(2, ()),
            joint([(Fraction(1, 2), (left, left)), (Fraction(1, 2), (right, right))], arity=2),
            joint([(Fraction(1, 2), (left, right)), (Fraction(1, 2), (right, left))], arity=2),
            joint([(Fraction(-7, 11), (Config(("AB", "AC", "BC"), 'Ω\n"\\\x01'), right))], arity=2)]


class SerializerObserverTests(unittest.TestCase):
    def setUp(self):
        self.manifest = freeze_manifest()
        self.value = fixture_values()[1]

    def test_actual_normal_packet_carries_exact_host_and_code_pins(self):
        packet = observe(self.value, self.manifest)
        self.assertEqual(packet["tag"], "observed_normal")
        self.assertEqual(packet["manifest"], self.manifest)
        self.assertEqual(packet["manifest"]["version"], list(sys.version_info))
        self.assertEqual(packet["output"], source.rows(self.value))
        self.assertEqual(packet["events"][0]["payload"], packet["input"])
        self.assertEqual(packet["events"][-1]["payload"], packet["output"])

    def test_ordered_frame_ledger_for_both_correlations(self):
        packets = [observe(v, self.manifest) for v in fixture_values()[1:3]]
        expected = ["rows.call"] + ["_row.call", "_graph.call", "_graph.return",
                                        "_graph.call", "_graph.return", "_row.return"] * 2 + ["rows.return"]
        for packet in packets:
            self.assertEqual([e["site"] for e in packet["events"]], expected)
            self.assertEqual(len(packet["events"]), 14)
        self.assertNotEqual(packets[0]["output"], packets[1]["output"])

    def test_exact_runtime_pin_mismatch_is_unsupported(self):
        changed = copy.deepcopy(self.manifest)
        changed["version"][2] += 1
        packet = observe(self.value, changed)
        self.assertEqual(packet["tag"], "unsupported")
        self.assertEqual(packet["events"], [])

    def test_changed_live_code_is_unsupported(self):
        with patch.object(source, "_graph", lambda _: {"edges": [], "tag": None}):
            self.assertEqual(observe(self.value, self.manifest)["tag"], "unsupported")

    def test_shadowed_builtin_is_unsupported(self):
        with patch.dict(vars(source), {"list": lambda _: []}):
            self.assertEqual(observe(self.value, self.manifest)["tag"], "unsupported")

    def test_empty_exact_event_limit_and_no_partial_success(self):
        empty = Joint(2, ())
        packet = observe(empty, self.manifest, event_limit=2)
        self.assertEqual(packet["tag"], "observed_normal")
        self.assertEqual(len(packet["events"]), 2)
        with patch("e7c_joint_serializer_observer.sys.setprofile") as install:
            rejected = observe(empty, self.manifest, event_limit=1)
            self.assertEqual(rejected["tag"], "resource_limit")
            self.assertNotIn("output", rejected)
            install.assert_not_called()

    def test_nonempty_exact_event_limit_and_one_less(self):
        self.assertEqual(observe(self.value, self.manifest, event_limit=14)["tag"], "observed_normal")
        rejected = observe(self.value, self.manifest, event_limit=13)
        self.assertEqual(rejected["tag"], "resource_limit")
        self.assertEqual(rejected["events"], [])

    def test_exact_row_limit_and_one_less(self):
        self.assertEqual(observe(self.value, self.manifest, row_limit=2)["tag"], "observed_normal")
        self.assertEqual(observe(self.value, self.manifest, row_limit=1)["tag"], "resource_limit")
        self.assertEqual(observe(self.value, self.manifest, row_limit=65)["tag"], "invalid_input")

    def test_exact_reported_byte_limit_and_one_less(self):
        packet = observe(self.value, self.manifest)
        bound = len(json.dumps(packet, ensure_ascii=False).encode())
        for _ in range(5):
            packet["limits"]["bytes"] = bound
            bound = len(json.dumps(packet, ensure_ascii=False).encode())
        exact = observe(self.value, self.manifest, byte_limit=bound)
        self.assertEqual(exact["tag"], "observed_normal")
        self.assertEqual(len(json.dumps(exact, ensure_ascii=False).encode()), bound)
        rejected = observe(self.value, self.manifest, byte_limit=bound - 1)
        self.assertEqual(rejected["tag"], "resource_limit")
        self.assertNotIn("output", rejected)

    def test_native_type_guard_and_observer_domain_rejection(self):
        for value in (object(), Joint(1, ())):
            self.assertEqual(observe(value, self.manifest)["tag"], "invalid_input")
        self.assertEqual(observe(self.value, self.manifest, event_limit=True)["tag"], "invalid_input")
        enormous = joint([(Fraction(1 << 257), (Config((), None), Config((), "")))], arity=2)
        self.assertEqual(observe(enormous, self.manifest)["tag"], "resource_limit")

    def test_preexisting_profiler_is_unsupported_and_preserved(self):
        def previous(frame, event, arg):
            return None
        sys.setprofile(previous)
        try:
            self.assertEqual(observe(self.value, self.manifest)["tag"], "unsupported")
            self.assertIs(sys.getprofile(), previous)
        finally:
            sys.setprofile(None)

    def test_host_observer_setup_failures_remain_distinct(self):
        for error, expected in [(MemoryError("host allocation"), "resource_limit"),
                                (OSError("host instrumentation"), "abnormal"),
                                (KeyboardInterrupt(), "abnormal")]:
            with patch("e7c_joint_serializer_observer.sys.setprofile", side_effect=error):
                packet = observe(self.value, self.manifest)
            self.assertEqual(packet["tag"], expected)
            self.assertEqual(packet["phase"], "observer_install")
            self.assertNotIn("output", packet)

    def test_postflight_manifest_drift_is_undetermined(self):
        changed = copy.deepcopy(self.manifest)
        changed["optimize"] += 1
        with patch("e7c_joint_serializer_observer.freeze_manifest",
                   side_effect=[self.manifest, changed]):
            packet = observe(self.value, self.manifest)
        self.assertEqual(packet["tag"], "undetermined")
        self.assertNotIn("output", packet)

    def test_missing_host_frame_observations_are_undetermined(self):
        with patch("e7c_joint_serializer_observer.sys.setprofile"):
            packet = observe(self.value, self.manifest)
        self.assertEqual(packet["tag"], "undetermined")
        self.assertNotIn("output", packet)

    def test_exporter_rejects_non_normal_and_code_injection(self):
        packet = observe(self.value, self.manifest)
        forged = copy.deepcopy(packet)
        forged["input"][0]["coefficient"]["numerator"] = "1); axiom forged : False"
        with self.assertRaises(ValueError):
            certificate_text([forged])
        with self.assertRaises(ValueError):
            certificate_text([observe(object(), self.manifest)])
        self.assertEqual(lean_string('Ω\n"\\\x01'), '"Ω\\n\\"\\\\\\u0001"')

    def test_saved_reported_runs_have_matching_portable_mathematical_content(self):
        saved = json.loads((ROOT / "fixtures/serializer-observed-captures.json").read_text())
        live = [observe(v, self.manifest) for v in fixture_values()]
        self.assertEqual(len(saved), 4)
        self.assertEqual(len(saved), len(live))
        for old, current in zip(saved, live):
            self.assertEqual(old["input"], current["input"])
            self.assertEqual(old["output"], current["output"])
            self.assertEqual(old["events"], current["events"])
        # Historical runtime pins are retained; this is not a replay at that host.
        self.assertEqual(certificate_text(saved),
                         (ROOT / "proof-packages/lean-core/E7CJointSerializerObservedFixtures.lean").read_text())


if __name__ == "__main__":
    unittest.main()
