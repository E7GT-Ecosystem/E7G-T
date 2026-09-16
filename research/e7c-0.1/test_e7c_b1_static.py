import copy
import json
from pathlib import Path
import unittest

from e7c_b1_static import Checker, Diagnostic, Type, check_document, parse_type, type_json


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


if __name__ == "__main__":
    unittest.main()
