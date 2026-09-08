---
title: "E7G-T Combined Family-State Profile"
version: "0.1-experimental"
profile_id: "CFS/0.1"
reference_model: "CG3/0.1"
kernel: "0.12-experimental"
date: "2026-09-08"
author: "Alexander Gregory Wingate and Oleksandr Razinkov"
copyright: "© 2026 Alexander Gregory Wingate and Oleksandr Razinkov"
license: "CC BY-SA 4.0"
status: "Experimental combined profile with a bounded executable reference model"
---

# E7G-T Combined Family-State Profile v0.1

**Purpose:** place an EEC-Q formal configuration state inside an SF symbolic family, so a whole algebraic combination can vary, extend, transform and later be realised without losing the distinction between family membership and formal coefficient arithmetic.

CFS/0.1 combines two independently usable E7G-T v0.12 profiles. SF supplies the outer parameter domain, constraints, symbolic dependence and realisation protocol. EEC-Q supplies the inner finite formal state, exact rational coefficients, pushforward, cancellation and typed extension. The combination does not equate a set of possible entities with a formal sum.

The companion **E7G-T_Combined_Family_State_v0.1.py** implements the bounded **CG3/0.1** model by combining the IC/0.1 interval carrier and polynomial expressions with FG3/0.1 graph states. The validation report records its internal checks.

## C.0 Status and terms

Capitalised MUST, MUST NOT, SHOULD and MAY express obligations on implementations claiming CFS compatibility. A declaration of compatibility MUST identify the outer SF model, inner EEC model, coefficient-expression grammar, supported operations, equality procedures and resource limits.

| Term | Meaning |
|---|---|
| Outer assignment | One admitted value of the SF parameter carrier |
| Inner state | The EEC-Q formal state constructed at one outer assignment |
| State family | A finite symbolic description of a family of inner states |
| Evaluation | Construction of the inner state at a supplied admitted assignment |
| Realisation | Selection over the outer family under declared objectives |
| Shared composition | Pointwise composition of state families using the same outer assignment |

CFS coefficients retain the meaning of their selected EEC profile. In CFS/0.1 they are exact rational formal coefficients. They are not probabilities, evidence weights or physical amplitudes. CFS/0.1 provides no interference, measurement or quantum execution semantics.

## C.1 Combined carrier

Pin an outer symbolic model, an inner configuration signature \(\Sigma\), context and inquiry. A combined family-state object is:

\[
\mathcal H=\langle\Lambda,K,S\rangle_\Sigma,
\qquad
D_{\mathcal H}=\{\lambda\in\Lambda:K(\lambda)\},
\]

where each admitted assignment constructs an inner EEC-Q state

\[
S(\lambda)
=\sum_{i=1}^{n} a_i(\lambda)\,\mathbf e_{\Gamma_i(\lambda)}
\in\mathcal F_\Sigma.
\]

The expression is finite: it has finitely many symbolic terms even when \(D_{\mathcal H}\) or the image of \(S\) is infinite. At every admitted assignment, inner canonicalisation collects equal configurations and removes coefficients that evaluate to zero.

The denotation of the outer family is the set of canonical inner states:

\[
\llbracket\mathcal H\rrbracket
=\{S(\lambda):\lambda\in D_{\mathcal H}\}.
\]

This is a set at the outer level. No addition or cancellation occurs merely because two assignments produce the same state. Within each \(S(\lambda)\), the selected EEC coefficient algebra applies.

Two parameter assignments may therefore denote the same inner state. A uniquely realised state does not imply a unique parameter assignment. An empty outer family differs from a nonempty family whose every member is the EEC zero state.

## C.2 Why the nesting direction matters

CFS/0.1 selects **SF outside and EEC inside**:

\[
\lambda\longmapsto S(\lambda).
\]

The outer family preserves symbolic variation and shared dependence. The inner state gives each assignment a complete algebraic configuration combination. This permits an unresolved program or construction to be transformed as a whole before a particular state is selected.

The reverse construction—an EEC formal sum whose basis elements are quoted SF families—is also meaningful, but it answers another question. It combines whole family descriptions algebraically; it does not create a parameterised state or license pointwise evaluation. Conversion between these two arrangements is never implicit.

## C.3 Evaluation, restriction, viewing and quotation

Evaluation at an admitted assignment is:

\[
\operatorname{eval}_\lambda(\mathcal H)=S(\lambda).
\]

Evaluation uses a supplied assignment. It is not realisation and does not assert that the assignment is optimal, observed or physically selected.

Restriction strengthens the outer constraint:

\[
\operatorname{restrict}_L(\mathcal H)
=\langle\Lambda,K\land L,S\rangle.
\]

A view retains the complete source and displays selected outer or inner properties. A projection constructs a new family and MUST state what information it identifies or discards. Quotation makes the whole combined construction an entity without evaluating or realising it.

## C.4 Pointwise algebra and pushforward

For compatible state families over the same pinned outer domain and context:

\[
(\mathcal H+\mathcal G)(\lambda)=S(\lambda)+T(\lambda),
\qquad
(b\mathcal H)(\lambda)=b(\lambda)S(\lambda),
\]

where the coefficient expression \(b\) and every resulting product must belong to the declared expression grammar.

For a total inner configuration map \(f\), pushforward is pointwise:

\[
(f_*\mathcal H)(\lambda)=f_*S(\lambda).
\]

Configuration images are collected inside each state. Thus a transformation can turn a varying family into a constant one through identification and symbolic coefficient collection.

For a partial inner rule, a strict CFS transformation is admitted only if the rule is defined on every configuration that occurs with a nonzero coefficient at at least one admitted assignment. Implementations MAY support a stronger symbolic proof procedure. They MUST NOT silently discard assignments or terms on which the rule fails.

Pointwise cancellation is evaluated under the outer assignment. A symbolic coefficient that is zero everywhere on the admitted domain contributes no inner branch. A coefficient that vanishes only at particular assignments removes the branch only at those assignments.

## C.5 Extension and dependence

Extension by a fixed inner state \(U\) is:

\[
\operatorname{Extend}_J(\mathcal H,U)(\lambda)
=\operatorname{Extend}_J(S(\lambda),U).
\]

For two families sharing the same outer assignment, dependent extension is pointwise:

\[
\operatorname{SharedExtend}_J(\mathcal H,\mathcal G)(\lambda)
=(e_J)_*\big(S(\lambda)\boxtimes T(\lambda)\big).
\]

The same \(\lambda\) appears in both operands. Replacing it with two independently chosen parameters changes the program. Shared extension can therefore create coefficient products such as \(a_i(\lambda)b_j(\lambda)\), while preserving their common origin.

Independent outer extension introduces a fresh parameter \(\mu\):

\[
\langle\Lambda\times M,K(\lambda)\land L(\mu),
(\lambda,\mu)\mapsto
\operatorname{Extend}_J(S(\lambda),T(\mu))\rangle.
\]

Constrained extension may introduce \(\mu\) together with a relation \(C(\lambda,\mu)\). An implementation MUST distinguish shared, independent and constrained outer parameters. CG3/0.1 implements shared pointwise composition and extension by a fixed inner state; general multivariate outer carriers remain outside the model.

## C.6 Realisation over inner states

A realisation objective is a declared function on canonical inner states. In the bounded reference model it is a rational linear observable:

\[
\ell\!\left(\sum_\Gamma c_\Gamma\mathbf e_\Gamma\right)
=\sum_\Gamma w_\Gamma c_\Gamma.
\]

Composing it with the state family produces an outer scalar expression:

\[
p_\ell(\lambda)=\ell(S(\lambda)).
\]

The SF realisation protocol then applies ordered objectives lexicographically. If the final residual image contains exactly one canonical inner state, the result is `UNIQUE`. If it contains at least two, it is `AMBIGUOUS`. `EMPTY`, `UNATTAINED`, `UNSUPPORTED`, `UNDETERMINED`, `UNBOUNDED` and `RESOURCE_LIMIT` retain their SF meanings when supported by the selected outer model.

The returned entity of a successful CFS realisation is an inner EEC state, including the zero state. The residual state family and source family remain available. No arbitrary member is selected from an ambiguous residual image.

Realisation and inner pushforward need not commute. A pushforward can identify previously distinct configurations and make a family uniquely realisable. Conversely, an objective may distinguish states using information that a pushforward removes. Any interchange law requires a mapped objective and proof over the admitted domain.

## C.7 Adapters to the component profiles

The following adapters are explicit:

1. Evaluating a CFS family at an admitted assignment returns one EEC state.
2. A CFS family whose inner image is proved singleton can be realised as one EEC state without choosing a unique assignment.
3. An EEC state can be embedded as a constant CFS family over any declared nonempty outer domain.
4. Replacing each inner state by its support produces an SF family of finite sets and discards coefficient values and cancellation semantics.
5. Turning an arbitrary SF family of configurations into CFS requires an explicit injection and coefficient assignment.

An infinite SF image cannot automatically become one finite-support EEC state. An EEC state cannot recover an outer parameterisation that was discarded.

## C.8 Bounded reference model CG3/0.1

CG3/0.1 combines these existing executable subsets:

- outer domains: IC/0.1 bounded rational intervals or finite rational point sets;
- inner configurations: FG3/0.1 fixed-labelled graphs;
- symbolic coefficients: exact rational polynomials in one parameter \(t\), degree at most eight;
- inner coefficients after evaluation: exact rational numbers;
- transformations: registered FG3 graph rules when total on the active symbolic support;
- extension: graph union or pairing with a fixed inner state;
- shared composition: pointwise graph union of two families over the identical domain and context;
- objectives: rational linear functionals on inner graph-state coefficients;
- continuous optimisation: inherited IC/0.1 constant, linear and quadratic exact optimisation;
- finite-domain optimisation: exact evaluation of admitted polynomial objectives.

The model accepts at most 64 interchange terms, 32 ordered objectives, 1,024 explicit outer points and the inherited 4,096-bit rational and degree-eight polynomial limits. The default per-stage candidate limit is 4,096.

CG3 does not implement graph-valued symbolic coordinates, arbitrary constraints, multivariate parameters, general EEC configurations, nonlinear observables, automatic theorem proving or quantum lowering.

## C.9 Worked construction

Let \(A\) be the empty FG3 graph and \(B\) the graph containing edge `AB`. Over \(0\le t\le1\), define:

\[
S(t)=t\mathbf e_A+(1-t)\mathbf e_B.
\]

At \(t=0\), evaluation gives \(\mathbf e_B\). At \(t=1\), it gives \(\mathbf e_A\). At \(t=\tfrac12\), it gives the exact state

\[
\tfrac12\mathbf e_A+\tfrac12\mathbf e_B.
\]

Without an objective, the outer state image is ambiguous. Maximising the coefficient of \(A\) realises \(t=1\) and returns \(\mathbf e_A\).

Now apply the total FG3 rule that adds edge `AB`. Both \(A\) and \(B\) map to \(B\), so:

\[
S'(t)=t\mathbf e_B+(1-t)\mathbf e_B=\mathbf e_B.
\]

The resulting outer family is constant and realises uniquely without an objective. This demonstrates a specifically combined behaviour: symbolic variation is retained outside, while configuration identification and coefficient collection occur inside.

For shared composition, if

\[
S(t)=t\mathbf e_A+(1-t)\mathbf e_B,
\qquad
T(t)=t\mathbf e_C+(1-t)\mathbf e_D,
\]

then their pointwise inner product uses coefficients \(t^2\), \(t(1-t)\) and \((1-t)^2\). It does not introduce an independent parameter \(u\).

## C.10 Laws and proof obligations

Within a common admitted domain and where every operation succeeds, CG3 checks representative instances of:

\[
\operatorname{eval}_\lambda(f_*\mathcal H)
=f_*\operatorname{eval}_\lambda(\mathcal H),
\]

\[
\operatorname{eval}_\lambda(\mathcal H+\mathcal G)
=\operatorname{eval}_\lambda(\mathcal H)
+\operatorname{eval}_\lambda(\mathcal G),
\]

and

\[
\operatorname{eval}_\lambda(
\operatorname{SharedExtend}_J(\mathcal H,\mathcal G))
=\operatorname{Extend}_J(
\operatorname{eval}_\lambda\mathcal H,
\operatorname{eval}_\lambda\mathcal G).
\]

These equalities do not license rewrites that change domain failures, resource outcomes, parameter dependence or the coefficient-expression grammar. A transformation that exceeds the polynomial-degree limit is unsupported even if some individual evaluations could be computed.

## C.11 Quantum and language boundary

CFS supplies a language-level form for an unresolved structured program: one symbol can denote a family of formal states, and connections between symbols can extend those states while preserving shared parameters. A compiler may later realise, specialise or lower such a construction.

A quantum profile would need a different or additional inner carrier with normalised complex amplitudes, physically valid state representations, permitted channels or unitary transformations, tensor-product and entanglement rules, measurement semantics and a mapping to an executable quantum intermediate representation. CFS rational cancellation alone does not provide those properties.

## C.12 Validation and development boundary

The companion implementation checks construction, endpoint and interior evaluation, ambiguity, exact realisation, pointwise pushforward, symbolic cancellation, the distinction between an empty outer family and a zero inner state, fixed extension, shared composition, lexicographic objectives, strict partial-rule failure, canonical interchange and malformed-input rejection.

The internal reference run on 2026-09-08 passed 40 named checks. These checks validate the bounded implementation against the rules above; they do not establish completeness of the general combined calculus.

The next useful expansion should be selected by a concrete program requiring one of: a jointly constrained multivariate outer carrier, configuration-valued symbolic terms, richer exact observables, or a separately specified complex-amplitude inner profile.
