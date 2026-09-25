import E7CEECQTwoStageExactCodec

/-!
Conditional refinement interface for the selected source and independent IR
execution paths. A `Trace` is an explicit external transition certificate.
It must account for every charged step, failed ledger append, row visit and
terminal observation. This file proves any such certificate refines the Lean
staged evaluator. It does not establish that the Python functions `evaluate`
or `execute` emit certificates for every admitted document; that is a separate
implementation verification obligation.
-/

namespace E7CEECQTwoStageImplementationPath
open E7CEECQTwoStageAllInput
open E7CEECQTwoStageOperational
open E7CEECQTwoStageExactCodec

inductive Path where
  | source | ir
  deriving DecidableEq, Repr

def charge (machine : Machine) : Machine :=
  { machine with
    steps := machine.steps + 1
    secondStarted := machine.secondStarted || attemptingSecond machine.cursor }

def append (first second : Policy) (machine : Machine) : Machine :=
  let (event, cursor) := advance first second machine.cursor
  { cursor := cursor
    steps := machine.steps + 1
    ledgerRev := event :: machine.ledgerRev
    secondStarted := machine.secondStarted || attemptingSecond machine.cursor }

theorem failed_second_append_charges_without_event (machine : Machine)
    (h : attemptingSecond machine.cursor = true) :
    (charge machine).steps = machine.steps + 1 ∧
    (charge machine).ledgerRev = machine.ledgerRev ∧
    (charge machine).secondStarted = true := by
  simp [charge, h]

/- The `Path` index requires a separate source or IR certificate, while the
admitted selected semantics prescribe the same observable transitions.
`append` cannot run when either resource is exhausted. A failed append
charges exactly one step and retains the old cursor and ledger. -/
inductive Trace (path : Path) (first second : Policy) :
    Nat → Nat → Machine → Observation → Prop where
  | terminal (fuel capacity : Nat) (machine : Machine) (outcome : Terminal)
      (h : finished machine.cursor = some outcome) :
      Trace path first second fuel capacity machine (observe machine outcome)
  | noFuel (capacity : Nat) (machine : Machine)
      (h : finished machine.cursor = none) :
      Trace path first second 0 capacity machine
        (observe machine (.resourceLimit (snapshot machine)))
  | noLedger (fuel : Nat) (machine : Machine)
      (h : finished machine.cursor = none) :
      Trace path first second (fuel + 1) 0 machine
        (observe (charge machine) (.resourceLimit (snapshot (charge machine))))
  | visited (fuel capacity : Nat) (machine : Machine) (result : Observation)
      (h : finished machine.cursor = none)
      (tail : Trace path first second fuel capacity
        (append first second machine) result) :
      Trace path first second (fuel + 1) (capacity + 1) machine result

theorem trace_refines_drive {path : Path} {first second : Policy}
    {fuel capacity : Nat} {machine : Machine} {result : Observation}
    (certificate : Trace path first second fuel capacity machine result) :
    result = drive fuel capacity first second machine := by
  induction certificate with
  | terminal fuel capacity machine outcome h =>
      cases fuel <;> simp [drive, h]
  | noFuel capacity machine h => simp [drive, h]
  | noLedger fuel machine h => simp [drive, h, charge]
  | visited fuel capacity machine result h tail ih =>
      simpa [drive, h, append] using ih

def initial (rs : List Row) : Machine :=
  { cursor := .firstAttempt rs, steps := 0, ledgerRev := [],
    secondStarted := false }

theorem source_or_ir_refines_run (path : Path) (rs : List WireRow)
    (first second : Policy) (budget : Budget) (result : Observation)
    (certificate : Trace path first second budget.stepBound
      budget.ledgerBound (initial (rs.map toRow)) result) :
    result = run (rs.map toRow) first second budget := by
  simpa [run, initial] using trace_refines_drive certificate

/- The exact Python-side paired certificate records two *instances*. In Lean,
the corresponding mathematical statement has explicit source and IR Trace
premises. An external checker cannot discharge those premises for all Python
program executions merely by running on a finite collection of documents. -/
theorem certified_source_ir_agree (rs : List WireRow)
    (first second : Policy) (budget : Budget)
    (sourceResult irResult : Observation)
    (sourceCertificate : Trace .source first second budget.stepBound
      budget.ledgerBound (initial (rs.map toRow)) sourceResult)
    (irCertificate : Trace .ir first second budget.stepBound
      budget.ledgerBound (initial (rs.map toRow)) irResult) :
    sourceResult = irResult ∧
    sourceResult.orderedLedger = (wirePlan rs first second).take
      (min budget.stepBound budget.ledgerBound) := by
  have hs := source_or_ir_refines_run .source rs first second budget
    sourceResult sourceCertificate
  have hi := source_or_ir_refines_run .ir rs first second budget
    irResult irCertificate
  constructor
  · exact hs.trans hi.symm
  · rw [hs]
    exact wire_budgeted_event_simulation rs first second budget

/- The exact admitted wire event plan is inherited by every certified path.
This conclusion carries complete correlated rows and coefficients in each
appended row event, including short-budget prefixes. -/
theorem certified_ledger_is_wire_prefix (path : Path) (rs : List WireRow)
    (first second : Policy) (budget : Budget) (result : Observation)
    (certificate : Trace path first second budget.stepBound
      budget.ledgerBound (initial (rs.map toRow)) result) :
    result.orderedLedger = (wirePlan rs first second).take
      (min budget.stepBound budget.ledgerBound) := by
  rw [source_or_ir_refines_run path rs first second budget result certificate]
  exact wire_budgeted_event_simulation rs first second budget

theorem certified_exhaustion_has_no_partial_partition (path : Path)
    (rs : List WireRow) (first second : Policy) (budget : Budget)
    (result : Observation)
    (certificate : Trace path first second budget.stepBound
      budget.ledgerBound (initial (rs.map toRow)) result)
    (short : min budget.stepBound budget.ledgerBound <
      (wirePlan rs first second).length) :
    result.terminal = .resourceLimit result.progress ∧
    result.progress.completedSteps =
      if budget.stepBound ≤ budget.ledgerBound then budget.stepBound
      else budget.ledgerBound + 1 := by
  have hs : min budget.stepBound budget.ledgerBound <
      (plan (rs.map toRow) first second).length := by
    simpa [wire_plan_simulation] using short
  have h := exhaustion_returns_prefix_and_steps (rs.map toRow)
    first second budget hs
  rw [source_or_ir_refines_run path rs first second budget result certificate]
  exact ⟨h.1, h.2.2⟩

end E7CEECQTwoStageImplementationPath
