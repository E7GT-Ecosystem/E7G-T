"""Selected WPC/0.2 constitution from actual local values, without encodings.

Constitution and strict reconstruction have different input sorts. This
finite allocation model does not implement arbitrary WPC presentation.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re

from wpc_allocation_b1 import AdmissionError, IDS, Whole


ROOT = Path(__file__).resolve().parents[3]
KERNELS = {
    "0.13-experimental-draft": (
        "E7G-T_Kernel_v0.13_Experimental_Canonical_Draft.md",
        "ecade9da08df04d257735d399848ebf2231590cabab8e48fa0b228db3051bdbe"),
    "0.14-experimental-draft": (
        "E7G-T_Kernel_v0.14_Experimental_Canonical_Draft.md",
        "a64a8d9ecbd417cbe59883e33be7529cb779354b377b3ac261488a2a81cfc43a"),
}
SOURCE_MODEL = ("packages/wpc-0.2/E7G-T_WPC_v0.2_Reference_Model.py",
                "5fe2e8d5f913f92ad8fbd0575607f569cbd211b13970174d537a9af14a493ea3")
EDITION = "E7C-WPC-UNENCODED-CONSTITUTION-B1/0.1-provisional"


def _pinned(path: str, digest: str) -> str:
    content = (ROOT / path).read_bytes()
    if sha256(content).hexdigest() != digest:
        raise AdmissionError("WPC source digest drift")
    return content.decode("utf-8")


def _wpc_section(text: str) -> str:
    start = re.search(r"^## X\.19\b.*$", text, re.M)
    if start is None:
        raise AdmissionError("WPC/0.2 source section missing")
    tail = text[start.start():]
    end = re.search(r"^(?:## X\.20\b|# Appendix V\b).*$", tail, re.M)
    if end is None:
        raise AdmissionError("WPC/0.2 section boundary missing")
    return tail[:end.start()]


def source_pin(kernel: str) -> str:
    if kernel not in KERNELS:
        raise AdmissionError("unsupported WPC/0.2 kernel edition")
    old = _wpc_section(_pinned(*KERNELS["0.13-experimental-draft"]))
    current = _wpc_section(_pinned(*KERNELS[kernel]))
    if old != current:
        raise AdmissionError("inherited WPC/0.2 text drift")
    _pinned(*SOURCE_MODEL)
    return KERNELS[kernel][1]


@dataclass(frozen=True)
class SemanticPresentation:
    kernel: str
    source_digest: str
    epoch: int
    manifest: tuple[str, ...]
    rows: tuple[tuple[str, int], ...]
    events: tuple[tuple, ...]


def presentation(kernel: str, epoch: int, manifest: tuple[str, ...],
                 rows: tuple[tuple[str, int], ...], events: tuple[tuple, ...] = ()):
    return SemanticPresentation(kernel, source_pin(kernel), epoch, manifest, rows, events)


@dataclass(frozen=True)
class SemanticWhole:
    kernel: str
    epoch: int
    members: tuple[str, ...]
    values: tuple[int, ...]
    events: tuple[tuple, ...]


@dataclass(frozen=True)
class Constitution:
    kernel: str
    tag: str
    value: SemanticWhole | None
    visited: int
    source: SemanticPresentation


def constitute(source: SemanticPresentation, step_bound: int) -> Constitution:
    if (type(source) is not SemanticPresentation or type(step_bound) is not int
            or step_bound < 0 or source.source_digest != source_pin(source.kernel)):
        raise AdmissionError("typed edition-bound presentation and budget required")
    if (type(source.epoch) is not int or source.epoch < 0 or
            type(source.manifest) is not tuple or not source.manifest or
            source.manifest != tuple(sorted(set(source.manifest))) or
            not set(source.manifest) <= set(IDS) or
            type(source.rows) is not tuple or len(source.rows) != len(source.manifest) or
            type(source.events) is not tuple or
            any(type(row) is not tuple or len(row) != 2 or
                type(row[0]) is not str or type(row[1]) is not int or
                not 0 <= row[1] <= 2 for row in source.rows)):
        raise AdmissionError("invalid finite unencoded presentation")
    visited = 0
    actual = []
    for expected, row in zip(source.manifest, source.rows):
        if visited >= step_bound:
            return Constitution(source.kernel, "resource_limit", None, visited, source)
        visited += 1
        if row[0] != expected:
            raise AdmissionError("coverage_incomplete")
        actual.append(row[1])
    try:
        whole = Whole(source.epoch, source.manifest, tuple(actual), source.events)
    except AdmissionError as exc:
        if str(exc) != "global_incompatibility":
            raise
        return Constitution(source.kernel, "incompatible", None, visited, source)
    return Constitution(source.kernel, "unique",
                        SemanticWhole(source.kernel, whole.epoch, whole.members,
                                      whole.values, whole.events), visited, source)
