# WP6 — E7-IR var-only provisional slice

Status: `merged_internal_slice; typed_binding_corrected_PR83; witness_adequacy_open`.

Base main: `f069561ee37f5908274a561843a8b40a96078440`.
Source: accepted bounded E7C WP2 and WP3-S specifications; disposable
WP3-I evaluator, explicitly without independent semantic-adequacy acceptance.
IR edition: `E7-IR/0.1-var-B1-provisional`.

This first instruction family lowers one admitted, closed `var` term after
source static checking and runtime-package admission. The IR envelope pins
the source calculus, static and dynamic rules, outcome extension and resource
policy. The correction also pins the finite interpretation edition and carries
exactly the atomic carrier lists needed for this variable type. It carries a
typed variable instruction, admitted value binding, static
effects, resource limits, structured source location, deterministic content
identities and a required capability list. Canonical JSON bytes round-trip;
unknown mandatory capabilities, unknown types, changed identities and invalid
editions are rejected. Re-bound values outside the pinned finite carrier and
malformed terminal outcomes fail even after recomputing the envelope ID. No
cast or profile operation is inferred.

The independent one-instruction IR evaluator checks zero-step precharge,
outcome-typed variable propagation, success value, ordered empty ledger and
resource progress against the source evaluator across two variables and three
step budgets. **The successful source evaluator binds an optional witness ID
into its result, while this IR evaluator returns an unbound optional witness.**
The comparison therefore checks successful value, ledger and progress but
does not establish full observable or witness equivalence. A digest of the
source document in the IR is only a location/identity pointer, not replay
material. An adversary replacing both the binding and its carrier and
recomputing the IDs can create a distinct self-consistent package; no
authenticity or source-package correspondence is inferred. A separately
supplied, complete source package and independent
witness check are needed before lowering adequacy or replayability can be
claimed. IR envelope digests detect accidental changes, not forgery or
external authority. There is no public stable schema or API.

Next WP6 gate: extend to named map application, carry complete replay inputs
or explicitly define and prove the witness correspondence, then establish
full source/IR observational adequacy for the selected fragment. Preserve
the WP3-S source semantics as authority. No canonical or product migration.
