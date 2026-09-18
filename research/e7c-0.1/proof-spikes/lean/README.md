# E7C/0.1 common spike — Lean 4 candidate

Status: `revision_addressed; exact_head_rereview_pending`

Baseline: merge commit `f8748d315bdfc22546d9172c33138ac1a8799f0c`

This bounded candidate instantiates the common proof-assistant spike recorded in
`E7C_0.1_PROOF_ASSISTANT_SELECTION.md`. It is a comparison artifact, not the E7C
calculus and not a release-profile implementation.

## Covered nucleus

- explicit `Config`, `Outcome Config` and strict `Map Config Config` types;
- binder-free variables and unary strict-map application;
- finite list-backed reusable term and map contexts;
- typed, unique and complete runtime environments and interpretation tables;
- capture-free substitution for the binder-free syntax;
- direct terminal-outcome bindings for outcome-typed variables;
- explicit `success`, `domainError` and missing-capability `unsupported` outcomes;
- finite list-backed interpretation tables without host callbacks;
- typing substitution;
- successful type preservation with environment and interpretation
  well-formedness premises explicit; and
- strict-map out-of-domain failure distinct from every success, including
  `success (config 0)`.

The preservation theorem is intentionally narrow: its runtime has only config
and text values, strict tables map natural-number config codes to config codes,
and it says nothing about the full WP3-S denotation or WP3-I replay machine.
An outcome-typed variable stores and returns a terminal outcome directly. A
missing interpretation table returns `unsupported`, while `domainError` is
reserved for a presented operand outside a strict table's domain or an
ill-typed raw value outside the theorem's admitted premises.

## Reproducibility record

| Item | Record |
| --- | --- |
| Tool | Lean 4 `v4.34.0` |
| Toolchain pin | `leanprover/lean4:v4.34.0` in `lean-toolchain` |
| Standard library | Lean core/prelude bundled with the pinned distribution; the proof module imports no external package |
| Build command | `lake build` from this directory |
| Admissions | none found by the successful build and axiom audit recorded below |
| Axioms | Lean's standard `propext`, explicitly allowlisted; no user axiom intended |
| Generated proof code | none |
| Trusted base | pinned Lean compiler/kernel, Lean's standard `propext`, bundled Lake, and the recorded host/build chain |

The initial builder environment did not contain Lean, Rocq or Isabelle. The
repository workflow therefore performs the executable Lean build and axiom
audit. At revision checkpoint `2e35b7a6e79c28b073e875b6644558c6636b3aef`,
workflow run `35368213608` built the corrected library and passed the axiom
audit with only the documented `propext` allowance. This is executable
candidate evidence, not an acceptance verdict. CI must pass again on every
later exact head, and the final exact head must still be reviewed.

The regression theorems check that an outcome variable propagates both
`success` and `domainError` directly, a missing interpretation returns
`unsupported`, and incomplete environment or interpretation records fail the
well-formedness premises.

## Non-claims

This artifact does not establish proof of the E7C metatheory, E7C or E7G-T
conformance, implementation correctness, semantic soundness, source truth,
domain validity, production readiness, comparative superiority of Lean, or an
independent review result. Lean remains the provisional first candidate because
it can be exercised in the available CI environment; Rocq and Isabelle have not
been compared here.
