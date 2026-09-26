import E7CEECQTwoStageOperational

/-!
The selected /0.6 IR second-attempt transition. This is a typed operational
relation for the boundary after the /0.5 child succeeded. Its connection to
the running Python IR executor has an explicit execution-adequacy premise;
the relation itself does not interpret CPython or canonical JSON.
-/

namespace E7CJointIRSecondAttempt
open E7CEECQTwoStageOperational
open E7CEECQTwoStageAllInput

def entry (keptRev excludedRev : List Row) (index steps : Nat)
    (ledgerRev : List Event) : Machine :=
  { cursor := .firstRows [] keptRev excludedRev index
    steps := steps, ledgerRev := ledgerRev, secondStarted := false }

inductive StepResult where
  | stopped (observation : Observation)
  | continued (machine : Machine)
  deriving DecidableEq, Repr

def chargedSecond (m : Machine) : Machine :=
  let charged := { m with steps := m.steps + 1 }
  { charged with secondStarted := true }

/- Each successor rule charges first. The append-blocked rule has no
   second-attempt event, but the start bit becomes true. -/
inductive IRStep (first second : Policy) :
    Nat → Nat → Machine → StepResult → Prop where
  | noFuel (m : Machine) (capacity : Nat) :
      IRStep first second 0 capacity m
        (.stopped (observe m (.resourceLimit (snapshot m))))
  | appendBlocked (m : Machine) (fuel : Nat)
      (h : attemptingSecond m.cursor = true)
      (unfinished : finished m.cursor = none) :
      IRStep first second (fuel + 1) 0 m
        (.stopped (observe (chargedSecond m)
          (.resourceLimit (snapshot (chargedSecond m)))))
  | appended (m : Machine) (fuel capacity : Nat) (e : Event)
      (nextCursor : Cursor) (h : attemptingSecond m.cursor = true)
      (unfinished : finished m.cursor = none)
      (advanceEq : advance first second m.cursor = (e, nextCursor)) :
      IRStep first second (fuel + 1) (capacity + 1) m
        (.continued { cursor := nextCursor
          steps := m.steps + 1
          ledgerRev := e :: m.ledgerRev
          secondStarted := true })

theorem entry_attempting_second (keptRev excludedRev : List Row)
    (index steps : Nat) (ledgerRev : List Event) :
    attemptingSecond (entry keptRev excludedRev index steps ledgerRev).cursor = true := rfl

theorem entry_unfinished (keptRev excludedRev : List Row)
    (index steps : Nat) (ledgerRev : List Event) :
    finished (entry keptRev excludedRev index steps ledgerRev).cursor = none := rfl

theorem blocked_has_exact_progress (keptRev excludedRev : List Row)
    (index steps fuel : Nat) (ledgerRev : List Event)
    (first second : Policy) :
    IRStep first second (fuel + 1) 0
      (entry keptRev excludedRev index steps ledgerRev)
      (.stopped (drive (fuel + 1) 0 first second
        (entry keptRev excludedRev index steps ledgerRev))) ∧
    (drive (fuel + 1) 0 first second
      (entry keptRev excludedRev index steps ledgerRev)).secondStarted = true ∧
    (drive (fuel + 1) 0 first second
      (entry keptRev excludedRev index steps ledgerRev)).orderedLedger = ledgerRev.reverse ∧
    (drive (fuel + 1) 0 first second
      (entry keptRev excludedRev index steps ledgerRev)).progress.completedSteps = steps + 1 := by
  refine ⟨?_, rfl, rfl, rfl⟩
  exact IRStep.appendBlocked
    (entry keptRev excludedRev index steps ledgerRev) fuel
    (entry_attempting_second keptRev excludedRev index steps ledgerRev)
    (entry_unfinished keptRev excludedRev index steps ledgerRev)

theorem append_has_one_second_event (keptRev excludedRev : List Row)
    (index steps fuel capacity : Nat) (ledgerRev : List Event)
    (first second : Policy) :
    ∃ nextCursor : Cursor,
      IRStep first second (fuel + 1) (capacity + 1)
        (entry keptRev excludedRev index steps ledgerRev)
        (.continued { cursor := nextCursor
          steps := steps + 1
          ledgerRev := .attempt .second :: ledgerRev
          secondStarted := true }) := by
  cases second with
  | ready =>
      exact ⟨_, .appended _ _ _ _ _ _ _
        (entry_attempting_second keptRev excludedRev index steps ledgerRev)
        (entry_unfinished keptRev excludedRev index steps ledgerRev) rfl⟩
  | unsupported =>
      exact ⟨_, .appended _ _ _ _ _ _ _
        (entry_attempting_second keptRev excludedRev index steps ledgerRev)
        (entry_unfinished keptRev excludedRev index steps ledgerRev) rfl⟩
  | undetermined =>
      exact ⟨_, .appended _ _ _ _ _ _ _
        (entry_attempting_second keptRev excludedRev index steps ledgerRev)
        (entry_unfinished keptRev excludedRev index steps ledgerRev) rfl⟩

/- A concrete executor-to-relation step is a *premise*, not obtained by
   interpreting the Python AST or by comparing a finite replay. -/
structure AdequateIRSecondStep
    (first second : Policy) (fuel capacity : Nat) (before : Machine)
    (actual : StepResult) : Prop where
  actual_derivation : IRStep first second fuel capacity before actual

theorem adequate_blocked_observation (keptRev excludedRev : List Row)
    (index steps fuel : Nat) (ledgerRev : List Event)
    (first second : Policy) (actual : StepResult)
    (h : AdequateIRSecondStep first second (fuel + 1) 0
      (entry keptRev excludedRev index steps ledgerRev) actual) :
    actual = .stopped (drive (fuel + 1) 0 first second
      (entry keptRev excludedRev index steps ledgerRev)) := by
  cases h.actual_derivation with
  | appendBlocked => rfl

end E7CJointIRSecondAttempt
