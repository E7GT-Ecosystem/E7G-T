"""Independent finite RGP-B1 structural adapter; no runtime authority claim."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json


EDITION = "E7C-RGP-FINITE-B1/0.1-provisional"
KERNEL, PROFILE, MODEL = "0.12.1-experimental", "RGP/0.1", "RGP-B1/0.1"
MAX_RECORD_BYTES = 16384
RECORD_KEYS = frozenset(("kernel", "profile", "model", "signature", "edition",
                         "carrier", "rules", "interface", "access_policy",
                         "invariants", "provenance", "placement"))


class AdmissionError(ValueError):
    pass


def canonical(value: dict) -> bytes:
    try:
        data = json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
        if len(data) > MAX_RECORD_BYTES or json.loads(data) != value:
            raise AdmissionError("noncanonical or oversized finite JSON record")
        return data
    except (TypeError, ValueError, RecursionError) as exc:
        raise AdmissionError("finite JSON record required") from exc


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class Placement:
    rank: int
    regime: str | None
    temporal_scope: str
    access_scope: str
    composition_scope: str

    def __post_init__(self):
        if type(self.rank) is not int or not 0 <= self.rank <= 1024:
            raise AdmissionError("finite construction rank required")
        if not all(type(x) is str and x for x in
                   (self.temporal_scope, self.access_scope, self.composition_scope)):
            raise AdmissionError("independent time, access and composition scopes required")
        if self.regime is not None and type(self.regime) is not str:
            raise AdmissionError("regime must be a string or absent")


@dataclass(frozen=True)
class Layer:
    signature: str
    edition: str
    carrier: dict
    rules: tuple[str, ...]
    interface: dict
    access_policy: dict[str, tuple[str, ...]]
    invariants: dict
    provenance: dict
    placement: Placement

    def __post_init__(self):
        if (type(self.signature) is not str or not self.signature or
                type(self.edition) is not str or not self.edition or
                type(self.placement) is not Placement or
                any(type(x) is not dict for x in
                    (self.carrier, self.interface, self.access_policy,
                     self.invariants, self.provenance)) or
                type(self.rules) is not tuple or
                any(type(x) is not str for x in self.rules) or
                any(type(k) is not str or type(v) is not tuple or
                    any(type(op) is not str for op in v)
                    for k, v in self.access_policy.items())):
            raise AdmissionError("typed layer record required")
        canonical(self.record())

    def record(self) -> dict:
        return {"kernel": KERNEL, "profile": PROFILE, "model": MODEL,
                "signature": self.signature, "edition": self.edition,
                "carrier": self.carrier, "rules": list(self.rules),
                "interface": self.interface,
                "access_policy": {k: list(v) for k, v in sorted(self.access_policy.items())},
                "invariants": self.invariants, "provenance": self.provenance,
                "placement": {"rank": self.placement.rank,
                              "regime": self.placement.regime,
                              "temporal_scope": self.placement.temporal_scope,
                              "access_scope": self.placement.access_scope,
                              "composition_scope": self.placement.composition_scope}}

    @property
    def identity(self) -> str:
        return sha(canonical(self.record()))


@dataclass(frozen=True)
class Hosted:
    host: str
    component_identity: str


def host(layer: Layer, host_identity: str) -> Hosted:
    if type(layer) is not Layer or type(host_identity) is not str or not host_identity:
        raise AdmissionError("typed host relation required")
    return Hosted(host_identity, layer.identity)


@dataclass(frozen=True)
class Generation:
    parent_identity: str
    child_identity: str
    rule_id: str
    rule_edition: str
    parameters: dict
    inherited_invariants: tuple[str, ...]
    introduced_variations: tuple[str, ...]
    unresolved: tuple[str, ...]


def generate(parent: Layer, *, rule_id: str, rule_edition: str,
             child_edition: str, parameters: dict, inherit: tuple[str, ...],
             introduced_variations: tuple[str, ...] = (),
             unresolved: tuple[str, ...] = ()) -> tuple[Layer, Generation]:
    """Admitted transform: shallow carrier update from finite parameters."""
    if (type(parent) is not Layer or rule_id not in parent.rules or
            not all(type(x) is str and x for x in (rule_id, rule_edition, child_edition))):
        raise AdmissionError("generation rule not admitted")
    if (type(parameters) is not dict or type(inherit) is not tuple or
            any(x not in parent.invariants for x in inherit) or
            any(type(x) is not str for x in inherit) or
            any(type(x) is not tuple or any(type(y) is not str for y in x)
                for x in (introduced_variations, unresolved)) or
            parent.placement.rank >= 1024):
        raise AdmissionError("generation parameters, inheritance or rank not admitted")
    child = replace(parent, edition=child_edition,
                    carrier={**parent.carrier, **parameters},
                    invariants={name: parent.invariants[name] for name in inherit},
                    provenance={"parent_identity": parent.identity, "rule": rule_id},
                    placement=replace(parent.placement, rank=parent.placement.rank + 1))
    edge = Generation(parent.identity, child.identity, rule_id, rule_edition,
                      parameters, inherit, introduced_variations, unresolved)
    return child, edge


@dataclass(frozen=True)
class View:
    source_identity: str
    role: str
    edition: str
    fields: dict
    preserved: tuple[str, ...]
    lost: tuple[str, ...]

    @property
    def exact(self) -> bool:
        return not self.lost


def project(layer: Layer, *, role: str, fields: tuple[str, ...], edition: str) -> View:
    if (type(layer) is not Layer or type(role) is not str or
            "view" not in layer.access_policy.get(role, ()) or
            type(fields) is not tuple or any(type(f) is not str for f in fields) or
            type(edition) is not str or not edition):
        raise AdmissionError("role or projection edition not admitted")
    source = layer.record()
    if any(f not in source for f in fields):
        raise AdmissionError("unknown projection field")
    selected = tuple(sorted(set(fields)))
    lost = tuple(sorted(set(source) - set(selected)))
    return View(layer.identity, role, edition,
                {f: source[f] for f in selected}, selected, lost)


@dataclass(frozen=True)
class Encoded:
    source_identity: str
    source_edition: str
    portion_index: str
    codec_edition: str
    payload: bytes
    payload_digest: str
    retention_tier: int


def encode_sr4(layer: Layer, *, portion_index: str, codec_edition: str) -> Encoded:
    if (type(layer) is not Layer or type(portion_index) is not str or
            not portion_index or type(codec_edition) is not str or not codec_edition):
        raise AdmissionError("typed encoding request required")
    payload = canonical(layer.record())
    return Encoded(layer.identity, layer.edition, portion_index,
                   codec_edition, payload, sha(payload), 4)


def decode_sr4(encoded: Encoded, *, codec_edition: str) -> dict:
    if type(encoded) is not Encoded or encoded.retention_tier != 4:
        raise AdmissionError("insufficient retention")
    if encoded.codec_edition != codec_edition:
        raise AdmissionError("unsupported decoder edition")
    if type(encoded.payload) is not bytes or sha(encoded.payload) != encoded.payload_digest:
        raise AdmissionError("invalid encoding")
    try:
        value = json.loads(encoded.payload.decode("utf-8"))
        if (type(value) is not dict or canonical(value) != encoded.payload or
                sha(encoded.payload) != encoded.source_identity or
                value.get("edition") != encoded.source_edition or
                (value.get("kernel"), value.get("profile"), value.get("model")) !=
                (KERNEL, PROFILE, MODEL)):
            raise AdmissionError("invalid source identity or edition")
    except (UnicodeDecodeError, ValueError, TypeError) as exc:
        raise AdmissionError("invalid encoding") from exc
    return value


def reconstruct(view: View, retained: Encoded | None = None) -> dict:
    if type(view) is not View:
        raise AdmissionError("typed view required")
    if (type(view.fields) is not dict or
            any(type(f) is not str for f in view.fields) or
            type(view.preserved) is not tuple or
            any(type(f) is not str for f in view.preserved) or
            view.preserved != tuple(sorted(view.fields)) or
            type(view.lost) is not tuple or
            view.lost != tuple(sorted(RECORD_KEYS - set(view.preserved)))):
        raise AdmissionError("inconsistent projection field account")
    if retained is None:
        if not view.exact or sha(canonical(view.fields)) != view.source_identity:
            raise AdmissionError("lossy projection requires complete retained source")
        return view.fields
    source = decode_sr4(retained, codec_edition=retained.codec_edition)
    if (retained.source_identity != view.source_identity or
            {f: source[f] for f in view.preserved} != view.fields):
        raise AdmissionError("retained source does not match view")
    return source


@dataclass(frozen=True)
class Composite:
    interface_edition: str
    component_identities: tuple[str, ...]


def compose(layers: tuple[Layer, ...], *, interface_edition: str) -> Composite:
    if (type(layers) is not tuple or not layers or
            any(type(x) is not Layer for x in layers) or
            type(interface_edition) is not str or not interface_edition):
        raise AdmissionError("typed finite composition required")
    identities = tuple(x.identity for x in layers)
    if len(set(identities)) != len(identities):
        raise AdmissionError("duplicate component occurrence requires explicit identity")
    return Composite(interface_edition, identities)


@dataclass(frozen=True)
class QuotedLayer:
    """Whole-layer payload; quotation does not run its rules or authorise access."""
    source_identity: str
    source_rank: int
    quotation_rank: int
    payload: bytes


def quote(layer: Layer) -> QuotedLayer:
    if type(layer) is not Layer or layer.placement.rank >= 1024:
        raise AdmissionError("finite layer quotation required")
    return QuotedLayer(layer.identity, layer.placement.rank,
                       layer.placement.rank + 1, canonical(layer.record()))


def unquote(quoted: QuotedLayer) -> dict:
    if type(quoted) is not QuotedLayer or type(quoted.payload) is not bytes:
        raise AdmissionError("whole quoted layer required")
    try:
        record = json.loads(quoted.payload.decode("utf-8"))
        if (type(record) is not dict or canonical(record) != quoted.payload or
                sha(quoted.payload) != quoted.source_identity or
                record.get("kernel") != KERNEL or record.get("profile") != PROFILE or
                record.get("model") != MODEL or
                type(quoted.source_rank) is not int or
                record.get("placement", {}).get("rank") != quoted.source_rank or
                quoted.quotation_rank != quoted.source_rank + 1):
            raise AdmissionError("quoted source or rank mismatch")
    except (UnicodeDecodeError, TypeError, ValueError, AttributeError) as exc:
        raise AdmissionError("invalid quoted payload") from exc
    return record


@dataclass(frozen=True)
class HostBoundary:
    interface_position: str
    interface_contract: str
    admitted_signature: str


@dataclass(frozen=True)
class HostRelation:
    host_identity: str
    quoted_source_identity: str
    interface_position: str
    interface_contract: str


def hosts(host_layer: Layer, component: QuotedLayer,
          boundary: HostBoundary) -> HostRelation:
    """Local finite §R.2 relation; does not execute the quoted component."""
    if (type(host_layer) is not Layer or type(component) is not QuotedLayer or
            type(boundary) is not HostBoundary or
            any(type(x) is not str or not x for x in
                (boundary.interface_position, boundary.interface_contract,
                 boundary.admitted_signature))):
        raise AdmissionError("typed host, component and boundary required")
    record = unquote(component)
    if (host_layer.interface.get(boundary.interface_position) !=
            boundary.interface_contract or
            record["signature"] != boundary.admitted_signature):
        raise AdmissionError("host boundary contract does not admit component")
    return HostRelation(host_layer.identity, component.source_identity,
                        boundary.interface_position, boundary.interface_contract)


@dataclass(frozen=True)
class LocalAccess:
    """Source is retained for the model; the role receives only `view`."""
    source: QuotedLayer
    role: str
    temporal_locality: str
    view: View


def contextual_view(layer: Layer, *, role: str, temporal_locality: str,
                    fields: tuple[str, ...], edition: str) -> LocalAccess:
    if type(temporal_locality) is not str or not temporal_locality:
        raise AdmissionError("explicit temporal locality required")
    view = project(layer, role=role, fields=fields, edition=edition)
    return LocalAccess(quote(layer), role, temporal_locality, view)
