# E7G-T Kernel v0.10-UC1

# Public Reference Specification

**Version:** v0.10-UC1  
**Date:** 2026-07-30  
**Status:** use-candidate public reference kernel  
**Project:** E7G-T — Extensional-Projective Order Geometry  
**Public posture:** geometry-first modelling language and practical calculus  
**Author:** Oleksandr Razinkov  
**Copyright:** © 2026 Oleksandr Razinkov  
**Licence:** [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/)  

---

## Licence and reuse

This kernel is licensed under CC BY-SA 4.0. You may share and adapt it for any purpose, provided you give appropriate credit, link to the licence, indicate whether changes were made, and distribute adaptations under the same licence. This licensing statement applies to this kernel document; third-party material, if any, remains subject to its own rights.

---

## 0. Status and Use Posture

E7G-T is a geometry-first modelling language and practical calculus.

Its purpose is to make the following visible:

- entity;
- order;
- time posture;
- context;
- boundary;
- projection;
- preservation;
- loss;
- reconstruction status;
- bridge mode;
- claim strength;
- admissible use;
- next move.

E7G-T is not established mathematics.  
E7G-T is not empirical physics.  
E7G-T is not a proof system.  
E7G-T is not a Theory of Everything.  
E7G-T is not a replacement for domain expertise.

It may be used to inspect, frame, lint, teach, document, and discipline reasoning around representations.

---

## 1. Public Definition

> E7G-T is a geometry-first modelling language and practical calculus for making projection, loss, reconstruction, bridge mode, and admissible use visible.

Expanded:

> E7G-T helps users inspect representations before relying on them. It asks what a chart, AI answer, proof text, translation, model, legal summary, or dashboard preserves, what it loses, what source it points to, what claim strength it can support, and what the next responsible move should be.

---

## 2. Core Question

For any concrete object, claim, output, proof, model, translation, chart, summary, or representation, ask:

> What do I do next with this?

E7G-T answers this by forcing the user to declare enough structure to avoid overreading the representation.

---

## 3. Core Discipline

Before relying on a representation, identify:

1. **Entity** — what is being examined.
2. **Order profile** — what kind of extension/view it is.
3. **Temporal regime** — how time is being treated.
4. **Context** — what frame gives it meaning.
5. **Boundary** — what is included and excluded.
6. **Operation** — what is being done.
7. **Preservation/loss** — what survives and what is lost.
8. **Reconstruction status** — whether source recovery is justified.
9. **Bridge mode** — whether domains are being crossed.
10. **Claim strength** — how strongly the claim may be stated.
11. **Admissible use** — what it may responsibly support.
12. **Stop condition** — when reliance must stop or downgrade.

### Minimum rule

Use the smallest level that changes the next move without hiding risk.

---

## 4. D-Order Table

D-orders are modelling orders, not literal physical dimensions by default.

| Order | Name | Practical reading |
|---|---|---|
| **D0** | Point-locality | mark, scalar, trace, pixel, result, accepted state |
| **D1** | Line-extension | path, sequence, interval, procedure, timeline segment |
| **D2** | Surface-extension | text, diagram, chart, dashboard, screen, map, interface |
| **D3** | Form-extension | object, artefact, body, product, local system, structured proof artefact |
| **D4** | Duration-extension | process, history, version, event sequence, lived development |
| **D5** | Variation-extension | option set, possibility field, design space, proof search, scenario space |
| **D6** | Transformation-extension | rule, operator, tactic, function, method, protocol, verification rule |
| **D7** | Context-extension | purpose, interpretation, measurement frame, bridge governance, admissible-use frame |

### D-order rule

Do not treat a lower-order view as the whole higher-order source.

---

## 5. Temporal Regime Table

Temporal regimes describe modelling posture, not ultimate metaphysics.

| Regime | Name | Practical reading |
|---|---|---|
| **TR0** | No-time / atemporal | treated outside sequence |
| **TR1** | Local-time | local ordered sequence |
| **TR2** | Shared-time | coordinated time across sequences |
| **TR3** | Branching-time | alternatives, forecasts, proof search, scenarios |
| **TR4** | Cyclic-time | recurrence, rhythm, iteration |
| **TR5** | Super-time / meta-time | time about time; model-time governing object-time |
| **TR6** | Timeless-completion | closed whole under declared closure context |

### Temporal rule

State the temporal regime when time posture affects the claim.

---

## 6. Primitive Moves

### 1. Place

Declare entity, order, time posture, and context.

```text
X : Dn @ TRi / C
```

### 2. Bound

Declare the operational boundary.

```text
∂X = B
```

### 3. Incide

Declare a relation between entities under context.

```text
A ⋈_C B
```

### 4. Extend

Move toward richer declared structure.

```text
X ↑ n
```

### 5. Slice

Select a contextual/local view.

```text
S_C^s(X)
```

### 6. Project

Render a lower-order view from a richer source or candidate source.

```text
π_C^{n→k}(X) = Y
```

### 7. Preserve / Lose

Name what survives and what does not survive.

```text
preserves: P
loses: L
```

### 8. Transform

Apply a declared rule-space.

```text
τ_T(X) = Y
```

### 9. Reconstruct

Attempt source recovery from a projection or trace.

```text
ρ_C(Y) ⇒ {X_i}
```

### 10. Bridge / Stop

Declare bridge mode or stop the claim.

```text
β_M^{A↔B}
Stop(reason)
```

---

## 7. Practical Laws

### Law 1 — Typing Before Operation

Place the entity before operating on it.

### Law 2 — Extension Is Not Projection

Building richer structure is not the same as rendering a lower-order view.

### Law 3 — Projection Is Not Reconstruction

A view of a source is not recovery of the source.

### Law 4 — Projection Loss Accumulates

Loss in a projection stack cannot be silently regained.

### Law 5 — Slice and Projection Need Not Commute

Slicing before projection and projecting before slicing may produce different results.

### Law 6 — Boundary Is Contextual But Not Arbitrary

Boundary may vary by use, but it must match the claim.

### Law 7 — Invariance Requires a Transformation Class

No invariant claim is complete without declaring what transformations it survives.

### Law 8 — Bridge Claims Inherit the Weakest Link

A bridge cannot support a stronger claim than its least-supported component.

### Law 9 — Empirical Language Requires Empirical Bridge

Reality-facing empirical claims require measurement, prediction or constraint, falsification condition, and evidence path.

### Law 10 — The Next Move Is the Practical Test

The value of the model is shown by the next admissible action it clarifies.

---

## 8. Bridge Modes

Bridge modes say how E7G-T language is being connected to another domain.

| Mode | Meaning | What it supports |
|---|---|---|
| **none** | no cross-domain bridge is claimed | internal modelling only |
| **contemplative-what-if** | imaginative or reflective use | exploration, fiction, meditation, ideation |
| **philosophical-interpretation** | conceptual interpretation | meaning-making, worldview discussion |
| **formal-analogy** | structural resemblance under declared mapping | analogy, modelling comparison |
| **formal-compatibility** | compatible with recognised formal substrate under definitions | possible formalisation path |
| **formal-proof** | proof discharged inside declared formal substrate | formal theorem/proof status |
| **empirical-testable** | claim tied to observation, measurement, prediction, falsification, evidence | reality-facing empirical proposal or support |
| **authority-source-linked** | claim tied to an official or authoritative source under scope | legal/admin/documentary source discipline |

### Bridge rule

Do not raise claim strength without the bridge mode required for that strength.

### Use posture note

“Operational” is not a bridge mode in this RC1 kernel. It is a **use posture**: E7G-T may be used operationally as a checklist, linter, worksheet, QA method, or decision-support frame. Operational use still requires the correct bridge mode for each claim.

---

## 9. Claim-Strength Ladder

1. intuition
2. metaphor
3. contemplative what-if
4. philosophical interpretation
5. formal analogy
6. formal compatibility
7. formal proof
8. empirical-testable proposal
9. empirically supported model
10. validated operational method
11. authority-issued decision

### Upgrade rule

Do not upgrade a claim by rhetoric.

Upgrade only by completing the required source, proof, test, authority, review, or validation path.

---

## 10. Practical Levels

### Level 1 — OneLine

Use for quick placement and overread blocking.

```text
E7-OneLine: X is treated as [order/role] under [context]; admissible move: [next move]; blocked overread: [one phrase].
```

### Level 2 — MiniCard

Use for ordinary review.

Fields:

```yaml
entity:
plainMeaning:
placement:
boundary:
projectionAccount:
preserved:
lost:
distortionRisk:
reconstructionStatus:
bridgeMode:
admissibleUse:
nonAdmissibleUse:
nextMove:
blockedOverread:
```

### Level 3 — FullCard

Use for reliance, publication, high-stakes work, formal claims, empirical-facing claims, legal/admin summaries, translation QA, or operational decisions.

Fields:

```yaml
entityOfConcern:
claim:
orderProfile:
temporalRegime:
context:
boundary:
sourceStack:
operation:
projectionPath:
preservationLoss:
transformationClass:
invariant:
reconstructionStatus:
bridgeMode:
claimStrength:
weakestLink:
admissibleUse:
nonAdmissibleUse:
stopCondition:
nextMove:
```

---

## 11. Notation Normalisation

### Placement

```text
X : Dn @ TRi / C
```

### Projection

```text
π_C^{n→k}(X) = Y
```

### Readable projection

```text
X : Dn @ TRi / C  --π_C^{n→k}-->  Y : Dk @ TRj / C'
```

### Full projection

```text
X : Dn @ TRi / C  --π_C^{n→k}-->  Y : Dk @ TRj / C'
[preserves: P; loses: L; use: U]
```

### Reconstruction

```text
ρ_C(Y) ⇒ {X_i}
```

### Candidate reconstruction

```text
ρ_C^{k→n}(Y) ⇝ X?
```

### Transformation

```text
τ_T(X) = Y
```

### Invariant

```text
Inv_T(X) = I
```

### Bridge

```text
β_M^{A↔B}
```

### Stop

```text
Stop(reason)
```

### Notation rule

Notation records discipline. It does not create discipline.

Use notation only when it clarifies the next move.

---

## 12. Core Anti-Overread Rules

### Projection rule

A projection is not the source.

### Summary rule

A summary is not the document.

### Chart rule

A chart is not the business.

### AI rule

An AI answer is not the source.

### Translation rule

A translation is not source identity.

### Proof rule

A proof sketch is not proof.

### Interface rule

An accepted interface state is not necessarily human explanation.

### Authority rule

A legal/admin summary is not authority.

### Analogy rule

An analogy is not proof.

### Model rule

A model is not reality.

---

## 13. Proof-of-Path Kernel

Proof-of-Path is an accountability record for the path by which a claim, proof, model, output, or representation moves from initial placement to stated status.

It records:

- claim;
- entity;
- substrate;
- assumptions;
- context;
- boundary;
- definitions;
- transformations;
- projection events;
- obligations created;
- obligations discharged;
- preserved invariants;
- losses;
- checks;
- unresolved obligations;
- bridge mode;
- claim strength;
- reliance tier;
- stop condition.

### Proof-of-Path rule

Proof-of-Path may document a proof path.

It is not itself a formal proof unless a declared formal substrate checks the proof.

---

## 14. Reality Bridge Kernel

Reality-facing claims require bridge discipline.

A RealityBridgeCard should include:

```yaml
claim:
sourceDomain:
targetDomain:
bridgeMode:
standardSubstrate:
observationProtocol:
measurementMap:
predictionOrConstraint:
falsificationCondition:
evidencePath:
weakestLink:
admissibleUse:
nonAdmissibleUse:
stopCondition:
```

### Reality bridge rule

Empirical language requires empirical bridge.

Without empirical bridge, use metaphor, interpretation, formal analogy, or stop.

---

## 15. Formal Neighbourhood Kernel

E7G-T may stand near established fields without claiming identity with them.

A FormalNeighbourhoodCard should include:

```yaml
field:
E7GTElement:
resemblance:
establishedTool:
currentBridgeMode:
whatE7GTCanLearn:
whatE7GTMustNotClaim:
possibleFormalisationPath:
stopCondition:
```

### Neighbourhood rule

Neighbourhood is not identity.

An E7G-T arrow is not automatically a morphism.  
An E7G-T projection is not automatically projective geometry.  
An E7G-T proof path is not automatically a formal proof.  
An E7G-T bridge is not automatically a functor, model, law, or empirical theory.

---

## 16. Failure-Mode Checklist

Before relying on an E7G-T account, check for:

- false identity;
- false reconstruction;
- hidden boundary shift;
- undeclared context;
- missing temporal regime;
- projection loss denial;
- slice mistaken for whole;
- invariant without transformation class;
- bridge inflation;
- formal-neighbourhood overclaim;
- empirical language without empirical bridge;
- proof text mistaken for proof object;
- AI fluency mistaken for evidence;
- interface accepted-state mistaken for explanation;
- legal/admin summary mistaken for authority;
- translation fluency mistaken for source preservation;
- dashboard movement mistaken for causal diagnosis;
- replacement of mature tools;
- missing stop condition.

---

## 17. Public-Use Cautions

When presenting E7G-T publicly:

- do not call it established mathematics;
- do not call it new physics;
- do not claim that D0–D7 are literal physical dimensions;
- do not claim that holographic reading proves a holographic universe;
- do not treat contemplative usefulness as empirical evidence;
- do not treat metaphor as proof;
- do not treat Proof-of-Path as formal proof;
- do not use E7G-T to avoid expert review;
- do not replace domain methods where stronger tools already exist.

Preferred public description:

> E7G-T is a geometry-first modelling language for inspecting representations before relying on them.

---

## 18. Minimal Examples

### AI answer

```text
E7-OneLine: An AI answer is treated as a D2/D7 textual projection under user-query context; admissible move: verify source and bridge mode; blocked overread: AI answer is not the source.
```

### Business dashboard

```text
E7-OneLine: A dashboard is treated as a D2 projection of a D4/D5 business system under reporting context; admissible move: inspect preserved metrics and lost causes; blocked overread: chart is not the business.
```

### Translation

```text
E7-OneLine: A translation is treated as a D2/D7 target-language projection of a source document under purpose context; admissible move: check preserved invariants; blocked overread: translation is not source identity.
```

### Proof assistant session

```text
E7-OneLine: A proof assistant session is treated as a D2/D6/D7 path through formal states under substrate context; admissible move: inspect assumptions, obligations, proof status, and explanation status; blocked overread: proof script is not the whole proof object.
```

### Legal/admin summary

```text
E7-OneLine: A legal/admin summary is treated as a D2/D7 projection of authority, facts, documents, and procedure under case-review context; admissible move: return to source stack; blocked overread: summary is not authority.
```

### Speculative physics analogy

```text
E7-OneLine: Quantum measurement-as-projection is treated as formal analogy unless empirical-testable bridge is declared; admissible move: state preservation/loss and stop condition; blocked overread: analogy is not new physics.
```

---

## 19. Maturity Statement

E7G-T v0.10-UC1 is mature enough to support:

- disciplined modelling;
- AI-output review;
- translation QA framing;
- dashboard critique;
- legal/admin summary linting;
- proof-path documentation;
- practical worksheets;
- pilot testing;
- public positioning as a modelling language.

It is not mature enough to support:

- claims of established mathematics;
- claims of new physics;
- empirical confirmation;
- replacement of expert methods;
- v1.0 public stability.

---

## 20. v1.0 Gate

E7G-T should not move to v1.0 until:

- terms are stable;
- notation is stable;
- bridge modes are consistently enforced;
- at least three Application Atlas entries are tested;
- at least two worksheets are tested on real examples;
- at least one Proof-of-Path worked example is checked in a real proof assistant or clearly labelled illustrative;
- source-backed references are cleaned;
- public language is simplified;
- overclaim risks are reduced.

---

## 21. UC1 Polish Notes

This UC1 polish pass makes the following changes from the v0.9 draft:

1. Shortens the public status posture.
2. Normalises “D-order” and “Temporal Regime” language.
3. Treats **operational** as a use posture, not a bridge mode.
4. Adds **formal-proof** and **authority-source-linked** as explicit bridge modes.
5. Adds compact anti-overread rules.
6. Tightens public-use cautions.
7. Aligns examples with APP-001, APP-002, APP-003, POP-001, POP-002, PG-001, and PG-002.
8. Keeps the kernel as a modelling language, not a theory-of-everything claim.
9. Reduces explanatory repetition.
10. Makes v1.0 gate conditions explicit.

---

## 22. Closing Rule

Place the entity.

Name the boundary.

Track the projection.

Record preservation and loss.

Declare bridge mode.

Limit claim strength.

State admissible use.

Stop when the projection cannot carry the claim.
