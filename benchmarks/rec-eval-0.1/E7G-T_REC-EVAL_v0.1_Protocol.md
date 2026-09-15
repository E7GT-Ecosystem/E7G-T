# E7G-T REC-EVAL/0.1 — controlled evaluation protocol

**Status:** experimental, preregistered protocol  
**Target profile:** REC/0.1 with bounded REC-B1/0.1  
**Normative language:** MUST, MUST NOT, SHOULD and MAY are to be read as requirement levels within this protocol only.

## 1. Question and boundary

REC-EVAL/0.1 asks a bounded empirical question:

> With the model, task, source universe and retrieval interface fixed, does a
> REC-enforced retrieval workflow reduce unsupported conclusions and preserve
> decision quality relative to retrieval alone at an acceptable cost?

It does not test whether E7G-T is true as an ontology, whether cited sources are
authoritative in every domain, or whether REC constitutes general logical
reasoning. A successful run supports only the tested model editions, cases,
prompts, source editions and execution environment.

## 2. Four arms

Every case/replicate cell MUST contain exactly these arms:

1. `ordinary`: task prompt and ordinary system instruction; no retrieval tool.
2. `checklist`: the same task plus a fixed, published evidence checklist; no retrieval tool.
3. `retrieval`: the same model receives the fixed retrieval interface over the frozen source universe.
4. `retrieval_rec`: the same retrieval interface plus REC/0.1 envelope construction, policy application and trace validation.

All arms MUST use the same model provider, model edition, decoding parameters,
case prompt and execution budget except for the declared intervention. The
source universe MUST be identical and content-addressed. Ordinary and checklist
arms do not receive a retrieval tool; therefore comparisons involving them are
descriptive. The preregistered primary contrast is `retrieval_rec` against
`retrieval`.

## 3. Cases and strata

A promotion-grade case set MUST contain at least 100 cases, with at least 15 in
each of these six strata:

- stale or superseded source editions;
- mutually supporting or refuting evidence with shared dependence;
- genuine independent conflict that must remain visible;
- semantic-scope expansion traps;
- temporal-scope expansion traps;
- modality shifts, including normative/descriptive and possibility/assertion.

Cases MAY inhabit more than one stratum, but one case counts toward only its
declared primary stratum for the minimum. Cases MUST define atomic gold units,
the justified action (`assert` or `abstain`), conflict applicability, accepted
source editions, and scope/time/modality ceilings before any evaluated output is
generated. Case authors MUST NOT tune gold labels after arm inspection.

## 4. Execution and randomisation

- Run at least three replicates per case/arm unless the model is provably deterministic.
- Randomise arm order within case and case order within replicate.
- Pin a `model_contract_sha256`, `source_universe_sha256`, `case_set_sha256`, prompt templates and retrieval configuration.
- Apply equal wall-clock and token budgets. Tool overhead MUST be counted.
- Preserve raw outputs and retrieval results outside the score file; put their SHA-256 digests in each observation.
- Record failures and timeouts as observations, not silent exclusions.
- Exclusion rules and retry policy MUST be fixed before execution.

## 5. Blinded adjudication

Adjudicators MUST see outputs under random opaque labels without arm names,
traces, latency, token counts or cost. At least 20% of outputs MUST be scored by
two adjudicators. Disagreement resolution and inter-rater agreement MUST be
reported. The final run document MUST set `adjudication_blinded` to `true` only
when this procedure was actually followed.

For every observation the adjudicator records:

- `gold_units`, `asserted_units`, `correct_units`, and `unsupported_units`;
- semantic-scope, temporal-scope and modality error counts;
- whether conflict retention applies and, if so, whether conflict was retained;
- expected and actual action (`assert` or `abstain`).

REC trace validity is checked mechanically after adjudication and is not shown
to the adjudicator. A valid REC trace is a mechanism measure, not proof that the
answer is correct.

## 6. Deterministic metrics

The scorer emits micro-aggregated:

- factual recall = `sum(correct_units) / sum(gold_units)`;
- asserted precision = `sum(correct_units) / sum(asserted_units)`;
- unsupported rate = `sum(unsupported_units) / sum(asserted_units)`;
- scope, temporal and modality error rates per asserted unit;
- conflict retention = retained/applicable cases;
- decision accuracy = cases whose actual action equals the gold action;
- abstention rate;
- mean latency, input tokens, output tokens and reported cost;
- valid-trace rate where trace validity is applicable.

Zero denominators produce `null`, never a favourable default. Counts are not
assumed mutually exclusive. The scorer also emits paired per-case/replicate
deltas for the primary contrast. It does not calculate significance or decide
promotion.

## 7. Preregistered promotion gate

No kernel maturity or AI-performance claim may be made from the synthetic
fixture or first-party conformance tests. A promotion claim requires:

1. at least 100 frozen cases and three replicates;
2. two independently operated evaluations, including at least two model families;
3. blinded adjudication and reported agreement;
4. a predeclared paired uncertainty analysis (paired bootstrap or a stronger justified method);
5. for `retrieval_rec - retrieval`, a 95% interval whose upper bound for unsupported-rate delta is below zero;
6. a 95% lower bound for decision-accuracy delta no lower than -0.02;
7. factual-recall degradation no worse than 0.02 at the point estimate;
8. no more than 0.05 absolute increase in inappropriate abstention on `assert` cases;
9. latency and token/cost effects reported without hiding REC construction or checker overhead.

Passing this gate would justify a bounded empirical statement, not universal
adoption. Failure, null results and excessive abstention MUST be published with
the same metrics.

## 8. Leakage and prohibited interpretations

Benchmark cases MUST NOT appear in prompt examples, REC demonstrations or
development fixtures. Developers who tune an arm against the evaluation set
MUST disclose the set as development data and evaluate on a new frozen set.

REC-EVAL conformance MUST NOT be described as proof of source truth, general AI
reasoning, scientific validity, domain authority, consciousness, holographic
ontology, or production readiness. The four-arm ladder MUST NOT be interpreted
as a clean causal estimate except for the matched retrieval-versus-REC contrast.

