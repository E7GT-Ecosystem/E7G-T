#!/usr/bin/env python3
"""Validate and deterministically score REC-EVAL/0.1 adjudication records."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ARMS = ("ordinary", "checklist", "retrieval", "retrieval_rec")
STRATA = (
    "stale_source", "dependent_evidence", "independent_conflict",
    "semantic_scope", "temporal_scope", "modality_shift",
)
EXECUTION_STATUSES = ("completed", "timeout", "tool_error", "model_error")
COUNT_FIELDS = (
    "gold_units", "asserted_units", "correct_units", "unsupported_units",
    "scope_errors", "temporal_errors", "modality_errors", "latency_ms",
    "input_tokens", "output_tokens",
)


class ValidationError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def validate_run(doc: dict[str, Any], *, require_complete: bool = True) -> None:
    _require(doc.get("schema_version") == "rec-eval-run-v1", "unsupported schema_version")
    _require(doc.get("data_class") in {"synthetic", "pilot", "promotion"}, "invalid data_class")
    for key in ("run_id", "case_set_sha256", "source_universe_sha256", "model_contract_sha256"):
        value = doc.get(key)
        _require(isinstance(value, str) and value.strip(), f"missing {key}")
    _require(isinstance(doc.get("adjudication_blinded"), bool), "adjudication_blinded must be boolean")
    observations = doc.get("observations")
    _require(isinstance(observations, list), "observations must be an array")
    if not observations:
        _require(not require_complete, "complete run must contain observations")
        return

    seen: set[tuple[str, str, str]] = set()
    cells: dict[tuple[str, str], set[str]] = defaultdict(set)
    for index, row in enumerate(observations):
        prefix = f"observation[{index}]"
        _require(isinstance(row, dict), f"{prefix} must be an object")
        for key in ("case_id", "replicate_id", "arm", "output_sha256", "adjudication_id"):
            _require(isinstance(row.get(key), str) and row[key], f"{prefix}.{key} missing")
        arm = row["arm"]
        _require(arm in ARMS, f"{prefix}.arm invalid")
        _require(row.get("primary_stratum") in STRATA, f"{prefix}.primary_stratum invalid")
        _require(row.get("execution_status") in EXECUTION_STATUSES, f"{prefix}.execution_status invalid")
        identity = (row["case_id"], row["replicate_id"], arm)
        _require(identity not in seen, f"duplicate observation {identity}")
        seen.add(identity)
        cells[(row["case_id"], row["replicate_id"])].add(arm)
        digest = row["output_sha256"]
        _require(len(digest) == 64 and all(c in "0123456789abcdef" for c in digest), f"{prefix}.output_sha256 invalid")
        for field in COUNT_FIELDS:
            value = row.get(field)
            _require(isinstance(value, int) and not isinstance(value, bool) and value >= 0, f"{prefix}.{field} invalid")
        cost = row.get("cost_usd")
        _require(isinstance(cost, (int, float)) and not isinstance(cost, bool) and cost >= 0, f"{prefix}.cost_usd invalid")
        _require(row["correct_units"] <= row["asserted_units"], f"{prefix}: correct exceeds asserted")
        _require(row["correct_units"] <= row["gold_units"], f"{prefix}: correct exceeds gold")
        _require(row["unsupported_units"] <= row["asserted_units"], f"{prefix}: unsupported exceeds asserted")
        _require(row.get("expected_action") in {"assert", "abstain"}, f"{prefix}.expected_action invalid")
        _require(row.get("actual_action") in {"assert", "abstain"}, f"{prefix}.actual_action invalid")
        applicable = row.get("conflict_applicable")
        _require(isinstance(applicable, bool), f"{prefix}.conflict_applicable must be boolean")
        retained = row.get("conflict_retained")
        _require(retained in ({True, False} if applicable else {None}), f"{prefix}.conflict_retained inconsistent")
        trace = row.get("rec_trace_valid")
        _require(trace in ({True, False} if arm == "retrieval_rec" else {None}), f"{prefix}.rec_trace_valid inconsistent")

    if require_complete:
        for cell, arms in cells.items():
            _require(arms == set(ARMS), f"incomplete matched cell {cell}: {sorted(arms)}")
        primary_by_case = {}
        for row in observations:
            previous = primary_by_case.setdefault(row["case_id"], row["primary_stratum"])
            _require(previous == row["primary_stratum"], f"case {row['case_id']} changes primary_stratum")
        if doc["data_class"] == "promotion":
            _require(doc["adjudication_blinded"], "promotion run must use blinded adjudication")
            case_ids = {row["case_id"] for row in observations}
            _require(len(case_ids) >= 100, "promotion run requires at least 100 cases")
            for case_id in case_ids:
                replicates = {row["replicate_id"] for row in observations if row["case_id"] == case_id}
                _require(len(replicates) >= 3, f"promotion case {case_id} requires at least three replicates")
            counts = {stratum: sum(value == stratum for value in primary_by_case.values()) for stratum in STRATA}
            for stratum, count in counts.items():
                _require(count >= 15, f"promotion run requires 15 primary cases in {stratum}; got {count}")


def validate_case_set(doc: dict[str, Any], *, require_cases: bool = True) -> dict[str, dict[str, Any]]:
    _require(doc.get("schema_version") == "rec-eval-case-set-v1", "unsupported case-set schema_version")
    _require(isinstance(doc.get("case_set_id"), str) and doc["case_set_id"], "missing case_set_id")
    _require(isinstance(doc.get("source_universe_sha256"), str) and doc["source_universe_sha256"], "missing case-set source digest")
    _require(doc.get("frozen_before_execution") is True, "case set was not frozen before execution")
    cases = doc.get("cases")
    _require(isinstance(cases, list), "cases must be an array")
    _require(cases or not require_cases, "case set is empty")
    result: dict[str, dict[str, Any]] = {}
    for index, case in enumerate(cases):
        prefix = f"case[{index}]"
        _require(isinstance(case, dict), f"{prefix} must be an object")
        case_id = case.get("case_id")
        _require(isinstance(case_id, str) and case_id, f"{prefix}.case_id missing")
        _require(case_id not in result, f"duplicate case_id {case_id}")
        _require(isinstance(case.get("prompt"), str) and case["prompt"], f"{prefix}.prompt missing")
        _require(case.get("primary_stratum") in STRATA, f"{prefix}.primary_stratum invalid")
        secondary = case.get("secondary_strata")
        _require(isinstance(secondary, list) and all(v in STRATA for v in secondary), f"{prefix}.secondary_strata invalid")
        _require(len(secondary) == len(set(secondary)), f"{prefix}.secondary_strata duplicate")
        sources = case.get("available_source_refs")
        _require(isinstance(sources, list) and sources and all(isinstance(v, str) and v for v in sources), f"{prefix}.available_source_refs invalid")
        gold = case.get("gold")
        _require(isinstance(gold, dict), f"{prefix}.gold missing")
        units = gold.get("units")
        _require(isinstance(units, list) and units, f"{prefix}.gold.units empty")
        unit_ids = [unit.get("unit_id") for unit in units if isinstance(unit, dict)]
        _require(len(unit_ids) == len(units) and all(isinstance(v, str) and v for v in unit_ids), f"{prefix}.gold unit invalid")
        _require(len(unit_ids) == len(set(unit_ids)), f"{prefix}.gold unit_id duplicate")
        for unit in units:
            _require(isinstance(unit.get("description"), str) and unit["description"], f"{prefix}.gold unit description missing")
            accepted = unit.get("accepted_source_refs")
            _require(isinstance(accepted, list) and accepted and all(v in sources for v in accepted), f"{prefix}.gold unit source invalid")
        _require(gold.get("expected_action") in {"assert", "abstain"}, f"{prefix}.gold.expected_action invalid")
        _require(isinstance(gold.get("conflict_applicable"), bool), f"{prefix}.gold.conflict_applicable invalid")
        for field in ("scope_ceiling", "temporal_ceiling"):
            _require(isinstance(gold.get(field), str) and gold[field], f"{prefix}.gold.{field} missing")
        modalities = gold.get("accepted_modalities")
        _require(isinstance(modalities, list) and modalities and all(isinstance(v, str) and v for v in modalities), f"{prefix}.gold.accepted_modalities invalid")
        result[case_id] = case
    return result


def validate_run_against_case_set(run: dict[str, Any], case_set: dict[str, Any]) -> None:
    cases = validate_case_set(case_set)
    _require(run["source_universe_sha256"] == case_set["source_universe_sha256"], "run and case set source digests differ")
    for row in run["observations"]:
        _require(row["case_id"] in cases, f"run references unknown case {row['case_id']}")
        case = cases[row["case_id"]]
        gold = case["gold"]
        _require(row["gold_units"] == len(gold["units"]), f"gold_units mismatch for {row['case_id']}")
        _require(row["primary_stratum"] == case["primary_stratum"], f"primary_stratum mismatch for {row['case_id']}")
        _require(row["expected_action"] == gold["expected_action"], f"expected_action mismatch for {row['case_id']}")
        _require(row["conflict_applicable"] == gold["conflict_applicable"], f"conflict_applicable mismatch for {row['case_id']}")


def _ratio(numerator: int | float, denominator: int | float) -> float | None:
    return None if denominator == 0 else round(numerator / denominator, 6)


def _mean(values: list[int | float]) -> float | None:
    return None if not values else round(sum(values) / len(values), 6)


def _arm_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    sums = {field: sum(row[field] for row in rows) for field in COUNT_FIELDS}
    asserted = sums["asserted_units"]
    applicable = [row for row in rows if row["conflict_applicable"]]
    trace_rows = [row for row in rows if row["rec_trace_valid"] is not None]
    return {
        "observations": len(rows),
        "factual_recall": _ratio(sums["correct_units"], sums["gold_units"]),
        "asserted_precision": _ratio(sums["correct_units"], asserted),
        "unsupported_rate": _ratio(sums["unsupported_units"], asserted),
        "scope_error_rate": _ratio(sums["scope_errors"], asserted),
        "temporal_error_rate": _ratio(sums["temporal_errors"], asserted),
        "modality_error_rate": _ratio(sums["modality_errors"], asserted),
        "conflict_retention": _ratio(sum(row["conflict_retained"] is True for row in applicable), len(applicable)),
        "decision_accuracy": _ratio(sum(row["actual_action"] == row["expected_action"] for row in rows), len(rows)),
        "abstention_rate": _ratio(sum(row["actual_action"] == "abstain" for row in rows), len(rows)),
        "valid_trace_rate": _ratio(sum(row["rec_trace_valid"] is True for row in trace_rows), len(trace_rows)),
        "execution_failure_rate": _ratio(sum(row["execution_status"] != "completed" for row in rows), len(rows)),
        "mean_latency_ms": _mean([row["latency_ms"] for row in rows]),
        "mean_input_tokens": _mean([row["input_tokens"] for row in rows]),
        "mean_output_tokens": _mean([row["output_tokens"] for row in rows]),
        "mean_cost_usd": _mean([row["cost_usd"] for row in rows]),
    }


def _case_metric(row: dict[str, Any], name: str) -> float | None:
    if name == "unsupported_rate":
        return None if row["asserted_units"] == 0 else row["unsupported_units"] / row["asserted_units"]
    if name == "factual_recall":
        return None if row["gold_units"] == 0 else row["correct_units"] / row["gold_units"]
    if name == "decision_accuracy":
        return float(row["actual_action"] == row["expected_action"])
    if name == "abstention":
        return float(row["actual_action"] == "abstain")
    raise AssertionError(name)


def score_run(doc: dict[str, Any], case_set: dict[str, Any] | None = None) -> dict[str, Any]:
    validate_run(doc)
    if case_set is not None:
        validate_run_against_case_set(doc, case_set)
    _require(doc["data_class"] != "promotion" or case_set is not None, "promotion scoring requires the frozen case set")
    by_arm: dict[str, list[dict[str, Any]]] = {arm: [] for arm in ARMS}
    by_cell: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in doc["observations"]:
        by_arm[row["arm"]].append(row)
        by_cell[(row["case_id"], row["replicate_id"])][row["arm"]] = row

    paired: dict[str, list[float]] = {name: [] for name in ("unsupported_rate", "factual_recall", "decision_accuracy", "abstention")}
    for arms in by_cell.values():
        for name in paired:
            rec = _case_metric(arms["retrieval_rec"], name)
            base = _case_metric(arms["retrieval"], name)
            if rec is not None and base is not None:
                paired[name].append(rec - base)

    source_digest = hashlib.sha256(json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "schema_version": "rec-eval-score-v1",
        "source_run_sha256": source_digest,
        "run_id": doc["run_id"],
        "data_class": doc["data_class"],
        "promotion_evidence": False,
        "arms": {arm: _arm_metrics(by_arm[arm]) for arm in ARMS},
        "primary_paired_delta_retrieval_rec_minus_retrieval": {
            name: {"mean": _mean(values), "paired_cells": len(values)} for name, values in paired.items()
        },
        "interpretation_boundary": "Deterministic descriptive scores only; no uncertainty interval or promotion decision is computed.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--case-set", type=Path, help="frozen case set used to cross-check adjudication labels")
    parser.add_argument("--allow-empty", action="store_true", help="validate an empty template without scoring")
    args = parser.parse_args(argv)
    try:
        doc = json.loads(args.run.read_text(encoding="utf-8"))
        if args.allow_empty:
            validate_run(doc, require_complete=False)
            print(json.dumps({"valid": True, "complete": bool(doc["observations"])}, sort_keys=True))
        else:
            case_set = json.loads(args.case_set.read_text(encoding="utf-8")) if args.case_set else None
            print(json.dumps(score_run(doc, case_set), indent=2, sort_keys=True))
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"REC-EVAL validation error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
