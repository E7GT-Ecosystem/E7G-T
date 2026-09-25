"""Text-derived finite RGP/0.2 read-only contextual-expression fragment.

This is a separately versioned interpretation, not an RGP/0.1 conversion,
whole/portion coherence model, or proof of RGP/0.2 profile adequacy.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


EDITION = "E7C-RGP02-EXPRESSION-B1/0.1-provisional"
KERNELS = ("0.13-experimental-draft", "0.14-experimental-draft")
PROFILE = "RGP/0.2"
MAX_BYTES = 16384


class AdmissionError(ValueError):
    pass


def _bytes(value):
    try:
        data = json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
        if len(data) > MAX_BYTES or json.loads(data) != value:
            raise AdmissionError("noncanonical or oversized JSON source")
        return data
    except (TypeError, ValueError, RecursionError) as exc:
        raise AdmissionError("finite canonical UTF-8 source required") from exc


def _name(value):
    if type(value) is not str or not value or len(value) > 256:
        raise AdmissionError("bounded nonempty identifier required")
    _bytes(value)
    return value


@dataclass(frozen=True)
class Whole:
    kernel: str
    edition: str
    fields: tuple[tuple[str, str], ...]

    def __post_init__(self):
        if self.kernel not in KERNELS or type(self.edition) is not str:
            raise AdmissionError("RGP/0.2 source kernel and edition required")
        _name(self.edition)
        if (type(self.fields) is not tuple or not self.fields
                or any(type(pair) is not tuple or len(pair) != 2
                       or type(pair[1]) is not str for pair in self.fields)):
            raise AdmissionError("finite string-field source required")
        for name, value in self.fields:
            _name(name)
            _bytes(value)
        if tuple(k for k, _ in self.fields) != tuple(sorted(set(k for k, _ in self.fields))):
            raise AdmissionError("source fields must be unique and ordered")
        _bytes(self.record())

    def record(self):
        return {"kernel": self.kernel, "profile": PROFILE, "edition": self.edition,
                "fields": dict(self.fields)}

    @property
    def identity(self):
        return sha256(_bytes(self.record())).hexdigest()


@dataclass(frozen=True)
class Portion:
    occurrence: str
    kernel: str
    source_edition: str
    source_identity: str
    codec_edition: str
    payload: bytes


def encode(whole: Whole, occurrence: str, codec_edition: str) -> Portion:
    if type(whole) is not Whole:
        raise AdmissionError("typed whole required")
    return Portion(_name(occurrence), whole.kernel, whole.edition,
                   whole.identity, _name(codec_edition), _bytes(whole.record()))


def decode(portion: Portion, codec_edition: str) -> Whole:
    if type(portion) is not Portion or portion.codec_edition != codec_edition:
        raise AdmissionError("decoder or portion edition unavailable")
    try:
        data = json.loads(portion.payload.decode("utf-8"))
        if (type(data) is not dict or set(data) != {"kernel", "profile", "edition", "fields"}
                or data["profile"] != PROFILE or type(data["fields"]) is not dict):
            raise AdmissionError("invalid SR4 payload")
        whole = Whole(data["kernel"], data["edition"],
                      tuple(sorted(data["fields"].items())))
        if (_bytes(whole.record()) != portion.payload or whole.identity != portion.source_identity
                or whole.kernel != portion.kernel or whole.edition != portion.source_edition):
            raise AdmissionError("portion does not recover its exact source")
        _name(portion.occurrence)
        return whole
    except (UnicodeError, ValueError, TypeError, KeyError, AttributeError) as exc:
        raise AdmissionError("invalid exact portion") from exc


@dataclass(frozen=True)
class Context:
    role: str
    time: str
    regime: str
    access: str
    composition: str
    inquiry: str

    def __post_init__(self):
        for field in (self.role, self.time, self.regime, self.access,
                      self.composition, self.inquiry):
            _name(field)


@dataclass(frozen=True)
class ExpressionRule:
    edition: str
    source_kernel: str
    source_edition: str
    codec_edition: str
    selected: tuple[str, ...]
    allowed_roles: tuple[str, ...]
    access_scope: str
    mode: str

    def __post_init__(self):
        if self.source_kernel not in KERNELS:
            raise AdmissionError("rule requires a declared draft kernel edition")
        for item in (self.edition, self.source_edition, self.codec_edition,
                     self.access_scope):
            _name(item)
        if (type(self.selected) is not tuple or
                self.selected != tuple(sorted(set(self.selected))) or
                type(self.allowed_roles) is not tuple or
                self.allowed_roles != tuple(sorted(set(self.allowed_roles))) or
                not self.allowed_roles or
                self.mode not in ("read_only", "state_changing", "generative")):
            raise AdmissionError("closed rule edition and mode required")
        for item in (*self.selected, *self.allowed_roles):
            _name(item)


@dataclass(frozen=True)
class LocalExpression:
    source_identity: str
    source_edition: str
    occurrence: str
    rule_edition: str
    context: Context
    fields: tuple[tuple[str, str], ...]
    lost: tuple[str, ...]
    mode: str


@dataclass(frozen=True)
class Outcome:
    tag: str
    expression: LocalExpression | None


def express(portion: Portion, context: Context, rule: ExpressionRule,
            budget: int) -> Outcome:
    if (type(context) is not Context or type(rule) is not ExpressionRule
            or type(budget) is not int or budget < 0):
        raise AdmissionError("typed context, rule and budget required")
    whole = decode(portion, rule.codec_edition)
    if whole.kernel != rule.source_kernel or whole.edition != rule.source_edition:
        return Outcome("domain_error", None)
    if context.role not in rule.allowed_roles or context.access != rule.access_scope:
        return Outcome("unsupported", None)
    if rule.mode != "read_only":
        return Outcome("unsupported", None)
    fields = dict(whole.fields)
    if any(key not in fields for key in rule.selected):
        return Outcome("undetermined", None)
    if len(rule.selected) > budget:
        return Outcome("resource_limit", None)
    selected = tuple((key, fields[key]) for key in rule.selected)
    lost = tuple(key for key in fields if key not in rule.selected)
    return Outcome("success", LocalExpression(whole.identity, whole.edition,
                   portion.occurrence, rule.edition, context, selected, lost,
                   rule.mode))
