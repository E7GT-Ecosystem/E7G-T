#!/usr/bin/env python3
"""Generate pinned deterministic model receipts and expected negative outcomes."""
import json
from pathlib import Path
import gcd02 as g

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "evidence"
OUTPUT.mkdir(exist_ok=True)


def dump(name, obj):
    (OUTPUT / name).write_text(json.dumps(obj, indent=2, sort_keys=True,
                                          ensure_ascii=False) + "\n", encoding="utf-8")


base = g.family(g.SIG0, "src", (g.make_config(g.SIG0),), "dep-1")
a = g.make_config(g.SIG1, ("A",))
r = g.make_config(g.SIG1, ("R",))
ar = g.make_config(g.SIG1, ("A", "R"))
e = g.make_config(g.SIG2, ("A", "E"))
h = g.family(g.SIG1, "v1", (a, r), "dep-1")
h_already = g.family(g.SIG1, "v1-c", (a, r, ar), "dep-1")
choice_req = {"op": "choose", "family": g.family_record(h), "candidate": g.config_record(a),
              "choice_id": "act-1", "actor_ref": "reviewer:alice"}
choice_receipt = g.receipt(choice_req)
malformed_e = g.config_record(e)
malformed_e["relations"].remove(["requires", "A", "E"])

inputs = [
    ("unchanged_semantics_access_only", {"op": "differentiate", "source": g.family_record(h),
                                          "target": g.family_record(h)}, "access_refinement_only"),
    ("no_pairwise_semantic_split", {"op": "differentiate", "source": g.family_record(base),
                                     "target": g.family_record(g.family(g.SIG1, "single", (a,)))}, "not_established"),
    ("within_generation_coarse_comparison", {"op": "generate_within", "family": g.family_record(h),
                                                "candidate": g.config_record(ar), "criterion": "root_only"}, "non_expansive"),
    ("within_generation_existing_alternative", {"op": "generate_within", "family": g.family_record(h_already),
                                                "candidate": g.config_record(ar)}, "non_expansive"),
    ("within_generation_wrong_candidate", {"op": "generate_within", "family": g.family_record(h),
                                            "candidate": g.config_record(a)}, "domain_error"),
    ("signature_extension_unsupported", {"op": "generate_signature", "family": g.family_record(base),
                                          "candidate": g.config_record(e)}, "unsupported"),
    ("signature_extension_invalid_missing_relation", {"op": "generate_signature", "family": g.family_record(h),
                                                      "candidate": malformed_e}, "invalid_input"),
    ("signature_extension_coarse_comparison", {"op": "generate_signature", "family": g.family_record(h),
                                                 "candidate": g.config_record(e), "criterion": "root_only"}, "non_expansive"),
    ("choice_nonmember", {"op": "choose", "family": g.family_record(h),
                          "candidate": g.config_record(ar), "choice_id": "act-2",
                          "actor_ref": "reviewer:alice"}, "rejected_nonmember"),
    ("choice_not_supplied", {"op": "choose", "family": g.family_record(h),
                             "candidate": None, "choice_id": "act-3",
                             "actor_ref": "reviewer:alice"}, "unresolved"),
    ("choice_unknown_policy", {"op": "choose", "family": g.family_record(h),
                              "candidate": None, "choice_id": "act-4", "actor_ref": "reviewer:alice",
                              "mechanism": "registered_policy", "policy": "other/v1"}, "unsupported"),
    ("model_commit_without_grant", {"op": "commit_model", "family": g.family_record(h),
                                    "choice_receipt": choice_receipt, "actor_ref": "reviewer:alice",
                                    "grant": "unapproved", "base_epoch": 0,
                                    "event_id": "evt-1"}, "unauthorised"),
    ("model_commit_stale_family", {"op": "commit_model", "family": g.family_record(g.family(g.SIG1,"v2", (a,r))),
                                  "choice_receipt": choice_receipt, "actor_ref": "reviewer:alice",
                                  "grant": "fixture-grant-alice", "base_epoch": 0,
                                  "event_id": "evt-2"}, "rejected"),
    ("finite_rank_exceeded", {"op": "lift", "source_id": "root", "steps": 9}, "resource_limit"),
    ("unknown_operation", {"op": "imaginary"}, "unsupported"),
]
negative = []
for case, req, expected in inputs:
    record = g.receipt(req)
    assert record["outcome"]["status"] == expected, (case, record["outcome"])
    assert g.verify_receipt(record)
    negative.append({"case": case, "expected_status": expected, "receipt": record})

example = g.complete_example()
assert len(example["stages"]) == 5
assert all(g.verify_receipt(r) for r in example["stages"].values())
dump("end_to_end_receipts.json", example)
dump("negative_receipts.json", {"model": g.MODEL, "negative_cases": negative,
                                "purpose": "expected explicit non-success outcomes, not failed test run"})
print(f"Wrote {len(example['stages'])} end-to-end and {len(negative)} expected-negative receipts.")
