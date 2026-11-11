# E7G-T GCD/0.2 — Isolated research package

**Status:** non-canonical mathematical research package, integrated in the source repository for inspection; not promoted to the kernel and not production-ready. Based on the supplied `GCD/0.1` proposal and checked against the unchanged `E7G-T v0.15-experimental-MSC1`. Existing product/profile pins remain unchanged.

Only the explicit typed carriers, laws, witnesses and test results are part of this mathematical research. Historical motivations do not form assumptions, axioms or evidence.

This package implements **semantic differentiation versus access refinement**, **within-signature generation**, **structural-kind signature generation**, **criterion-relative novelty**, **grounding and old-choice preservation**, **explicit selection with immutable logical act identity**, **typed chosen-description-to-family adapter**, **model-only (not external) commitment**, **finite rank/lineage**, and **deterministic content-addressed replay**.

## Start here

1. Read `GCD_0.2_RESEARCH_SPECIFICATION.md` for types, laws, domains and conformance scope.
2. Run `python3 test_gcd02.py --json-report evidence/conformance_run.json`.
3. Run `python3 make_evidence.py` to regenerate the end-to-end and negative-case evidence.
4. Run `python3 replay_all.py evidence/end_to_end_receipts.json evidence/negative_receipts.json`.
5. Read `INDEPENDENT_REVIEW_HANDOFF.md` before external evaluation.

No packages, secrets, network access or third-party services are required. The evaluator's hard-coded model authorisation grant is **not** production authentication.

## Files

| File | Purpose |
|---|---|
| `GCD_0.2_RESEARCH_SPECIFICATION.md` | Formal research specification and exact finite carrier |
| `gcd02.py` | Bounded typed evaluator and deterministic witness/replay API |
| `test_gcd02.py` | Unit checks and exhaustive bounded enumerations |
| `make_evidence.py` | Produces deterministic example and negative-case receipt packets |
| `replay_all.py` | Re-evaluates and verifies recorded receipts |
| `evidence/` | First-party conformance logs, generated receipts and replay report |
| `COMPATIBILITY_MATRIX.md` | Edition-pinned v0.15 compatibility posture |
| `MATHEMATICAL_RESEARCH_SCOPE.md` | Mathematics-only scope and interpretation boundary |
| `RESEARCH_LIMITATIONS_AND_OBLIGATIONS.md` | Open proof, security, empirical and promotion gates |
| `INDEPENDENT_REVIEW_HANDOFF.md` | Reproduction and review instructions |
| `SHA256SUMS.txt` | File manifest for exact delivered package |

## Primary outcome

The model illustrates additional evidence obligations that a bare branch label or version-control diff does not provide *by itself*. It does **not** demonstrate that a well-engineered state machine/event log cannot implement them, or that GCD has empirical superiority. The central next question for external review is whether the **reusable, typed witness discipline** justifies its integration cost.
