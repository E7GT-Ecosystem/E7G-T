import copy
import json
from importlib.machinery import SourceFileLoader
import unittest


rec = SourceFileLoader("rec", "packages/rec-0.1/e7gt_rec_v0_1.py").load_module()
checker = SourceFileLoader("rec_checker", "packages/rec-0.1/check_trace.py").load_module()


def resigned(witness):
    value = copy.deepcopy(witness)
    value.pop("witness_sha256", None)
    value["witness_sha256"] = checker.digest(value)
    return value


class RECReferenceModelTests(unittest.TestCase):
    def setUp(self):
        self.envelope = rec.demo_envelope()

    def test_reference_checks(self):
        report = rec.run_reference_checks()
        self.assertGreaterEqual(report["checks_passed"], 30)

    def test_reference_trace_passes_independent_checker(self):
        witness = rec.evaluate(self.envelope).witness
        self.assertTrue(checker.check(self.envelope, witness))

    def test_neither_is_not_false(self):
        self.envelope["evidence"] = []
        result = rec.evaluate(self.envelope).witness
        self.assertEqual(result["statuses"]["target-preserves"], "neither")

    def test_both_is_not_collapsed(self):
        self.envelope["evidence"].append({
            "id": "independent-support", "claim_id": "target-preserves",
            "polarity": "support", "source_id": "review", "source_edition": "1",
            "provenance_group": "review-1",
            "scope": {"document": "target-1", "jurisdiction": "declared"},
        })
        result = rec.evaluate(self.envelope).witness
        self.assertEqual(result["query"]["status"], "both")
        self.assertIn("target-preserves", result["conflicts"])

    def test_stale_evidence_is_historical_not_current(self):
        self.envelope["evidence"][1]["valid_to"] = "2026-09-14T00:00:00Z"
        result = rec.evaluate(self.envelope).witness
        self.assertEqual(result["query"]["status"], "neither")
        self.assertEqual(result["stale_evidence"], ["target-clause-7"])

    def test_future_evidence_is_not_current(self):
        self.envelope["evidence"][1]["valid_from"] = "2026-09-16T00:00:00Z"
        result = rec.evaluate(self.envelope).witness
        self.assertEqual(result["query"]["status"], "neither")

    def test_report_policy_does_not_authorise_reliance(self):
        self.envelope["query"]["policy"] = "report"
        result = rec.evaluate(self.envelope).witness
        self.assertEqual(result["query"]["next_action"], "report_status")

    def test_refutation_can_trigger_declared_rule(self):
        self.envelope["claims"].append({
            "id": "block", "proposition": "delivery check fails", "modality": "fact",
            "scope": {"document": "target-1", "jurisdiction": "declared"},
            "temporal_scope": "contract-term",
        })
        self.envelope["rules"] = [{
            "id": "block-on-failure",
            "premises": [{"claim_id": "target-preserves", "requires": "refuted"}],
            "conclusion": {"claim_id": "block", "polarity": "support"},
        }]
        result = rec.evaluate(self.envelope).witness
        self.assertEqual(result["statuses"]["block"], "supported")

    def test_fixed_point_rule_chain(self):
        scope = {"document": "target-1", "jurisdiction": "declared"}
        for claim_id in ("review", "stop"):
            self.envelope["claims"].append({
                "id": claim_id, "proposition": claim_id, "modality": "fact",
                "scope": scope, "temporal_scope": "contract-term",
            })
        self.envelope["rules"] = [
            {"id": "z-second", "premises": [{"claim_id": "review", "requires": "supported"}], "conclusion": {"claim_id": "stop", "polarity": "support"}},
            {"id": "a-first", "premises": [{"claim_id": "target-preserves", "requires": "refuted"}], "conclusion": {"claim_id": "review", "polarity": "support"}},
        ]
        result = rec.evaluate(self.envelope).witness
        self.assertEqual(result["statuses"]["stop"], "supported")
        self.assertEqual([x["rule_id"] for x in result["rule_applications"]], ["a-first", "z-second"])

    def test_duplicate_rule_application_is_prevented(self):
        self.envelope["claims"].append({
            "id": "review", "proposition": "review", "modality": "fact",
            "scope": {"document": "target-1", "jurisdiction": "declared"},
            "temporal_scope": "contract-term",
        })
        self.envelope["rules"] = [{
            "id": "review-rule", "premises": [{"claim_id": "target-preserves", "requires": "refuted"}],
            "conclusion": {"claim_id": "review", "polarity": "support"},
        }]
        result = rec.evaluate(self.envelope).witness
        self.assertEqual(len(result["rule_applications"]), 1)

    def test_scope_narrowing_is_allowed(self):
        self.envelope["claims"].append({
            "id": "narrow", "proposition": "narrow conclusion", "modality": "fact",
            "scope": {"document": "target-1", "jurisdiction": "declared", "section": "7"},
            "temporal_scope": "contract-term",
        })
        self.envelope["rules"] = [{
            "id": "narrow-rule", "premises": [{"claim_id": "target-preserves", "requires": "refuted"}],
            "conclusion": {"claim_id": "narrow", "polarity": "support"},
        }]
        self.assertEqual(rec.evaluate(self.envelope).witness["statuses"]["narrow"], "supported")

    def test_scope_expansion_is_rejected(self):
        self.envelope["claims"].append({
            "id": "broad", "proposition": "broad conclusion", "modality": "fact",
            "scope": {}, "temporal_scope": "contract-term",
        })
        self.envelope["rules"] = [{
            "id": "bad", "premises": [{"claim_id": "target-preserves", "requires": "refuted"}],
            "conclusion": {"claim_id": "broad", "polarity": "support"},
        }]
        with self.assertRaisesRegex(rec.RECError, "expands scope"):
            rec.evaluate(self.envelope)

    def test_temporal_scope_change_is_rejected(self):
        self.envelope["claims"].append({
            "id": "future", "proposition": "future conclusion", "modality": "fact",
            "scope": {"document": "target-1", "jurisdiction": "declared"},
            "temporal_scope": "future-term",
        })
        self.envelope["rules"] = [{
            "id": "bad-time", "premises": [{"claim_id": "target-preserves", "requires": "refuted"}],
            "conclusion": {"claim_id": "future", "polarity": "support"},
        }]
        with self.assertRaisesRegex(rec.RECError, "temporal scope"):
            rec.evaluate(self.envelope)

    def test_modality_change_requires_bridge(self):
        self.envelope["claims"].append({
            "id": "must-review", "proposition": "must review", "modality": "obligation",
            "scope": {"document": "target-1", "jurisdiction": "declared"},
            "temporal_scope": "contract-term",
        })
        self.envelope["rules"] = [{
            "id": "must", "premises": [{"claim_id": "target-preserves", "requires": "refuted"}],
            "conclusion": {"claim_id": "must-review", "polarity": "support"},
        }]
        with self.assertRaisesRegex(rec.RECError, "modality without bridge"):
            rec.evaluate(self.envelope)

    def test_authorised_modality_bridge_is_explicit(self):
        self.envelope["claims"].append({
            "id": "must-review", "proposition": "must review", "modality": "obligation",
            "scope": {"document": "target-1", "jurisdiction": "declared"},
            "temporal_scope": "contract-term",
        })
        self.envelope["rules"] = [{
            "id": "must", "premises": [{"claim_id": "target-preserves", "requires": "refuted"}],
            "conclusion": {"claim_id": "must-review", "polarity": "support"},
            "modality_bridge": {"from": ["fact"], "to": "obligation", "authority": "workflow-policy-1"},
        }]
        result = rec.evaluate(self.envelope).witness
        self.assertEqual(result["statuses"]["must-review"], "supported")

    def test_duplicate_claim_identity_rejected(self):
        self.envelope["claims"].append(copy.deepcopy(self.envelope["claims"][0]))
        with self.assertRaisesRegex(rec.RECError, "duplicate claim"):
            rec.evaluate(self.envelope)

    def test_evidence_must_cover_claim_scope(self):
        self.envelope["evidence"][0]["scope"] = {"document": "source-1"}
        with self.assertRaisesRegex(rec.RECError, "does not cover"):
            rec.evaluate(self.envelope)

    def test_tampered_envelope_is_rejected_by_checker(self):
        witness = rec.evaluate(self.envelope).witness
        self.envelope["edition"] = "2"
        with self.assertRaisesRegex(checker.TraceError, "edition mismatch|envelope digest"):
            checker.check(self.envelope, witness)

    def test_tampered_witness_hash_is_rejected(self):
        witness = copy.deepcopy(rec.evaluate(self.envelope).witness)
        witness["query"]["status"] = "supported"
        with self.assertRaisesRegex(checker.TraceError, "witness digest"):
            checker.check(self.envelope, witness)

    def test_resigned_forged_status_is_still_rejected(self):
        witness = copy.deepcopy(rec.evaluate(self.envelope).witness)
        witness["query"]["status"] = "supported"
        witness = resigned(witness)
        with self.assertRaisesRegex(checker.TraceError, "trace mismatch: query"):
            checker.check(self.envelope, witness)

    def test_resigned_erased_conflict_is_rejected(self):
        self.envelope["evidence"].append({
            "id": "support", "claim_id": "target-preserves", "polarity": "support",
            "source_id": "review", "source_edition": "1", "provenance_group": "review",
            "scope": {"document": "target-1", "jurisdiction": "declared"},
        })
        witness = copy.deepcopy(rec.evaluate(self.envelope).witness)
        witness["conflicts"] = []
        witness = resigned(witness)
        with self.assertRaisesRegex(checker.TraceError, "trace mismatch: conflicts"):
            checker.check(self.envelope, witness)

    def test_resigned_erased_stale_evidence_is_rejected(self):
        self.envelope["evidence"][1]["valid_to"] = "2026-09-14T00:00:00Z"
        witness = copy.deepcopy(rec.evaluate(self.envelope).witness)
        witness["stale_evidence"] = []
        witness = resigned(witness)
        with self.assertRaisesRegex(checker.TraceError, "trace mismatch: stale_evidence"):
            checker.check(self.envelope, witness)

    def test_evidence_duplicates_do_not_become_independence(self):
        self.envelope["evidence"].append({
            "id": "same-origin", "claim_id": "source-prohibits", "polarity": "support",
            "source_id": "copy", "source_edition": "1", "provenance_group": "contract-pair-1",
            "scope": {"document": "source-1", "jurisdiction": "declared"},
        })
        result = rec.evaluate(self.envelope).witness
        self.assertEqual(result["provenance_groups_by_claim"]["source-prohibits"], ["contract-pair-1"])

    def test_canonical_result_ignores_input_list_order(self):
        first = rec.evaluate(self.envelope).witness
        self.envelope["evidence"].reverse()
        second = rec.evaluate(self.envelope).witness
        self.assertNotEqual(first["envelope_sha256"], second["envelope_sha256"])
        for key in ("statuses", "query", "admitted_evidence", "conflicts"):
            self.assertEqual(first[key], second[key])


if __name__ == "__main__":
    unittest.main()
