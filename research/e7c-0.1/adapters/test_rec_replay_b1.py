"""Selected REC source evaluator and independent replay integration checks."""

import copy
import json
from pathlib import Path
import unittest

from rec_replay_b1 import (BridgeError, MODULE_EDITION, admit, checker, evaluator,
                           execute, replay)

FIXTURE = (Path(__file__).resolve().parents[3] / "packages" / "rec-0.1"
           / "fixtures" / "translation_clause_envelope.json")


class RECReplayTests(unittest.TestCase):
    def setUp(self):
        self.source = json.loads(FIXTURE.read_text())

    def test_source_witness_is_replayed_with_pinned_policy_and_provenance(self):
        envelope = admit(self.source)
        source_result = evaluator.evaluate(self.source).witness
        actual = execute(envelope)
        self.assertEqual(actual, replay(envelope, source_result))
        self.assertEqual(actual.edition, MODULE_EDITION)
        self.assertEqual(actual.envelope_sha256, source_result["envelope_sha256"])
        self.assertEqual(actual.witness_sha256, source_result["witness_sha256"])
        self.assertEqual(actual.query_status, source_result["query"]["status"])
        self.assertEqual(actual.next_action, source_result["query"]["next_action"])
        self.assertEqual(dict(actual.provenance_groups),
                         {k: tuple(v) for k, v in source_result["provenance_groups_by_claim"].items()})
        self.assertIn("independent_replay", actual.incurred)

    def test_snapshotted_envelope_and_edition_mismatch(self):
        envelope = admit(self.source)
        expected = execute(envelope)
        self.source["query"]["policy"] = "report"
        self.source["evidence"][0]["source_edition"] = "later"
        self.assertEqual(execute(envelope), expected)
        changed = admit(self.source)
        with self.assertRaisesRegex(BridgeError, "independent_replay_failed"):
            replay(changed, evaluator.evaluate(envelope.value()).witness)
        self.source["model"] = "future"
        with self.assertRaisesRegex(BridgeError, "source_edition_mismatch"):
            admit(self.source)

    def test_four_statuses_and_policy_remain_separate(self):
        claim_id = self.source["query"]["claim_id"]
        for polarities, status, action in (
            ((), "neither", "seek_evidence_or_abstain"),
            (("support",), "supported", "rely_within_declared_scope"),
            (("refute",), "refuted", "do_not_rely"),
            (("support", "refute"), "both", "resolve_conflict_or_abstain"),
        ):
            case = copy.deepcopy(self.source)
            case["evidence"] = []
            for polarity in polarities:
                case["evidence"].append({"id": polarity, "claim_id": claim_id,
                    "polarity": polarity, "source_id": polarity + "-source",
                    "source_edition": "1", "provenance_group": "same-origin",
                    "scope": case["claims"][1]["scope"]})
            actual = execute(admit(case))
            self.assertEqual((actual.query_status, actual.next_action), (status, action))
            if len(polarities) == 2:
                self.assertEqual(dict(actual.provenance_groups)[claim_id], ("same-origin",))
            case["query"]["policy"] = "report"
            self.assertEqual(execute(admit(case)).query_status, status)
            self.assertEqual(execute(admit(case)).next_action, "report_status")

    def test_re_signed_forgery_and_extra_weight_rejected(self):
        envelope = admit(self.source)
        forged = copy.deepcopy(evaluator.evaluate(self.source).witness)
        forged["query"]["next_action"] = "rely_within_declared_scope"
        unsigned = dict(forged)
        unsigned.pop("witness_sha256")
        forged["witness_sha256"] = checker.digest(unsigned)
        with self.assertRaisesRegex(BridgeError, "independent_replay_failed"):
            replay(envelope, forged)
        weighted = copy.deepcopy(self.source)
        weighted["evidence"][0]["weight"] = 0.9
        with self.assertRaisesRegex(BridgeError, "evidence_shape_mismatch"):
            admit(weighted)

    def test_scope_expansion_rejected_before_execution(self):
        wrong = copy.deepcopy(self.source)
        wrong["evidence"][0]["scope"] = {}
        with self.assertRaisesRegex(BridgeError, "source_admission_failed"):
            admit(wrong)


if __name__ == "__main__":
    unittest.main()
