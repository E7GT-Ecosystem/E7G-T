"""Bounded executable reference model for E7G-T REC/0.1.

REC/0.1 evaluates a finite claim/evidence/rule envelope.  It deliberately
separates information status from truth, retains support and refutation at the
same time, rejects hidden scope or modality expansion, and emits a canonical
reasoning witness.  This is a reference subset, not a general theorem prover,
fact checker, legal reasoner, or empirical claim that an LLM becomes better.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from typing import Any, Iterable, Mapping


KERNEL = "0.14-experimental-draft"
PROFILE = "REC/0.1-proposed"
MODEL = "REC-B1/0.1"


class RECError(ValueError):
    """Typed admission or evaluation failure."""


class Status(str, Enum):
    NEITHER = "neither"
    SUPPORTED = "supported"
    REFUTED = "refuted"
    BOTH = "both"

    @classmethod
    def from_bits(cls, positive: bool, negative: bool) -> "Status":
        return {
            (False, False): cls.NEITHER,
            (True, False): cls.SUPPORTED,
            (False, True): cls.REFUTED,
            (True, True): cls.BOTH,
        }[(positive, negative)]


MODALITIES = {
    "fact",
    "obligation",
    "permission",
    "prohibition",
    "possibility",
    "prediction",
    "recommendation",
}
POLARITIES = {"support", "refute"}
REQUIREMENTS = {"supported", "refuted"}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise RECError(message)


def _unique(items: Iterable[Mapping[str, Any]], kind: str) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for item in items:
        item_id = item.get("id")
        _expect(isinstance(item_id, str) and item_id != "", f"{kind} id required")
        _expect(item_id not in result, f"duplicate {kind} id: {item_id}")
        result[item_id] = item
    return result


def _parse_time(value: str) -> datetime:
    _expect(isinstance(value, str) and value != "", "timestamp required")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RECError(f"invalid timestamp: {value}") from exc
    _expect(parsed.tzinfo is not None, "timestamp must include timezone")
    return parsed.astimezone(timezone.utc)


def scope_is_narrower_or_equal(candidate: Mapping[str, str], source: Mapping[str, str]) -> bool:
    """Return true when candidate preserves every constraint in source."""
    return all(candidate.get(key) == value for key, value in source.items())


def evidence_is_current(evidence: Mapping[str, Any], as_of: str) -> bool:
    point = _parse_time(as_of)
    start = evidence.get("valid_from")
    end = evidence.get("valid_to")
    if start is not None and point < _parse_time(start):
        return False
    if end is not None and point > _parse_time(end):
        return False
    return True


def _validate_claim(claim: Mapping[str, Any]) -> None:
    _expect(isinstance(claim.get("proposition"), str) and claim["proposition"], "claim proposition required")
    _expect(claim.get("modality") in MODALITIES, "unsupported claim modality")
    _expect(isinstance(claim.get("scope"), dict), "claim scope must be an object")
    _expect(all(isinstance(k, str) and isinstance(v, str) for k, v in claim["scope"].items()), "scope coordinates must be strings")
    _expect(isinstance(claim.get("temporal_scope"), str) and claim["temporal_scope"], "claim temporal_scope required")


def _validate_envelope(envelope: Mapping[str, Any]) -> tuple[dict[str, Mapping[str, Any]], dict[str, Mapping[str, Any]], dict[str, Mapping[str, Any]]]:
    _expect(envelope.get("kernel") == KERNEL, "kernel pin mismatch")
    _expect(envelope.get("profile") == PROFILE, "profile pin mismatch")
    _expect(envelope.get("model") == MODEL, "model pin mismatch")
    _expect(isinstance(envelope.get("reasoning_id"), str) and envelope["reasoning_id"], "reasoning_id required")
    _expect(isinstance(envelope.get("edition"), str) and envelope["edition"], "edition required")
    _parse_time(envelope.get("as_of"))
    claims = _unique(envelope.get("claims", []), "claim")
    evidence = _unique(envelope.get("evidence", []), "evidence")
    rules = _unique(envelope.get("rules", []), "rule")
    _expect(bool(claims), "at least one claim required")
    for claim in claims.values():
        _validate_claim(claim)
    for item in evidence.values():
        _expect(item.get("claim_id") in claims, "evidence references unknown claim")
        _expect(item.get("polarity") in POLARITIES, "unsupported evidence polarity")
        _expect(isinstance(item.get("source_id"), str) and item["source_id"], "source_id required")
        _expect(isinstance(item.get("source_edition"), str) and item["source_edition"], "source_edition required")
        _expect(isinstance(item.get("provenance_group"), str) and item["provenance_group"], "provenance_group required")
        _expect(isinstance(item.get("scope"), dict), "evidence scope must be an object")
        _expect(scope_is_narrower_or_equal(item["scope"], claims[item["claim_id"]]["scope"]), "evidence does not cover claim scope")
        if item.get("valid_from") is not None:
            _parse_time(item["valid_from"])
        if item.get("valid_to") is not None:
            _parse_time(item["valid_to"])
            if item.get("valid_from") is not None:
                _expect(_parse_time(item["valid_from"]) <= _parse_time(item["valid_to"]), "invalid evidence validity interval")
    for rule in rules.values():
        premises = rule.get("premises")
        conclusion = rule.get("conclusion")
        _expect(isinstance(premises, list) and premises, "rule premises required")
        _expect(isinstance(conclusion, dict), "rule conclusion required")
        for premise in premises:
            _expect(premise.get("claim_id") in claims, "rule premise references unknown claim")
            _expect(premise.get("requires") in REQUIREMENTS, "unsupported premise requirement")
        _expect(conclusion.get("claim_id") in claims, "rule conclusion references unknown claim")
        _expect(conclusion.get("polarity") in POLARITIES, "unsupported conclusion polarity")
        output_claim = claims[conclusion["claim_id"]]
        for premise in premises:
            input_claim = claims[premise["claim_id"]]
            _expect(scope_is_narrower_or_equal(output_claim["scope"], input_claim["scope"]), "rule expands scope")
            _expect(
                output_claim["temporal_scope"] == input_claim["temporal_scope"]
                or input_claim["temporal_scope"] == "any",
                "rule changes temporal scope without bridge",
            )
        modalities = {claims[p["claim_id"]]["modality"] for p in premises}
        output_modality = output_claim["modality"]
        bridge = rule.get("modality_bridge")
        if output_modality not in modalities:
            _expect(isinstance(bridge, dict), "rule changes modality without bridge")
            _expect(sorted(bridge.get("from", [])) == sorted(modalities), "modality bridge source mismatch")
            _expect(bridge.get("to") == output_modality, "modality bridge target mismatch")
            _expect(isinstance(bridge.get("authority"), str) and bridge["authority"], "modality bridge authority required")
    query = envelope.get("query")
    _expect(isinstance(query, dict), "query required")
    _expect(query.get("claim_id") in claims, "query references unknown claim")
    _expect(query.get("policy") in {"report", "rely_if_supported_only"}, "unsupported query policy")
    return claims, evidence, rules


def _has_requirement(bits: tuple[bool, bool], requirement: str) -> bool:
    return bits[0] if requirement == "supported" else bits[1]


@dataclass(frozen=True)
class Evaluation:
    witness: Mapping[str, Any]

    @property
    def sha256(self) -> str:
        return digest(self.witness)


def evaluate(envelope: Mapping[str, Any]) -> Evaluation:
    claims, evidence, rules = _validate_envelope(envelope)
    bits: dict[str, list[bool]] = {claim_id: [False, False] for claim_id in claims}
    evidence_by_claim: dict[str, list[str]] = {claim_id: [] for claim_id in claims}
    stale: list[str] = []
    admitted_evidence: list[str] = []
    provenance_groups: dict[str, set[str]] = {claim_id: set() for claim_id in claims}
    for evidence_id in sorted(evidence):
        item = evidence[evidence_id]
        if not evidence_is_current(item, envelope["as_of"]):
            stale.append(evidence_id)
            continue
        claim_id = item["claim_id"]
        polarity_index = 0 if item["polarity"] == "support" else 1
        bits[claim_id][polarity_index] = True
        evidence_by_claim[claim_id].append(evidence_id)
        admitted_evidence.append(evidence_id)
        provenance_groups[claim_id].add(item["provenance_group"])

    applications: list[dict[str, Any]] = []
    applied: set[str] = set()
    changed = True
    while changed:
        changed = False
        for rule_id in sorted(rules):
            if rule_id in applied:
                continue
            rule = rules[rule_id]
            if all(_has_requirement(tuple(bits[p["claim_id"]]), p["requires"]) for p in rule["premises"]):
                conclusion = rule["conclusion"]
                index = 0 if conclusion["polarity"] == "support" else 1
                before = bits[conclusion["claim_id"]][index]
                bits[conclusion["claim_id"]][index] = True
                applied.add(rule_id)
                applications.append({
                    "rule_id": rule_id,
                    "premises": [dict(p) for p in rule["premises"]],
                    "conclusion": dict(conclusion),
                })
                changed = changed or not before

    statuses = {claim_id: Status.from_bits(*bits[claim_id]).value for claim_id in sorted(claims)}
    conflicts = [claim_id for claim_id, status in statuses.items() if status == Status.BOTH.value]
    query = envelope["query"]
    query_status = statuses[query["claim_id"]]
    if query["policy"] == "report":
        next_action = "report_status"
    elif query_status == Status.SUPPORTED.value:
        next_action = "rely_within_declared_scope"
    elif query_status == Status.BOTH.value:
        next_action = "resolve_conflict_or_abstain"
    elif query_status == Status.REFUTED.value:
        next_action = "do_not_rely"
    else:
        next_action = "seek_evidence_or_abstain"

    witness: dict[str, Any] = {
        "kernel": KERNEL,
        "profile": PROFILE,
        "model": MODEL,
        "reasoning_id": envelope["reasoning_id"],
        "edition": envelope["edition"],
        "as_of": envelope["as_of"],
        "envelope_sha256": digest(envelope),
        "statuses": statuses,
        "query": {
            "claim_id": query["claim_id"],
            "status": query_status,
            "policy": query["policy"],
            "next_action": next_action,
        },
        "admitted_evidence": admitted_evidence,
        "stale_evidence": stale,
        "evidence_by_claim": {key: value for key, value in sorted(evidence_by_claim.items())},
        "provenance_groups_by_claim": {key: sorted(value) for key, value in sorted(provenance_groups.items())},
        "rule_applications": applications,
        "conflicts": conflicts,
        "unsupported_steps": [],
        "scope": dict(claims[query["claim_id"]]["scope"]),
        "temporal_scope": claims[query["claim_id"]]["temporal_scope"],
        "modality": claims[query["claim_id"]]["modality"],
    }
    witness["witness_sha256"] = digest(witness)
    return Evaluation(witness)


def demo_envelope() -> dict[str, Any]:
    return {
        "kernel": KERNEL,
        "profile": PROFILE,
        "model": MODEL,
        "reasoning_id": "translation-clause-demo",
        "edition": "1",
        "as_of": "2026-09-15T00:00:00Z",
        "claims": [
            {
                "id": "source-prohibits",
                "proposition": "supplier disclose data without consent",
                "modality": "prohibition",
                "scope": {"document": "source-1", "jurisdiction": "declared"},
                "temporal_scope": "contract-term",
            },
            {
                "id": "target-preserves",
                "proposition": "target preserves source modality",
                "modality": "fact",
                "scope": {"document": "target-1", "jurisdiction": "declared"},
                "temporal_scope": "contract-term",
            },
        ],
        "evidence": [
            {
                "id": "source-clause-7",
                "claim_id": "source-prohibits",
                "polarity": "support",
                "source_id": "source-contract",
                "source_edition": "1",
                "provenance_group": "contract-pair-1",
                "scope": {"document": "source-1", "jurisdiction": "declared"},
                "valid_from": "2026-01-01T00:00:00Z",
            },
            {
                "id": "target-clause-7",
                "claim_id": "target-preserves",
                "polarity": "refute",
                "source_id": "target-contract",
                "source_edition": "1",
                "provenance_group": "contract-pair-1",
                "scope": {"document": "target-1", "jurisdiction": "declared"},
                "valid_from": "2026-01-01T00:00:00Z",
            },
        ],
        "rules": [],
        "query": {"claim_id": "target-preserves", "policy": "rely_if_supported_only"},
    }


def run_reference_checks() -> dict[str, Any]:
    checks: list[str] = []

    def check(condition: bool, name: str) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    envelope = demo_envelope()
    result = evaluate(envelope).witness
    check(result["query"]["status"] == "refuted", "refuted query retained")
    check(result["query"]["next_action"] == "do_not_rely", "refuted query blocks reliance")
    check(result["statuses"]["source-prohibits"] == "supported", "support recorded")
    check(result["conflicts"] == [], "no invented conflict")
    check(result["unsupported_steps"] == [], "no invented unsupported step")
    check(result["envelope_sha256"] == digest(envelope), "envelope digest bound")
    unsigned = dict(result)
    witness_hash = unsigned.pop("witness_sha256")
    check(witness_hash == digest(unsigned), "witness digest bound")
    check(result == evaluate(envelope).witness, "deterministic replay")
    check(len(result["admitted_evidence"]) == 2, "two evidence records admitted")
    check(result["provenance_groups_by_claim"]["target-preserves"] == ["contract-pair-1"], "provenance group retained")

    conflict = json.loads(json.dumps(envelope))
    conflict["evidence"].append({
        "id": "reviewer-support",
        "claim_id": "target-preserves",
        "polarity": "support",
        "source_id": "review",
        "source_edition": "1",
        "provenance_group": "independent-review",
        "scope": {"document": "target-1", "jurisdiction": "declared"},
    })
    conflict_result = evaluate(conflict).witness
    check(conflict_result["query"]["status"] == "both", "conflict preserved as both")
    check(conflict_result["conflicts"] == ["target-preserves"], "conflict listed")
    check(conflict_result["query"]["next_action"] == "resolve_conflict_or_abstain", "conflict prevents reliance")

    stale = json.loads(json.dumps(envelope))
    stale["evidence"][1]["valid_to"] = "2026-09-14T23:59:59Z"
    stale_result = evaluate(stale).witness
    check(stale_result["query"]["status"] == "neither", "stale evidence does not decide current query")
    check(stale_result["stale_evidence"] == ["target-clause-7"], "stale evidence exposed")
    check(stale_result["query"]["next_action"] == "seek_evidence_or_abstain", "neither requires evidence or abstention")

    chained = json.loads(json.dumps(envelope))
    chained["claims"].append({
        "id": "delivery-blocked", "proposition": "delivery preservation check fails",
        "modality": "fact", "scope": {"document": "target-1", "jurisdiction": "declared"},
        "temporal_scope": "contract-term",
    })
    chained["rules"].append({
        "id": "failed-preservation-blocks",
        "premises": [{"claim_id": "target-preserves", "requires": "refuted"}],
        "conclusion": {"claim_id": "delivery-blocked", "polarity": "support"},
    })
    chained_result = evaluate(chained).witness
    check(chained_result["statuses"]["delivery-blocked"] == "supported", "declared rule derives support")
    check(len(chained_result["rule_applications"]) == 1, "rule application recorded once")
    check(chained_result["rule_applications"][0]["rule_id"] == "failed-preservation-blocks", "rule identity retained")

    invalid_cases: list[tuple[str, str, Any]] = []
    invalid_cases.append(("wrong kernel rejected", "kernel pin", lambda x: x.update(kernel="bad")))
    invalid_cases.append(("wrong profile rejected", "profile pin", lambda x: x.update(profile="bad")))
    invalid_cases.append(("wrong model rejected", "model pin", lambda x: x.update(model="bad")))
    invalid_cases.append(("empty claims rejected", "at least one claim", lambda x: x.update(claims=[])))
    invalid_cases.append(("unknown query rejected", "query references", lambda x: x["query"].update(claim_id="missing")))
    invalid_cases.append(("unsupported policy rejected", "unsupported query policy", lambda x: x["query"].update(policy="guess")))
    invalid_cases.append(("duplicate claim rejected", "duplicate claim", lambda x: x["claims"].append(dict(x["claims"][0]))))
    invalid_cases.append(("unknown evidence claim rejected", "unknown claim", lambda x: x["evidence"][0].update(claim_id="missing")))
    invalid_cases.append(("unknown polarity rejected", "polarity", lambda x: x["evidence"][0].update(polarity="maybe")))
    invalid_cases.append(("missing provenance group rejected", "provenance_group", lambda x: x["evidence"][0].update(provenance_group="")))
    invalid_cases.append(("naive timestamp rejected", "timezone", lambda x: x.update(as_of="2026-09-15T00:00:00")))
    invalid_cases.append(("inverted validity rejected", "validity interval", lambda x: x["evidence"][0].update(valid_from="2026-09-16T00:00:00Z", valid_to="2026-09-15T00:00:00Z")))
    for name, pattern, mutator in invalid_cases:
        candidate = json.loads(json.dumps(envelope))
        mutator(candidate)
        try:
            evaluate(candidate)
        except RECError as exc:
            check(pattern in str(exc), name)
        else:
            raise AssertionError(name)

    scope_case = json.loads(json.dumps(chained))
    scope_case["claims"][-1]["scope"] = {}
    try:
        evaluate(scope_case)
    except RECError as exc:
        check("expands scope" in str(exc), "scope expansion rejected")
    else:
        raise AssertionError("scope expansion rejected")

    modality_case = json.loads(json.dumps(chained))
    modality_case["claims"][-1]["modality"] = "obligation"
    try:
        evaluate(modality_case)
    except RECError as exc:
        check("modality without bridge" in str(exc), "modality escalation rejected")
    else:
        raise AssertionError("modality escalation rejected")

    modality_case["rules"][0]["modality_bridge"] = {
        "from": ["fact"], "to": "obligation", "authority": "policy-map-1"
    }
    bridged = evaluate(modality_case).witness
    check(bridged["statuses"]["delivery-blocked"] == "supported", "authorised modality bridge admitted")

    return {
        "kernel": KERNEL,
        "profile": PROFILE,
        "model": MODEL,
        "checks_passed": len(checks),
        "checks": checks,
        "scope": "Finite propositional information-flow subset; not truth proof or full REC conformance.",
    }


if __name__ == "__main__":
    print(json.dumps(run_reference_checks(), indent=2, ensure_ascii=False))
