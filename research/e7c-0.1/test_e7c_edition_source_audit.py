"""Check the edition text audit fails closed on drift and a changed source pin."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e7c_edition_source_audit import FILES, ROOT, SourceDrift, audit, audit_pinned


class EditionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.texts = tuple((ROOT / p).read_text(encoding="utf-8") for p in FILES)

    def test_pinned_editions(self):
        self.assertEqual(len(audit_pinned()), 6)

    def test_inherited_sf_mutation_is_detected(self):
        texts = list(self.texts)
        texts[2] = texts[2].replace("## X.16 Optional symbolic families", "## X.16 Optional altered families", 1)
        with self.assertRaisesRegex(SourceDrift, "v0.14 SF"):
            audit(tuple(texts))

    def test_inherited_wpc_mutation_is_detected(self):
        texts = list(self.texts)
        texts[2] = texts[2].replace("## X.19 Optional reciprocal whole", "## X.19 Optional altered whole", 1)
        with self.assertRaisesRegex(SourceDrift, "v0.14 WPC"):
            audit(tuple(texts))

    def test_operative_eec_mutation_is_detected(self):
        texts = list(self.texts)
        texts[1] = texts[1].replace("## X.6 Viewing, identification", "## X.6 Collapsing identification", 1)
        with self.assertRaisesRegex(SourceDrift, "v0.13 EEC-Q"):
            audit(tuple(texts))


if __name__ == "__main__":
    unittest.main()
