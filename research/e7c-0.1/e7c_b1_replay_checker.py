"""Independent replay checker for disposable E7C-B1 WP3-I witnesses.

This module does not import the evaluator.  It separately implements the B1
dynamic rules and treats the supplied derivation record as an untrusted claim.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Mapping

from e7c_b1_admission import AdmissionError, validate_runtime_package
from e7c_b1_canonical import (
    CALCULUS_EDITION,
    CLAIM_CLASS,
    DIGEST_EDITION,
    DYNAMIC_RULES_ID,
    ENCODING_EDITION,
    GROUP_ORDER,
    OUTCOME_EXTENSION_EDITION,
    STATIC_RULES_ID,
    WITNESS_EDITION,
    bind_node_ids,
    canonical_key,
    digest,
    flatten_bound_tree,
    group_digest_payload,
    is_success,
    node_digest_payload,
    outcome,
    resource_limit,
)
from e7c_b1_static import Checker, Diagnostic


class ReplayReject(Exception):
    def __init__(self, diagnostic: str, detail: str = "") -> None:
        super().__init__(detail)
        self.diagnostic = diagnostic
        self.detail = detail


@dataclass
class ReplayState:
    beta: dict[str, Any]
    steps: int = 0
    candidates: int = 0
    entries: list[dict[str, Any]] = field(default_factory=list)
    last_key: str | None = None

    def snapshot(self) -> dict[str, Any]:
        return {
            "completed_steps": self.steps,
            "completed_candidate_checks": self.candidates,
            "completed_ledger_entries": len(self.entries),
            "last_candidate_key": self.last_key,
            "ledger_prefix": copy.deepcopy(self.entries),
        }

    def take_step(self) -> bool:
        if self.steps == self.beta["step_bound"]:
            return False
        self.steps += 1
        return True

    def take_candidate(self) -> bool:
        if self.candidates == self.beta["candidate_bound"]:
            return False
        self.candidates += 1
        return True

    def complete_candidate(self, key: str) -> None:
        self.last_key = key

    def add_entry(self, atom: Mapping[str, Any], detail: Mapping[str, Any]) -> bool:
        if len(self.entries) == self.beta["ledger_entry_bound"]:
            return False
        self.entries.append({
            "ordinal": len(self.entries),
            "static_atom": copy.deepcopy(dict(atom)),
            "detail": copy.deepcopy(dict(detail)),
        })
        return True


def _replay_node(term: Any, rule: str, pre: Mapping[str, Any], state: ReplayState,
                 terminal: Mapping[str, Any], children: list[dict[str, Any]],
                 step_count: int, additions: list[dict[str, Any]],
                 keys: list[str]) -> dict[str, Any]:
    return {
        "rule_id": rule,
        "rule_edition": DYNAMIC_RULES_ID,
        "term": copy.deepcopy(term),
        "pre_state": copy.deepcopy(dict(pre)),
        "completed_charges": {
            "steps": step_count,
            "candidates": len(keys),
            "ledger": len(additions),
        },
        "ledger_entries_appended": copy.deepcopy(additions),
        "candidate_keys_examined": list(keys),
        "terminal_outcome": copy.deepcopy(dict(terminal)),
        "post_state": state.snapshot(),
        "children": children,
    }


class ReplayMachine:
    """A rule engine intentionally separate from ``Evaluator``."""

    def __init__(self, environment: Mapping[str, Any], values: Mapping[str, Any],
                 interpretation: Mapping[str, Any], beta: Mapping[str, Any]) -> None:
        self.env = copy.deepcopy(dict(environment))
        self.values = copy.deepcopy(dict(values))
        self.model = copy.deepcopy(dict(interpretation))
        self.state = ReplayState(copy.deepcopy(dict(beta)))

    def limit(self) -> dict[str, Any]:
        return resource_limit(self.state.beta, self.state.snapshot())

    def table(self, section: str, name: str) -> Mapping[str, Any]:
        return self.model.get(section, {}).get(name, {})

    @staticmethod
    def table_case(record: Mapping[str, Any], value: Any) -> Mapping[str, Any] | None:
        wanted = canonical_key(value)
        for case in record.get("cases", []):
            if canonical_key(case.get("input")) == wanted:
                return case
        return None

    @staticmethod
    def guard(record: Mapping[str, Any], capability: str, obligation: str) -> dict[str, Any] | None:
        if record["capability"] is not True:
            return outcome("unsupported", capability)
        if record["obligation"] != "resolved":
            return outcome("undetermined", obligation)
        return None

    def append(self, atom: Mapping[str, Any], detail: Mapping[str, Any], additions: list[dict[str, Any]]) -> bool:
        if not self.state.add_entry(atom, detail):
            return False
        additions.append(copy.deepcopy(self.state.entries[-1]))
        return True

    def finish(self, term: Mapping[str, Any], rule: str, pre: Mapping[str, Any],
               child: dict[str, Any], terminal: Mapping[str, Any],
               additions: list[dict[str, Any]], keys: list[str]):
        return dict(terminal), _replay_node(
            term, rule, pre, self.state, terminal, [child], 1, additions, keys
        )

    def execute(self, term: Mapping[str, Any]):
        pre = self.state.snapshot()
        if not self.state.take_step():
            terminal = self.limit()
            return terminal, _replay_node(
                term, f"{term.get('tag', 'unknown')}.step_limit", pre, self.state,
                terminal, [], 0, [], []
            )
        tag = term["tag"]
        if tag == "var":
            bound = copy.deepcopy(self.values[term["name"]])
            terminal = bound if self.env["variables"][term["name"]]["tag"] == "outcome" else outcome("success", bound)
            return terminal, _replay_node(term, "var", pre, self.state, terminal, [], 1, [], [])
        child_outcome, child = self.execute(term["arg"])
        if not is_success(child_outcome):
            return child_outcome, _replay_node(
                term, f"{tag}.propagate", pre, self.state, child_outcome,
                [child], 1, [], []
            )
        handlers = {
            "apply": self.apply,
            "view": self.view,
            "restrict": self.restrict,
            "reconstruct": self.reconstruct,
            "classify": self.classify,
        }
        return handlers[tag](term, child_outcome["value"], pre, child)

    def apply(self, term, value, pre, child):
        name = term["declaration"]
        declaration = self.env["maps"][name]
        record = self.table("maps", name)
        additions: list[dict[str, Any]] = []
        atom = {"dimension": "evidence", "payload": canonical_key({
            "domain_policy": declaration["domain_policy"],
            "failure_family": declaration["failure_family"],
            "map_declaration": name,
            "map_edition": declaration["map_edition"],
            "outcome_extension": declaration["outcome_extension"],
        })}
        if not self.append(atom, {"declaration": name, "event": "map_attempt"}, additions):
            return self.finish(term, "apply.ledger_limit", pre, child, self.limit(), additions, [])
        if declaration["domain_policy"] != "total":
            partial_detail = {"declaration": name, "event": "partial_map_attempt"}
            if declaration["domain_policy"] == "filtering":
                case = self.table_case(record, value)
                partial_detail.update({
                    "retained": copy.deepcopy(case.get("retained", [])) if case else [],
                    "excluded": copy.deepcopy(case.get("excluded", [])) if case else [],
                })
            partiality = {"dimension": "partiality", "payload": canonical_key({
                "domain_policy": declaration["domain_policy"],
                "failure_family": declaration["failure_family"],
                "map_declaration": name,
                "map_edition": declaration["map_edition"],
            })}
            if not self.append(partiality, partial_detail, additions):
                return self.finish(term, "apply.ledger_limit", pre, child, self.limit(), additions, [])
        stopped = self.guard(record, f"map:{name}", f"map-domain:{name}")
        if stopped:
            return self.finish(term, "apply.guard", pre, child, stopped, additions, [])
        case = self.table_case(record, value)
        if case is None:
            raise ReplayReject("missing_replay_material", f"map case {name}")
        if declaration["domain_policy"] == "total" and (
            case.get("in_domain") is not True or "output" not in case
        ):
            raise ReplayReject("missing_replay_material", f"total map target {name}")
        if case.get("in_domain") is not True:
            terminal = outcome("domain_error", f"outside-domain:{name}")
        elif "output" not in case:
            terminal = outcome("domain_error", f"no-target-value:{name}")
        else:
            terminal = outcome("success", case["output"])
        return self.finish(term, "apply", pre, child, terminal, additions, [])

    def view(self, term, value, pre, child):
        name = term["declaration"]
        declaration = self.env["views"][name]
        additions: list[dict[str, Any]] = []
        view_detail = {
            "declaration": name,
            "event": "view",
            "preserved_observations": sorted(set(declaration["preserved_observations"])),
            "excluded_observations": sorted(set(declaration["excluded_observations"])),
            "quotient_relation": declaration["quotient_relation"],
        }
        if not self.append({"dimension": "inquiry", "payload": declaration["inquiry"]},
                           view_detail, additions):
            return self.finish(term, "view.ledger_limit", pre, child, self.limit(), additions, [])
        if declaration["kind"] == "projection":
            atom = {"dimension": "loss", "payload": canonical_key({
                "excluded": sorted(set(declaration["excluded_observations"])),
                "preserved": sorted(set(declaration["preserved_observations"])),
                "quotient_relation": declaration["quotient_relation"],
            })}
            if not self.append(atom, {"declaration": name, "event": "projection_loss"}, additions):
                return self.finish(term, "view.ledger_limit", pre, child, self.limit(), additions, [])
        if not self.append(
            {"dimension": "alternatives", "payload": declaration["reconstruction_obligation"]},
            {"declaration": name, "event": "reconstruction_boundary"}, additions
        ):
            return self.finish(term, "view.ledger_limit", pre, child, self.limit(), additions, [])
        record = self.table("views", name)
        stopped = self.guard(record, f"view:{name}", f"view:{name}")
        if stopped:
            return self.finish(term, "view.guard", pre, child, stopped, additions, [])
        case = self.table_case(record, value)
        if case is None or "output" not in case:
            raise ReplayReject("missing_replay_material", f"view case {name}")
        terminal = outcome("success", {
            "kind": declaration["kind"],
            "declaration": name,
            "representation": case["output"],
            "source_return_token": copy.deepcopy(value) if declaration["kind"] == "source_preserving" else None,
        })
        return self.finish(term, "view", pre, child, terminal, additions, [])

    def restrict(self, term, value, pre, child):
        name = term["declaration"]
        record = self.table("restrictions", name)
        additions: list[dict[str, Any]] = []
        if not self.append(
            {"dimension": "alternatives", "payload": name},
            {"declaration": name, "event": "restriction_partition"}, additions
        ):
            return self.finish(term, "restrict.ledger_limit", pre, child, self.limit(), additions, [])
        stopped = self.guard(record, f"restriction:{name}", f"restriction:{name}")
        if stopped:
            return self.finish(term, "restrict.guard", pre, child, stopped, additions, [])
        retained_keys = set(record["retained_keys"])
        ordered = sorted(value, key=canonical_key)
        retained: list[Any] = []
        excluded: list[Any] = []
        keys: list[str] = []
        for item in ordered:
            key = canonical_key(item)
            if not self.state.take_candidate():
                return self.finish(term, "restrict.candidate_limit", pre, child, self.limit(), additions, keys)
            if key in retained_keys:
                retained.append(item)
            else:
                excluded.append(item)
            self.state.complete_candidate(key)
            keys.append(key)
        detail = {"declaration": name, "retained": retained, "excluded": excluded}
        self.state.entries[-1]["detail"] = copy.deepcopy(detail)
        additions[-1]["detail"] = copy.deepcopy(detail)
        return self.finish(term, "restrict", pre, child, outcome("success", retained), additions, keys)

    def reconstruct(self, term, value, pre, child):
        name = term["declaration"]
        record = self.table("reconstructions", name)
        additions: list[dict[str, Any]] = []
        keys: list[str] = []
        events = (
            ({"dimension": "resources", "payload": term["resource_policy"]}, "resource_reliance"),
            ({"dimension": "alternatives", "payload": name}, "fibre_alternatives"),
        )
        for atom, event in events:
            if not self.append(atom, {"declaration": name, "event": event}, additions):
                return self.finish(term, "reconstruct.ledger_limit", pre, child, self.limit(), additions, keys)
        stopped = self.guard(record, f"enumeration:{name}", f"reconstruction:{name}")
        if stopped:
            return self.finish(term, "reconstruct.guard", pre, child, stopped, additions, keys)
        for obligation in ("carrier_finite", "equality_resolved", "constraint_resolved"):
            if record[obligation] is not True:
                return self.finish(term, "reconstruct.undetermined", pre, child,
                                   outcome("undetermined", f"{obligation}:{name}"), additions, keys)
        fibre: list[Any] = []
        target = value["representation"]
        view_name = self.env["reconstructions"][name]["view_policy"]
        view_table = self.table("views", view_name)
        for candidate in record["carrier"]:
            key = canonical_key(candidate)
            if not self.state.take_candidate():
                return self.finish(term, "reconstruct.candidate_limit", pre, child, self.limit(), additions, keys)
            case = self.table_case(view_table, candidate)
            if case is None or "output" not in case:
                raise ReplayReject(
                    "missing_replay_material", f"reconstruction comparison {key}"
                )
            if canonical_key(case["output"]) == canonical_key(target):
                fibre.append(copy.deepcopy(candidate))
            self.state.complete_candidate(key)
            keys.append(key)
        return self.finish(term, "reconstruct", pre, child, outcome("success", fibre), additions, keys)

    def classify(self, term, value, pre, child):
        name = term["declaration"]
        additions: list[dict[str, Any]] = []
        if not self.append({"dimension": "inquiry", "payload": name},
                           {"declaration": name, "event": "classification"}, additions):
            return self.finish(term, "classify.ledger_limit", pre, child, self.limit(), additions, [])
        record = self.table("criteria", name)
        stopped = self.guard(record, f"criterion:{name}", f"criterion:{name}")
        if stopped:
            return self.finish(term, "classify.guard", pre, child, stopped, additions, [])
        classes: dict[str, dict[str, Any]] = {}
        keys: list[str] = []
        for item in sorted(value, key=canonical_key):
            key = canonical_key(item)
            if not self.state.take_candidate():
                return self.finish(term, "classify.candidate_limit", pre, child, self.limit(), additions, keys)
            case = self.table_case(record, item)
            if case is None:
                raise ReplayReject("missing_replay_material", f"criterion case {name}")
            label = canonical_key(case["output"])
            classes.setdefault(label, {"criterion_value": case["output"], "members": []})["members"].append(item)
            self.state.complete_candidate(key)
            keys.append(key)
        return self.finish(term, "classify", pre, child,
            outcome("success", [classes[key] for key in sorted(classes)]), additions, keys)


EXPECTED_TOP_LEVEL = set(GROUP_ORDER) | {"integrity"}
EXPECTED_GROUP_KEYS = {
    "identity": {"witness_edition", "judgement_class", "claim_class", "witness_identifier"},
    "rule_pins": {
        "calculus_edition", "static_rules_identity", "dynamic_rules_identity",
        "outcome_extension_edition",
    },
    "evaluation_claim": {
        "term", "static_judgement", "terminal_outcome", "ordered_ledger",
        "resource_progress",
    },
    "static_inputs": {"environment"},
    "runtime_inputs": {"values", "interpretation"},
    "resource_input": {"beta"},
    "derivation_record": {"root_node_id", "nodes_bottom_up"},
    "external_assumptions": {
        "source_references", "authority_asserted", "scope", "time", "modality",
        "model_edition", "policy_labels",
    },
    "integrity": {"encoding_edition", "digest_edition", "group_digests", "root_digest"},
}


def _require_shape(witness: Any) -> Mapping[str, Any]:
    if not isinstance(witness, Mapping) or set(witness) != EXPECTED_TOP_LEVEL:
        raise ReplayReject("malformed_witness", "unexpected envelope groups")
    for name in EXPECTED_TOP_LEVEL:
        if not isinstance(witness[name], Mapping):
            raise ReplayReject("malformed_witness", f"group {name} is not an object")
        missing = EXPECTED_GROUP_KEYS[name] - set(witness[name])
        if missing:
            raise ReplayReject("missing_replay_material", f"missing fields in group {name}")
        if set(witness[name]) != EXPECTED_GROUP_KEYS[name]:
            raise ReplayReject("malformed_witness", f"unexpected fields in group {name}")
    return witness


def _verify_integrity(witness: Mapping[str, Any]) -> None:
    identity = witness["identity"]
    if identity.get("witness_edition") != WITNESS_EDITION:
        raise ReplayReject("unknown_witness_edition")
    if identity.get("claim_class") != CLAIM_CLASS:
        raise ReplayReject("authority_claim_escalation")
    integrity = witness["integrity"]
    if integrity.get("encoding_edition") != ENCODING_EDITION or integrity.get("digest_edition") != DIGEST_EDITION:
        raise ReplayReject("edition_mismatch", "encoding or digest edition")
    computed_groups = [
        {"group_name": name, "group_digest": digest(group_digest_payload(name, witness[name]))}
        for name in GROUP_ORDER
    ]
    if integrity.get("group_digests") != computed_groups:
        raise ReplayReject("digest_mismatch", "group digest mismatch")
    root_payload = {
        "encoding_edition": ENCODING_EDITION,
        "digest_edition": DIGEST_EDITION,
        "group_digests": computed_groups,
    }
    root = digest(root_payload)
    if integrity.get("root_digest") != root:
        raise ReplayReject("digest_mismatch", "root digest mismatch")
    identifier = f"{WITNESS_EDITION}:{root}"
    if identity.get("witness_identifier") != identifier:
        raise ReplayReject("identity_mismatch", "top-level witness identifier")
    terminal = witness["evaluation_claim"].get("terminal_outcome", {})
    if terminal.get("tag") == "success" and terminal.get("optional_witness") != identifier:
        raise ReplayReject("identity_mismatch", "nested optional witness")


def _verify_nodes(witness: Mapping[str, Any]) -> None:
    record = witness["derivation_record"]
    nodes = record.get("nodes_bottom_up")
    if not isinstance(nodes, list) or not nodes:
        raise ReplayReject("missing_replay_material", "derivation nodes")
    by_id: dict[str, Mapping[str, Any]] = {}
    positions: dict[str, int] = {}
    for position, node in enumerate(nodes):
        if not isinstance(node, Mapping) or not isinstance(node.get("node_id"), str):
            raise ReplayReject("malformed_witness", "derivation node")
        node_id = node["node_id"]
        if node_id in by_id:
            raise ReplayReject("malformed_witness", "duplicate derivation node identifier")
        if not isinstance(node.get("child_node_ids"), list) or not all(
            isinstance(child, str) for child in node["child_node_ids"]
        ):
            raise ReplayReject("malformed_witness", "derivation child identifiers")
        by_id[node_id] = node
        positions[node_id] = position
    root = record.get("root_node_id")
    if root != nodes[-1]["node_id"] or root not in by_id:
        raise ReplayReject("identity_mismatch", "root node identity")
    for node_id, node in by_id.items():
        for child in node["child_node_ids"]:
            if child not in by_id:
                raise ReplayReject("missing_replay_material", "dangling derivation child")
            if positions[child] >= positions[node_id]:
                raise ReplayReject("derivation_order_mismatch", "child is not earlier in bottom-up order")
    reachable: set[str] = set()
    active: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in active:
            raise ReplayReject("derivation_order_mismatch", "derivation cycle")
        if node_id in reachable:
            return
        active.add(node_id)
        for child in by_id[node_id]["child_node_ids"]:
            visit(child)
        active.remove(node_id)
        reachable.add(node_id)

    visit(root)
    if reachable != set(by_id):
        raise ReplayReject("malformed_witness", "orphan derivation node")
    for node in nodes:
        if node["node_id"] != digest(node_digest_payload(node)):
            raise ReplayReject("digest_mismatch", "node identity")


def _strip_witness_binding(terminal: Any) -> Any:
    value = copy.deepcopy(terminal)
    if isinstance(value, dict) and value.get("tag") == "success":
        value["optional_witness"] = None
    return value


def check_witness(witness: Any, resolver: Mapping[str, bytes] | None = None) -> dict[str, Any]:
    """Replay one complete inline witness. ``resolver`` is reserved for digests."""
    try:
        envelope = _require_shape(witness)
        _verify_integrity(envelope)
        _verify_nodes(envelope)
        pins = envelope["rule_pins"]
        expected_pins = {
            "calculus_edition": CALCULUS_EDITION,
            "static_rules_identity": STATIC_RULES_ID,
            "dynamic_rules_identity": DYNAMIC_RULES_ID,
            "outcome_extension_edition": OUTCOME_EXTENSION_EDITION,
        }
        if any(pins.get(name) != value for name, value in expected_pins.items()):
            raise ReplayReject("edition_mismatch", "rule pins")
        try:
            environment = envelope["static_inputs"]["environment"]
            runtime = envelope["runtime_inputs"]
            values = runtime["values"]
            interpretation = runtime["interpretation"]
            beta = envelope["resource_input"]["beta"]
            term = envelope["evaluation_claim"]["term"]
        except (KeyError, TypeError):
            raise ReplayReject("missing_replay_material") from None
        if not isinstance(beta, Mapping) or set(beta) != {
            "step_bound", "candidate_bound", "ledger_entry_bound", "policy_edition"
        }:
            raise ReplayReject("malformed_witness", "resource policy shape")
        if any(not isinstance(beta[name], int) or beta[name] < 0 for name in (
            "step_bound", "candidate_bound", "ledger_entry_bound"
        )):
            raise ReplayReject("malformed_witness", "resource bounds")
        try:
            static = Checker(environment).check(term).as_dict()
        except Diagnostic as diagnostic:
            raise ReplayReject("static_judgement_mismatch", diagnostic.code) from diagnostic
        claim = envelope["evaluation_claim"]
        if static != claim.get("static_judgement"):
            raise ReplayReject("static_judgement_mismatch")
        try:
            validate_runtime_package(environment, values, interpretation)
        except AdmissionError as error:
            raise ReplayReject(error.diagnostic, error.detail) from error
        machine = ReplayMachine(environment, values, interpretation, beta)
        terminal, tree = machine.execute(term)
        if terminal != _strip_witness_binding(claim.get("terminal_outcome")):
            raise ReplayReject("outcome_mismatch")
        if machine.state.entries != claim.get("ordered_ledger"):
            raise ReplayReject("ledger_mismatch")
        if machine.state.snapshot() != claim.get("resource_progress"):
            raise ReplayReject("resource_accounting_mismatch")
        replay_tree = bind_node_ids(tree)
        replay_nodes = flatten_bound_tree(replay_tree)
        if replay_nodes != envelope["derivation_record"].get("nodes_bottom_up"):
            raise ReplayReject("derivation_order_mismatch")
        if replay_tree["node"]["node_id"] != envelope["derivation_record"].get("root_node_id"):
            raise ReplayReject("identity_mismatch", "replayed root node")
        return {
            "status": "accepted",
            "claim": CLAIM_CLASS,
            "witness_identifier": envelope["identity"]["witness_identifier"],
        }
    except ReplayReject as rejection:
        return {
            "status": "rejected",
            "diagnostic": rejection.diagnostic,
            "detail": rejection.detail,
        }
    except (KeyError, TypeError, ValueError) as error:
        return {
            "status": "rejected",
            "diagnostic": "malformed_witness",
            "detail": str(error),
        }
