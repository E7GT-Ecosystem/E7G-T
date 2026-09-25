import E7CEECQTwoStageOperational

/-!
First-stage control-flow skeleton for the selected Joint source and IR paths.
Charging precedes the ledger append and a row is visited only with both
resources available. These are the branches the actual Python AST pin audits.
This Lean machine is NOT a verified translation of Python or the IR executor;
that implementation correspondence is an independent open obligation.
-/

namespace E7CJointFirstCodeSkeleton
open E7CEECQTwoStageAllInput
open E7CEECQTwoStageOperational

inductive ChildTerminal where
  | complete (retained excluded : List Row)
  | resourceLimit
  | unsupported
  | undetermined
  deriving DecidableEq, Repr

structure ChildObservation where
  terminal : ChildTerminal
  orderedLedger : List Event
  steps : Nat
  deriving DecidableEq, Repr

def child (terminal : ChildTerminal) (eventsRev : List Event)
    (steps : Nat) : ChildObservation :=
  ⟨terminal, eventsRev.reverse, steps⟩

def visit : List Row → List Row → List Row → Nat → Nat → Nat → Nat →
    List Event → ChildObservation
  | [], keptRev, excludedRev, _, steps, _, _, ledgerRev =>
      child (.complete keptRev.reverse excludedRev.reverse) ledgerRev steps
  | _ :: _, _, _, _, steps, 0, _, ledgerRev =>
      child .resourceLimit ledgerRev steps
  | _ :: _, _, _, _, steps, _ + 1, 0, ledgerRev =>
      child .resourceLimit ledgerRev (steps + 1)
  | r :: rest, keptRev, excludedRev, index, steps, fuel + 1, capacity + 1,
      ledgerRev =>
      if r.left.ab then
        visit rest keptRev (r :: excludedRev) (index + 1) (steps + 1)
          fuel capacity (.row .first index r true :: ledgerRev)
      else
        visit rest (r :: keptRev) excludedRev (index + 1) (steps + 1)
          fuel capacity (.row .first index r false :: ledgerRev)

def run (rs : List Row) (policy : Policy) : Nat → Nat → ChildObservation
  | 0, _ => child .resourceLimit [] 0
  | _ + 1, 0 => child .resourceLimit [] 1
  | fuel + 1, capacity + 1 =>
      let ledger := [.attempt .first]
      match policy with
      | .unsupported => child .unsupported ledger 1
      | .undetermined => child .undetermined ledger 1
      | .ready => visit rs [] [] 0 1 fuel capacity ledger

theorem zero_fuel (rs : List Row) (policy : Policy) (capacity : Nat) :
    run rs policy 0 capacity = ⟨.resourceLimit, [], 0⟩ := by
  rfl

theorem failed_attempt_append (rs : List Row) (policy : Policy) (fuel : Nat) :
    run rs policy (fuel + 1) 0 = ⟨.resourceLimit, [], 1⟩ := by
  rfl

theorem unsupported_stops_before_rows (rs : List Row) (fuel capacity : Nat) :
    run rs .unsupported (fuel + 1) (capacity + 1) =
      ⟨.unsupported, [.attempt .first], 1⟩ := by
  rfl

theorem undetermined_stops_before_rows (rs : List Row) (fuel capacity : Nat) :
    run rs .undetermined (fuel + 1) (capacity + 1) =
      ⟨.undetermined, [.attempt .first], 1⟩ := by
  rfl

theorem failed_row_append (r : Row) (rest : List Row)
    (ledgerRev : List Event) (steps index fuel : Nat) :
    visit (r :: rest) [] [] index steps (fuel + 1) 0 ledgerRev =
      ⟨.resourceLimit, ledgerRev.reverse, steps + 1⟩ := by
  rfl

theorem visit_all (rs keptRev excludedRev : List Row)
    (index steps : Nat) (ledgerRev : List Event) :
    (visit rs keptRev excludedRev index steps rs.length rs.length
      ledgerRev).terminal =
      .complete
        (keptRev.reverse ++ rs.filter (fun r => !r.left.ab))
        (excludedRev.reverse ++ rs.filter (fun r => r.left.ab)) := by
  induction rs generalizing keptRev excludedRev index steps ledgerRev with
  | nil => rfl
  | cons r rest ih =>
      cases h : r.left.ab <;>
        simp [visit, h, ih, List.filter_cons, List.reverse_cons, List.append_assoc]

theorem sufficient_exact_budget (rs : List Row) :
    (run rs .ready (rs.length + 1) (rs.length + 1)).terminal =
      .complete (rs.filter (fun r => !r.left.ab))
        (rs.filter (fun r => r.left.ab)) := by
  simpa [run, child] using visit_all rs [] [] 0 1 [.attempt .first]

end E7CJointFirstCodeSkeleton
