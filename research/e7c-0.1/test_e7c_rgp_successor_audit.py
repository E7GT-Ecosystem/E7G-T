"""Fail closed if a predecessor clause drifts or a new typed relation vanishes."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e7c_rgp_successor_audit import FILES, ROOT, SourceDrift, audit, audit_pinned


class RGPDelta(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = tuple((ROOT / p).read_text(encoding="utf-8") for p in FILES)

    def test_pinned_sections(self):
        self.assertEqual(audit_pinned()["unchanged_v0121_to_v013"], (3, 4, 6, 7))

    def test_inherited_projection_mutation(self):
        texts = list(self.sources)
        texts[1] = texts[1].replace("### R.4 Local projection and reconstruction",
                                    "### R.4 Local projection and silent reconstruction", 1)
        with self.assertRaisesRegex(SourceDrift, "R.4"):
            audit(tuple(texts))

    def test_missing_contextual_expression(self):
        texts = list(self.sources)
        texts[1] = texts[1].replace("\\mathsf{Expresses}",
                                    "\\mathsf{Removed}", 1)
        with self.assertRaisesRegex(SourceDrift, "R.2"):
            audit(tuple(texts))

    def test_changed_v014_inheritance(self):
        texts = list(self.sources)
        texts[2] = texts[2].replace("### R.8 Recursive composition",
                                    "### R.8 Altered composition", 1)
        with self.assertRaisesRegex(SourceDrift, "v0.14 changed inherited R.8"):
            audit(tuple(texts))


if __name__ == "__main__":
    unittest.main()
