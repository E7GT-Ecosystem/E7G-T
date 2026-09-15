# REC-EVAL/0.1

REC-EVAL/0.1 is the preregistered evaluation package for the optional E7G-T
REC/0.1 profile. It tests whether adding REC to a retrieval workflow changes
observable answer quality and operational cost. It is not itself a kernel
version and contains no empirical performance claim.

The package compares four arms with one frozen model contract and one frozen
source universe:

| Arm | Intervention |
| --- | --- |
| `ordinary` | ordinary answer prompting; no retrieval tool |
| `checklist` | ordinary prompting plus a fixed evidence checklist; no retrieval tool |
| `retrieval` | retrieval from the frozen source universe; no REC envelope |
| `retrieval_rec` | the same retrieval interface plus REC/0.1 envelope and trace checking |

The primary causal contrast is `retrieval_rec - retrieval`. The four-arm ladder
is descriptive because source access differs between the first two and last two
arms.

## Contents

- `E7G-T_REC-EVAL_v0.1_Protocol.md` — preregistered design and promotion gate;
- `rec-eval-run-v1.schema.json` — interchange contract for adjudicated runs;
- `rec-eval-case-set-v1.schema.json` — contract for frozen prompts and gold keys;
- `score_rec_eval.py` — dependency-free validator and deterministic scorer;
- `run_template.json` — deliberately empty run template;
- `case_set_template.json` — deliberately empty case-set template;
- `fixtures/synthetic_scoring_fixture.json` — synthetic scorer exercise only;
- `fixtures/synthetic_expected_scores.json` — expected deterministic output;
- `test_score_rec_eval.py` — external unit tests for validation and scoring;
- `E7G-T_REC-EVAL_v0.1_Validation.json` — first-party package validation record.

## Reproduce package checks

```bash
python3 -m unittest discover -s benchmarks/rec-eval-0.1 -p 'test_*.py' -v
python3 benchmarks/rec-eval-0.1/score_rec_eval.py \
  benchmarks/rec-eval-0.1/fixtures/synthetic_scoring_fixture.json \
  --case-set benchmarks/rec-eval-0.1/fixtures/synthetic_case_set.json
python3 -m json.tool benchmarks/rec-eval-0.1/rec-eval-run-v1.schema.json
python3 -m json.tool benchmarks/rec-eval-0.1/run_template.json
```

The fixture is labelled `synthetic` and must never be reported as evidence that
REC improves an AI system. Real results require frozen prompts, source bundles,
raw-output digests, blinded adjudication, all four matched arms, and the sample
and independence requirements in the protocol.
