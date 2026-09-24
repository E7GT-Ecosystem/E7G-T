"""Pinned cross-edition conformance for the selected B2 sequencing slice."""

import copy
import hashlib
import json
from pathlib import Path

from e7_ir_conformance_b1 import build_manifest as build_b1
from e7_ir_success_sequence_b2 import compare_replay, lower, parse, serialize
from e7c_b1_canonical import canonical_key, digest
from e7c_success_sequence_b2 import admit
from e7c_success_sequence_checker_b2 import check_sequence

HERE = Path(__file__).resolve().parent / "fixtures" / "wp5_ir"
EDITION = "E7-IR-CROSS-SLICE-CONFORMANCE/0.2-B2-provisional"


def build_manifest():
    original = (HERE / "success_sequence_ir.json").read_bytes()
    seed = json.loads(original)
    source = seed["source_document"]
    variants = (
        ("success", None),
        ("first_unsupported", "first_unsupported"),
        ("first_undetermined", "first_undetermined"),
        ("continuation_domain_error", "continuation_domain_error"),
        ("step_limit", "step_limit"),
        ("ledger_limit", "ledger_limit"),
    )
    rows = []
    for label, change in variants:
        candidate = copy.deepcopy(source)
        if change == "first_unsupported":
            candidate["interpretation"]["maps"]["total_identity"]["capability"] = False
        elif change == "first_undetermined":
            candidate["interpretation"]["maps"]["total_identity"]["obligation"] = "unresolved"
        elif change == "continuation_domain_error":
            # This value is already admitted by the finite carrier.
            candidate["values"]["source_config"] = {"id": "b", "valid": False}
        elif change == "step_limit":
            candidate["resource_policy"]["step_bound"] = 3
        elif change == "ledger_limit":
            candidate["resource_policy"]["ledger_entry_bound"] = 1
        ir = lower(candidate)
        assert parse(serialize(ir)) == ir
        replay = compare_replay(ir)
        witness = ir["source_witness"]
        assert check_sequence(witness)["status"] == "accepted"
        _, _, static = admit(candidate)
        claim = replay["ir_result"]
        assert claim == witness["claim"]
        assert all(entry["static_atom"] in static["effects"] for entry in claim["ordered_ledger"])
        assert claim["resource_progress"]["completed_steps"] <= candidate["resource_policy"]["step_bound"]
        assert len(claim["ordered_ledger"]) <= candidate["resource_policy"]["ledger_entry_bound"]
        if label.startswith("first_"):
            assert [entry["detail"]["declaration"] for entry in claim["ordered_ledger"]] == ["total_identity"]
        rows.append({"case": label, "source_document_digest": digest(candidate),
                     "ir_edition": ir["ir_edition"], "ir_identifier": ir["id"],
                     "witness_identifier": witness["id"],
                     "static_type": static["type"],
                     "static_effects": [canonical_key(item) for item in static["effects"]],
                     "ledger_dimensions": [entry["static_atom"]["dimension"]
                                           for entry in claim["ordered_ledger"]],
                     "terminal_tag": claim["terminal_outcome"]["tag"],
                     "completed_steps": claim["resource_progress"]["completed_steps"]})
    return {"edition": EDITION,
            "b1_manifest_digest": digest(build_b1()),
            "b2_seed_fixture_sha256": hashlib.sha256(original).hexdigest(),
            "scope": "five B1 fixtures and six selected B2 sequencing observations",
            "source_authority": "E7G-T-v0.12.1/RGP2-experimental",
            "no_profile_or_product_promotion": True, "b2_cases": rows}
