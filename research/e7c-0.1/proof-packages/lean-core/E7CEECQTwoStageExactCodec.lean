import E7CEECQTwoStageOperational

/-!
Exact value-level boundary for the admitted binary FG3 Joint. `WireGraph`
retains the canonical Python edge list and the nullable, unrestricted string tag.
`WireRow` retains both correlated coordinates and a normalized rational value.
Python's admission separately checks positive reduced denominator, nonzero
coefficient, at most 64 rows, unique support and canonical row ordering.
Those Python parser properties are premises, not consequences of this module.
-/

namespace E7CEECQTwoStageExactCodec
open E7CEECQTwoStageAllInput
open E7CEECQTwoStageOperational

structure WireGraph where
  edges : List String
  tag : Option String
  deriving DecidableEq, Repr

def toGraph (g : WireGraph) : Graph :=
  ⟨g.edges.contains "AB", g.edges.contains "AC",
    g.edges.contains "BC", g.tag⟩

def fromGraph (g : Graph) : WireGraph :=
  ⟨(if g.ab then ["AB"] else []) ++
    (if g.ac then ["AC"] else []) ++
    (if g.bc then ["BC"] else []), g.tag⟩

def canonicalGraph (g : WireGraph) : Prop := fromGraph (toGraph g) = g

theorem graph_roundtrip (g : Graph) : toGraph (fromGraph g) = g := by
  cases g with
  | mk ab ac bc tag =>
      cases ab <;> cases ac <;> cases bc <;> rfl

theorem null_differs_from_empty (ab ac bc : Bool) :
    (⟨ab, ac, bc, none⟩ : Graph) ≠ ⟨ab, ac, bc, some ""⟩ := by
  intro h
  cases h

structure WireRow where
  left : WireGraph
  right : WireGraph
  coefficient : Rat
  deriving DecidableEq, Repr

def toRow (r : WireRow) : Row :=
  ⟨toGraph r.left, toGraph r.right, r.coefficient⟩

def fromRow (r : Row) : WireRow :=
  ⟨fromGraph r.left, fromGraph r.right, r.coefficient⟩

theorem row_roundtrip (r : Row) : toRow (fromRow r) = r := by
  cases r with
  | mk left right coefficient =>
      simp [toRow, fromRow, graph_roundtrip]

theorem canonical_row_roundtrip (r : WireRow)
    (hl : canonicalGraph r.left) (hr : canonicalGraph r.right) :
    fromRow (toRow r) = r := by
  cases r with
  | mk left right coefficient =>
      simp [fromRow, toRow, canonicalGraph] at hl hr ⊢
      simp [hl, hr]

theorem canonical_rows_injective (a b : WireRow)
    (al : canonicalGraph a.left) (ar : canonicalGraph a.right)
    (bl : canonicalGraph b.left) (br : canonicalGraph b.right)
    (h : toRow a = toRow b) : a = b := by
  calc
    a = fromRow (toRow a) := (canonical_row_roundtrip a al ar).symm
    _ = fromRow (toRow b) := congrArg fromRow h
    _ = b := canonical_row_roundtrip b bl br

def wirePartition (rs : List WireRow) : Partition := source (rs.map toRow)

theorem first_predicate_preserved (r : WireRow) :
    (toRow r).left.ab = r.left.edges.contains "AB" := rfl

theorem second_predicate_preserved (r : WireRow) :
    (toRow r).right.bc = r.right.edges.contains "BC" := rfl

theorem ordered_three_way_mapping (rs : List WireRow) :
    wirePartition rs =
      ⟨(rs.filter (fun r => ! (toRow r).left.ab && ! (toRow r).right.bc)).map toRow,
       (rs.filter (fun r => (toRow r).left.ab)).map toRow,
       (rs.filter (fun r => ! (toRow r).left.ab && (toRow r).right.bc)).map toRow⟩ := by
  simp [wirePartition, source, List.filter_map, Function.comp_def]

theorem ir_preserves_exact_partition (rs : List WireRow) :
    ir (rs.map toRow) = wirePartition rs :=
  all_rows_partition_agreement (rs.map toRow)

/- Independent wire-side event specification. Each row event retains the
whole pair and coefficient; the second pass traverses the first retained
rows, not an inferred product of marginals. -/
def wireFirstRows : List WireRow → Nat → List Event
  | [], _ => []
  | r :: rest, index =>
      .row .first index (toRow r) (r.left.edges.contains "AB") ::
        wireFirstRows rest (index + 1)

def wireSecondRows : List WireRow → Nat → List Event
  | [], _ => []
  | r :: rest, index =>
      .row .second index (toRow r) (r.right.edges.contains "BC") ::
        wireSecondRows rest (index + 1)

theorem wire_first_step (rs : List WireRow) (index : Nat) :
    wireFirstRows rs index = firstRows (rs.map toRow) index := by
  induction rs generalizing index with
  | nil => rfl
  | cons r rest ih => simp [wireFirstRows, firstRows, first_predicate_preserved, ih]

theorem wire_second_step (rs : List WireRow) (index : Nat) :
    wireSecondRows rs index = secondRows (rs.map toRow) index := by
  induction rs generalizing index with
  | nil => rfl
  | cons r rest ih => simp [wireSecondRows, secondRows, second_predicate_preserved, ih]

def wirePlan (rs : List WireRow) (first second : Policy) : List Event :=
  if first ≠ .ready then [.attempt .first]
  else if second ≠ .ready then
    .attempt .first :: wireFirstRows rs 0 ++ [.attempt .second]
  else
    .attempt .first :: wireFirstRows rs 0 ++
      (.attempt .second :: wireSecondRows
        (rs.filter (fun r => !(toRow r).left.ab)) 0)

theorem wire_plan_simulation (rs : List WireRow) (first second : Policy) :
    wirePlan rs first second = plan (rs.map toRow) first second := by
  cases first <;> cases second <;>
    simp [wirePlan, plan, firstTrace, secondTrace, wire_first_step,
      wire_second_step, List.filter_map, Function.comp_def]

theorem wire_budgeted_event_simulation (rs : List WireRow)
    (first second : Policy) (budget : Budget) :
    (run (rs.map toRow) first second budget).orderedLedger =
      (wirePlan rs first second).take
        (min budget.stepBound budget.ledgerBound) := by
  rw [wire_plan_simulation]
  exact run_ledger_matches_plan (rs.map toRow) first second budget

/- Every successful operational transition emits the next exact event in
the independently specified ordered plan. This is a one-step simulation of
the *selected abstract rule*. The Python and independent IR implementations
are checked against it by the cross-language witness suite; their code is
not imported into Lean and no theorem here asserts Python implementation
correctness. -/
theorem abstract_one_step_simulation (first second : Policy) (cursor : Cursor)
    (h : finished cursor = none) :
    future first second cursor =
      (advance first second cursor).1 ::
        future first second (advance first second cursor).2 :=
  future_advance first second cursor h

def failedSecondAppendRow : Row :=
  ⟨⟨false, false, true, none⟩, ⟨false, true, false, some ""⟩, (-2 : Rat)⟩

/- Python fixture: one row, step bound 4, ledger bound 2. The second
attempt consumes step 3, cannot append event 3, and sets secondStarted. -/
theorem failed_second_append_cross_language_fixture :
    (run [failedSecondAppendRow] .ready .ready ⟨4, 2⟩).terminal =
      .resourceLimit (run [failedSecondAppendRow] .ready .ready ⟨4, 2⟩).progress ∧
    (run [failedSecondAppendRow] .ready .ready ⟨4, 2⟩).orderedLedger =
      [.attempt .first, .row .first 0 failedSecondAppendRow false] ∧
    (run [failedSecondAppendRow] .ready .ready ⟨4, 2⟩).progress.completedSteps = 3 ∧
    (run [failedSecondAppendRow] .ready .ready ⟨4, 2⟩).progress.firstExcluded =
      some [] ∧
    (run [failedSecondAppendRow] .ready .ready ⟨4, 2⟩).secondStarted = true := by
  simp [run, drive, advance, finished, snapshot, observe,
    firstExcludedAt, attemptingSecond, failedSecondAppendRow]

end E7CEECQTwoStageExactCodec
