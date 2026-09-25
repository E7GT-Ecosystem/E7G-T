"""Pin RGP/0.1 -> /0.2 source delta; textual, not semantic fidelity."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
FILES = (
    "E7G-T_Kernel_v0.12.1_Experimental_Canonical_Reference.md",
    "E7G-T_Kernel_v0.13_Experimental_Canonical_Draft.md",
    "E7G-T_Kernel_v0.14_Experimental_Canonical_Draft.md",
)
DIGESTS = (
    "4c7784bcd653471a097329361b17b13c3b45e1592df6204243370ca0190935b1",
    "ecade9da08df04d257735d399848ebf2231590cabab8e48fa0b228db3051bdbe",
    "a64a8d9ecbd417cbe59883e33be7529cb779354b377b3ac261488a2a81cfc43a",
)
UNCHANGED = (3, 4, 6, 7)
CHANGED = (0, 1, 2, 5, 8, 9, 10, 11, 12)


class SourceDrift(ValueError):
    pass


def sections(text: str) -> dict[int, str]:
    beginning = re.search(r"^## X\.18\b.*$", text, re.M)
    if beginning is None:
        raise SourceDrift("RGP section absent")
    remaining = text[beginning.end():]
    boundary = re.search(r"^(?:## X\.19\b|# Appendix V\b).*$", remaining, re.M)
    if boundary is None:
        raise SourceDrift("RGP section boundary absent")
    rgp = remaining[:boundary.start()]
    headings = list(re.finditer(r"^### R\.(\d+)\b.*$", rgp, re.M))
    if [int(m[1]) for m in headings] != list(range(13)):
        raise SourceDrift("RGP subsection list changed")
    return {int(m[1]): rgp[m.start():headings[i + 1].start()
                           if i + 1 < len(headings) else len(rgp)]
            for i, m in enumerate(headings)}


def audit(texts: tuple[str, str, str]) -> dict[str, tuple[int, ...]]:
    old, successor, inherited = (sections(s) for s in texts)
    if "RGP/0.1" not in texts[0].split("## X.18", 1)[1].splitlines()[0]:
        raise SourceDrift("predecessor identity changed")
    if any("RGP/0.2" not in t.split("## X.18", 1)[1].splitlines()[0]
           for t in texts[1:]):
        raise SourceDrift("successor identity changed")
    for index in UNCHANGED:
        if old[index] != successor[index]:
            raise SourceDrift(f"unexpected inherited R.{index} change")
    for index in CHANGED:
        if old[index] == successor[index]:
            raise SourceDrift(f"missing R.{index} successor change")
    for index in range(13):
        if successor[index] != inherited[index]:
            raise SourceDrift(f"v0.14 changed inherited R.{index}")
    for index, token in ((1, "\\(X\\)"), (2, "\\mathsf{Expresses}"),
                         (5, "WPC/0.1"), (8, "reconstructive whole"),
                         (10, "R14")):
        if token not in successor[index]:
            raise SourceDrift(f"new R.{index} construct absent: {token}")
    return {"unchanged_v0121_to_v013": UNCHANGED,
            "changed_v0121_to_v013": CHANGED,
            "unchanged_v013_to_v014": tuple(range(13))}


def audit_pinned(root: Path = ROOT) -> dict[str, tuple[int, ...]]:
    raw = tuple((root / name).read_bytes() for name in FILES)
    for name, data, digest in zip(FILES, raw, DIGESTS):
        if sha256(data).hexdigest() != digest:
            raise SourceDrift(f"source digest changed: {name}")
    return audit(tuple(data.decode("utf-8") for data in raw))


if __name__ == "__main__":
    for label, sections_ in audit_pinned().items():
        print(f"{label}: {', '.join('R.' + str(i) for i in sections_)}")
