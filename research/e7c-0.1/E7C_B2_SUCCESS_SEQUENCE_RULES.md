# E7C-B2/0.1 selected success sequence: static and operational rules

Status: `drafted_provisional_semantics`; source edition
`E7C-B2/0.1-success-sequence-provisional`. This document specifies the
bounded constructor implemented in PR #91 and pinned by PR #92. It is a
candidate rule for exact-head review, not a change to accepted E7C-B1 or the
published v0.12.1/RGP2 kernel.

## Syntax, admission and static judgement

The only admitted form is `sequence_success(first, then_map)`, where
`first = apply(total_identity, var source_config)` and `then_map` is either
`strict_normalise` or `total_identity`. The complete source document retains
the B1 environment, values, interpretation, resource policy, outcome edition,
pins and external assumptions, with the distinct B2 source edition. All B1
closed-carrier and interpretation admission checks run before evaluation.

Write `Γ ⊢ t : T ! ε` for a B1 static judgement, `ξ` for the pinned outcome
extension, `A` for the first map's target and `B` for the selected continuation
map's target. Let `evidence(m)` and, for a strict map only, `partiality(m)`
be the B1 static atoms of map `m`. The *selected* B2 rule is:

```text
Γ ⊢ first : Outcome[A, ξ] ! ε₁
Γ ⊢ var source_config : A ! ∅
then_map : A -> B   with outcome extension ξ
then_map ∈ {strict_normalise, total_identity}
first is exactly apply(total_identity, var source_config)
────────────────────────────────────────────────────────────────────────
Γ ⊢ sequence_success(first, then_map) : Outcome[B, ξ]
    ! (ε₁ ∪ {evidence(then_map)} ∪ partial(then_map))
```

`partial(m) = {partiality(m)}` for `strict_normalise` and `∅` for
`total_identity`. The union is a set of possible effects, not a promise that
every run emits them. Exact nominal types, map and outcome editions, and
declared domain policies must match. No `Outcome[A, ξ]` becomes an `A` by
implicit conversion. The explicit constructor is the sole elimination point.
There is no variable binder, substitution rule, recursive continuation or
arbitrary first term in this edition.

## Bounded operational relation

An observation is `(terminal, L, p)`: a tagged whole terminal outcome, an
ordered ledger `L`, and resource progress `p`. The charge `seq` consumes one
step before its child. Given outer policy `β` with `step_bound = n` and
`ledger_entry_bound = k`:

1. Admit the *entire* document independently of `n` and `k`. For `n = 0`,
   return `resource_limit(β, progress(0, []))` with no child witness.
2. For `n > 0`, evaluate `first` using the B1 evaluator with step bound
   `n - 1` and unchanged ledger bound `k`. Require a complete B1 child witness.
   If its progress reports `s` completed steps and ledger `L`, outer progress
   has `1 + s` steps and exactly `L` as its ledger prefix.
3. If the child is `resource_limit`, return a resource limit under *outer*
   policy `β` with the outer progress. If the child is any other non-success,
   propagate its exact tag and payload with unchanged `L`; do not charge or
   interpret the continuation. In the present first-map fragment the reachable
   non-resource tags are `unsupported` and `undetermined`.
4. If the child succeeds but `1 + s = n`, return the outer resource limit
   before starting the continuation. Otherwise charge one continuation step.
   Attempt its evidence entry, then its strict-partiality entry if applicable,
   each subject to `k`. A failed append returns `resource_limit(β, p)` before
   any subsequent guard or map case. Check capability, then obligation, then
   the unique admitted finite case for the child's successful value. Return
   `unsupported`, `undetermined`, `domain_error` or `success` accordingly.

The continuation receives only the *value* of a successful first outcome;
neither a non-success outcome nor its diagnostic can become an input value.
Ledger order is first-map events before continuation evidence before
continuation partiality. Each resource limit retains all completed steps and
entries. Terminal comparison includes tag and payload, not just successful
values. At no point does failure of one finite branch become a partial
successful collection.

## Model-relative observation and current evidence

For a fully admitted finite interpretation `M`, define the meaning of this
selected term as the observation obtained by the above bounded relation:
`⟦sequence_success(first,m)⟧(M,β) = (terminal,L,p)`. Equality of meanings
requires equality of all three fields. This is deliberately model-relative:
the interpretation tables and their truth/authority are supplied, not proved.
It does not assert a denotational adequacy theorem for general B1 or B2.

PR #91 supplies a source evaluator, a separate replay checker, and a versioned
IR executor. PR #92 pins success, first unsupported, first undetermined,
continuation domain error, step limit and ledger limit observations. The tests
cover a finite input/budget grid and tamper cases. These establish internal
agreement on the admitted examples; they do not prove total progress,
preservation, ledger soundness or lowering adequacy for all admitted inputs.

## Proof obligations and compatibility

| Obligation | Precise target | Current evidence |
| --- | --- | --- |
| B2-T01 determinism | One admitted `(M,β)` yields one whole observation | Bounded tests; proof open |
| B2-T02 progress | An admitted term yields a terminal tag or explicit resource limit | Bounded tests; proof open |
| B2-T03 successful preservation | `success(v)` implies `v : B` under typed, unique, complete interpretation | Bounded tests; proof open |
| B2-T04 effect bound | Every entry in `L` belongs to the static union; order and prefix obey the rules | Bounded tests; proof open |
| B2-T05 short circuit | A non-success first outcome adds no continuation charge or entry | Bounded tests; proof open |
| B2-T06 replay/IR adequacy | Independent checker accepts exactly valid derivations and IR preserves whole observations | Finite differential only; proof open |

The separate Lean module `E7CB2Sequence.lean` models an *abstract trace
algebra* in which a B1 child trace is already available. It proves, by
reduction of its clauses, zero-bound child independence and exact
non-success payload/ledger preservation for selected tags. These are local
lemmas about the Lean definition. The module does not model B1 admission,
map interpretation, ledger capacity, a well-formed residual-budget child,
Python witness replay or source/IR adequacy. It is therefore a bounded
sub-lemma toward B2-T05, which remains open for the actual E7C-B2 relation.

The admitted source and IR editions are new. B1 typing/evaluation, witness
format and published canonical material do not migrate. All existing product
IDs, schemas, data and APIs retain their meanings. A general binder, broader
first term, changed outcome semantics or profile adoption needs a separate
reviewed edition and its own compatibility argument.
