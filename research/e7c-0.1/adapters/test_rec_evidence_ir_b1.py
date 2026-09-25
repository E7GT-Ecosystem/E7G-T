"""Independent finite evidence rule against the REC source and replay checker."""

import copy
import json
from pathlib import Path
import unittest

from rec_evidence_ir_b1 import Unsupported, admit as admit_ir, evaluate
from rec_replay_b1 import admit as admit_source, evaluator, execute


FIXTURE = (Path(__file__).resolve().parents[3] / "packages" / "rec-0.1"
           / "fixtures" / "translation_clause_envelope.json")


def one_claim():
    doc = json.loads(FIXTURE.read_text())
    doc["claims"] = [doc["claims"][1]]
    doc["evidence"] = [doc["evidence"][1]]
    return doc


class RECEvidenceIR(unittest.TestCase):
    def compare(self, doc):
        # Admission is a stated premise: this adapter first checks the pinned
        # source envelope; the candidate independently computes the status.
        admitted = admit_source(doc)
        source = evaluator.evaluate(admitted.value()).witness
        checked = execute(admitted)
        candidate = evaluate(admit_ir(doc), len(doc["evidence"]))
        claim = doc["query"]["claim_id"]
        self.assertEqual(checked.query_status, source["query"]["status"])
        self.assertEqual((candidate.status, candidate.action),
                         (source["statuses"][claim], source["query"]["next_action"]))
        self.assertEqual(candidate.admitted, tuple(source["admitted_evidence"]))
        self.assertEqual(candidate.stale, tuple(source["stale_evidence"]))
        self.assertEqual(candidate.provenance,
                         tuple(source["provenance_groups_by_claim"][claim]))
        return candidate

    def test_four_statuses_and_both_policies(self):
        base = one_claim()
        for polarities, expected in (((), "neither"), (("support",), "supported"),
                                     (("refute",), "refuted"),
                                     (("support", "refute"), "both")):
            for policy in ("report", "rely_if_supported_only"):
                doc = copy.deepcopy(base)
                doc["query"]["policy"] = policy
                doc["evidence"] = []
                for polarity in polarities:
                    item = copy.deepcopy(base["evidence"][0])
                    item["id"] = polarity
                    item["polarity"] = polarity
                    doc["evidence"].append(item)
                self.assertEqual(self.compare(doc).status, expected)

    def test_stale_boundaries_and_resource_progress(self):
        doc = one_claim()
        doc["evidence"][0]["valid_to"] = "2026-09-14T23:59:59Z"
        self.assertEqual((self.compare(doc).status, self.compare(doc).stale),
                         ("neither", ("target-clause-7",)))
        doc = one_claim()
        query = admit_ir(doc)
        self.assertEqual((evaluate(query, 0).outcome, evaluate(query, 0).progress,
                          evaluate(query, 0).status), ("resource_limit", 0, None))
        doc["evidence"].append({**copy.deepcopy(doc["evidence"][0]),
                                 "id": "a-first", "polarity": "support"})
        partial = evaluate(admit_ir(doc), 1)
        self.assertEqual((partial.outcome, partial.progress, partial.admitted,
                          partial.status, partial.action),
                         ("resource_limit", 1, ("a-first",), None, None))
        self.compare(doc)

    def test_rule_closure_and_scope_are_not_admitted_as_this_rule(self):
        doc = one_claim()
        doc["rules"] = [{"id": "rule", "premises": [], "conclusion": {}}]
        with self.assertRaisesRegex(Unsupported, "one_claim_no_rules"):
            admit_ir(doc)
        doc = one_claim()
        doc["evidence"][0]["scope"] = {}
        with self.assertRaisesRegex(Unsupported, "scope_expansion"):
            admit_ir(doc)
        doc = one_claim()
        doc["query"]["policy"] = "rely"
        with self.assertRaisesRegex(Unsupported, "policy"):
            admit_ir(doc)


if __name__ == "__main__":
    unittest.main()
