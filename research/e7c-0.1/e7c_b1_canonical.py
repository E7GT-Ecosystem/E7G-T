"""Canonical data helpers for the disposable E7C-B1 WP3-I package.

This module contains encoding and immutable-data utilities only.  The evaluator
and replay checker deliberately do not share evaluation control flow.
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Mapping


ENCODING_EDITION = "e7c-b1-canonical-json-0.1"
DIGEST_EDITION = "sha256-0.1"
WITNESS_EDITION = "e7c-b1-witness-0.1-experimental"
CALCULUS_EDITION = "E7C-B1/0.1"
STATIC_RULES_ID = "E7C-WP2/B1@ed2a49de"
DYNAMIC_RULES_ID = "E7C-WP3-S/B1@bae84fb7"
CLAIM_CLASS = "bounded_derivation_replay"
OUTCOME_EXTENSION_EDITION = "core-1"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_key(value: Any) -> str:
    return canonical_bytes(value).decode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def outcome(tag: str, payload: Any = None) -> dict[str, Any]:
    if tag == "success":
        return {"tag": tag, "value": copy.deepcopy(payload), "optional_witness": None}
    fields = {
        "domain_error": "diagnostic",
        "unsupported": "capability",
        "undetermined": "obligation",
    }
    if tag not in fields:
        raise ValueError(f"unsupported terminal tag {tag!r}")
    return {"tag": tag, fields[tag]: copy.deepcopy(payload)}


def resource_limit(beta: Mapping[str, Any], progress: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "tag": "resource_limit",
        "bound": copy.deepcopy(dict(beta)),
        "progress": copy.deepcopy(dict(progress)),
    }


def is_success(value: Mapping[str, Any]) -> bool:
    return value.get("tag") == "success"


def node_digest_payload(node: Mapping[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(dict(node))
    payload.pop("node_id", None)
    return payload


def bind_node_ids(node: Mapping[str, Any]) -> dict[str, Any]:
    """Bind node IDs bottom-up without hashing a node's own identifier."""
    bound = copy.deepcopy(dict(node))
    children = [bind_node_ids(child) for child in bound.pop("children", [])]
    bound["child_node_ids"] = [child["node"]["node_id"] for child in children]
    bound["node_id"] = digest(node_digest_payload(bound))
    return {"node": bound, "children": children}


def flatten_bound_tree(tree: Mapping[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for child in tree["children"]:
        result.extend(flatten_bound_tree(child))
    result.append(copy.deepcopy(tree["node"]))
    return result


GROUP_ORDER = (
    "identity",
    "rule_pins",
    "evaluation_claim",
    "static_inputs",
    "runtime_inputs",
    "resource_input",
    "derivation_record",
    "external_assumptions",
)


def group_digest_payload(name: str, group: Mapping[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(dict(group))
    if name == "identity":
        payload.pop("witness_identifier", None)
    elif name == "evaluation_claim":
        terminal = payload.get("terminal_outcome")
        if isinstance(terminal, dict) and terminal.get("tag") == "success":
            terminal.pop("optional_witness", None)
    return payload


def bind_envelope(envelope: Mapping[str, Any]) -> dict[str, Any]:
    bound = copy.deepcopy(dict(envelope))
    group_digests = [
        {"group_name": name, "group_digest": digest(group_digest_payload(name, bound[name]))}
        for name in GROUP_ORDER
    ]
    root_payload = {
        "encoding_edition": ENCODING_EDITION,
        "digest_edition": DIGEST_EDITION,
        "group_digests": group_digests,
    }
    root_digest = digest(root_payload)
    identifier = f"{WITNESS_EDITION}:{root_digest}"
    bound["identity"]["witness_identifier"] = identifier
    terminal = bound["evaluation_claim"]["terminal_outcome"]
    if terminal.get("tag") == "success":
        terminal["optional_witness"] = identifier
    bound["integrity"] = {**root_payload, "root_digest": root_digest}
    return bound
