"""Disposable E7C-B1 WP3-I evaluator and witness emitter.

The input and witness shapes are experimental review artifacts, not public
schemas or APIs.  This module makes no general correctness or conformance claim.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Mapping

from e7c_b1_admission import AdmissionError, validate_runtime_package
from e7c_b1_canonical import (
    CALCULUS_EDITION,
    CLAIM_CLASS,
    DYNAMIC_RULES_ID,
    JUDGEMENT_CLASS,
    OUTCOME_EXTENSION_EDITION,
    RESOURCE_POLICY_EDITION,
    STATIC_RULES_ID,
    WITNESS_EDITION,
    bind_envelope,
    bind_node_ids,
    canonical_key,
    flatten_bound_tree,
    is_success,
    outcome,
    require_canonical_json,
    resource_limit,
    validate_external_assumptions,
)
from e7c_b1_static import Checker, Diagnostic


REQUIRED_RESOURCE_FIELDS = {
    "step_bound",
    "candidate_bound",
    "ledger_entry_bound",
    "policy_edition",
}


class EvaluationInputError(ValueError):
    pass


@dataclass
class State:
    beta: dict[str, Any]
    steps: int = 0
    candidates: int = 0
    ledger: list[dict[str, Any]] = field(default_factory=list)
    last_candidate_key: str | None = None

    def progress(self) -> dict[str, Any]:
        return {
            "completed_steps": self.steps,
            "completed_candidate_checks": self.candidates,
            "completed_ledger_entries": len(self.ledger),
            "last_candidate_key": self.last_candidate_key,
            "ledger_prefix": copy.deepcopy(self.ledger),
        }

    def charge_step(self) -> bool:
        if self.steps >= self.beta["step_bound"]:
            return False
        self.steps += 1
        return True

    def charge_candidate(self) -> bool:
        if self.candidates >= self.beta["candidate_bound"]:
            return False
        self.candidates += 1
        return True

    def complete_candidate(self, key: str) -> None:
        self.last_candidate_key = key

    def append(self, atom: Mapping[str, Any], detail: Mapping[str, Any]) -> bool:
        if len(self.ledger) >= self.beta["ledger_entry_bound"]:
            return False
        self.ledger.append(
            {
                "ordinal": len(self.ledger),
                "static_atom": copy.deepcopy(dict(atom)),
                "detail": copy.deepcopy(dict(detail)),
            }
        )
        return True


def _node(term: Any, rule_id: str, pre: Mapping[str, Any], state: State,
          terminal: Mapping[str, Any], children: list[dict[str, Any]],
          charges: Mapping[str, Any], appended: list[dict[str, Any]],
          candidates: list[str]) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "rule_edition": DYNAMIC_RULES_ID,
        "term": copy.deepcopy(term),
        "pre_state": copy.deepcopy(dict(pre)),
        "completed_charges": copy.deepcopy(dict(charges)),
        "ledger_entries_appended": copy.deepcopy(appended),
        "candidate_keys_examined": list(candidates),
        "terminal_outcome": copy.deepcopy(dict(terminal)),
        "post_state": state.progress(),
        "children": children,
    }


class Evaluator:
    def __init__(self, document: Mapping[str, Any]) -> None:
        try:
            require_canonical_json(document)
        except (TypeError, ValueError, OverflowError) as error:
            raise EvaluationInputError(f"invalid canonical evaluation document: {error}") from error
        required = {
            "environment", "term", "values", "interpretation", "resource_policy",
            "pins", "external_assumptions",
        }
        if type(document) is not dict or set(document) != required:
            raise EvaluationInputError("evaluation document has an unexpected shape")
        self.document = copy.deepcopy(dict(document))
        self.environment = self.document["environment"]
        self.term = self.document["term"]
        self.values = self.document["values"]
        self.interpretation = self.document["interpretation"]
        self.beta = self.document["resource_policy"]
        if self.document["pins"] != {"outcome_extension_edition": OUTCOME_EXTENSION_EDITION}:
            raise EvaluationInputError("unsupported outcome extension edition")
        if not isinstance(self.beta, dict) or set(self.beta) != REQUIRED_RESOURCE_FIELDS:
            raise EvaluationInputError("resource policy has an unexpected shape")
        if any(type(self.beta[name]) is not int or self.beta[name] < 0 for name in (
            "step_bound", "candidate_bound", "ledger_entry_bound"
        )):
            raise EvaluationInputError("resource bounds must be non-negative integers")
        if type(self.beta["policy_edition"]) is not str or self.beta["policy_edition"] != RESOURCE_POLICY_EDITION:
            raise EvaluationInputError("unsupported resource policy edition")
        try:
            validate_external_assumptions(self.document["external_assumptions"])
        except ValueError as error:
            raise EvaluationInputError(str(error)) from error
        try:
            self.static = Checker(self.environment).check(self.term).as_dict()
        except Diagnostic as diagnostic:
            raise EvaluationInputError(
                f"{diagnostic.code} at {diagnostic.path}: {diagnostic.message}"
            ) from diagnostic
        try:
            validate_runtime_package(self.environment, self.values, self.interpretation)
        except AdmissionError as error:
            raise EvaluationInputError(f"{error.diagnostic}: {error.detail}") from error
        self.state = State(copy.deepcopy(self.beta))

    def run(self) -> dict[str, Any]:
        terminal, tree = self._eval(self.term)
        bound_tree = bind_node_ids(tree)
        derivation_nodes = flatten_bound_tree(bound_tree)
        envelope = {
            "identity": {
                "witness_edition": WITNESS_EDITION,
                "judgement_class": JUDGEMENT_CLASS,
                "claim_class": CLAIM_CLASS,
            },
            "rule_pins": {
                "calculus_edition": CALCULUS_EDITION,
                "static_rules_identity": STATIC_RULES_ID,
                "dynamic_rules_identity": DYNAMIC_RULES_ID,
                "outcome_extension_edition": self.document["pins"]["outcome_extension_edition"],
            },
            "evaluation_claim": {
                "term": copy.deepcopy(self.term),
                "static_judgement": copy.deepcopy(self.static),
                "terminal_outcome": copy.deepcopy(terminal),
                "ordered_ledger": copy.deepcopy(self.state.ledger),
                "resource_progress": self.state.progress(),
            },
            "static_inputs": {"environment": copy.deepcopy(self.environment)},
            "runtime_inputs": {
                "values": copy.deepcopy(self.values),
                "interpretation": copy.deepcopy(self.interpretation),
            },
            "resource_input": {"beta": copy.deepcopy(self.beta)},
            "derivation_record": {
                "root_node_id": bound_tree["node"]["node_id"],
                "nodes_bottom_up": derivation_nodes,
            },
            "external_assumptions": copy.deepcopy(self.document["external_assumptions"]),
        }
        witness = bind_envelope(envelope)
        return {
            "status": "evaluated",
            "terminal_outcome": copy.deepcopy(witness["evaluation_claim"]["terminal_outcome"]),
            "ordered_ledger": copy.deepcopy(self.state.ledger),
            "resource_progress": self.state.progress(),
            "witness": witness,
        }

    def _limit(self) -> dict[str, Any]:
        return resource_limit(self.beta, self.state.progress())

    def _eval(self, term: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        pre = self.state.progress()
        if not self.state.charge_step():
            terminal = self._limit()
            return terminal, _node(term, f"{term.get('tag', 'unknown')}.step_limit", pre,
                self.state, terminal, [], {"steps": 0, "candidates": 0, "ledger": 0}, [], [])
        tag = term["tag"]
        if tag == "var":
            value = copy.deepcopy(self.values[term["name"]])
            variable_type = self.environment["variables"][term["name"]]
            terminal = value if variable_type["tag"] == "outcome" else outcome("success", value)
            return terminal, _node(term, "var", pre, self.state, terminal, [],
                {"steps": 1, "candidates": 0, "ledger": 0}, [], [])

        child_terminal, child = self._eval(term["arg"])
        if not is_success(child_terminal):
            return child_terminal, _node(term, f"{tag}.propagate", pre, self.state,
                child_terminal, [child], {"steps": 1, "candidates": 0, "ledger": 0}, [], [])

        method = getattr(self, f"_eval_{tag}")
        return method(term, child_terminal["value"], pre, child)

    def _append(self, atom: Mapping[str, Any], detail: Mapping[str, Any], appended: list[dict[str, Any]]) -> bool:
        if not self.state.append(atom, detail):
            return False
        appended.append(copy.deepcopy(self.state.ledger[-1]))
        return True

    def _table(self, section: str, name: str) -> Mapping[str, Any]:
        return self.interpretation.get(section, {}).get(name, {})

    def _guard(self, record: Mapping[str, Any], capability: str, obligation: str) -> dict[str, Any] | None:
        if record["capability"] is not True:
            return outcome("unsupported", capability)
        resolution = record["obligation"]
        if resolution != "resolved":
            return outcome("undetermined", obligation)
        return None

    def _lookup_case(self, record: Mapping[str, Any], value: Any) -> Mapping[str, Any] | None:
        key = canonical_key(value)
        return next((case for case in record.get("cases", []) if canonical_key(case.get("input")) == key), None)

    def _finish(self, term: Mapping[str, Any], rule: str, pre: Mapping[str, Any], child: dict[str, Any],
                terminal: Mapping[str, Any], appended: list[dict[str, Any]], candidates: list[str]) -> tuple[dict[str, Any], dict[str, Any]]:
        return dict(terminal), _node(term, rule, pre, self.state, terminal, [child],
            {"steps": 1, "candidates": len(candidates), "ledger": len(appended)}, appended, candidates)

    def _eval_apply(self, term: Mapping[str, Any], value: Any, pre: Mapping[str, Any], child: dict[str, Any]):
        name = term["declaration"]
        decl = self.environment["maps"][name]
        record = self._table("maps", name)
        appended: list[dict[str, Any]] = []
        evidence = {"dimension": "evidence", "payload": canonical_key({
            "domain_policy": decl["domain_policy"], "failure_family": decl["failure_family"],
            "map_declaration": name, "map_edition": decl["map_edition"],
            "outcome_extension": decl["outcome_extension"],
        })}
        if not self._append(evidence, {"declaration": name, "event": "map_attempt"}, appended):
            return self._finish(term, "apply.ledger_limit", pre, child, self._limit(), appended, [])
        if decl["domain_policy"] != "total":
            partial_detail = {"declaration": name, "event": "partial_map_attempt"}
            if decl["domain_policy"] == "filtering":
                case = self._lookup_case(record, value)
                partial_detail.update({
                    "retained": copy.deepcopy(case.get("retained", [])) if case else [],
                    "excluded": copy.deepcopy(case.get("excluded", [])) if case else [],
                })
            atom = {"dimension": "partiality", "payload": canonical_key({
                "domain_policy": decl["domain_policy"], "failure_family": decl["failure_family"],
                "map_declaration": name, "map_edition": decl["map_edition"],
            })}
            if not self._append(atom, partial_detail, appended):
                return self._finish(term, "apply.ledger_limit", pre, child, self._limit(), appended, [])
        guarded = self._guard(record, f"map:{name}", f"map-domain:{name}")
        if guarded:
            return self._finish(term, "apply.guard", pre, child, guarded, appended, [])
        case = self._lookup_case(record, value)
        if case is None:
            raise EvaluationInputError(f"missing map interpretation case for {name}")
        if decl["domain_policy"] == "total" and (
            case.get("in_domain") is not True or "output" not in case
        ):
            raise EvaluationInputError(f"total map {name} lacks a target value")
        if case.get("in_domain") is not True:
            terminal = outcome("domain_error", f"outside-domain:{name}")
        elif "output" not in case:
            terminal = outcome("domain_error", f"no-target-value:{name}")
        else:
            terminal = outcome("success", case["output"])
        return self._finish(term, "apply", pre, child, terminal, appended, [])

    def _eval_view(self, term: Mapping[str, Any], value: Any, pre: Mapping[str, Any], child: dict[str, Any]):
        name = term["declaration"]
        decl = self.environment["views"][name]
        record = self._table("views", name)
        appended: list[dict[str, Any]] = []
        view_detail = {
            "declaration": name,
            "event": "view",
            "preserved_observations": sorted(set(decl["preserved_observations"])),
            "excluded_observations": sorted(set(decl["excluded_observations"])),
            "quotient_relation": decl["quotient_relation"],
        }
        if not self._append({"dimension": "inquiry", "payload": decl["inquiry"]},
                            view_detail, appended):
            return self._finish(term, "view.ledger_limit", pre, child, self._limit(), appended, [])
        if decl["kind"] == "projection":
            atom = {"dimension": "loss", "payload": canonical_key({
                "excluded": sorted(set(decl["excluded_observations"])),
                "preserved": sorted(set(decl["preserved_observations"])),
                "quotient_relation": decl["quotient_relation"],
            })}
            if not self._append(atom, {"declaration": name, "event": "projection_loss"}, appended):
                return self._finish(term, "view.ledger_limit", pre, child, self._limit(), appended, [])
        if not self._append({"dimension": "alternatives", "payload": decl["reconstruction_obligation"]},
                            {"declaration": name, "event": "reconstruction_boundary"}, appended):
            return self._finish(term, "view.ledger_limit", pre, child, self._limit(), appended, [])
        guarded = self._guard(record, f"view:{name}", f"view:{name}")
        if guarded:
            return self._finish(term, "view.guard", pre, child, guarded, appended, [])
        case = self._lookup_case(record, value)
        if case is None or "output" not in case:
            raise EvaluationInputError(f"missing view interpretation case for {name}")
        terminal = outcome("success", {
            "kind": decl["kind"], "declaration": name, "representation": case["output"],
            "source_return_token": copy.deepcopy(value) if decl["kind"] == "source_preserving" else None,
        })
        return self._finish(term, "view", pre, child, terminal, appended, [])

    def _eval_restrict(self, term: Mapping[str, Any], value: Any, pre: Mapping[str, Any], child: dict[str, Any]):
        name = term["declaration"]
        record = self._table("restrictions", name)
        appended: list[dict[str, Any]] = []
        if not self._append(
            {"dimension": "alternatives", "payload": name},
            {"declaration": name, "event": "restriction_partition"},
            appended,
        ):
            return self._finish(term, "restrict.ledger_limit", pre, child, self._limit(), appended, [])
        guarded = self._guard(record, f"restriction:{name}", f"restriction:{name}")
        if guarded:
            return self._finish(term, "restrict.guard", pre, child, guarded, appended, [])
        ordered = sorted(value, key=canonical_key)
        retained: list[Any] = []
        excluded: list[Any] = []
        retained_keys = set(record["retained_keys"])
        candidates: list[str] = []
        for item in ordered:
            key = canonical_key(item)
            if not self.state.charge_candidate():
                return self._finish(term, "restrict.candidate_limit", pre, child, self._limit(), appended, candidates)
            if key in retained_keys:
                retained.append(item)
            else:
                excluded.append(item)
            self.state.complete_candidate(key)
            candidates.append(key)
        detail = {"declaration": name, "retained": retained, "excluded": excluded}
        self.state.ledger[-1]["detail"] = copy.deepcopy(detail)
        appended[-1]["detail"] = copy.deepcopy(detail)
        return self._finish(term, "restrict", pre, child, outcome("success", retained), appended, candidates)

    def _eval_reconstruct(self, term: Mapping[str, Any], value: Any, pre: Mapping[str, Any], child: dict[str, Any]):
        name = term["declaration"]
        record = self._table("reconstructions", name)
        appended: list[dict[str, Any]] = []
        candidates: list[str] = []
        for atom, event in (
            ({"dimension": "resources", "payload": term["resource_policy"]}, "resource_reliance"),
            ({"dimension": "alternatives", "payload": name}, "fibre_alternatives"),
        ):
            if not self._append(atom, {"declaration": name, "event": event}, appended):
                return self._finish(term, "reconstruct.ledger_limit", pre, child, self._limit(), appended, candidates)
        guarded = self._guard(record, f"enumeration:{name}", f"reconstruction:{name}")
        if guarded:
            return self._finish(term, "reconstruct.guard", pre, child, guarded, appended, candidates)
        for obligation in ("carrier_finite", "equality_resolved", "constraint_resolved"):
            if record[obligation] is not True:
                return self._finish(term, "reconstruct.undetermined", pre, child,
                    outcome("undetermined", f"{obligation}:{name}"), appended, candidates)
        carrier = record["carrier"]
        target = value["representation"]
        fibre: list[Any] = []
        view_record = self._table("views", self.environment["reconstructions"][name]["view_policy"])
        for candidate in carrier:
            key = canonical_key(candidate)
            if not self.state.charge_candidate():
                return self._finish(term, "reconstruct.candidate_limit", pre, child, self._limit(), appended, candidates)
            case = self._lookup_case(view_record, candidate)
            if case is None or "output" not in case:
                raise EvaluationInputError(
                    f"missing reconstruction comparison for candidate {key}"
                )
            if canonical_key(case["output"]) == canonical_key(target):
                fibre.append(copy.deepcopy(candidate))
            self.state.complete_candidate(key)
            candidates.append(key)
        return self._finish(term, "reconstruct", pre, child, outcome("success", fibre), appended, candidates)

    def _eval_classify(self, term: Mapping[str, Any], value: Any, pre: Mapping[str, Any], child: dict[str, Any]):
        name = term["declaration"]
        record = self._table("criteria", name)
        appended: list[dict[str, Any]] = []
        if not self._append({"dimension": "inquiry", "payload": name},
                            {"declaration": name, "event": "classification"}, appended):
            return self._finish(term, "classify.ledger_limit", pre, child, self._limit(), appended, [])
        guarded = self._guard(record, f"criterion:{name}", f"criterion:{name}")
        if guarded:
            return self._finish(term, "classify.guard", pre, child, guarded, appended, [])
        classes: dict[str, dict[str, Any]] = {}
        candidates: list[str] = []
        for item in sorted(value, key=canonical_key):
            key = canonical_key(item)
            if not self.state.charge_candidate():
                return self._finish(term, "classify.candidate_limit", pre, child, self._limit(), appended, candidates)
            case = self._lookup_case(record, item)
            if case is None:
                raise EvaluationInputError(f"missing criterion interpretation case for {name}")
            label = canonical_key(case["output"])
            classes.setdefault(label, {"criterion_value": case["output"], "members": []})["members"].append(item)
            self.state.complete_candidate(key)
            candidates.append(key)
        terminal = outcome("success", [classes[key] for key in sorted(classes)])
        return self._finish(term, "classify", pre, child, terminal, appended, candidates)


def evaluate(document: Mapping[str, Any]) -> dict[str, Any]:
    try:
        return Evaluator(document).run()
    except EvaluationInputError:
        raise
    except (AdmissionError, Diagnostic, KeyError, TypeError, ValueError, OverflowError, RecursionError) as error:
        raise EvaluationInputError(f"invalid evaluation document: {error}") from error
