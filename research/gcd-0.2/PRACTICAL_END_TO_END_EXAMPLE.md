# Worked example — evidence-gated release in an AI-assisted document workflow

**Status:** executed *in the finite reference model*. This is a modelled hypothetical workflow, not a deployed document processor, legal-review system, or actual authorisation. No external mutation is performed.

## Problem

An AI assistant proposes alternative release paths for a consequential document. A reviewer must know which possibilities existed at the time of the decision, whether a new path truly differs from the existing ones, whether new requirements change the admitted structural vocabulary, which source decision caused the addition, what the reviewer selected, and whether selection was later enacted.

An ordinary source-control diff may record before/after bytes and a simple state machine may record state transitions, but neither **by itself** mandates semantic distinction witnesses, preservation embeddings across schema editions, exact choice-family membership, actor-versus-authority separation, or recomputation of a choice-event outcome. Mature state-machine/event-sourcing systems **could** implement these same checks; this example proves neither exclusivity nor superiority.

## Exact bounded run

| Stage | Exact input → output | Checked additional information |
|---|---|---|
| 1. Constitutive differentiation | coarse `{W}` → `{W,A}` and `{W,R}` under `Σ1` | A and R are exactly distinct semantic structures but both ground to the source; exhaustive comparison gives strict refinement |
| 2. Generation in old signature | `H={A,R}` → `H'={A,R,A+R}` | New mixed branch uses only registered `Σ1` kinds; all originals remain; kind-set novelty established |
| 3. Signature-generative extension | `Σ1` family → embedded `Σ2` family plus `A+E` | New node kind `evidence_gate`, relation `requires(A,E)`, exact binding to grounded approval path; four alternatives retained |
| 4. Selective choice | Reviewer-supplied `A+E` against exact `Σ2` family | Source family content/edition, membership witness, shared dependency, immutable logical choice occurrence, unverified actor claim, no enactment |
| 5. Model-only commitment | Selection receipt + fixture grant → new *model* epoch | Explicit independent commit gate and event; no file, network, physical or production state change |

The five deterministic canonical receipts, with exact input and typed output, are in `evidence/end_to_end_receipts.json`. Every stage replays successfully under `gcd02.py`. Replay report: `evidence/replay_report.json`.

## Negative injection demonstrated

1. **Display-only distinction:** reconfigure observation access over the same semantic signature. The checker reports `access_refinement_only`, not constitution.
2. **Old path renamed or coarsened:** ask for an expansive branch at `root_only` equivalence. The candidate is not a novel criterion class: `non_expansive`.
3. **Invalid new kind use:** an `evidence_gate` without the mandatory `requires` relation cannot be admitted: `invalid_input`.
4. **Non-member choice:** attempt to select a branch absent from the exact source family: `rejected_nonmember`.
5. **Unauthorised update:** provide a replayable choice receipt without the fixture grant: `unauthorised`.
6. **History confusion:** two choices of the same configuration with different occurrence IDs remain distinct acts.
7. **Order effects:** choose approval first, then explicitly seed and generate — the new singleton-seeded family excludes the old rejection branch, whereas generate first then choose retains it in the source family. The difference is recorded rather than silently projected away.
8. **False receipt status:** an attacker who edits `external_enactment` to true and recalculates the SHA-256 digest still fails replay against the registered operation. **Important:** an attacker can author a different *valid* request and its consistent receipt; this check is not historic authentication.

## Consequential improvement being tested

The result is **a specific, inspectable decision trail** that tells a reviewer which structural distinction arose, what alternatives were protected, exactly what was chosen and whether any commitment was actually modelled. The information avoids several failure modes that a naive branching log or ordinary text diff does not automatically detect.

To claim practical *value beyond an engineered conventional system*, a subsequent independent pilot must compare against a conventional typed workflow engine with schema validation, policy checks, event sourcing and audit logging; assess unsupported-claim prevention, error rates, reviewer effort and cost. Such comparative evidence is **not yet established**. The present example demonstrates additional explicit *contractual behaviour*, not market validation.

## Potential user and buyer (hypotheses, not verified demand)

- **User:** a document assurance, review or compliance engineer validating generated workflow alternatives.
- **Buyer hypothesis:** an organisation responsible for auditable high-stakes document approval.
- **Risk reduced in the model:** conflating a renamed/displayed option, structurally new option, selected plan and authorised commit.
- **Next credible evidence:** run GCD and a strong conventional workflow baseline on the same externally supplied change requests with independent expert grading.
