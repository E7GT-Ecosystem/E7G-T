"""Exact edition binding for the previously admitted finite SF/CFS points.

Identical source sections permit this selected replay across draft editions;
they do not give general symbolic-family or CFS semantic adequacy.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re

from sfcfs_points_b1 import Family, Realisation, realise, restrict, shared_union


ROOT = Path(__file__).resolve().parents[3]
KERNEL_FILES = {
    "0.12.1-experimental": (
        "E7G-T_Kernel_v0.12.1_Experimental_Canonical_Reference.md",
        "4c7784bcd653471a097329361b17b13c3b45e1592df6204243370ca0190935b1"),
    "0.13-experimental-draft": (
        "E7G-T_Kernel_v0.13_Experimental_Canonical_Draft.md",
        "ecade9da08df04d257735d399848ebf2231590cabab8e48fa0b228db3051bdbe"),
    "0.14-experimental-draft": (
        "E7G-T_Kernel_v0.14_Experimental_Canonical_Draft.md",
        "a64a8d9ecbd417cbe59883e33be7529cb779354b377b3ac261488a2a81cfc43a"),
}
MODELS = {
    "E7G-T_Symbolic_Families_v0.1.py":
        "0a827d55cc95c4840ba5427e8585378b23ee6a3b00296856f192176cb4a2dca8",
    "E7G-T_Combined_Family_State_v0.1.py":
        "ed6ba76f6638c859e65d9908ecd4ef2539cd1348df8249471ca706a51b94d542",
}


class EditionAdmission(ValueError):
    pass


def _source_text(path: Path, digest: str) -> str:
    content = path.read_bytes()
    if sha256(content).hexdigest() != digest:
        raise EditionAdmission(f"source digest drift: {path.name}")
    return content.decode("utf-8")


def _section(text: str, start: str, end: str) -> str:
    match = re.search(r"^## X\." + start + r"\b.*$", text, re.M)
    if match is None:
        raise EditionAdmission(f"missing X.{start} section")
    tail = text[match.start():]
    boundary = re.search(r"^## X\." + end + r"\b.*$", tail, re.M)
    if boundary is None:
        raise EditionAdmission(f"missing X.{end} boundary")
    return tail[:boundary.start()]


def source_pins(kernel: str) -> tuple[str, str, str]:
    if kernel not in KERNEL_FILES:
        raise EditionAdmission("unsupported source kernel edition")
    baseline_file, baseline_digest = KERNEL_FILES["0.12.1-experimental"]
    candidate_file, candidate_digest = KERNEL_FILES[kernel]
    baseline = _source_text(ROOT / baseline_file, baseline_digest)
    candidate = _source_text(ROOT / candidate_file, candidate_digest)
    for first, second in (("16", "17"), ("17", "18")):
        if _section(baseline, first, second) != _section(candidate, first, second):
            raise EditionAdmission(f"inherited X.{first} text changed")
    for filename, digest in MODELS.items():
        _source_text(ROOT / filename, digest)
    return candidate_digest, MODELS["E7G-T_Symbolic_Families_v0.1.py"], \
        MODELS["E7G-T_Combined_Family_State_v0.1.py"]


@dataclass(frozen=True)
class BoundFamily:
    kernel: str
    kernel_sha256: str
    sf_model_sha256: str
    cfs_model_sha256: str
    value: Family


def bind(kernel: str, value: Family) -> BoundFamily:
    if type(value) is not Family:
        raise EditionAdmission("finite SF/CFS family required")
    return BoundFamily(kernel, *source_pins(kernel), value)


def _checked(bound: BoundFamily) -> None:
    if type(bound) is not BoundFamily or type(bound.value) is not Family or (
            bound.kernel_sha256, bound.sf_model_sha256, bound.cfs_model_sha256
            ) != source_pins(bound.kernel):
        raise EditionAdmission("family binding does not match the pinned edition")


def shared(left: BoundFamily, right: BoundFamily) -> BoundFamily:
    _checked(left)
    _checked(right)
    if left.kernel != right.kernel:
        raise EditionAdmission("shared family operation cannot mix kernel editions")
    return bind(left.kernel, shared_union(left.value, right.value))


def restrict_points(source: BoundFamily, points: tuple) -> BoundFamily:
    _checked(source)
    return bind(source.kernel, restrict(source.value, points))


@dataclass(frozen=True)
class BoundRealisation:
    kernel: str
    result: Realisation
    source: BoundFamily


def realise_bound(source: BoundFamily, budget: int) -> BoundRealisation:
    _checked(source)
    return BoundRealisation(source.kernel, realise(source.value, budget), source)
