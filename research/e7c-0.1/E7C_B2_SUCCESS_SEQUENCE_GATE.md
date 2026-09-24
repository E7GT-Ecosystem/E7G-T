# E7C-B2/0.1 — explicit success-only sequence candidate

Status: `merged_provisional_research; owner_authorized_for_research_implementation`.
Base: PR #90 merge `5ecd397a07c8ca940d803cdb03f570b6dd7a4530`.
PR #91 merged as `a1f253e1dd4841adff3c8442a1629e1cf704708e`;
exact reviewed head in PR metadata.
Source edition: `E7C-B2/0.1-success-sequence-provisional`.
IR edition: `E7-IR/0.3-success-sequence-B2-provisional`.

The explicit selected static, charge, propagation and observation rules are
recorded in `E7C_B2_SUCCESS_SEQUENCE_RULES.md`, with six separately named
proof obligations. They remain provisional and are not a general binder.
An abstract Lean trace module isolates the no-continuation-on-failure branch;
its proof does not establish correspondence to Python or close B2-T05.

## Rule and scope

The opt-in term is `sequence_success(first, then_map)`. This first bounded
fragment admits `first = apply(total_identity, var source_config)` and an
explicit `then_map` of `strict_normalise` or `total_identity`. Static admission
checks the first `Outcome[A,core-1]`, the continuation's source type `A`,
matching outcome-extension editions, declaration policies and the union of
the two map effect rows. It is a selected named-map continuation, not a
general binder or a new implicit coercion. B1 stays outcome-terminal and its
parser, accepted rules, editions and fixtures are unchanged.

Evaluation charges the sequence step first, then the first map and its
variable read. On the first map's success it charges the continuation step,
appends its evidence and any strict-partiality entry, checks its guard and
finite map case, and returns its terminal result. On first-step
`unsupported` or `undetermined`, it propagates that exact terminal tag
without evaluating or appending continuation entries. A
resource limit also stops immediately, with the outer resource bound and
all completed charges/entries reported. Ledger entries stay ordered; an
exhausted ledger precedes the corresponding guard or semantic failure.
The current first map is total, so its reachable non-success tags are
`unsupported`, `undetermined` and `resource_limit`; `domain_error` is
exercised at the strict continuation. A future first map that can fail in
its domain needs a separately reviewed extension. The continuation cannot
catch or turn a non-success into a success.

`e7c_success_sequence_b2.py` emits a complete source package and inline
witness. `e7c_success_sequence_checker_b2.py` verifies the B1 child using
the existing independently implemented B1 checker, binds it to the exact
derived input, then independently recomputes the successor step, ledger,
terminal and resources. It shares static/data admission but no successor
evaluation control flow. A changed claim, child value or source binding is
rejected even if the outer digest is recomputed. Digests provide identity,
not external authenticity. The source success retains `optional_witness=null`
while the complete B2 witness is a separate result field.

`e7_ir_success_sequence_b2.py` pins source/IR editions, typed input,
intermediate and output types, both map editions, continuation policy,
effects, source location, a typed var binding/carrier and complete B2
replay material. Its independently coded evaluator handles all three
pre-continuation charges, short circuit, subsequent charge and ledger.
`compare_replay` checks the complete selected terminal/ledger/progress
observation against the independently checked source witness.

The committed `fixtures/wp5_ir/success_sequence.json` and
`fixtures/wp5_ir/success_sequence_ir.json` are complete canonical packages.
Tests cover both continuations, three admitted input configurations, five
step budgets, four ledger budgets and four capability/obligation conditions
(480 comparisons in each source and IR suite), exact replay, a conventional
finite map baseline, changed identities and a mismatched intermediate type.

The subsequent cross-edition conformance manifest binds the B1 manifest and
six selected B2 observations: success, first-map unsupported, first-map
undetermined, continuation domain error, step limit and ledger limit. Each
row is regenerated from complete source/IR replay and checks effects,
ordered entries, bounds and terminal correspondence. These are finite
observations, not a proof of all lowering or independent external review.

Reproduce:

```sh
python -m unittest discover -s research/e7c-0.1 -p 'test_e7c_success_sequence_b2.py' -v
python -m unittest discover -s research/e7c-0.1 -p 'test_e7_ir_success_sequence_b2.py' -v
python -m unittest discover -s research/e7c-0.1 -p 'test_*.py' -q
```

Open obligations: specify general scoped binders/substitution if this
selected continuation is extended; prove B2 progress, successful type
preservation, effect/ledger bounds and source/IR lowering adequacy; broaden
admitted continuations and obtain independent semantic/security review.
This slice does not close ADR-001/004/005/007/011, WP6, WP7, any profile's
general fidelity, or WP8–WP10. Published v0.12.1/RGP2 and product data,
identities, schemas and APIs remain unchanged.
