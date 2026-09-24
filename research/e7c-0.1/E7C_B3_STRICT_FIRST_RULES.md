# E7C-B3/0.1: selected strict-first success sequence (provisional)

This opt-in edition tests a type-changing and potentially failing first map.
It does not revise the accepted B1 grammar or the provisional B2 edition.

## Closed construction

`sequence_success(apply(strict_normalise, source_config), total_identity_b)`
has input `Config["Sigma-A"]`, intermediate and output `Config["Sigma-B"]`,
and outcome extension `core-1`. The finite first map is strict: its admitted
input `{"id":"b","valid":false}` is outside the domain. The second map is
total over both admitted Sigma-B values (`{"id":"A"}`, `{"id":"C"}`).
Both maps have edition-bound declarations and complete finite tables. Admission
uses the B1 checker for the first application and a fresh *static-only* variable
of the exact intermediate nominal type for the second application. There is
no implicit conversion of an outcome into an input or of Sigma-A into Sigma-B.

## Selected evaluation and replay

The parent constructor costs one step. The B1 first application costs two
steps and writes its evidence and partiality ledger entries in that order,
subject to the B1 resource policy. On a non-success terminal, evaluation
returns that tag and never charges or records the continuation. Only a
successful first result can charge one more step and attempt the total map;
its evidence ledger entry precedes its table lookup. A bound reached between
the first result and continuation yields `resource_limit` with the completed
ledger prefix. The separately coded checker replays the complete B1 child
witness, reconstructs the outer result and rejects altered inputs or claims.

The canonical success and first-domain-error fixtures include the full
source, interpretation, environment, budgets, ordered ledger, child witness,
and replay envelope. The finite tests compare success with a conventional
strict-map control and cover all three source inputs, steps 0–4, ledger
bounds 0–3 and selected capability/obligation variations.

This establishes only this selected, finite construction under asserted
fixture assumptions. No general bind theorem, arbitrary continuation,
canonical migration, profile conformance or product correctness follows.

## Typed IR continuation

`E7-IR/0.4-strict-first-B3-provisional` pins the source document and complete
replayed source witness, a separately versioned typed instruction, and a
typed variable argument IR. Its executor independently charges the parent,
first map, variable and successful continuation, then interprets the two map
tables and ledger atoms. A finite differential checks the entire terminal,
ledger and resource progress against source replay for every selected input,
small resource bound and capability/obligation variation. Parsing rejects
rebound nominal types, source values and source witness claims. This finite
differential is not a general compiler-correctness proof.
