"""Pin the exact Python AST of the four selected implementation entry points.

This detects changes to reviewed branches, loops and serialization calls.
It is a source-identity check, not a proof of CPython semantics.
"""

import ast
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENTRY_POINTS = {
    ("e7c_eecq_joint_restrict_b1.py", "evaluate"):
        "685451517407181e7497969e26a0e459251bccbb312fd5eb6e8999c84b97d1e8",
    ("e7_ir_eecq_joint_restrict_b1.py", "execute"):
        "2b15481321215e93ab678555944487861448cd633034db38e4ebffa7855aa01c",
    ("e7c_eecq_two_stage_b1.py", "evaluate"):
        "98587004312e6ff76d8e26e12fa086aa9e55f8ce0368fa2d3eee7bbf48021979",
    ("e7_ir_eecq_two_stage_b1.py", "execute"):
        "efbe7c90190ea053c7633af7cbad48fad087e39474f9a851d392e5a38a77992b",
}


def fingerprint(code: str, entry: str) -> str:
    nodes = [n for n in ast.parse(code).body if isinstance(n, ast.FunctionDef)
             and n.name == entry]
    if len(nodes) != 1:
        raise ValueError("entry point missing or duplicated")
    return hashlib.sha256(ast.dump(nodes[0], include_attributes=False).encode()).hexdigest()


def check_repository() -> None:
    for (name, entry), expected in ENTRY_POINTS.items():
        if fingerprint((ROOT / name).read_text(), entry) != expected:
            raise ValueError("implementation AST changed: " + name)
