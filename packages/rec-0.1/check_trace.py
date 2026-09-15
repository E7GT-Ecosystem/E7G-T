"""Independent bounded checker for REC-B1/0.1 reasoning witnesses.

This checker intentionally does not import the reference evaluator.  It checks
the envelope binding, replays evidence polarity and declared rule firing, then
compares the recorded statuses, applications, query action, scope and hashes.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Mapping


KERNEL = "0.14-experimental-draft"
PROFILE = "REC/0.1-proposed"
MODEL = "REC-B1/0.1"
MODALITIES = {"fact", "obligation", "permission", "prohibition", "possibility", "prediction", "recommendation"}


class TraceError(ValueError):
    """The supplied trace is not a valid REC-B1 witness."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def parse_time(value: str) -> datetime:
    try:
        point = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise TraceError("invalid timestamp") from exc
    if point.tzinfo is None:
        raise TraceError("timestamp has no timezone")
    return point.astimezone(timezone.utc)


def current(item: Mapping[str, Any], as_of: str) -> bool:
    point = parse_time(as_of)
    if item.get("valid_from") is not None and point < parse_time(item["valid_from"]):
        return False
    if item.get("valid_to") is not None and point > parse_time(item["valid_to"]):
        return False
    return True


def status(bits: list[bool]) -> str:
    return {
        (False, False): "neither",
        (True, False): "supported",
        (False, True): "refuted",
        (True, True): "both",
    }[tuple(bits)]


def expected_action(query_status: str, policy: str) -> str:
    if policy == "report":
        return "report_status"
    return {
        "supported": "rely_within_declared_scope",
        "refuted": "do_not_rely",
        "both": "resolve_conflict_or_abstain",
        "neither": "seek_evidence_or_abstain",
    }[query_status]


def check(envelope: Mapping[str, Any], witness: Mapping[str, Any]) -> bool:
    for field, expected in (("kernel", KERNEL), ("profile", PROFILE), ("model", MODEL)):
        if envelope.get(field) != expected or witness.get(field) != expected:
            raise TraceError(f"{field} binding mismatch")
    if witness.get("reasoning_id") != envelope.get("reasoning_id"):
        raise TraceError("reasoning identity mismatch")
    if witness.get("edition") != envelope.get("edition"):
        raise TraceError("edition mismatch")
    if witness.get("as_of") != envelope.get("as_of"):
        raise TraceError("as_of mismatch")
    if witness.get("envelope_sha256") != digest(envelope):
        raise TraceError("envelope digest mismatch")

    unsigned = dict(witness)
    supplied_witness_hash = unsigned.pop("witness_sha256", None)
    if supplied_witness_hash != digest(unsigned):
        raise TraceError("witness digest mismatch")

    claims = {item["id"]: item for item in envelope["claims"]}
    evidence = {item["id"]: item for item in envelope["evidence"]}
    rules = {item["id"]: item for item in envelope["rules"]}
    if len(claims) != len(envelope["claims"]) or len(evidence) != len(envelope["evidence"]) or len(rules) != len(envelope["rules"]):
        raise TraceError("duplicate identifier")

    for claim in claims.values():
        if claim.get("modality") not in MODALITIES or not isinstance(claim.get("scope"), dict):
            raise TraceError("invalid claim")
    for item in evidence.values():
        claim = claims.get(item.get("claim_id"))
        if claim is None:
            raise TraceError("unknown evidence claim")
        if not all(item.get("scope", {}).get(key) == value for key, value in claim["scope"].items()):
            raise TraceError("evidence scope mismatch")
        if not item.get("source_id") or not item.get("source_edition") or not item.get("provenance_group"):
            raise TraceError("incomplete evidence binding")
    for rule in rules.values():
        premises = rule.get("premises")
        conclusion = rule.get("conclusion")
        if not isinstance(premises, list) or not premises or not isinstance(conclusion, dict):
            raise TraceError("invalid rule")
        if conclusion.get("claim_id") not in claims or conclusion.get("polarity") not in {"support", "refute"}:
            raise TraceError("invalid rule conclusion")
        output = claims[conclusion["claim_id"]]
        modalities = set()
        for premise in premises:
            if premise.get("claim_id") not in claims or premise.get("requires") not in {"supported", "refuted"}:
                raise TraceError("invalid rule premise")
            source = claims[premise["claim_id"]]
            modalities.add(source["modality"])
            if not all(output["scope"].get(key) == value for key, value in source["scope"].items()):
                raise TraceError("rule scope expansion")
            if output["temporal_scope"] != source["temporal_scope"] and source["temporal_scope"] != "any":
                raise TraceError("rule temporal expansion")
        if output["modality"] not in modalities:
            bridge = rule.get("modality_bridge")
            if not isinstance(bridge, dict):
                raise TraceError("missing modality bridge")
            if sorted(bridge.get("from", [])) != sorted(modalities) or bridge.get("to") != output["modality"] or not bridge.get("authority"):
                raise TraceError("invalid modality bridge")

    query = envelope.get("query", {})
    if query.get("claim_id") not in claims or query.get("policy") not in {"report", "rely_if_supported_only"}:
        raise TraceError("invalid query")

    bits = {claim_id: [False, False] for claim_id in claims}
    admitted: list[str] = []
    stale: list[str] = []
    by_claim = {claim_id: [] for claim_id in claims}
    groups = {claim_id: set() for claim_id in claims}
    for evidence_id in sorted(evidence):
        item = evidence[evidence_id]
        if item["claim_id"] not in claims:
            raise TraceError("unknown evidence claim")
        if not current(item, envelope["as_of"]):
            stale.append(evidence_id)
            continue
        index = {"support": 0, "refute": 1}.get(item["polarity"])
        if index is None:
            raise TraceError("unknown evidence polarity")
        claim_id = item["claim_id"]
        bits[claim_id][index] = True
        admitted.append(evidence_id)
        by_claim[claim_id].append(evidence_id)
        groups[claim_id].add(item["provenance_group"])

    applications: list[dict[str, Any]] = []
    used: set[str] = set()
    changed = True
    while changed:
        changed = False
        for rule_id in sorted(rules):
            if rule_id in used:
                continue
            rule = rules[rule_id]
            ready = True
            for premise in rule["premises"]:
                premise_bits = bits[premise["claim_id"]]
                ready = ready and (premise_bits[0] if premise["requires"] == "supported" else premise_bits[1])
            if ready:
                conclusion = rule["conclusion"]
                index = 0 if conclusion["polarity"] == "support" else 1
                before = bits[conclusion["claim_id"]][index]
                bits[conclusion["claim_id"]][index] = True
                used.add(rule_id)
                applications.append({
                    "rule_id": rule_id,
                    "premises": [dict(p) for p in rule["premises"]],
                    "conclusion": dict(conclusion),
                })
                changed = changed or not before

    statuses = {key: status(bits[key]) for key in sorted(bits)}
    conflicts = [key for key in sorted(statuses) if statuses[key] == "both"]
    query = envelope["query"]
    query_status = statuses[query["claim_id"]]
    expected_query = {
        "claim_id": query["claim_id"],
        "status": query_status,
        "policy": query["policy"],
        "next_action": expected_action(query_status, query["policy"]),
    }
    expected_exact = {
        "statuses": statuses,
        "query": expected_query,
        "admitted_evidence": admitted,
        "stale_evidence": stale,
        "evidence_by_claim": {key: value for key, value in sorted(by_claim.items())},
        "provenance_groups_by_claim": {key: sorted(value) for key, value in sorted(groups.items())},
        "rule_applications": applications,
        "conflicts": conflicts,
        "unsupported_steps": [],
        "scope": dict(claims[query["claim_id"]]["scope"]),
        "temporal_scope": claims[query["claim_id"]]["temporal_scope"],
        "modality": claims[query["claim_id"]]["modality"],
    }
    required_keys = {
        "kernel", "profile", "model", "reasoning_id", "edition", "as_of",
        "envelope_sha256", "statuses", "query", "admitted_evidence",
        "stale_evidence", "evidence_by_claim", "provenance_groups_by_claim",
        "rule_applications", "conflicts", "unsupported_steps", "scope",
        "temporal_scope", "modality", "witness_sha256",
    }
    if set(witness) != required_keys:
        raise TraceError("non-canonical witness fields")
    for key, value in expected_exact.items():
        if witness.get(key) != value:
            raise TraceError(f"trace mismatch: {key}")
    return True


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Check a REC-B1/0.1 reasoning witness")
    parser.add_argument("envelope")
    parser.add_argument("witness")
    args = parser.parse_args()
    with open(args.envelope, encoding="utf-8") as source:
        envelope = json.load(source)
    with open(args.witness, encoding="utf-8") as source:
        witness = json.load(source)
    check(envelope, witness)
    print(json.dumps({"valid": True, "witness_sha256": witness["witness_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
