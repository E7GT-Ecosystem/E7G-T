/-!
A selected FG3 strict-union refinement for one admitted support row.
The fixed edges AB/AC/BC are represented by three booleans. Optional tags
are represented by Option Nat under a fixed injective tag encoding. This
module proves a relation between two Lean definitions, not to Python code.
-/

namespace E7CS1FG3Single

structure Graph where
  ab : Bool
  ac : Bool
  bc : Bool
  tag : Option Nat
  deriving DecidableEq, Repr

def unionGraph (left right : Graph) : Graph :=
  ⟨left.ab || right.ab, left.ac || right.ac,
   left.bc || right.bc, left.tag⟩

/- Both coordinates are fixed-edge FG3 graphs. The nominal S1 module and
signature edition remains an external premise. Canonical support has already
been admitted, so its one coefficient is nonzero. -/
structure AdmittedRow where
  left : Graph
  right : Graph
  coefficient : Rat
  nonzero : coefficient ≠ 0

abbrev State := List (Graph × Rat)

inductive Terminal where
  | success (state : State)
  | domainError
  | resourceLimit
  deriving DecidableEq, Repr

inductive Event where
  | strictSuccess (visits support : Nat)
  | strictDomain (visits offendingIndex : Nat)
  deriving DecidableEq, Repr

structure Observation where
  terminal : Terminal
  steps : Nat
  visits : Nat
  ledger : List Event
  deriving DecidableEq, Repr

/- Source equation for the selected one-row FG3 join, after admission and
canonical support construction; none is whole domain failure. -/
def sourceOne (row : AdmittedRow) : Option (Graph × Rat) :=
  if row.left.tag = row.right.tag then
    some (unionGraph row.left row.right, row.coefficient)
  else none

def sourceTerminal (value : Option (Graph × Rat)) : Terminal :=
  match value with
  | some image => .success [image]
  | none => .domainError

/- Two term entries (strict_union, then its variable) precede the visit.
The visit is charged before tag comparison, as in the S1 evaluator. -/
def runOne (row : AdmittedRow) (maxSteps maxVisits : Nat) : Observation :=
  if maxSteps < 2 then
    ⟨.resourceLimit, maxSteps, 0, []⟩
  else if maxVisits = 0 then
    ⟨.resourceLimit, 2, 0, []⟩
  else if row.left.tag = row.right.tag then
    ⟨.success [(unionGraph row.left row.right, row.coefficient)],
     2, 1, [.strictSuccess 1 1]⟩
  else
    ⟨.domainError, 2, 1, [.strictDomain 1 0]⟩

theorem sufficient_budget_refines (row : AdmittedRow) (maxSteps maxVisits : Nat)
    (stepsOK : 2 ≤ maxSteps) (visitsOK : 1 ≤ maxVisits) :
    (runOne row maxSteps maxVisits).terminal =
      sourceTerminal (sourceOne row) := by
  have notStepBound : ¬ maxSteps < 2 := Nat.not_lt.mpr stepsOK
  have notVisitBound : maxVisits ≠ 0 := Nat.ne_of_gt visitsOK
  by_cases compatible : row.left.tag = row.right.tag
  · simp [runOne, sourceOne, sourceTerminal, notStepBound,
      notVisitBound, compatible]
  · simp [runOne, sourceOne, sourceTerminal, notStepBound,
      notVisitBound, compatible]

theorem insufficient_steps_precede_domain (row : AdmittedRow)
    (maxSteps maxVisits : Nat) (short : maxSteps < 2) :
    runOne row maxSteps maxVisits =
      ⟨.resourceLimit, maxSteps, 0, []⟩ := by
  simp [runOne, short]

theorem insufficient_visits_precede_domain (row : AdmittedRow)
    (maxSteps : Nat) (stepsOK : 2 ≤ maxSteps) :
    runOne row maxSteps 0 = ⟨.resourceLimit, 2, 0, []⟩ := by
  simp [runOne, Nat.not_lt.mpr stepsOK]

theorem compatible_observation (row : AdmittedRow) (maxSteps maxVisits : Nat)
    (stepsOK : 2 ≤ maxSteps) (visitsOK : 1 ≤ maxVisits)
    (compatible : row.left.tag = row.right.tag) :
    runOne row maxSteps maxVisits =
      ⟨.success [(unionGraph row.left row.right, row.coefficient)],
       2, 1, [.strictSuccess 1 1]⟩ := by
  simp [runOne, Nat.not_lt.mpr stepsOK, Nat.ne_of_gt visitsOK, compatible]

theorem incompatible_observation (row : AdmittedRow) (maxSteps maxVisits : Nat)
    (stepsOK : 2 ≤ maxSteps) (visitsOK : 1 ≤ maxVisits)
    (bad : row.left.tag ≠ row.right.tag) :
    runOne row maxSteps maxVisits =
      ⟨.domainError, 2, 1, [.strictDomain 1 0]⟩ := by
  simp [runOne, Nat.not_lt.mpr stepsOK, Nat.ne_of_gt visitsOK, bad]

/- Exact collision arithmetic needed by the following multi-row package.
The zero output has empty support, not a zero-weight row. -/
def collectSame (graph : Graph) (first second : Rat) : State :=
  if first + second = 0 then [] else [(graph, first + second)]

theorem opposite_coefficients_cancel (graph : Graph) (amount : Rat) :
    collectSame graph amount (-amount) = [] := by
  simp [collectSame, Rat.add_neg_cancel]

end E7CS1FG3Single
