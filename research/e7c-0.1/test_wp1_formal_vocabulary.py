from pathlib import Path
import re
import unittest


HERE = Path(__file__).resolve().parent


class WP1FormalVocabularyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.charter = (HERE / "E7C_0.1_CHARTER.md").read_text(encoding="utf-8")
        cls.vocabulary = (HERE / "E7C_0.1_FORMAL_VOCABULARY.md").read_text(encoding="utf-8")
        cls.modules = (HERE / "E7C_0.1_PROFILE_MODULE_CONTRACT.md").read_text(encoding="utf-8")

    def test_candidate_nucleus_families_are_typed(self):
        rows = re.findall(r"^\| `([^`]+)` \| ([^|]+) \|", self.vocabulary, re.MULTILINE)
        expected = {"Entity[K]", "Description[A,R]", "Config[S]", "Map[A,B_t,D,P]",
                    "View[A,V,Q]", "Encoding[A,R,S]", "History[A,H]",
                    "Outcome[A,X]", "Ledger[E]", "Witness[J,W]"}
        self.assertTrue(expected <= {name for name, _ in rows})
        self.assertTrue(all(parameters.strip() for _, parameters in rows))
        for meta_sort in ("EntityKind", "ConfigSignature", "RepresentationContract",
                          "DomainPolicy", "MapEdition", "InquiryId", "HistoryPolicy",
                          "OutcomeExtensionEdition", "EffectVocabularyEdition",
                          "JudgementClass", "WitnessEdition", "IndexSignature",
                          "ResourcePolicy"):
            self.assertIn(f"`{meta_sort}`", self.vocabulary)

    def test_equality_judgements_are_separate_and_conversion_is_bounded(self):
        for marker in ("equiv_{\\mathsf{def}}", "=_{\\mathsf{den}}",
                       "approx_{\\mathsf{obs}}", "sim_{\\mathsf{phase}}"):
            self.assertIn(marker, self.vocabulary)
        self.assertIn(
            "No observational, phase, representation or reconstruction relation licenses\n"
            "type conversion",
            self.charter,
        )

    def test_effects_and_runtime_ledger_are_distinct(self):
        self.assertIn("static effect bound", self.vocabulary)
        self.assertIn("runtime effect/loss ledger", self.vocabulary)
        for dimension in ("partiality", "loss", "inquiry", "access", "authority",
                          "alternatives", "evidence", "history", "resources", "bridge"):
            self.assertIsNotNone(
                re.search(rf"^\| {dimension} \|", self.vocabulary, re.MULTILINE),
                dimension,
            )

    def test_adapter_dispositions_are_closed(self):
        for disposition in ("faithful_embedding",
                            "faithful_interpretation_with_explicit_loss",
                            "partial_translation", "unsupported"):
            self.assertIn(f"`{disposition}`", self.modules)

    def test_wp1_does_not_authorize_implementation(self):
        combined = self.charter + self.vocabulary + self.modules
        self.assertIn("no evaluation rules", combined.lower())
        self.assertIn("does not itself authorize WP2/WP3", combined)


if __name__ == "__main__":
    unittest.main()
