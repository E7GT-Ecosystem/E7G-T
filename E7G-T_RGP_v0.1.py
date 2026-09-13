"""Bounded executable reference model for E7G-T RGP/0.1.

This module implements a deliberately finite subset of Kernel v0.12.1 §X.18.
It demonstrates typed generation, projection, composition and exact SR4
whole-bearing encoding.  It is not a general RGP runtime or an external-system
conformance claim.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import IntEnum
import hashlib
import json
from typing import Any, Callable, Mapping, Sequence


KERNEL = "0.12.1-experimental"
PROFILE = "RGP/0.1"
MODEL = "RGP-B1/0.1"


class RGPError(ValueError):
    """A typed RGP admission or operation failure."""


class RetentionTier(IntEnum):
    SR0 = 0
    SR1 = 1
    SR2 = 2
    SR3 = 3
    SR4 = 4


def canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


@dataclass(frozen=True)
class Placement:
    rank: int
    regime: str | None
    temporal_scope: str
    access_scope: str
    composition_scope: str

    def __post_init__(self) -> None:
        if self.rank < 0:
            raise RGPError("rank must be finite and non-negative")


@dataclass(frozen=True)
class Layer:
    signature: str
    edition: str
    carrier: Mapping[str, Any]
    rules: tuple[str, ...]
    interface: Mapping[str, Any]
    access_policy: Mapping[str, tuple[str, ...]]
    invariants: Mapping[str, Any]
    provenance: Mapping[str, Any]
    placement: Placement

    def canonical_record(self) -> dict[str, Any]:
        return {
            "kernel": KERNEL,
            "profile": PROFILE,
            "model": MODEL,
            "signature": self.signature,
            "edition": self.edition,
            "carrier": self.carrier,
            "rules": list(self.rules),
            "interface": self.interface,
            "access_policy": {
                role: list(operations)
                for role, operations in sorted(self.access_policy.items())
            },
            "invariants": self.invariants,
            "provenance": self.provenance,
            "placement": {
                "rank": self.placement.rank,
                "regime": self.placement.regime,
                "temporal_scope": self.placement.temporal_scope,
                "access_scope": self.placement.access_scope,
                "composition_scope": self.placement.composition_scope,
            },
        }

    @property
    def identity(self) -> str:
        return digest(self.canonical_record())


@dataclass(frozen=True)
class GenerationEdge:
    parent_identity: str
    child_identity: str
    rule_id: str
    rule_edition: str
    parameters: Mapping[str, Any]
    inherited_invariants: tuple[str, ...]
    introduced_variations: tuple[str, ...]
    unresolved: tuple[str, ...]


@dataclass(frozen=True)
class Projection:
    source_identity: str
    role: str
    projection_edition: str
    view: Mapping[str, Any]
    preserved: tuple[str, ...]
    lost: tuple[str, ...]
    reconstruction: str


@dataclass(frozen=True)
class EncodedPortion:
    source_identity: str
    source_edition: str
    portion_index: str
    encoder_edition: str
    decoder_edition: str
    payload: bytes
    payload_digest: str
    retention_tier: RetentionTier


@dataclass(frozen=True)
class Composite:
    interface_edition: str
    component_identities: tuple[str, ...]
    preserves_component_identity: bool

    @property
    def identity(self) -> str:
        return digest(
            {
                "interface_edition": self.interface_edition,
                "component_identities": list(self.component_identities),
                "preserves_component_identity": self.preserves_component_identity,
            }
        )


def generate(
    parent: Layer,
    *,
    rule_id: str,
    rule_edition: str,
    child_edition: str,
    parameters: Mapping[str, Any],
    transform: Callable[[Mapping[str, Any], Mapping[str, Any]], Mapping[str, Any]],
    inherit: Sequence[str],
    introduced_variations: Sequence[str] = (),
    unresolved: Sequence[str] = (),
) -> tuple[Layer, GenerationEdge]:
    if rule_id not in parent.rules:
        raise RGPError("unsupported generation rule")
    missing = sorted(set(inherit) - set(parent.invariants))
    if missing:
        raise RGPError(f"unknown inherited invariants: {missing}")
    child = replace(
        parent,
        edition=child_edition,
        carrier=dict(transform(parent.carrier, parameters)),
        invariants={name: parent.invariants[name] for name in inherit},
        provenance={"parent_identity": parent.identity, "rule": rule_id},
        placement=replace(parent.placement, rank=parent.placement.rank + 1),
    )
    return child, GenerationEdge(
        parent_identity=parent.identity,
        child_identity=child.identity,
        rule_id=rule_id,
        rule_edition=rule_edition,
        parameters=dict(parameters),
        inherited_invariants=tuple(inherit),
        introduced_variations=tuple(introduced_variations),
        unresolved=tuple(unresolved),
    )


def project(layer: Layer, *, role: str, fields: Sequence[str], edition: str) -> Projection:
    if "view" not in layer.access_policy.get(role, ()):
        raise RGPError("role is not admitted for view")
    source = layer.canonical_record()
    unknown = sorted(set(fields) - set(source))
    if unknown:
        raise RGPError(f"unknown projection fields: {unknown}")
    selected = tuple(sorted(set(fields)))
    lost = tuple(sorted(set(source) - set(selected)))
    return Projection(
        source_identity=layer.identity,
        role=role,
        projection_edition=edition,
        view={name: source[name] for name in selected},
        preserved=selected,
        lost=lost,
        reconstruction="singleton" if not lost else "non_singleton_or_unproved",
    )


def encode_sr4(layer: Layer, *, portion_index: str, codec_edition: str) -> EncodedPortion:
    payload = canonical_bytes(layer.canonical_record())
    return EncodedPortion(
        source_identity=layer.identity,
        source_edition=layer.edition,
        portion_index=portion_index,
        encoder_edition=codec_edition,
        decoder_edition=codec_edition,
        payload=payload,
        payload_digest=hashlib.sha256(payload).hexdigest(),
        retention_tier=RetentionTier.SR4,
    )


def decode_sr4(portion: EncodedPortion, *, codec_edition: str) -> Mapping[str, Any]:
    if portion.retention_tier is not RetentionTier.SR4:
        raise RGPError("insufficient")
    if codec_edition != portion.decoder_edition:
        raise RGPError("unsupported")
    if hashlib.sha256(portion.payload).hexdigest() != portion.payload_digest:
        raise RGPError("invalid_encoding")
    try:
        source = json.loads(portion.payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RGPError("invalid_encoding") from exc
    if digest(source) != portion.source_identity:
        raise RGPError("invalid_encoding")
    return source


def compose(layers: Sequence[Layer], *, interface_edition: str) -> Composite:
    if not layers:
        raise RGPError("composition requires at least one component")
    identities = tuple(layer.identity for layer in layers)
    if len(set(identities)) != len(identities):
        raise RGPError("component occurrences must be explicitly distinguished")
    return Composite(interface_edition, identities, True)

