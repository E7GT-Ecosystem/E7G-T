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
        expected = {"Entity[K]", "Description[A,rho]", "Config[Sigma]",
                    "Map[A,B_t,delta,mu]", "View[A,V,iota]",
                    "Encoding[A,V,rho,tau]", "History[A,eta]",
                    "Outcome[A,xi]", "Ledger[epsilon_d]", "Witness[j,omega]"}
        families = {name for name, _ in rows}
        self.assertTrue(expected <= families)
        self.assertTrue(all(parameters.strip() for _, parameters in rows))

    def test_metavariables_have_exact_declared_sorts(self):
        expected_rows = (
            "| `K` | `EntityKind` |", "| `Sigma` | `ConfigSignature` |",
            "| `rho` | `RepresentationContract` |", "| `delta` | `DomainPolicy` |",
            "| `mu` | `MapEdition` |", "| `iota` | `InquiryId` |",
            "| `eta` | `HistoryPolicy` |",
            "| `xi`, `xi_f`, `xi_p`, `xi_r`, `xi_k` | `OutcomeExtensionEdition` |",
            "| `epsilon_d` | `EffectVocabularyEdition` |",
            "| `j` | `JudgementClass` |", "| `omega` | `WitnessEdition` |",
            "| `I`, `J` | `IndexSignature` |", "| `beta` | `ResourcePolicy` |",
            "| `tau` | `RetentionStrength` |", "| `f` | `MapDeclaration` |",
            "| `q` | `ViewPolicy` |", "| `p` | `RestrictionPolicy` |",
            "| `r` | `ReconstructionPolicy` |", "| `kappa` | `CriterionId` |",
            "| `m`, `n` | `ModuleId` |", "| `e_s`, `e_t` | `EditionId` |",
            "| `a` | `AdapterId` |", "| `d` | `FidelityDisposition` |",
            "| `x` | `SuccessValue` |", "| `w_o` | `OptionalWitness` |",
            "| `diag` | `Diagnostic` |", "| `cap` | `Capability` |",
            "| `obl` | `Obligation` |", "| `bound` | `ResourceBound` |",
            "| `progress` | `ProgressRecord` |",
        )
        for row in expected_rows:
            self.assertIn(row, self.vocabulary)
        for row in (
            "| `Delta` | `SignatureEnvironment` |",
            "| `Gamma` | `VariableResourceContext` |",
            "| `Phi` | `ObligationContext` |",
            "| `epsilon` | `StaticEffectBound` |",
            "| `lambda` | `RuntimeLedger` |",
            "| `M` | `ModelId` |", "| `O` | `ObservationFamily` |",
            "| `t`, `u`, `v` | `Term` |", "| `o` | `TerminalOutcome` |",
        ):
            self.assertIn(row, self.vocabulary)
        self.assertIn("`ProfileId`, `ModuleId`, `AdapterId`, `EditionId`", self.vocabulary)

    def test_evaluation_policy_and_outcome_payloads_are_unambiguous(self):
        self.assertIn(r"\vdash_{\beta} t \Downarrow (o,\lambda)", self.vocabulary)
        self.assertIn("where `beta` is an explicit resource policy", self.vocabulary)
        self.assertNotIn(r"\vdash_{B}", self.vocabulary)
        for constructor in (
            "success(x,w_o)", "type_error(diag)", "domain_error(diag)",
            "unsupported(cap)", "undetermined(obl)",
            "resource_limit(bound,progress)", "invalid_input(diag)",
        ):
            self.assertIn(f"`{constructor}`", self.vocabulary)
        for overloaded in (
            "success(a,w)", "type_error(d)", "domain_error(d)",
            "unsupported(c)", "undetermined(p)",
            "resource_limit(b,p)", "invalid_input(d)",
        ):
            self.assertNotIn(f"`{overloaded}`", self.vocabulary)

    def test_operation_indices_and_outputs_are_consistently_typed(self):
        declarations = (
            "f:MapDeclaration[A,B_t,delta,mu]",
            "q:ViewPolicy[A,V,iota]",
            "p:RestrictionPolicy[I,J,A]",
            "r:ReconstructionPolicy[A,V,iota]",
            "`kappa:CriterionId`",
        )
        for declaration in declarations:
            self.assertIn(declaration, self.vocabulary)
        for signature in (
            r"\mathsf{apply}_{f}: A \to \mathsf{Outcome}[B_t,xi_f]",
            r"\mathsf{view}_{q}: A \to \mathsf{View}[A,V,iota]",
            r"\mathsf{Outcome}[\mathsf{Family}[J,A],xi_p]",
            r"\mathsf{reconstruct}_{r,beta}: \mathsf{View}[A,V,iota]",
            r"\mathsf{Outcome}[\mathsf{Fibre}[A,r],xi_r]",
            r"\mathsf{Outcome}[\mathsf{Partition}[A,kappa],xi_k]",
        ):
            self.assertIn(signature, self.vocabulary)

    def test_module_adapter_judgement_has_no_overloaded_or_untyped_symbols(self):
        self.assertIn(r"\Delta \vdash m@e_s\;\mathsf{module}", self.vocabulary)
        self.assertIn(r"\Delta \vdash a:m@e_s \Rightarrow n@e_t\;[d]", self.vocabulary)
        self.assertIn("`m,n:ModuleId`, `e_s,e_t:EditionId`, `a:AdapterId`, and\n"
                      "`d:FidelityDisposition`", self.vocabulary)
        for stale in ("P@e", "F:P@e", "C@c", "Encoding[A,R,S]",
                      "Family[J,A],X_p", "View[A,V,Q]"):
            self.assertNotIn(stale, self.vocabulary)

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
