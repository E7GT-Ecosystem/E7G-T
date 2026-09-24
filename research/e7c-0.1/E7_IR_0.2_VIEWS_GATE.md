# WP6 — source-preserving and lossy view IR slice

Status: `draft_review_candidate; selected_bounded_fragment_only`.
Base: PR #87 merge `6fda83b3913b1d87022f556ad8f771949d5e7bcf`.
Branch: `codex/e7c-ir-views`; exact head in PR metadata.
Edition: `E7-IR/0.2-view-var-B1-provisional`.

The admitted terms are `view(source_preserving_inventory, var
source_config)` and `view(lossy_projection, var source_config)` over the
finite configuration carrier established in PR #85. This adds two typed
instructions with pinned source/target types, policy kind, inquiry,
preserved and excluded observations, quotient relation, reconstruction
obligation, static effects, location and content identity. A projection
never acquires a source-return token from its representation.

Each canonical IR envelope includes the full source document, a complete
inline witness accepted by the separately implemented checker, and a
versioned typed variable instruction. The independent view executor
precharges parent then child, records inquiry, optionally records loss,
records alternatives, checks capability and obligation, then returns the
finite table representation. `compare_replay` compares terminal result,
ledger and resource progress with the replayed source claim. As in the
earlier WP6 slices, the IR success remains unbound and reports the checked
source witness identifier separately.

Committed complete packages:

- `fixtures/wp5_ir/source_graph_view.json`: retained exact source token;
- `fixtures/wp5_ir/lossy_graph_projection.json`: null source token and an
  explicit loss ledger entry.

The conventional baseline is a plain finite lookup of three configurations
and their selected representations; it does not call either evaluator.
Tests cover two policies, three bindings, three step budgets, four ledger
budgets and three guard cases (216 comparisons), edition/identity and
source-token tampering, and an essential rejected-composition example.

The source checker rejects `apply(strict_normalise,
apply(total_identity,var source_config))`: the inner map returns
`Outcome[Config["Sigma-A"],"core-1"]`, while the outer requires a
`Config["Sigma-A"]` argument. Any future `bind`/outcome-elimination
constructor needs an explicit new type/effect/dynamic rule, failure
propagation, ledger order and proof obligations. This package makes no
implicit extraction or source language revision.

Reproduce with `python -m unittest discover -s research/e7c-0.1 -p
'test_e7_ir_views_b1.py' -v`. The result is a finite internal differential,
not profile-wide fidelity, general lowering adequacy, source truth,
independent external reproduction or product readiness. Existing canonical
and product contracts remain unchanged.
