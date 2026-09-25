"""Pinned textual audit of the three kernel editions; no semantic adequacy claim."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FILES = (
    "E7G-T_Kernel_v0.12.1_Experimental_Canonical_Reference.md",
    "E7G-T_Kernel_v0.13_Experimental_Canonical_Draft.md",
    "E7G-T_Kernel_v0.14_Experimental_Canonical_Draft.md",
)
SHA256 = (
    "4c7784bcd653471a097329361b17b13c3b45e1592df6204243370ca0190935b1",
    "ecade9da08df04d257735d399848ebf2231590cabab8e48fa0b228db3051bdbe",
    "a64a8d9ecbd417cbe59883e33be7529cb779354b377b3ac261488a2a81cfc43a",
)


class SourceDrift(ValueError):
    pass


def section(text: str, start: str, end: str) -> str:
    """Return a complete X-numbered section, stopping at the next declared boundary."""
    first = re.search(r"^## " + re.escape(start) + r"\b.*$", text, re.M)
    if first is None:
        raise SourceDrift(f"missing section {start}")
    tail = text[first.start():]
    last = re.search(r"^(?:## " + re.escape(end) + r"\b|# Appendix V\b).*$", tail, re.M)
    if last is None:
        raise SourceDrift(f"missing boundary {end} after {start}")
    return tail[:last.start()]


def require_equal(left: str, right: str, label: str) -> None:
    if left != right:
        raise SourceDrift(f"{label}: inherited section changed")


def audit(texts: tuple[str, str, str]) -> dict[str, str]:
    old, v13, v14 = texts
    # The operational EEC-Q clauses are retained with one explicit example
    # interchange-edition edit; X.14-X.15 have separately changed guidance.
    old_core = section(old, "X.2", "X.14")
    new_core = section(v13, "X.2", "X.14")
    require_equal(
        old_core.replace('"kernel": "0.12.1-experimental"',
                         '"kernel": "0.13-experimental-draft"'),
        new_core, "v0.13 EEC-Q operative text except kernel example edition",
    )
    require_equal(new_core, section(v14, "X.2", "X.14"),
                  "v0.14 EEC-Q operative text")
    if section(old, "X.14", "X.16") == section(v13, "X.14", "X.16"):
        raise SourceDrift("v0.13 EEC-Q compatibility guidance change missing")
    if section(v13, "X.14", "X.16") == section(v14, "X.14", "X.16"):
        raise SourceDrift("v0.14 EEC-Q REC guidance change missing")
    for name, start, end in (("SF", "X.16", "X.17"),
                             ("CFS", "X.17", "X.18")):
        require_equal(section(old, start, end), section(v13, start, end),
                      f"v0.13 {name}")
        require_equal(section(v13, start, end), section(v14, start, end),
                      f"v0.14 {name}")
    rgp_old = section(old, "X.18", "X.19")
    rgp_new = section(v13, "X.18", "X.19")
    if "RGP/0.1" not in rgp_old.splitlines()[0] or "RGP/0.2" not in rgp_new.splitlines()[0]:
        raise SourceDrift("RGP profile identity transition missing")
    require_equal(rgp_new, section(v14, "X.18", "X.19"), "v0.14 RGP/0.2")
    wpc13 = section(v13, "X.19", "X.20")
    require_equal(wpc13, section(v14, "X.19", "X.20"), "v0.14 WPC/0.2")
    for token in ("WPC-Evolution/0.1", "WPC-Distributed/0.1"):
        if token not in wpc13:
            raise SourceDrift(f"missing distinct WPC module {token}")
    if "REC/0.1" not in section(v14, "X.20", "X.21"):
        raise SourceDrift("missing v0.14 REC module")
    return {
        "EEC-Q X.2-X.13": "same operative text except v0.13 example edition; X.14-X.15 changed twice",
        "SF X.16": "identical source text in all three editions",
        "CFS X.17": "identical source text in all three editions",
        "RGP X.18": "v0.1 to v0.2 change; v0.13 to v0.14 text identical",
        "WPC X.19": "v0.13 to v0.14 text identical; optional modules distinct",
        "REC X.20": "v0.14 addition",
    }


def audit_pinned(root: Path = ROOT) -> dict[str, str]:
    raw = tuple((root / name).read_bytes() for name in FILES)
    for name, data, digest in zip(FILES, raw, SHA256):
        if hashlib.sha256(data).hexdigest() != digest:
            raise SourceDrift(f"source digest changed: {name}")
    return audit(tuple(data.decode("utf-8") for data in raw))


if __name__ == "__main__":
    for section_name, finding in audit_pinned().items():
        print(f"{section_name}: {finding}")
