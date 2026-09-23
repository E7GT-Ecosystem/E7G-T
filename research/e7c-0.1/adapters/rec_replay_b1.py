"""Bounded WP5 REC integration of its pinned evaluator and independent checker.

This module adds a closed typed boundary and an immutable envelope snapshot.
It delegates REC-B1 semantics to the source model, and always checks the
produced witness with the separately implemented checker before returning.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parents[3] / "packages" / "rec-0.1"
MODULE_EDITION = "E7C-REC-REPLAY-B1/0.1-provisional"
SOURCE_PINS = ("0.14-experimental-draft", "REC/0.1-proposed", "REC-B1/0.1")
ENVELOPE_KEYS = {"kernel", "profile", "model", "reasoning_id", "edition",
                 "as_of", "claims", "evidence", "rules", "query"}
CLAIM_KEYS = {"id", "proposition", "modality", "scope", "temporal_scope"}
EVIDENCE_KEYS = {"id", "claim_id", "polarity", "source_id", "source_edition",
                 "provenance_group", "scope", "valid_from", "valid_to"}
RULE_KEYS = {"id", "premises", "conclusion", "modality_bridge"}


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, PACKAGE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


evaluator = _load("rec_source_evaluator", "e7gt_rec_v0_1.py")
checker = _load("rec_independent_checker", "check_trace.py")


class BridgeError(ValueError):
    pass


@dataclass(frozen=True)
class Envelope:
    edition: str
    snapshot: bytes

    def value(self):
        return json.loads(self.snapshot)


@dataclass(frozen=True)
class CheckedTrace:
    edition: str
    envelope_sha256: str
    witness_sha256: str
    statuses: tuple[tuple[str, str], ...]
    query_status: str
    next_action: str
    provenance_groups: tuple[tuple[str, tuple[str, ...]], ...]
    incurred: tuple[str, ...]


def _shape(value: dict):
    if type(value) is not dict or set(value) != ENVELOPE_KEYS:
        raise BridgeError("envelope_shape_mismatch")
    for name, allowed, mandatory in (
        ("claims", CLAIM_KEYS, CLAIM_KEYS),
        ("evidence", EVIDENCE_KEYS, EVIDENCE_KEYS - {"valid_from", "valid_to"}),
        ("rules", RULE_KEYS, RULE_KEYS - {"modality_bridge"}),
    ):
        rows = value[name]
        if type(rows) is not list or any(type(row) is not dict or
                                         not mandatory <= set(row) or
                                         set(row) - allowed for row in rows):
            raise BridgeError(name + "_shape_mismatch")
    if type(value["query"]) is not dict or set(value["query"]) != {"claim_id", "policy"}:
        raise BridgeError("query_shape_mismatch")
    for rule in value["rules"]:
        if (type(rule["premises"]) is not list or
            any(type(p) is not dict or set(p) != {"claim_id", "requires"}
                for p in rule["premises"]) or
            type(rule["conclusion"]) is not dict or
            set(rule["conclusion"]) != {"claim_id", "polarity"} or
            ("modality_bridge" in rule and
             (type(rule["modality_bridge"]) is not dict or
              set(rule["modality_bridge"]) != {"from", "to", "authority"}))):
            raise BridgeError("rule_shape_mismatch")


def admit(value: dict) -> Envelope:
    """Check the exact selected source schema and semantic guards, then freeze."""
    _shape(value)
    if tuple(value[k] for k in ("kernel", "profile", "model")) != SOURCE_PINS:
        raise BridgeError("source_edition_mismatch")
    try:
        evaluator._validate_envelope(value)
        snapshot = evaluator.canonical_bytes(value)
    except (evaluator.RECError, TypeError, ValueError) as exc:
        raise BridgeError("source_admission_failed: " + str(exc)) from exc
    return Envelope(MODULE_EDITION, snapshot)


def replay(envelope: Envelope, witness: dict) -> CheckedTrace:
    """An independent checker must replay the *same* immutable envelope."""
    if type(envelope) is not Envelope or envelope.edition != MODULE_EDITION:
        raise BridgeError("wrong_envelope_sort")
    if type(witness) is not dict:
        raise BridgeError("witness_shape_mismatch")
    try:
        checker.check(envelope.value(), witness)
    except (checker.TraceError, KeyError, TypeError, ValueError) as exc:
        raise BridgeError("independent_replay_failed: " + str(exc)) from exc
    return CheckedTrace(
        MODULE_EDITION, witness["envelope_sha256"], witness["witness_sha256"],
        tuple(sorted(witness["statuses"].items())), witness["query"]["status"],
        witness["query"]["next_action"],
        tuple(sorted((k, tuple(v)) for k, v in
                     witness["provenance_groups_by_claim"].items())),
        ("evidence_read", "rule_closure", "independent_replay"),
    )


def execute(envelope: Envelope) -> CheckedTrace:
    if type(envelope) is not Envelope or envelope.edition != MODULE_EDITION:
        raise BridgeError("wrong_envelope_sort")
    try:
        witness = evaluator.evaluate(envelope.value()).witness
    except evaluator.RECError as exc:
        raise BridgeError("source_evaluation_failed: " + str(exc)) from exc
    return replay(envelope, witness)
