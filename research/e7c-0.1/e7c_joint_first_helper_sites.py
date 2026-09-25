"""Check the actual helper bodies and the code sites carrying their contracts.

This produces syntactic evidence only. The semantic bridge for CPython's
comprehensions, Fraction, sorting, equality, JSON and hashlib stays open.
"""

import ast
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent
# These are complete normalized function ASTs, including their nested bodies.
FUNCTIONS = {
    ("e7c_eecq_joint_restrict_b1.py", "admit"): "02686f71546ef8d328c32e5321a7eec0d08628b50281cdbc7ebc4b4ee9900408",
    ("e7c_eecq_joint_restrict_b1.py", "rows"): "d398cd44f71be111bfb0598805813a89d445ad09c2eb6fe3b2c3e535a8ab68a0",
    ("e7c_eecq_joint_restrict_b1.py", "_row"): "93d2971bdcf3796b7e688cd1ccff45a3d4ed7934b9b7ef9d1c22cdd7b28d386f",
    ("e7c_eecq_joint_restrict_b1.py", "_graph"): "e24060d0457a10f3cf155f49966203d9eb1a4e658417fc739f243d78daa1d295",
    ("e7c_eecq_joint_restrict_b1.py", "evaluate"): "685451517407181e7497969e26a0e459251bccbb312fd5eb6e8999c84b97d1e8",
    ("adapters/eec_q_fg3_joint_b1.py", "joint"): "895a144ef2ed8c98c6c436cee9c4591cc07bb7a68d2e7cb9ff69a89f2100231f",
    ("adapters/eec_q_fg3_joint_b1.py", "restrict_joint_absent"): "61c00515756ed00fa6060cf967ace958b79ac560dab04635a3ab6b737e451c06",
    ("adapters/eec_q_fg3_joint_b1.py", "Joint.__post_init__"): "bf054e3ee0a2271a49a122b1350a54afc8a9f77685f81796cc93fe19e0778b27",
    ("adapters/eec_q_fg3_b1.py", "Config.__post_init__"): "ba7d6085689cebeaffb4a5d46dbf5a15c09e405c54e34f4e97381178ee967d65",
    ("adapters/eec_q_fg3_b1.py", "Config.identity"): "226291c923dd5694adb2898c8fde025d2f3d4cda7e51048cbd1c32452c7a6133",
    ("e7c_b1_canonical.py", "canonical_key"): "096482aeb7dbfae03622a51897378a2e9ab863e4f829ed3fb13adefc85955a2c",
    ("e7c_b1_canonical.py", "canonical_bytes"): "d3f4d158929ed058cddd4b86f8e60d1a51acf62a228f773150347abfcd070019",
    ("e7c_b1_canonical.py", "digest"): "e13f92c4baf84eccba089dc18b96bead3711049b841548a7f556f53505c9fd34",
    ("e7c_b1_canonical.py", "require_canonical_json"): "201c5a74316b65b26508d120ed3801a15b9bb3d0dfbe8e02b25181ac9342405d",
    ("e7_ir_eecq_joint_restrict_b1.py", "instruction"): "70b39f21df2dc833c153cbdafac2190ebf1c74e18499b67566826e148fb3fd41",
    ("e7_ir_eecq_joint_restrict_b1.py", "lower"): "e3ee2d1b7798b84d9f23d8ab19b78075ce7e57abc798869758c595b4b7b38160",
    ("e7_ir_eecq_joint_restrict_b1.py", "serialize"): "5c350948c11575446a9ded695a81e902c7273d668871c444d31f85ce097e3af3",
    ("e7_ir_eecq_joint_restrict_b1.py", "parse"): "ffe50e5682c2f0ab2bb05681266ebcba86d8ea5c0322d105ec4186be0f908a8f",
    ("e7_ir_eecq_joint_restrict_b1.py", "execute"): "2b15481321215e93ab678555944487861448cd633034db38e4ebffa7855aa01c",
}


def function(code, qualified):
    scope = ast.parse(code).body
    for part in qualified.split("."):
        matches = [n for n in scope if isinstance(n, (ast.FunctionDef, ast.ClassDef))
                   and n.name == part]
        if len(matches) != 1:
            raise ValueError("helper missing or ambiguous: " + qualified)
        node = matches[0]
        scope = node.body
    return node


def exact(node, expected):
    return ast.dump(node, include_attributes=False) == ast.dump(
        ast.parse(expected).body[0], include_attributes=False)


def checked_sites(files=None):
    """Reject an unpinned helper or any change to the critical contract sites."""
    files = files or {name: (ROOT / name).read_text() for name, _ in FUNCTIONS}
    nodes = {}
    for (name, qualified), fingerprint in FUNCTIONS.items():
        node = function(files[name], qualified)
        digest = hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()
        if digest != fingerprint:
            raise ValueError("helper AST changed: " + name + ":" + qualified)
        nodes[qualified] = node

    admit = nodes["admit"]
    # The source only returns the Joint after this explicit ordered wire-row
    # equality guard; a helper return bypassing it invalidates the contract.
    guards = [n for n in ast.walk(admit) if isinstance(n, ast.If)
              and ast.unparse(n.test) == "rows(value) != source['rows']"]
    if len(guards) != 1 or not any(isinstance(n, ast.Raise) for n in guards[0].body):
        raise ValueError("admission lacks ordered-row postcondition")
    if not isinstance(admit.body[-1], ast.Try) or not any(
            isinstance(n, ast.Return) and ast.unparse(n.value) == "value"
            for n in admit.body[-1].body):
        raise ValueError("admission return moved outside checked path")

    restrict = nodes["restrict_joint_absent"]
    comprehensions = [n for n in ast.walk(restrict) if isinstance(n, ast.ListComp)]
    if len(comprehensions) != 2:
        raise ValueError("partition must select exactly two portions")
    tests = [ast.unparse(comp.generators[0].ifs[0]) for comp in comprehensions]
    if tests != ["edge not in atoms[coordinate].edges",
                 "edge in atoms[coordinate].edges"]:
        raise ValueError("partition predicates no longer complement")
    for comp in comprehensions:
        if len(comp.generators) != 1 or ast.unparse(comp.generators[0].iter) != "source.terms" \
                or ast.unparse(comp.elt) != "(c, atoms)":
            raise ValueError("partition changed joint row or order")
    if not exact(restrict.body[-1],
                 "return joint(retained, arity=source.arity), joint(excluded, arity=source.arity)"):
        raise ValueError("partition normalization or returned portions changed")

    source_evaluate = function(files["e7c_eecq_joint_restrict_b1.py"], "evaluate")
    finish = next(n for n in source_evaluate.body if isinstance(n, ast.FunctionDef)
                  and n.name == "finish")
    progress = next(n for n in source_evaluate.body if isinstance(n, ast.FunctionDef)
                    and n.name == "progress")
    if not any(exact(n, 'witness["id"] = digest(witness)') for n in finish.body):
        raise ValueError("witness serialization loses digest binding")
    if not any(isinstance(n, ast.Return) and "ledger_prefix" in ast.unparse(n)
               and "copy.deepcopy(ledger)" in ast.unparse(n) for n in progress.body):
        raise ValueError("progress loses independent ledger snapshot")
    return {"admission": "guarded_ordered_wire_rows",
            "partition": "complementary_authoritative_joint_filters",
            "serialization": "deepcopied_ledger_and_digest_bound_witness",
            "ir": "pinned_lower_parse_serialize_helpers"}
