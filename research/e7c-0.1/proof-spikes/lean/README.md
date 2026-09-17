# E7C/0.1 common spike — Lean 4 candidate

Status: `implementation_in_progress; executable_result_pending`

Baseline: merge commit `f8748d315bdfc22546d9172c33138ac1a8799f0c`

This bounded candidate instantiates the common proof-assistant spike recorded in
`E7C_0.1_PROOF_ASSISTANT_SELECTION.md`. It is a comparison artifact, not the E7C
calculus and not a release-profile implementation.

## Covered nucleus

- explicit `Config`, `Outcome Config` and strict `Map Config Config` types;
- binder-free variables and unary strict-map application;
- finite list-backed reusable term and map contexts;
- capture-free substitution for the binder-free syntax;
- explicit `success` and `domainError` outcomes;
- finite list-backed interpretation tables without host callbacks;
- typing substitution;
- successful type preservation for the bounded evaluator; and
- strict-map out-of-domain failure distinct from every success, including
  `success (config 0)`.

The preservation theorem is intentionally narrow: its runtime has only config
and text values, strict tables map natural-number config codes to config codes,
and it says nothing about the full WP3-S denotation or WP3-I replay machine.

## Reproducibility record

| Item | Record |
| --- | --- |
| Tool | Lean 4 `v4.34.0` |
| Toolchain pin | `leanprover/lean4:v4.34.0` in `lean-toolchain` |
| Standard library | `Std` bundled with the pinned Lean distribution; no external packages |
| Build command | `lake build` from this directory |
| Admissions | none intended; CI build and axiom audit pending |
| Axioms | Lean's standard `propext`, explicitly allowlisted; no user axiom intended |
| Generated proof code | none |
| Trusted base | pinned Lean compiler/kernel, Lean's standard `propext`, bundled Lake/Std, and the host/build chain used to execute them |

The initial builder environment did not contain Lean, Rocq or Isabelle. The
repository workflow therefore performs the first executable Lean build and
axiom audit. Until that workflow succeeds and its exact head is reviewed, this
artifact does not carry an executable-spike acceptance verdict.

## Non-claims

This artifact does not establish proof of the E7C metatheory, E7C or E7G-T
conformance, implementation correctness, semantic soundness, source truth,
domain validity, production readiness, comparative superiority of Lean, or an
independent review result. Lean remains the provisional first candidate because
it can be exercised in the available CI environment; Rocq and Isabelle have not
been compared here.
