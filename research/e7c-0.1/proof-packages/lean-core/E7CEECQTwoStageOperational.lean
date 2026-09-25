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
  .attempt .second :: secondRows (rs.filter (fun r => !r.left.ab)) 0

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
  | stopped (terminal : Terminal) (firstExcluded : Option (List Row))
  deriving DecidableEq, Repr

def finished : Cursor → Option Terminal
  | .secondRows [] retainedRev excluded secondExcludedRev _ =>
      some (.success ⟨retainedRev.reverse, excluded, secondExcludedRev.reverse⟩)
  | .stopped t _ => some t
  | _ => none

def firstExcludedAt : Cursor → Option (List Row)
  | .firstRows [] _ excludedRev _ => some excludedRev.reverse
  | .secondAttempt _ excluded => some excluded
  | .secondRows _ _ excluded _ _ => some excluded
  | .stopped _ excluded => excluded
  | _ => none

/- `advance` is called only AFTER a step has been charged and ledger space
checked. In particular its row branches cannot run on either exhausted bound. -/
def advance (first second : Policy) : Cursor → Event × Cursor
  | .firstAttempt rs =>
      (.attempt .first, match first with
        | .ready => .firstRows rs [] [] 0
        | .unsupported => .stopped (.unsupported .first) none
        | .undetermined => .stopped (.undetermined .first) none)
  | .firstRows (r :: rs) keptRev excludedRev i =>
      if r.left.ab then
        (.row .first i r true, .firstRows rs keptRev (r :: excludedRev) (i + 1))
      else
        (.row .first i r false, .firstRows rs (r :: keptRev) excludedRev (i + 1))
  | .firstRows [] keptRev excludedRev _ =>
      (.attempt .second, match second with
        | .ready => .secondRows keptRev.reverse [] excludedRev.reverse [] 0
        | .unsupported => .stopped (.unsupported .second) (some excludedRev.reverse)
        | .undetermined => .stopped (.undetermined .second) (some excludedRev.reverse))
  | .secondAttempt kept excluded =>
      (.attempt .second, match second with
        | .ready => .secondRows kept [] excluded [] 0
        | .unsupported => .stopped (.unsupported .second) (some excluded)
        | .undetermined => .stopped (.undetermined .second) (some excluded))
  | .secondRows (r :: rs) retainedRev excluded secondExcludedRev i =>
      if r.right.bc then
        (.row .second i r true,
          .secondRows rs retainedRev excluded (r :: secondExcludedRev) (i + 1))
      else
        (.row .second i r false,
          .secondRows rs (r :: retainedRev) excluded secondExcludedRev (i + 1))
  | .secondRows [] retainedRev excluded secondExcludedRev i =>
      (.attempt .second, .secondRows [] retainedRev excluded secondExcludedRev i)
  | .stopped t excluded => (.attempt .first, .stopped t excluded)

/- Independent continuation specification for a cursor. This is used in
proofs; the evaluator never builds it before charging a step. -/
def futureFirst (second : Policy) : List Row → List Row → Nat → List Event
  | [], keptRev, _ =>
      .attempt .second ::
        if second = .ready then secondRows keptRev.reverse 0 else []
  | r :: rs, keptRev, i =>
      .row .first i r r.left.ab ::
        futureFirst second rs (if r.left.ab then keptRev else r :: keptRev) (i + 1)

def future (first second : Policy) : Cursor → List Event
  | .firstAttempt rs =>
      .attempt .first :: if first = .ready then futureFirst second rs [] 0 else []
  | .firstRows rs keptRev _ i => futureFirst second rs keptRev i
  | .secondAttempt kept _ =>
      .attempt .second :: if second = .ready then secondRows kept 0 else []
  | .secondRows rs _ _ _ i => secondRows rs i
  | .stopped _ _ => []

theorem finished_has_no_future (first second : Policy) (cursor : Cursor)
    (terminal : Terminal) (h : finished cursor = some terminal) :
    future first second cursor = [] := by
  cases cursor with
  | firstAttempt rs => simp [finished] at h
  | firstRows rs keptRev excludedRev i => simp [finished] at h
  | secondAttempt kept excluded => simp [finished] at h
  | secondRows rs retainedRev excluded secondExcludedRev i =>
      cases rs with
      | nil => rfl
      | cons r rs => simp [finished] at h
  | stopped t excluded => rfl

theorem future_advance (first second : Policy) (cursor : Cursor)
    (h : finished cursor = none) :
    future first second cursor =
      (advance first second cursor).1 ::
        future first second (advance first second cursor).2 := by
  cases cursor with
  | firstAttempt rs => cases first <;> simp [future, advance, futureFirst]
  | firstRows rs keptRev excludedRev i =>
      cases rs with
      | nil => cases second <;> simp [future, futureFirst, advance]
      | cons r rs =>
          cases h_ab : r.left.ab <;>
            simp [future, futureFirst, advance, h_ab]
  | secondAttempt kept excluded => cases second <;> simp [future, advance]
  | secondRows rs retainedRev excluded secondExcludedRev i =>
      cases rs with
      | nil => simp [finished] at h
      | cons r rs => cases h_bc : r.right.bc <;>
          simp [future, secondRows, advance, h_bc]
  | stopped t excluded => simp [finished] at h

theorem futureFirst_agrees_with_plan (second : Policy) (rs keptRev : List Row)
    (i : Nat) :
    futureFirst second rs keptRev i = firstRows rs i ++
      (.attempt .second :: if second = .ready then
        secondRows (keptRev.reverse ++ rs.filter (fun r => !r.left.ab)) 0
      else []) := by
  induction rs generalizing keptRev i with
  | nil => cases second <;> simp [futureFirst, firstRows]
  | cons r rs ih =>
      cases h : r.left.ab <;>
        simp [futureFirst, firstRows, ih, h, List.reverse_cons, List.append_assoc]

theorem future_start_is_plan (rs : List Row) (first second : Policy) :
    future first second (.firstAttempt rs) = plan rs first second := by
  cases first <;> cases second <;>
    simp [future, plan, firstTrace, secondTrace, futureFirst_agrees_with_plan]

/- The residual partition represented by the cursor, including rows that
have not yet been visited. This expression is proof-only. -/
def partitionAt : Cursor → Option Partition
  | .firstAttempt rs => some (source rs)
  | .firstRows remaining keptRev excludedRev _ =>
      let kept := keptRev.reverse ++ remaining.filter (fun r => !r.left.ab)
      some ⟨kept.filter (fun r => !r.right.bc),
        excludedRev.reverse ++ remaining.filter (fun r => r.left.ab),
        kept.filter (fun r => r.right.bc)⟩
  | .secondAttempt kept excluded =>
      some ⟨kept.filter (fun r => !r.right.bc), excluded,
        kept.filter (fun r => r.right.bc)⟩
  | .secondRows remaining retainedRev excluded secondExcludedRev _ =>
      some ⟨retainedRev.reverse ++ remaining.filter (fun r => !r.right.bc),
        excluded, secondExcludedRev.reverse ++ remaining.filter (fun r => r.right.bc)⟩
  | .stopped (.success value) _ => some value
  | .stopped _ _ => none

theorem ready_step_preserves_partition (cursor : Cursor)
    (h : finished cursor = none) :
    partitionAt (advance .ready .ready cursor).2 = partitionAt cursor := by
  cases cursor with
  | firstAttempt rs =>
      simp [advance, partitionAt, source, List.filter_filter, Bool.and_comm]
  | firstRows rs keptRev excludedRev i =>
      cases rs with
      | nil => simp [advance, partitionAt, List.filter_append]
      | cons r rs =>
          cases h_ab : r.left.ab <;>
            simp [advance, partitionAt, h_ab, List.reverse_cons,
              List.filter_append, List.append_assoc]
  | secondAttempt kept excluded => simp [advance, partitionAt]
  | secondRows rs retainedRev excluded secondExcludedRev i =>
      cases rs with
      | nil => simp [finished] at h
      | cons r rs =>
          cases h_bc : r.right.bc <;>
            simp [advance, partitionAt, h_bc, List.reverse_cons,
              List.filter_append, List.append_assoc]
  | stopped t excluded => simp [finished] at h

theorem finished_success_is_partition (cursor : Cursor) (value : Partition)
    (h : finished cursor = some (.success value)) :
    partitionAt cursor = some value := by
  cases cursor with
  | firstAttempt rs => simp [finished] at h
  | firstRows rs keptRev excludedRev i => simp [finished] at h
  | secondAttempt kept excluded => simp [finished] at h
  | secondRows rs retainedRev excluded secondExcludedRev i =>
      cases rs with
      | nil => simpa [finished, partitionAt] using h
      | cons r rs => simp [finished] at h
  | stopped t excluded =>
      simp [finished] at h
      cases t <;> simp_all [partitionAt]

structure Machine where
  cursor : Cursor
  steps : Nat
  ledgerRev : List Event
  secondStarted : Bool
  deriving DecidableEq, Repr

def attemptingSecond : Cursor → Bool
  | .firstRows [] _ _ _ => true
  | .secondAttempt _ _ => true
  | _ => false

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
    secondStarted := machine.secondStarted }

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
          let charged := { charged with
            secondStarted := machine.secondStarted || attemptingSecond machine.cursor }
          match capacity with
          | 0 => observe charged (.resourceLimit (snapshot charged))
          | space + 1 =>
              let (event, cursor) := advance first second machine.cursor
              drive fuel space first second
                { cursor := cursor, steps := charged.steps,
                  ledgerRev := event :: machine.ledgerRev,
                  secondStarted := charged.secondStarted }

def run (rs : List Row) (first second : Policy) (budget : Budget) : Observation :=
  drive budget.stepBound budget.ledgerBound first second
    { cursor := .firstAttempt rs, steps := 0, ledgerRev := [], secondStarted := false }

theorem finished_partition (cursor : Cursor) (terminal : Terminal)
    (value : Partition) (hfin : finished cursor = some terminal)
    (hpart : partitionAt cursor = some value) :
    terminal = .success value := by
  cases cursor with
  | firstAttempt rs => simp [finished] at hfin
  | firstRows rs keptRev excludedRev i => simp [finished] at hfin
  | secondAttempt kept excluded => simp [finished] at hfin
  | secondRows rs retainedRev excluded secondExcludedRev i =>
      cases rs with
      | nil =>
          simp [finished, partitionAt] at hfin hpart
          cases hpart
          exact hfin.symm
      | cons r rs => simp [finished] at hfin
  | stopped t excluded =>
      cases t <;> simp_all [finished, partitionAt]

theorem drive_sufficient (fuel capacity : Nat) (machine : Machine)
    (value : Partition)
    (hpart : partitionAt machine.cursor = some value)
    (hsteps : (future .ready .ready machine.cursor).length ≤ fuel)
    (hledger : (future .ready .ready machine.cursor).length ≤ capacity) :
    (drive fuel capacity .ready .ready machine).terminal = .success value := by
  induction fuel generalizing capacity machine with
  | zero =>
      cases hfin : finished machine.cursor with
      | some terminal =>
          have ht := finished_partition machine.cursor terminal value hfin hpart
          simp [drive, hfin, observe, ht]
      | none =>
          have hstep := future_advance .ready .ready machine.cursor hfin
          simp [hstep] at hsteps
  | succ fuel ih =>
      cases hfin : finished machine.cursor with
      | some terminal =>
          have ht := finished_partition machine.cursor terminal value hfin hpart
          simp [drive, hfin, observe, ht]
      | none =>
          have hstep := future_advance .ready .ready machine.cursor hfin
          cases capacity with
          | zero => simp [hstep] at hledger
          | succ capacity =>
              let nextCursor := (advance .ready .ready machine.cursor).2
              have hp : partitionAt nextCursor = some value := by
                simpa [nextCursor] using
                  (ready_step_preserves_partition machine.cursor hfin).trans hpart
              have hs : (future .ready .ready nextCursor).length ≤ fuel := by
                simp [hstep, nextCursor] at hsteps ⊢
                exact hsteps
              have hc : (future .ready .ready nextCursor).length ≤ capacity := by
                simp [hstep, nextCursor] at hledger ⊢
                exact hledger
              let nextMachine : Machine :=
                { cursor := nextCursor, steps := machine.steps + 1,
                  ledgerRev := (advance .ready .ready machine.cursor).1 :: machine.ledgerRev,
                  secondStarted := machine.secondStarted || attemptingSecond machine.cursor }
              have hrec := ih capacity nextMachine hp hs hc
              simpa [drive, hfin, nextMachine, nextCursor] using hrec

theorem sufficient_budgets_produce_partition (rs : List Row) (budget : Budget)
    (steps : (plan rs .ready .ready).length ≤ budget.stepBound)
    (ledger : (plan rs .ready .ready).length ≤ budget.ledgerBound) :
    (run rs .ready .ready budget).terminal = .success (source rs) := by
  apply drive_sufficient budget.stepBound budget.ledgerBound
    { cursor := .firstAttempt rs, steps := 0, ledgerRev := [], secondStarted := false }
    (source rs)
  · rfl
  · simpa [future_start_is_plan] using steps
  · simpa [future_start_is_plan] using ledger

theorem drive_short_terminal (first second : Policy) (fuel capacity : Nat)
    (machine : Machine)
    (short : min fuel capacity < (future first second machine.cursor).length) :
    (drive fuel capacity first second machine).terminal =
      .resourceLimit (drive fuel capacity first second machine).progress := by
  induction fuel generalizing capacity machine with
  | zero =>
      cases h : finished machine.cursor with
      | some terminal =>
          have empty := finished_has_no_future first second machine.cursor terminal h
          simp [empty] at short
      | none => simp [drive, h, observe]
  | succ fuel ih =>
      cases h : finished machine.cursor with
      | some terminal =>
          have empty := finished_has_no_future first second machine.cursor terminal h
          simp [empty] at short
      | none =>
          cases capacity with
          | zero => simp [drive, h, observe]
          | succ capacity =>
              have hstep := future_advance first second machine.cursor h
              have tailShort : min fuel capacity <
                  (future first second (advance first second machine.cursor).2).length := by
                rw [hstep] at short
                simpa using short
              let nextMachine : Machine :=
                { cursor := (advance first second machine.cursor).2,
                  steps := machine.steps + 1,
                  ledgerRev := (advance first second machine.cursor).1 :: machine.ledgerRev,
                  secondStarted := machine.secondStarted || attemptingSecond machine.cursor }
              have hrec := ih capacity nextMachine tailShort
              simpa [drive, h, nextMachine] using hrec

theorem drive_short_steps (first second : Policy) (fuel capacity : Nat)
    (machine : Machine)
    (short : min fuel capacity < (future first second machine.cursor).length) :
    (drive fuel capacity first second machine).progress.completedSteps =
      machine.steps + (if fuel ≤ capacity then fuel else capacity + 1) := by
  induction fuel generalizing capacity machine with
  | zero =>
      cases h : finished machine.cursor with
      | some terminal =>
          have empty := finished_has_no_future first second machine.cursor terminal h
          simp [empty] at short
      | none => simp [drive, h, observe, snapshot]
  | succ fuel ih =>
      cases h : finished machine.cursor with
      | some terminal =>
          have empty := finished_has_no_future first second machine.cursor terminal h
          simp [empty] at short
      | none =>
          cases capacity with
          | zero => simp [drive, h, observe, snapshot]
          | succ capacity =>
              have hstep := future_advance first second machine.cursor h
              have tailShort : min fuel capacity <
                  (future first second (advance first second machine.cursor).2).length := by
                rw [hstep] at short
                simpa using short
              let nextMachine : Machine :=
                { cursor := (advance first second machine.cursor).2,
                  steps := machine.steps + 1,
                  ledgerRev := (advance first second machine.cursor).1 :: machine.ledgerRev,
                  secondStarted := machine.secondStarted || attemptingSecond machine.cursor }
              have hrec := ih capacity nextMachine tailShort
              by_cases bound : fuel ≤ capacity
              · simpa [drive, h, nextMachine, bound, Nat.add_assoc, Nat.add_comm,
                  Nat.add_left_comm] using hrec
              · simpa [drive, h, nextMachine, bound, Nat.add_assoc, Nat.add_comm,
                  Nat.add_left_comm] using hrec

theorem drive_ledger_prefix (first second : Policy) (fuel capacity : Nat)
    (machine : Machine) :
    (drive fuel capacity first second machine).orderedLedger =
      machine.ledgerRev.reverse ++
        (future first second machine.cursor).take (min fuel capacity) := by
  induction fuel generalizing capacity machine with
  | zero =>
      cases h : finished machine.cursor with
      | none => simp [drive, h, observe, snapshot]
      | some terminal =>
          simp [drive, h, observe, snapshot, finished_has_no_future first second
            machine.cursor terminal h]
  | succ fuel ih =>
      cases h : finished machine.cursor with
      | some terminal =>
          simp [drive, h, observe, snapshot, finished_has_no_future first second
            machine.cursor terminal h]
      | none =>
          cases capacity with
          | zero => simp [drive, h, observe, snapshot]
          | succ capacity =>
              have hstep := future_advance first second machine.cursor h
              simp [drive, h, ih, hstep, List.reverse_cons, List.append_assoc]

/- Therefore the real traversal ledger is the prefix of the independent
complete plan for every policy and budget, whether complete or exhausted. -/
theorem run_ledger_matches_plan (rs : List Row) (first second : Policy)
    (budget : Budget) :
    (run rs first second budget).orderedLedger =
      (plan rs first second).take (min budget.stepBound budget.ledgerBound) := by
  simpa [run, future_start_is_plan] using
    drive_ledger_prefix first second budget.stepBound budget.ledgerBound
      { cursor := .firstAttempt rs, steps := 0, ledgerRev := [], secondStarted := false }

theorem drive_progress_fields (first second : Policy) (fuel capacity : Nat)
    (machine : Machine) :
    (drive fuel capacity first second machine).progress.ledgerPrefix =
      (drive fuel capacity first second machine).orderedLedger ∧
    (drive fuel capacity first second machine).progress.secondExcludedPrefix =
      secondExcluded (drive fuel capacity first second machine).orderedLedger := by
  induction fuel generalizing capacity machine with
  | zero =>
      cases h : finished machine.cursor <;> simp [drive, h, observe, snapshot]
  | succ fuel ih =>
      cases h : finished machine.cursor with
      | some terminal => simp [drive, h, observe, snapshot]
      | none =>
          cases capacity with
          | zero => simp [drive, h, observe, snapshot]
          | succ capacity =>
              simpa [drive, h] using ih capacity
                { cursor := (advance first second machine.cursor).2,
                  steps := machine.steps + 1,
                  ledgerRev := (advance first second machine.cursor).1 :: machine.ledgerRev,
                  secondStarted := machine.secondStarted || attemptingSecond machine.cursor }

theorem exhaustion_returns_prefix_and_steps (rs : List Row)
    (first second : Policy) (budget : Budget)
    (short : min budget.stepBound budget.ledgerBound <
      (plan rs first second).length) :
    (run rs first second budget).terminal =
      .resourceLimit (run rs first second budget).progress ∧
    (run rs first second budget).orderedLedger =
      (plan rs first second).take (min budget.stepBound budget.ledgerBound) ∧
    (run rs first second budget).progress.completedSteps =
      if budget.stepBound ≤ budget.ledgerBound then budget.stepBound
      else budget.ledgerBound + 1 := by
  have hshort : min budget.stepBound budget.ledgerBound <
      (future first second (.firstAttempt rs)).length := by
    simpa [future_start_is_plan] using short
  refine ⟨?_, run_ledger_matches_plan rs first second budget, ?_⟩
  · simpa [run] using drive_short_terminal first second budget.stepBound
      budget.ledgerBound
      { cursor := .firstAttempt rs, steps := 0, ledgerRev := [],
        secondStarted := false } hshort
  · simpa [run] using drive_short_steps first second budget.stepBound
      budget.ledgerBound
      { cursor := .firstAttempt rs, steps := 0, ledgerRev := [],
        secondStarted := false } hshort

/- The second attempt starts when its step is charged, including when a
full ledger prevents the attempt event from being appended. This law holds
for any completed first-stage accumulators and policy. -/
theorem failed_second_append_starts (keptRev excludedRev : List Row)
    (events : List Event) (steps fuel index : Nat) (first second : Policy) :
    (drive (fuel + 1) 0 first second
      { cursor := .firstRows [] keptRev excludedRev index, steps := steps,
        ledgerRev := events, secondStarted := false }).secondStarted = true ∧
    (drive (fuel + 1) 0 first second
      { cursor := .firstRows [] keptRev excludedRev index, steps := steps,
        ledgerRev := events, secondStarted := false }).orderedLedger = events.reverse ∧
    (drive (fuel + 1) 0 first second
      { cursor := .firstRows [] keptRev excludedRev index, steps := steps,
        ledgerRev := events, secondStarted := false }).terminal =
      .resourceLimit ⟨steps + 1, events.reverse, some excludedRev.reverse,
        secondExcluded events.reverse⟩ := by
  constructor
  · rfl
  constructor <;> rfl

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

/- Adversarial executable controls exercise stops on both stages. These are
finite checks, not the missing all-list refinement theorem. -/
private def sampleGraph (ab bc : Bool) : Graph :=
  ⟨ab, false, bc, none⟩

private def sampleRow : Row :=
  ⟨sampleGraph false false, sampleGraph false false, 1⟩

example : (run [sampleRow] .ready .ready ⟨10, 1⟩).terminal =
    .resourceLimit ⟨2, [.attempt .first], none, []⟩ := by decide

example : (run [sampleRow] .ready .ready ⟨4, 2⟩).secondStarted = true ∧
    (run [sampleRow] .ready .ready ⟨4, 2⟩).terminal =
      .resourceLimit ⟨3, [.attempt .first, .row .first 0 sampleRow false],
        some [], []⟩ := by decide

example : (run [sampleRow] .ready .ready ⟨10, 3⟩).terminal =
    .resourceLimit ⟨4,
      [.attempt .first, .row .first 0 sampleRow false, .attempt .second],
      some [], []⟩ := by decide

example : (run [sampleRow] .ready .ready ⟨4, 4⟩).terminal =
    .success (source [sampleRow]) := by decide

example : (run [sampleRow] .ready .unsupported ⟨3, 3⟩).progress.firstExcluded =
    some [] := by decide

end E7CEECQTwoStageOperational
