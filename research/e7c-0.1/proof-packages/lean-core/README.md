# E7C/0.1 WP4 Lean core extension

Status: `draft; exact_head_review_required`

Baseline: merge commit `2dcd06c6fda9c13b9ce40500bc835912e06cd245`

This package extends the accepted bounded Lean feasibility spike with the next
small formal nucleus. It is deliberately separate from the spike so that the
accepted artifact remains unchanged and this extension can be reviewed at an
exact head.

## Covered fragment

- variables, including direct propagation of terminal outcome bindings;
- unary strict maps over finite `Config` tables;
- unary source-preserving views with explicit source return;
- finite family restrictions;
- deterministic functional evaluation and a corresponding inductive rule
  relation;
- successful value-type preservation under explicit environment and
  interpretation well-formedness premises;
- static effect membership and runtime ledger-order preservation; and
- a rule-correspondence table against the external WP2 and WP3-S documents.

The formalized well-formedness premises require unique and complete runtime
bindings, unique declarations and interpretation entries, complete
interpretations for admitted declarations, and unique finite table inputs.
Missing interpretation is represented by `unsupported`; it is not converted
to a strict-map `domainError`.

## Reproducibility

| Item | Record |
| --- | --- |
| Tool | Lean 4 `v4.34.0` |
| Toolchain pin | `leanprover/lean4:v4.34.0` |
| Dependencies | Lean core/prelude only |
| Build | `lake build` from this directory |
| Axiom audit | repository workflow, allowing Lean's standard `propext` and `Quot.sound` only |
| Workflow actions | `actions/checkout@11d5960a326750d5838078e36cf38b85af677262`; `leanprover/lean-action@50fcf42d2e460296f1a34b402e990d1b24f8b596` |
| Admissions | no `sorry`, `admit`, user axiom or opaque external oracle intended |
| Trusted base | pinned Lean compiler/kernel, bundled Lake, standard `propext` and `Quot.sound`, and CI host/build chain |

`Quot.sound` is reported only for ordered-ledger/effect containment and their
typed transport theorems. Successful type preservation and successful-ledger
exactness do not report it. The allowance is explicit rather than an assertion
that the extension retained the feasibility spike's smaller `propext`-only
audit surface; it does not permit a user axiom or `Classical.choice`.

## Review boundary and non-claims

The package is a bounded projection, not a formalization of the whole external
calculus. In particular, it omits resource indices and charge precedence,
total and filtering maps, projections, reconstruction, classification,
obligations, witness replay and denotational semantics. Effect atoms retain
only the declaration identity needed by the fragment. The external static row is represented by a duplicate-free finite list under
set membership and idempotent union. The separate `staticTrace` list preserves
repeated WP3 events and their order. The nested failing-child example is a raw
term invariant: WP2 rejects its outcome-typed operand in value position. The
typed regression instead covers strict-map domain failure and its ledger.

Passing the build, repository tests and axiom audit would establish only that
this Lean source compiles under the recorded trusted base and that the named
Lean theorems have no unallowlisted reported axioms. It would not establish
external-rule adequacy, complete E7C metatheory, conformance, implementation
correctness, semantic soundness, final proof-assistant selection, comparative
superiority of Lean, production readiness or independent review.

Lean remains the provisional implementation vehicle. This package must stay
draft and unmerged until its exact head is reviewed.
