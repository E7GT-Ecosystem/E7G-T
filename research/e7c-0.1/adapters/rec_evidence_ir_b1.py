"""Independent finite REC evidence-only interpretation, v0.14/REC-B1.

This selected rule does not interpret REC rule closure or source authority.
"""

from dataclasses import dataclass
from datetime import datetime, timezone


EDITION = "E7C-REC-EVIDENCE-B1/0.1-provisional"
SOURCE = ("0.14-experimental-draft", "REC/0.1-proposed", "REC-B1/0.1")


class Unsupported(ValueError):
    pass


@dataclass(frozen=True)
class EvidenceRow:
    identity: str
    polarity: str
    provenance: str
    valid_from: str | None
    valid_to: str | None


@dataclass(frozen=True)
class Query:
    edition: str
    claim_id: str
    policy: str
    as_of: str
    rows: tuple[EvidenceRow, ...]


@dataclass(frozen=True)
class Observation:
    outcome: str
    status: str | None
    action: str | None
    admitted: tuple[str, ...]
    stale: tuple[str, ...]
    provenance: tuple[str, ...]
    progress: int


def _instant(text: str) -> datetime:
    if not isinstance(text, str):
        raise Unsupported("invalid_time")
    try:
        result = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise Unsupported("invalid_time") from exc
    if result.tzinfo is None:
        raise Unsupported("unqualified_time")
    return result.astimezone(timezone.utc)


def admit(doc: dict) -> Query:
    """A source envelope subset: one claim, no rules, valid scoped evidence."""
    if not isinstance(doc, dict) or tuple(doc.get(x) for x in ("kernel", "profile", "model")) != SOURCE:
        raise Unsupported("edition")
    claims, evidence = doc.get("claims"), doc.get("evidence")
    if not isinstance(claims, list) or len(claims) != 1 or not isinstance(evidence, list) or doc.get("rules") != []:
        raise Unsupported("one_claim_no_rules")
    claim = claims[0]
    query = doc.get("query")
    if not isinstance(claim, dict) or not isinstance(query, dict) or query.get("claim_id") != claim.get("id"):
        raise Unsupported("query_claim")
    if query.get("policy") not in ("report", "rely_if_supported_only"):
        raise Unsupported("policy")
    if not isinstance(claim.get("scope"), dict) or not isinstance(claim.get("id"), str) or not claim["id"]:
        raise Unsupported("claim_scope")
    _instant(doc.get("as_of"))
    seen, rows = set(), []
    for item in evidence:
        if not isinstance(item, dict) or item.get("claim_id") != claim["id"] or item.get("polarity") not in ("support", "refute"):
            raise Unsupported("evidence_reference")
        identity, provenance = item.get("id"), item.get("provenance_group")
        if not isinstance(identity, str) or not identity or identity in seen or not isinstance(provenance, str) or not provenance:
            raise Unsupported("evidence_identity")
        seen.add(identity)
        scope = item.get("scope")
        if not isinstance(scope, dict) or any(scope.get(k) != v for k, v in claim["scope"].items()):
            raise Unsupported("scope_expansion")
        start, end = item.get("valid_from"), item.get("valid_to")
        if start is not None:
            _instant(start)
        if end is not None:
            _instant(end)
        if start is not None and end is not None and _instant(start) > _instant(end):
            raise Unsupported("invalid_interval")
        rows.append(EvidenceRow(identity, item["polarity"], provenance, start, end))
    return Query(EDITION, claim["id"], query["policy"], doc["as_of"],
                 tuple(sorted(rows, key=lambda row: row.identity)))


def evaluate(query: Query, max_visits: int) -> Observation:
    if type(query) is not Query or query.edition != EDITION or type(max_visits) is not int or max_visits < 0:
        raise Unsupported("evaluation_sort")
    point = _instant(query.as_of)
    admitted, stale, provenance = [], [], set()
    positive = negative = False
    for count, row in enumerate(query.rows):
        if count >= max_visits:
            return Observation("resource_limit", None, None, tuple(admitted), tuple(stale),
                               tuple(sorted(provenance)), count)
        if ((row.valid_from is not None and point < _instant(row.valid_from)) or
            (row.valid_to is not None and point > _instant(row.valid_to))):
            stale.append(row.identity)
            continue
        admitted.append(row.identity)
        provenance.add(row.provenance)
        positive |= row.polarity == "support"
        negative |= row.polarity == "refute"
    status = {(False, False): "neither", (True, False): "supported",
              (False, True): "refuted", (True, True): "both"}[(positive, negative)]
    action = ("report_status" if query.policy == "report" else {
        "neither": "seek_evidence_or_abstain", "supported": "rely_within_declared_scope",
        "refuted": "do_not_rely", "both": "resolve_conflict_or_abstain"}[status])
    return Observation("success", status, action, tuple(admitted), tuple(stale),
                       tuple(sorted(provenance)), len(query.rows))
