# E7C-B2 selected finite Python/Lean trace bridge

Status: `internally_tested_candidate; exact_head_review_required`.
Baseline: PR #95 merge `fe1679a231a9da4006d6835786e258165d70cb83`.
Branch: `codex/e7c-b2-finite-bridge`; exact review head in PR metadata.

This finite bridge evaluates 13 named B2 source documents. Each source
witness is independently replayed. Its versioned IR is independently
executed and compared with the source's full terminal, ledger and progress.
When the child succeeds and the continuation has a step available, a separate
B1 direct map is evaluated at the *child's successful value*, with the
remaining ledger capacity. Its two-step variable/map evaluation is related
to B2's one-step continuation: the variable read has already happened in
the child. That B1 witness is independently replayed. A separate relation
then reconstructs the B2 observation from the child and direct map, including
ordinal rebasing and the outer resource-limit bound. It must match the full
B2 source claim before any erasure for Lean.

The cases cover both continuations, a strict continuation domain error,
first and continuation capability/obligation failure, child and continuation
step limits, zero bound, and first/evidence/partiality ledger exhaustion.
`b2_lean_finite_bridge.json` pins the seed checksum, source and witness IDs,
full source claims, and the encoding tables. Ledger codes preserve static
atom and detail but omit ordinals only after exact ordered ledger comparison.
Success values and diagnostics use separate injective dictionaries over the
selected finite cases. Full resource-limit payloads and B1 optional witness
pointers are compared in Python before the Lean trace erasure.

`E7CB2FiniteBridge.lean` consists of generated, kernel-checked examples
for the abstract `E7CB2Sequence.sequence` definition, one per case. The
Python test regenerates the complete manifest and Lean file from the pinned
seed and the independently replayed source/B1/IR paths. The Lean build and
axiom audit are a separate hosted gate. No `sorry`, user axiom or admitted
oracle is introduced.

This is **finite correspondence evidence**, not a general Python/Lean
refinement theorem. The Lean model has Nat codes instead of exact nominal
types/JSON, takes a pre-evaluated B1 child, and does not enforce carrier
admission, complete interpretation, ledger capacity or witness trust. The
relation's Python assertions are first-party validation, not a formal proof
that every admitted B2 input satisfies them. B2-T05/T06 remain open, as do
general WP4/WP6/WP7 gates and independent reproduction. Published
v0.12.1/RGP2 and all product identities, schemas and APIs stay unchanged.
