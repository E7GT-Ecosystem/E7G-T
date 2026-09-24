# WP6 — finite cross-slice conformance checkpoint

Status: `review_candidate; first_party_internal_only`.
Base: PR #88 merge `1518da87da76b6dff2ba3592152e9ba27f2f9342`.
Branch: `codex/e7c-ir-conformance`; exact head in PR metadata.
Edition: `E7-IR-CROSS-SLICE-CONFORMANCE/0.1-provisional`.

`fixtures/wp5_ir/ir_conformance_manifest.json` pins byte hashes of five
complete replay packages: var, strict map, total map, source-preserving view
and lossy projection. It also records each source document digest, IR edition,
witness identifier, static type/effects, ordered ledger dimensions, terminal
tag and step count. `e7_ir_conformance_b1.py` rebuilds this record and
validates each source witness with the independent checker, executes each
selected IR, compares source/IR observations, and checks that every actual
ledger atom belongs to the source's declared static effect row. The earlier
slice suites cover resource/guard failures and tamper cases; this manifest
uses the five committed successful reference cases.

The conventional comparisons live with the corresponding slice tests and
are limited to those finite inputs. This manifest is not a release schema,
general compiler conformance, proof of lowering adequacy or cross-profile
faithful embedding. It provides a repeatable internal checkpoint for the
next WP6 and WP7 work. The current B1 source type system rejects implicit
composition of outcome-producing map applications; this checkpoint does
not change that rule or the witness trust boundary.

Reproduce: `python -m unittest discover -s research/e7c-0.1 -p
'test_*.py' -q`. Published E7G-T v0.12.1/RGP2 remains the experimental
canonical source; no profile, schema, data, API or product migration occurs.
