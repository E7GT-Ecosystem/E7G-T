# E7G-T MSC/0.1 — Multi-Scope Coherence

**Status:** optional speculative formal-research proposal  
**Profile identifier:** `MSC/0.1`  
**Bounded implementation:** `MSC-B1/0.1`

## MSC.0 Purpose and non-claims

MSC formalises a question left open between RGP and WPC:

> When several bounded wholes are admitted at different scopes, under what
> declared maps and criteria do they form one compatible multi-scope family?

MSC does not assert that any represented scope exists externally, that reality
is infinitely nested, that a higher scope controls a lower scope, or that a
compatible family is unique or complete. `REC/0.1` remains reserved for the
Reasoning–Evidence Calculus.

## MSC.1 Typed finite scope diagram

A finite MSC diagram is

```math
\mathfrak D=\langle S,\preceq,\{B_s\},\{V_a\},\mathcal M,\mathcal L,Q,M\rangle,
```

where $S$ is a finite set of scopes, $B_s$ is the state carrier of the
whole at scope $s$, $V_a$ are declared comparison carriers,
$\mathcal M$ is a family of typed partial maps, $\mathcal L$ is a family of
scope links, $Q$ contains comparison criteria, and $M$ records editions,
domains and provenance.

$\mathcal L$ is a finite acyclic scope-extension graph. The scope order
$\preceq$ is its reflexive-transitive closure; it is not an additional
unvalidated relation. Links need not be supplied for every comparable pair.

For every link $e:s\preceq t$, MSC requires maps with a common codomain:

```math
P_e:B_t\rightharpoonup V_e,
\qquad
C_e:B_s\rightharpoonup V_e.
```

`P_e` projects the higher-scope whole into a comparison view. `C_e` is the
**lower-scope comparison map** translating the independently constituted
lower-scope whole into that same view. The bridge is the complete span:

```math
B_s\xrightarrow{C_e}V_e\xleftarrow{P_e}B_t.
```

The names
`projection`, `participation`, `containment`, `scope extension` and `encoding`
remain separately typed. Neither map is assumed invertible.

## MSC.2 Link coherence

A pair $(w_s,w_t)$ is coherent at link $e$ when both maps are defined and

```math
P_e(w_t)\approx_{Q_e}C_e(w_s).
```

This does not assert $P_e(w_t)=w_s$. Literal equality is available only when
the carriers and declared criterion license it.

## MSC.3 Compatible scope family

For partial abstract maps, first define the jointly evaluable assignments:

```math
A_{\mathfrak D}
=
\left\{(w_s)_{s\in S}\in\prod_{s\in S}B_s
\;\middle|\;
w_t\in\operatorname{dom}(P_e)
\land
w_s\in\operatorname{dom}(C_e)
\text{ for every }e:s\preceq t
\right\}.
```

The compatible-family set is

```math
\Omega_{\mathfrak D}
=
\left\{
(w_s)_{s\in S}\in A_{\mathfrak D}
\;\middle|\;
P_e(w_t)\approx_{Q_e}C_e(w_s)
\text{ for every }e:s\preceq t
\right\}.
```

The closure classifier is:

```math
\operatorname{Close}(\mathfrak D)=
\begin{cases}
\operatorname{unique}(\omega), & |\Omega_{\mathfrak D}|=1,\\
\operatorname{ambiguous}(\Omega_{\mathfrak D}), & |\Omega_{\mathfrak D}|>1,\\
\operatorname{incompatible}(O), & |\Omega_{\mathfrak D}|=0,\\
\operatorname{unsupported}, & \text{a required map or criterion is unavailable},\\
\operatorname{resource\_limit}, & \text{the declared bound is exceeded},\\
\operatorname{undetermined}, & \text{the admitted procedure cannot decide.}
\end{cases}
```

Here $O$ is an obstruction record; it establishes incompatibility only within
the pinned carriers, maps, criteria and boundaries. If
$A_{\mathfrak D}=\varnothing$, evaluation is `unsupported`, not
`incompatible`.

## MSC.4 Link-wise versus global closure

MSC uses **link-wise satisfiability**: every individual declared link admits at
least one coherent endpoint pair when considered independently. This does not
claim every mathematical notion of pairwise consistency among overlapping
constraint projections. Link-wise satisfiability does not imply a globally
compatible family:

```math
\bigl(\forall e\in\mathcal L:\Omega_e\ne\varnothing\bigr)
\not\Rightarrow
\Omega_{\mathfrak D}\ne\varnothing.
```

MSC-B1 includes a finite parity-cycle counterexample. This is a principal
reason to treat multi-scope closure as more than independent link checking.

## MSC.5 Projection composition

For typed maps $f_1,\ldots,f_n$, MSC may compare a direct map $d$ with their
composition when source and target carriers match:

```math
d\stackrel?=f_n\circ\cdots\circ f_1.
```

Results are `commuting`, `criterion_commuting`, `non_commuting`,
`domain_mismatch`, `unsupported`, or `undetermined`. Direct and staged access
need not preserve the same information.

## MSC.6 Access-induced quotient

For occurrence $i$, context $\xi$, and a declared observation family
$\mathcal O_{i,\xi}$:

```math
w\sim_{i,\xi}w'
\iff
\forall o\in\mathcal O_{i,\xi},\;o(w)=o(w').
```

The equivalence class $[w]_{i,\xi}$ is the locally distinguishable state.
For partial observations, equivalence requires both applications to be defined
and equal, or both to be undefined under the same declared missingness rule.
Stochastic observations require a separately declared distributional
criterion; raw-value equality is not silently applied.

When $\mathcal O_{i,\xi}=\varnothing$, the induced relation is universal and
the quotient has one class. This represents no distinguishing access.

MSC therefore separates:

1. retained content;
2. accessible operations;
3. contextual expression; and
4. authority to act.

Exact WPC retention does not imply that a local actor can access or authorise
the retained content.

## MSC.7 Cross-scope invariants and retention strength

For a common invariant carrier $K$, typed extractors

```math
\kappa_s:B_s\rightharpoonup K
```

preserve an invariant on the compatible-family set when, for every
$\omega\in\Omega_{\mathfrak D}$, every selected $\kappa_s(w_s)$ is defined and
all selected values agree. Undefined extraction on a member of
$\Omega_{\mathfrak D}$ reports `unsupported`; undefined extraction outside
$\Omega_{\mathfrak D}$ does not defeat preservation. The strongest established
statement must be named:

- SR0: lineage only;
- SR1: shared invariant;
- SR2: shared generative rule;
- SR3: criterion-relative recovery;
- SR4: exact reconstruction.

SR1 must not be reported as SR4. When MSC composes WPC/0.2, the source of
lineage must be explicit as an input or a deterministic derivation.

## MSC.8 Reconstruction fibres

Define the scope coordinate projection by

```math
\pi_s((w_u)_{u\in S})=w_s.
```

For a scope state $b\in B_s$, its scope-state reconstruction fibre is

```math
\operatorname{Rec}_s(b)
=
\{\omega\in\Omega_{\mathfrak D}\mid\pi_s(\omega)=b\}.
```

For an observation map $o:B_s\rightharpoonup V$ and observed value $v$, the
observation fibre is

```math
\operatorname{ObsRec}_{s,o}(v)
=
\{\omega\in\Omega_{\mathfrak D}\mid
\pi_s(\omega)\in\operatorname{dom}(o)
\land o(\pi_s(\omega))=v\}.
```

A scope state and a local observation therefore determine different fibres;
neither automatically identifies a unique enclosing family.

## MSC.9 Symbolically unbounded families

MSC-Core/0.1 is finite. A potentially unbounded hierarchy may be described by
SF/0.1 and examined through declared finite windows $\mathfrak D_{\le N}$.
Success at every tested $N$ does not establish a completed infinite hierarchy
unless a separate theorem licenses that inference.

## MSC.10 Laws

| ID | Law |
| --- | --- |
| MS1 | Every evaluated scope diagram has an explicit finite boundary. |
| MS2 | Scope extension, participation, projection, encoding and authority remain separately typed. |
| MS3 | Every coherence comparison uses maps into a declared common carrier and a pinned criterion. |
| MS4 | A local whole is not identified with a higher-scope projection without an explicit identity bridge. |
| MS5 | Link-wise coherence does not establish global closure. |
| MS6 | A local view determines a reconstruction fibre, not automatically a unique enclosing family. |
| MS7 | Retention, accessibility, expression and authority are independent coordinates. |
| MS8 | Cross-scope commonality reports its strongest established SR tier. |
| MS9 | A higher scope has no automatic decision authority over a lower-scope occurrence. |
| MS10 | Finite evaluation does not establish a completed infinite hierarchy. |
| MS11 | Closure outcomes remain distinct; incompatibility and unsupported evaluation are not conflated. |
| MS12 | Structural compatibility establishes model-relative coherence, not external existence or universal completeness. |

## MSC.11 Compositional extensions

The following remain proposed extension families rather than MSC-Core
obligations:

- `MSC-H`: UC5 history envelopes and cross-scope temporal cuts;
- `MSC-L`: WPC-Evolution proposal lifts and reconciliation across scopes;
- `MSC-C`: RGP capability regimes and capability-preserving transitions;
- `MSC-F`: WPC materialisation/extraction/constitution fixed points;
- `MSC-R`: recursive or symbolically unbounded scope families.

History-wide compatibility must not be described as reverse causation. A local
proposal must not rewrite an enclosing whole without an admitted lift,
reconciliation and successor commitment. Fixed-point closure establishes
internal consistency only, not causal self-creation.

## MSC.12 Bounded reference profile

`MSC-B1/0.1` supports finite string-valued carriers, partial generic maps,
**total-on-admitted-carrier coherence maps**, exact-equality link criteria,
exhaustive compatible-family enumeration up to a caller-supplied combination
limit, link-wise satisfiability, access quotients, scope-state and observation
fibres, exact map-commutation tests and cross-scope invariant checks. Requiring
total coherence maps is the bounded implementation policy; the abstract
profile retains the partial-domain semantics above.

It does not implement general category-theoretic limits, sheaf cohomology,
symbolic infinity, probabilistic observations, temporal histories, proposal
lifts, fixed-point solvers, theorem proving or distributed execution.

## MSC.13 Promotion conditions

Promotion beyond research proposal requires:

1. formal review of carriers, partiality and comparison typing;
2. an independently constructed pairwise/global obstruction example;
3. an external implementation reproducing the required outcomes;
4. at least one concrete end-to-end consumer where MSC changes a real next move;
5. explicit compatibility with the corrected WPC lineage contract; and
6. preservation of the distinction between model coherence and empirical truth.
