import E7CEECQTwoStageAllInput

/-!
Budget-sensitive operational model for the selected correlated two-stage
restriction. The planned order is first attempt, all first rows, second
attempt, then only first-retained rows. Budget truncation charges a step
before checking ledger space. Python/IR encoding correspondence is external.
-/

namespace E7CEECQTwoStageOperational
open E7CEECQTwoStageAllInput

inductive Stage where
  | first | second
  deriving DecidableEq, Repr

inductive Policy where
  | ready | unsupported | undetermined
  deriving DecidableEq, Repr

inductive Event where
  | attempt (stage : Stage)
  | row (stage : Stage) (index : Nat) (value : Row) (excluded : Bool)
  deriving DecidableEq, Repr

structure Budget where
  stepBound : Nat
  ledgerBound : Nat
  deriving DecidableEq, Repr

def firstRows : List Row → Nat → List Event
  | [], _ => []
  | r :: rs, i => .row .first i r r.left.ab :: firstRows rs (i + 1)

def secondRows : List Row → Nat → List Event
  | [], _ => []
  | r :: rs, i => .row .second i r r.right.bc :: secondRows rs (i + 1)

def firstTrace (rs : List Row) : List Event :=
  .attempt .first :: firstRows rs 0

def secondTrace (rs : List Row) : List Event :=
  .attempt .second :: secondRows (source rs).retained 0

def plan (rs : List Row) (first second : Policy) : List Event :=
  if first ≠ .ready then [.attempt .first]
  else if second ≠ .ready then firstTrace rs ++ [.attempt .second]
  else firstTrace rs ++ secondTrace rs

structure Cut where
  complete : Bool
  steps : Nat
  ledger : List Event
  deriving DecidableEq, Repr

def cut (events : List Event) (budget : Budget) : Cut :=
  let capacity := min budget.stepBound budget.ledgerBound
  let complete := decide (events.length ≤ capacity)
  { complete := complete
    ledger := events.take capacity
    steps := if complete then events.length
             else if budget.stepBound ≤ budget.ledgerBound
                  then budget.stepBound else budget.ledgerBound + 1 }

/- A resource terminal has a progress record, never a partial Partition. -/
structure Progress where
  completedSteps : Nat
  ledgerPrefix : List Event
  firstExcluded : Option (List Row)
  secondExcludedPrefix : List Row
  deriving DecidableEq, Repr

inductive Terminal where
  | success (value : Partition)
  | resourceLimit (progress : Progress)
  | unsupported (stage : Stage)
  | undetermined (stage : Stage)
  deriving DecidableEq, Repr

structure Observation where
  terminal : Terminal
  orderedLedger : List Event
  progress : Progress
  secondStarted : Bool
  deriving DecidableEq, Repr

def secondExcluded (events : List Event) : List Row :=
  events.filterMap fun event =>
    match event with
    | .row .second _ value true => some value
    | _ => none

def progress (rs : List Row) (first : Policy) (charged : Cut) : Progress :=
  { completedSteps := charged.steps
    ledgerPrefix := charged.ledger
    firstExcluded := if decide (first = .ready) && decide ((firstTrace rs).length ≤ charged.ledger.length)
                     then some (source rs).firstExcluded else none
    secondExcludedPrefix := secondExcluded charged.ledger }

def completedTerminal (rs : List Row) (first second : Policy) : Terminal :=
  match first with
  | .unsupported => .unsupported .first
  | .undetermined => .undetermined .first
  | .ready =>
    match second with
    | .unsupported => .unsupported .second
    | .undetermined => .undetermined .second
    | .ready => .success (source rs)

def run (rs : List Row) (first second : Policy) (budget : Budget) : Observation :=
  let charged := cut (plan rs first second) budget
  let p := progress rs first charged
  { terminal := if charged.complete then completedTerminal rs first second
                else .resourceLimit p
    orderedLedger := charged.ledger
    progress := p
    secondStarted := decide (first = .ready) && decide ((firstTrace rs).length < charged.steps) }

theorem sufficient_budgets_produce_partition (rs : List Row) (budget : Budget)
    (steps : (plan rs .ready .ready).length ≤ budget.stepBound)
    (ledger : (plan rs .ready .ready).length ≤ budget.ledgerBound) :
    (run rs .ready .ready budget).terminal = .success (source rs) := by
  have enough : (plan rs .ready .ready).length ≤
      min budget.stepBound budget.ledgerBound := Nat.le_min.mpr ⟨steps, ledger⟩
  simp [run, cut, enough, completedTerminal]

theorem exhaustion_returns_prefix (rs : List Row) (first second : Policy)
    (budget : Budget)
    (short : ¬ (plan rs first second).length ≤
      min budget.stepBound budget.ledgerBound) :
    (run rs first second budget).terminal =
      .resourceLimit (run rs first second budget).progress ∧
    (run rs first second budget).orderedLedger =
      (plan rs first second).take (min budget.stepBound budget.ledgerBound) := by
  simp [run, cut, short]

theorem full_success_agrees_with_recursive_partition (rs : List Row) (budget : Budget)
    (steps : (plan rs .ready .ready).length ≤ budget.stepBound)
    (ledger : (plan rs .ready .ready).length ≤ budget.ledgerBound) :
    (run rs .ready .ready budget).terminal = .success (ir rs) := by
  rw [all_rows_partition_agreement]
  exact sufficient_budgets_produce_partition rs budget steps ledger

end E7CEECQTwoStageOperational
