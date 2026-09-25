"""Selected RGP/0.2 contextual-expression cases for both draft editions."""

from dataclasses import replace
import unittest

from rgp02_expression_b1 import (AdmissionError, Context, ExpressionRule,
                                 Whole, decode, encode, express)


def fixture(kernel):
    base = Whole(kernel, "source-edition-A", (("hidden", "alpha"),
                                               ("visible", "same")))
    context = Context("reader", "t0", "r0", "local", "scope-A", "question-A")
    rule = ExpressionRule("display/1", base.edition, "sr4/1", ("visible",),
                          ("reader",), "local", "read_only")
    return base, context, rule


class RGP02Expression(unittest.TestCase):
    def test_pinned_success_and_distinct_sorts(self):
        for kernel in ("0.13-experimental-draft", "0.14-experimental-draft"):
            with self.subTest(kernel=kernel):
                whole, context, rule = fixture(kernel)
                first, second = (encode(whole, i, "sr4/1") for i in ("left", "right"))
                self.assertEqual(decode(first, "sr4/1"), whole)
                x, y = express(first, context, rule, 1), express(second, context, rule, 1)
                self.assertEqual((x.tag, y.tag), ("success", "success"))
                self.assertEqual(x.expression.fields, y.expression.fields)
                self.assertEqual(x.expression.fields,
                                 tuple((key, dict(whole.fields)[key])
                                       for key in rule.selected))
                self.assertNotEqual(x.expression.occurrence, y.expression.occurrence)
                self.assertNotEqual(x.expression, whole)
                self.assertEqual(x.expression.lost, ("hidden",))
                other = Whole(kernel, "source-edition-A", (("hidden", "beta"),
                                                           ("visible", "same")))
                z = express(encode(other, "left", "sr4/1"), context, rule, 1)
                self.assertEqual(z.expression.fields, x.expression.fields)
                self.assertNotEqual(z.expression.source_identity, x.expression.source_identity)

    def test_context_authority_resource_and_unavailable_mode(self):
        whole, context, rule = fixture("0.13-experimental-draft")
        portion = encode(whole, "left", "sr4/1")
        self.assertEqual(express(portion, context, rule, 0).tag, "resource_limit")
        self.assertEqual(express(portion, replace(context, role="guest"), rule, 1).tag,
                         "unsupported")
        self.assertEqual(express(portion, context,
                                 replace(rule, mode="generative"), 1).tag, "unsupported")
        self.assertEqual(express(portion, context,
                                 replace(rule, selected=("missing",)), 1).tag,
                         "undetermined")
        self.assertEqual(express(portion, context,
                                 replace(rule, source_edition="other"), 1).tag,
                         "domain_error")

    def test_cross_edition_and_tampering(self):
        a, context, rule = fixture("0.13-experimental-draft")
        b, _, _ = fixture("0.14-experimental-draft")
        self.assertNotEqual(a.identity, b.identity)
        first, second = encode(a, "left", "sr4/1"), encode(b, "right", "sr4/1")
        self.assertNotEqual(decode(first, "sr4/1").kernel,
                            decode(second, "sr4/1").kernel)
        for corrupted in (replace(first, source_edition="other"),
                          replace(first, payload=first.payload[:-1]),
                          replace(first, source_identity=second.source_identity)):
            with self.subTest(corrupted=corrupted), self.assertRaises(AdmissionError):
                express(corrupted, context, rule, 2)
        with self.assertRaises(AdmissionError):
            decode(first, "sr4/old")


if __name__ == "__main__":
    unittest.main()
