import copy
import json
from pathlib import Path
import unittest

from e7c_b1_static import (
    Checker,
    Diagnostic,
    Effect,
    Type,
    check_document,
    parse_type,
    type_json,
)


HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures" / "wp2"


class E7CB1StaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.positive = json.loads((FIXTURES / "positive.json").read_text(encoding="utf-8"))
        cls.negative = json.loads((FIXTURES / "negative.json").read_text(encoding="utf-8"))
        cls.specification = (HERE / "E7C_0.1_STATIC_SEMANTICS.md").read_text(encoding="utf-8")
        cls.checker = Checker(cls.positive["environment"])

    def test_positive_fixtures_have_exact_types_and_effects(self):
        for case in self.positive["cases"]:
            with self.subTest(case=case["id"]):
                result = self.checker.check(case["term"]).as_dict()
                self.assertEqual(result, case["expected"])

    def test_negative_fixtures_have_controlled_diagnostics(self):
        for case in self.negative["cases"]:
            with self.subTest(case=case["id"]):
                document = {"environment": self.positive["environment"], "term": case["term"]}
                result = check_document(document)
                self.assertEqual(result["status"], "diagnostic")
                self.assertEqual(result["diagnostic"]["category"], case["category"])
                self.assertEqual(result["diagnostic"]["code"], case["code"])

    def test_type_round_trip_is_canonical(self):
        source = self.positive["environment"]["variables"]["source_config"]
        parsed = parse_type(source)
        self.assertEqual(parse_type(type_json(parsed)), parsed)

    def test_rendered_types_are_unambiguous(self):
        left = parse_type(
            {
                "tag": "family",
                "args": ["I,A", {"tag": "base", "args": ["B"]}],
            }
        )
        right = parse_type(
            {
                "tag": "family",
                "args": ["I", {"tag": "base", "args": ["A,B"]}],
            }
        )
        self.assertEqual(left.render(), 'Family["I,A",Base["B"]]')
        self.assertEqual(right.render(), 'Family["I",Base["A,B"]]')
        self.assertNotEqual(left.render(), right.render())

    def test_extra_ast_fields_are_invalid_input(self):
        term = copy.deepcopy(self.positive["cases"][0]["term"])
        term["surprise"] = True
        result = check_document({"environment": self.positive["environment"], "term": term})
        self.assertEqual(result["diagnostic"]["code"], "E7C-S002")

    def test_unknown_type_tag_is_invalid_input(self):
        with self.assertRaisesRegex(Diagnostic, "unknown type tag"):
            parse_type({"tag": "truth", "args": []})

    def test_unrecognised_domain_policy_is_rejected_eagerly(self):
        environment = copy.deepcopy(self.positive["environment"])
        environment["maps"]["strict_normalise"]["domain_policy"] = "maybe"
        result = check_document({"environment": environment, "term": {"tag": "var", "name": "source_config"}})
        self.assertEqual(result["diagnostic"]["code"], "E7C-S010")

    def test_unrecognised_map_type_domain_policy_is_rejected(self):
        with self.assertRaises(Diagnostic) as raised:
            parse_type(
                {
                    "tag": "map",
                    "args": [
                        {"tag": "base", "args": ["A"]},
                        {"tag": "base", "args": ["B"]},
                        "maybe",
                        "map-1",
                    ],
                }
            )
        self.assertEqual(raised.exception.code, "E7C-S010")
        self.assertEqual(raised.exception.path, "$.type.args[2]")

    def test_outcome_typed_variable_is_admitted_as_terminal_only(self):
        result = self.checker.check({"tag": "var", "name": "terminal_result"})
        self.assertEqual(result.type.tag, "outcome")

    def test_directly_nested_outcome_is_rejected(self):
        with self.assertRaises(Diagnostic) as raised:
            parse_type(
                {
                    "tag": "outcome",
                    "args": [
                        {
                            "tag": "outcome",
                            "args": [{"tag": "config", "args": ["Sigma-A"]}, "core-1"],
                        },
                        "core-2",
                    ],
                }
            )
        self.assertEqual(raised.exception.code, "E7C-S013")

    def test_outcome_nested_inside_value_constructor_is_rejected(self):
        with self.assertRaises(Diagnostic) as raised:
            parse_type(
                {
                    "tag": "family",
                    "args": [
                        "I",
                        {
                            "tag": "outcome",
                            "args": [
                                {"tag": "config", "args": ["Sigma-A"]},
                                "core-1",
                            ],
                        },
                    ],
                }
            )
        self.assertEqual(raised.exception.code, "E7C-S013")

    def test_restriction_cannot_consume_family_of_outcomes(self):
        environment = copy.deepcopy(self.positive["environment"])
        environment["restrictions"]["select_J"]["element"] = {
            "tag": "outcome",
            "args": [{"tag": "config", "args": ["Sigma-A"]}, "core-1"],
        }
        result = check_document(
            {
                "environment": environment,
                "term": {
                    "tag": "restrict",
                    "declaration": "select_J",
                    "arg": {"tag": "var", "name": "source_family"},
                },
            }
        )
        self.assertEqual(result["diagnostic"]["code"], "E7C-S013")
        self.assertEqual(
            result["diagnostic"]["path"],
            "$.environment.restrictions.select_J.element",
        )

    def test_map_cannot_consume_outcome_without_eliminator(self):
        environment = copy.deepcopy(self.positive["environment"])
        environment["maps"]["strict_normalise"]["source"] = {
            "tag": "outcome",
            "args": [{"tag": "config", "args": ["Sigma-A"]}, "core-1"],
        }
        result = check_document(
            {"environment": environment, "term": {"tag": "var", "name": "source_config"}}
        )
        self.assertEqual(result["diagnostic"]["code"], "E7C-S013")

    def test_map_cannot_produce_nested_outcome(self):
        environment = copy.deepcopy(self.positive["environment"])
        environment["maps"]["strict_normalise"]["target"] = {
            "tag": "outcome",
            "args": [{"tag": "config", "args": ["Sigma-B"]}, "core-1"],
        }
        result = check_document(
            {"environment": environment, "term": {"tag": "var", "name": "source_config"}}
        )
        self.assertEqual(result["diagnostic"]["code"], "E7C-S013")

    def test_checker_snapshots_declarations_at_admission(self):
        environment = copy.deepcopy(self.positive["environment"])
        checker = Checker(environment)
        environment["maps"]["strict_normalise"]["domain_policy"] = "total"
        result = checker.check(
            {
                "tag": "apply",
                "declaration": "strict_normalise",
                "arg": {"tag": "var", "name": "source_config"},
            }
        )
        self.assertIn(
            Effect(
                "partiality",
                '{"domain_policy":"strict","failure_family":"domain-errors-1","map_declaration":"strict_normalise","map_edition":"map-1"}',
            ),
            result.effects,
        )

    def test_non_object_document_is_controlled_invalid_input(self):
        result = check_document([])
        self.assertEqual(result["diagnostic"]["category"], "invalid_input")

    def test_declared_effect_row_is_deduplicated(self):
        result = self.checker.check(
            {
                "tag": "view",
                "declaration": "lossy_projection",
                "arg": {"tag": "var", "name": "source_config"},
            }
        )
        self.assertEqual(len(result.effects), len(set(result.effects)))

    def test_structured_loss_payloads_are_unambiguous(self):
        left_environment = copy.deepcopy(self.positive["environment"])
        right_environment = copy.deepcopy(self.positive["environment"])
        left_environment["views"]["lossy_projection"]["excluded_observations"] = ["a,b", "c"]
        right_environment["views"]["lossy_projection"]["excluded_observations"] = ["a", "b,c"]
        term = {
            "tag": "view",
            "declaration": "lossy_projection",
            "arg": {"tag": "var", "name": "source_config"},
        }
        left = Checker(left_environment).check(term)
        right = Checker(right_environment).check(term)
        self.assertNotEqual(left.effects, right.effects)

    def test_lossy_projection_is_not_exactly_reconstructable(self):
        result = self.checker.check(
            {
                "tag": "view",
                "declaration": "lossy_projection",
                "arg": {"tag": "var", "name": "source_config"},
            }
        )
        self.assertEqual(result.type.tag, "projection")
        with self.assertRaises(Diagnostic) as raised:
            self.checker.check(
                {
                    "tag": "reconstruct",
                    "declaration": "exact_reconstruction",
                    "resource_policy": "bounded-100",
                    "arg": {
                        "tag": "view",
                        "declaration": "lossy_projection",
                        "arg": {"tag": "var", "name": "source_config"},
                    },
                }
            )
        self.assertEqual(raised.exception.code, "E7C-T002")

    def test_projection_cannot_claim_exact_source_return(self):
        environment = copy.deepcopy(self.positive["environment"])
        environment["views"]["lossy_projection"]["reconstruction_obligation"] = (
            "exact_source_return"
        )
        result = check_document(
            {"environment": environment, "term": {"tag": "var", "name": "source_config"}}
        )
        self.assertEqual(result["diagnostic"]["code"], "E7C-S011")

    def test_input_depth_limit_is_controlled(self):
        term = {"tag": "var", "name": "source_config"}
        for _ in range(70):
            term = {"tag": "apply", "declaration": "total_identity", "arg": term}
        result = check_document({"environment": self.positive["environment"], "term": term})
        self.assertEqual(result["status"], "diagnostic")
        self.assertEqual(result["diagnostic"]["category"], "invalid_input")
        self.assertEqual(result["diagnostic"]["code"], "E7C-S012")

    def test_input_node_limit_is_controlled(self):
        document = {"environment": self.positive["environment"], "term": [None] * 10_001}
        result = check_document(document)
        self.assertEqual(result["status"], "diagnostic")
        self.assertEqual(result["diagnostic"]["code"], "E7C-S012")

    def test_denotational_or_phase_equality_is_not_conversion(self):
        left = Type("config", ("Sigma-A",))
        right = Type("config", ("Sigma-B",))
        with self.assertRaises(Diagnostic) as raised:
            self.checker._expect(left, right, "$.term")
        self.assertEqual(raised.exception.code, "E7C-T002")

    def test_checker_has_no_evaluation_entrypoint(self):
        self.assertFalse(hasattr(self.checker, "evaluate"))

    def test_every_executable_constructor_has_a_specification_rule(self):
        for heading in (
            "### Variable",
            "### Map application",
            "### View",
            "### Restriction",
            "### Reconstruction",
            "### Classification",
        ):
            self.assertIn(heading, self.specification)

    def test_specification_preserves_wp2_boundary(self):
        normalized = " ".join(self.specification.split())
        for boundary in (
            "does not define evaluation",
            "never consulted by the checker",
            "not a decision for the abstract calculus",
            "does not certify completeness",
        ):
            self.assertIn(boundary, normalized)

    def test_specification_defines_bounded_effect_contract(self):
        normalized = " ".join(self.specification.split()).lower()
        for contract in (
            r"\varepsilon_1 \subseteq \varepsilon_2",
            "sequential composition and the path-insensitive branch join are both set union",
            r"\mathsf{atoms}(\lambda) \subseteq \varepsilon",
        ):
            self.assertIn(contract, normalized)


if __name__ == "__main__":
    unittest.main()
