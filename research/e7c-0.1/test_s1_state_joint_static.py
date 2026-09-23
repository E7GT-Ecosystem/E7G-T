"""S1 successor exact state/joint type rules and rejection boundaries."""

import unittest

from e7c_s1_state_joint_static import EDITION, REGISTERED_MODULES, check_document, parse_type


MODULE = next(iter(REGISTERED_MODULES))


def state(signature="FG3-graph", module=MODULE):
    return {"tag": "state", "args": [module, signature]}


def var(name):
    return {"tag": "var", "name": name}


def document(term, variables=None):
    return {"edition": EDITION, "variables": variables or {"a": state(), "b": state()}, "term": term}


class StateJointStaticTests(unittest.TestCase):
    def test_registered_state_and_pair_product(self):
        product = {"tag": "independent", "left": var("a"), "right": var("b")}
        result = check_document(document(product))
        self.assertEqual(result, {"status": "ok", "type": f'Joint[State["{MODULE}","FG3-graph"],State["{MODULE}","FG3-graph"]]', "effects": [{"dimension": "resources", "payload": "finite_joint_product"}]})
        projected = check_document(document({"tag": "marginal", "coordinate": 1, "arg": product}))
        self.assertEqual(projected["type"], parse_type(state()).render())
        self.assertEqual(projected["effects"], [{"dimension": "resources", "payload": "finite_joint_product"}, {"dimension": "resources", "payload": "finite_marginal"}])

    def test_cross_module_and_unregistered_signatures_fail_admission(self):
        self.assertEqual(check_document(document(var("a"), {"a": state("different")}))["diagnostic"]["code"], "E7C-S1-004")
        self.assertEqual(check_document(document(var("a"), {"a": state(module="invented")}))["diagnostic"]["code"], "E7C-S1-004")

    def test_joint_arity_coordinate_and_malformed_coordinates(self):
        self.assertEqual(check_document(document(var("j"), {"j": {"tag": "joint", "args": [state()]}}))["diagnostic"]["code"], "E7C-S1-003")
        self.assertEqual(check_document(document(var("j"), {"j": {"tag": "joint", "args": [state(), {"tag": "base", "args": ["x"]}]}}))["diagnostic"]["code"], "E7C-S1-004")
        self.assertEqual(check_document(document({"tag": "marginal", "coordinate": True, "arg": var("j")}, {"j": {"tag": "joint", "args": [state(), state()]}}))["diagnostic"]["code"], "E7C-S1-T03")

    def test_no_implicit_state_conversion_or_nested_outcome(self):
        product = {"tag": "independent", "left": var("a"), "right": var("b")}
        self.assertEqual(check_document(document({"tag": "independent", "left": product, "right": var("a")}))["diagnostic"]["code"], "E7C-S1-T02")
        nested = {"tag": "state", "args": [MODULE, {"tag": "outcome", "args": [state(), "xi"]}]}
        self.assertEqual(check_document(document(var("j"), {"j": nested}))["status"], "diagnostic")
        outcome = {"tag": "outcome", "args": [state(), "xi"]}
        self.assertEqual(check_document(document(var("j"), {"j": outcome}))["type"], parse_type(outcome).render())

    def test_edition_is_separate_from_accepted_b1(self):
        d = document(var("a"))
        d["edition"] = "E7C-B1/0.1"
        self.assertEqual(check_document(d)["diagnostic"]["code"], "E7C-S1-004")


if __name__ == "__main__":
    unittest.main()
