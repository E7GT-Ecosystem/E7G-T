"""Check the experimental canonical source against its pinned predecessors."""

import hashlib
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / "E7G-T_Kernel_v0.15_Experimental_Canonical_Reference.md"
V14 = ROOT / "E7G-T_Kernel_v0.14_Experimental_Canonical_Draft.md"
MSC = ROOT / "proposals/msc-0.1/E7G-T_MSC_v0.1_Multi-Scope_Coherence_Proposal.md"
MANIFEST = ROOT / "E7G-T_v0.15_Experimental_Release_Manifest.md"


def part(source, before, after):
    assert source.count(before) == 1, before
    assert source.count(after) == 1, after
    return source.split(before, 1)[1].split(after, 1)[0]


def main():
    current, prior, msc = (p.read_text() for p in (NEW, V14, MSC))
    marker = "<!-- BEGIN PRESERVED UC5 BODY -->"
    end = "<!-- END PRESERVED UC5 BODY -->"
    assert part(current, marker, end) == part(prior, marker, end), "UC5 changed"

    # The inherited mature profile bodies remain exact, even when the edition's
    # status and migration prose outside those sections changes.
    for n in (16, 17, 18, 19):
        start = f"## X.{n} "
        stop = f"## X.{n + 1} "
        assert part(current, start, stop) == part(prior, start, stop), f"X.{n} changed"
    assert part(current, "## C.0 Purpose and boundary\n", "## X.21 ").rstrip() == part(
        prior, "## C.0 Purpose and boundary\n", "# Appendix V —"
    ).rstrip(), "REC profile body changed"

    imported = part(current, "<!-- BEGIN INHERITED MSC/0.1 BODY -->\n",
                    "<!-- END INHERITED MSC/0.1 BODY -->")
    assert imported == msc.split("\n", 1)[1].rstrip() + "\n", "MSC body changed"

    manifest = MANIFEST.read_text()
    for name in (NEW.name, V14.name, MSC.relative_to(ROOT).as_posix()):
        digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        assert re.search(r"\| `" + re.escape(name) + r"` \|[^\n]*`" + digest + r"` \|",
                         manifest), f"missing or stale manifest hash: {name}"
    assert 'version: "0.15-experimental"' in current
    assert 'WPC-Distributed is unsupported' in current
    assert 'Python/IR-to-Lean implementation link' in current
    print("v0.15: UC5, WPC/RGP/SF/CFS, REC, MSC and source hashes verified")


if __name__ == "__main__":
    main()
