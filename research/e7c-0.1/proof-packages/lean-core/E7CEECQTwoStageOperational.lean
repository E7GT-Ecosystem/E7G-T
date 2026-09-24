import E7CEECQTwoStageAllInput

/-!
Fuelled operational model for the selected correlated two-stage restriction.
The interpreter visits rows in order after charging a step and checking ledger
space. The full plan is retained separately as an independent specification.
Python/IR encoding correspondence is external.
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

/- The cursor holds only rows reached so far and the as-yet-unvisited tail.
The second stage receives first-retained rows only after the first stage ends. -/
inductive Cursor where
  | firstAttempt (rs : List Row)
  | firstRows (remaining keptRev excludedRev : List Row) (index : Nat)
  | secondAttempt (kept excluded : List Row)
  | secondRows (remaining retainedRev excluded secondExcludedRev : List Row) (index : Nat)
  | stopped (terminal : Terminal)
  deriving DecidableEq, Repr

def finished : Cursor → Option Terminal
  | .secondRows [] retainedRev excluded secondExcludedRev _ =>
      some (.success ⟨retainedRev.reverse, excluded, secondExcludedRev.reverse⟩)
  | .stopped t => some t
  | _ => none

def firstExcludedAt : Cursor → Option (List Row)
  | .firstRows [] _ excludedRev _ => some excludedRev.reverse
  | .secondAttempt _ excluded => some excluded
  | .secondRows _ _ excluded _ _ => some excluded
  | .stopped _ => none
  | _ => none

/- `advance` is called only AFTER a step has been charged and ledger space
checked. In particular its row branches cannot run on either exhausted bound. -/
def advance (first second : Policy) : Cursor → Event × Cursor
  | .firstAttempt rs =>
      (.attempt .first, match first with
        | .ready => .firstRows rs [] [] 0
        | .unsupported => .stopped (.unsupported .first)
        | .undetermined => .stopped (.undetermined .first))
  | .firstRows (r :: rs) keptRev excludedRev i =>
      if r.left.ab then
        (.row .first i r true, .firstRows rs keptRev (r :: excludedRev) (i + 1))
      else
        (.row .first i r false, .firstRows rs (r :: keptRev) excludedRev (i + 1))
  | .firstRows [] keptRev excludedRev _ =>
      (.attempt .second, match second with
        | .ready => .secondRows keptRev.reverse [] excludedRev.reverse [] 0
        | .unsupported => .stopped (.unsupported .second)
        | .undetermined => .stopped (.undetermined .second))
  | .secondAttempt kept excluded =>
      (.attempt .second, match second with
        | .ready => .secondRows kept [] excluded [] 0
        | .unsupported => .stopped (.unsupported .second)
        | .undetermined => .stopped (.undetermined .second))
  | .secondRows (r :: rs) retainedRev excluded secondExcludedRev i =>
      if r.right.bc then
        (.row .second i r true,
          .secondRows rs retainedRev excluded (r :: secondExcludedRev) (i + 1))
      else
        (.row .second i r false,
          .secondRows rs (r :: retainedRev) excluded secondExcludedRev (i + 1))
  | .secondRows [] retainedRev excluded secondExcludedRev i =>
      (.attempt .second, .secondRows [] retainedRev excluded secondExcludedRev i)
  | .stopped t => (.attempt .first, .stopped t)

structure Machine where
  cursor : Cursor
  steps : Nat
  ledgerRev : List Event
  deriving DecidableEq, Repr

def snapshot (machine : Machine) : Progress :=
  { completedSteps := machine.steps
    ledgerPrefix := machine.ledgerRev.reverse
    firstExcluded := firstExcludedAt machine.cursor
    secondExcludedPrefix := secondExcluded machine.ledgerRev.reverse }

def observe (machine : Machine) (terminal : Terminal) : Observation :=
  let p := snapshot machine
  { terminal := terminal
    orderedLedger := p.ledgerPrefix
    progress := p
    secondStarted := p.ledgerPrefix.any (fun e => e == .attempt .second) }

/- Fuel decreases at each attempted event. The zero-step branch does not
advance or inspect a row. An exhausted ledger consumes the attempted step,
then returns without calling `advance` and without appending an event. -/
def drive : Nat → Nat → Policy → Policy → Machine → Observation
  | 0, _, _, _, machine =>
      match finished machine.cursor with
      | some terminal => observe machine terminal
      | none => observe machine (.resourceLimit (snapshot machine))
  | fuel + 1, capacity, first, second, machine =>
      match finished machine.cursor with
      | some terminal => observe machine terminal
      | none =>
          let charged := { machine with steps := machine.steps + 1 }
          match capacity with
          | 0 => observe charged (.resourceLimit (snapshot charged))
          | space + 1 =>
              let (event, cursor) := advance first second machine.cursor
              drive fuel space first second
                { cursor := cursor, steps := charged.steps,
                  ledgerRev := event :: machine.ledgerRev }

def run (rs : List Row) (first second : Policy) (budget : Budget) : Observation :=
  drive budget.stepBound budget.ledgerBound first second
    { cursor := .firstAttempt rs, steps := 0, ledgerRev := [] }

/- These local laws expose the critical stop behavior directly, without
appealing to the complete planned trace. -/
theorem zero_steps_never_traverse (rs : List Row) (first second : Policy)
    (capacity : Nat) :
    (run rs first second ⟨0, capacity⟩).orderedLedger = [] ∧
    (run rs first second ⟨0, capacity⟩).terminal =
      .resourceLimit ⟨0, [], none, []⟩ := by
  constructor <;> rfl

theorem failed_first_append_consumes_step (rs : List Row) (first second : Policy)
    (fuel : Nat) :
    (run rs first second ⟨fuel + 1, 0⟩).orderedLedger = [] ∧
    (run rs first second ⟨fuel + 1, 0⟩).terminal =
      .resourceLimit ⟨1, [], none, []⟩ := by
  constructor <;> rfl

end E7CEECQTwoStageOperational
