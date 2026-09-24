# WP6 — strict named-map IR successor, finite graph case

Status: `draft_review_candidate; no_general_IR_or_profile_promotion`.
Base: PR #85 merge `2a31ec2a810d1cee8a0c8f0300b56d6250b54cd0`.
IR edition: `E7-IR/0.1-strict-map-var-B1-provisional`. Source and all
adapter editions remain pinned by the WP5/IR integration matrix and the
inline document. This edition is a successor capability, not a change to the
earlier `E7-IR/0.1-var-B1-provisional` instruction.

## What runs

The only admitted program is `strict_normalise(var source_config)` on the
finite `Config["Sigma-A"]` carrier from PR #85. Lowering checks the complete
source document and emits a canonical, content-identified envelope containing
the source document, a complete inline source witness, a separately admitted
var IR, its source digest and the mandatory strict-map capability. Parsing
rejects unknown editions/capabilities, changed values or argument IR,
different source runtime packages, missing material and witnesses that fail
the independent B1 replay checker.

The independent two-step IR executor charges the outer application and the
argument read, appends evidence then partiality entries, checks capability
and obligation, and uses the finite table for the terminal result. The
`compare_replay` gate compares the IR result with the independently replayed
source claim, including terminal tag/value or diagnostic, ledger order and
resource progress. Source success binds a witness identifier; the IR result
keeps `optional_witness=null` and the comparison returns the checked source
witness identifier separately. No IR witness or full observable equivalence
has been proved.

The committed `fixtures/wp5_ir/strict_graph_map.json` includes every byte of
the canonical IR envelope, source document and replay witness. Its successful
graph input maps to `{"id":"A"}`. The conventional reference in the test is
an explicit finite control table for the selected graph and one outside-domain
case; it neither calls the E7C source evaluator nor the IR executor.

Tests cover 4 step budgets × 4 ledger budgets × 4 capability/domain/obligation
cases (64 comparisons), canonical round trip and replay, and changed witness,
argument binding and mandatory capability with recomputed outer identities.
Run `python -m unittest discover -s research/e7c-0.1 -p
'test_e7_ir_strict_map_b1.py' -v` from the repository root.

This does not translate FG3 state addition, map push or general EEC-Q
operations into E7C. The graph is still an opaque nominal configuration in a
test carrier. Witness checking establishes internal reproducibility under
explicit assumptions, not source truth or external authority. Extending WP6
requires a versioned general map instruction with proof obligations for
typed preservation, effects, resource and witness correspondence, and
independent profile differentials before any canonical or product promotion.
