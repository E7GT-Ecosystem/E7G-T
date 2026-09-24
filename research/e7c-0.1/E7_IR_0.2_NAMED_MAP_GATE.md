# WP6 — versioned named-map IR, finite var operand

Status: `draft_review_candidate; selected_bounded_fragment_only`.
Base: PR #86 merge `0a5267ab3bd83cb33b8aa5d650eefe3572a4f81b`.
Branch: `codex/e7c-ir-named-maps` (review head recorded in PR metadata).
IR edition: `E7-IR/0.2-named-map-var-B1-provisional`.

The successor retains the v0.1 var and strict-map editions unchanged. It
admits exactly two previously declared B1 maps over `var source_config`:
`strict_normalise` (strict, `Config["Sigma-A"]` to `Config["Sigma-B"]`)
and `total_identity` (total, `Config["Sigma-A"]` to itself). The typed
instruction pins the declared input and output types, map edition, domain
policy, static effects, source location, deterministic identity and required
capability. Parser validation reconstructs these fields from the complete
source package, validates the argument's var IR and independently replays
the inline source witness. Unknown constructors, editions, output types or
rebound argument packages fail admission.

The separate IR executor handles the parent/child step precharges, evidence
ledger and strict-only partiality ledger, capability/obligation guard and
finite interpretation case. `compare_replay` checks terminal tag/value or
diagnostic, ordered ledger and resource progress against the replayed source
claim, leaving the IR witness slot unbound and reporting the source witness
ID separately. The source supplies the meaning; an IR digest does not
authenticate a source. There is no general map or complete source/IR
observable-equivalence theorem.

The canonical fixture `fixtures/wp5_ir/total_graph_map.json` supplies the
complete source document and witness for the total map over the selected
FG3 graph. Tests also exercise both maps across three values, three step
budgets, three ledger budgets and three guard cases (162 comparisons), and
compare admitted terminal results to a plain finite control table. The
total map writes evidence but no partiality entry; the strict map records
both in order, including cases that subsequently fail. Resource exhaustion
precedes lookup or guard when its bound is reached.

Reproduce:

```sh
python -m unittest discover -s research/e7c-0.1 -p 'test_e7_ir_named_maps_b1.py' -v
python -m unittest discover -s research/e7c-0.1 -p 'test_*.py' -q
```

These are internal finite differentials, not a general faithful embedding
of EEC-Q, a mechanised lowering proof, independent external review,
canonical change, product integration, or authority/source-truth claim.
Next WP6 gate: formalize typed lowering and preservation for a declared
map family beyond the fixed var operand, including compositional resource,
ledger and witness correspondence; do not silently change the existing
source map or witness semantics.
