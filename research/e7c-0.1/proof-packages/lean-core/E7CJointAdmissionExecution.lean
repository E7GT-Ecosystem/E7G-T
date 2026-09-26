import E7CJointAdmissionCalls

/-!
Small operational semantics for the selected successful `admit` suffix.
The source AST pin selects this suffix; primitive CPython adequacy remains a
separate premise recorded in the companion gate note. This module proves that
the mathematical execution of the pinned calls yields the #135 call
derivation. It does not assume the desired row observation: it assumes only
that execution takes the actual equality-guard true branch and returns.
-/
namespace E7CJointAdmissionExecution
open E7CEECQTwoStageAllInput
open E7CEECQTwoStageExactCodec
open E7CJointAdmissionGenerated
open E7CJointAdmissionCalls

def CanonicalWireRows (source : List WireRow) : Prop :=
  ∀ row ∈ source, canonicalGraph row.left ∧ canonicalGraph row.right

/- Each constructor models the mathematical outcome of one selected source
   call. The final constructor models the actual `if rows(value) != source`
   rejection or fallthrough, not an assumed equality of the desired rows. -/
inductive AdmissionStep (normalizer : List Row → List Row)
    (source : List WireRow) :
    List Row → List Row → List WireRow → Bool → Option (List Row) → Prop where
  | evaluated (parsed result : List Row) (encoded : List WireRow)
      (hparse : parsed = parseRows source)
      (hjoint : result = normalizer parsed)
      (hrows : encoded = serializeRows result)
      (hguard : decide (encoded = source) = true) :
      AdmissionStep normalizer source parsed result encoded true (some result)
  | rejected (parsed result : List Row) (encoded : List WireRow)
      (hparse : parsed = parseRows source)
      (hjoint : result = normalizer parsed)
      (hrows : encoded = serializeRows result)
      (hguard : decide (encoded = source) = false) :
      AdmissionStep normalizer source parsed result encoded false none

/- A normal-return execution consists of the parser result, the Joint result,
   the `rows` serialization and the truth value of the built-in equality
   guard. `returned` is the control-flow fact that this execution reached the
   source return statement rather than its rejection branch. -/
inductive PythonNormalExecution (normalizer : List Row → List Row)
    (source : List WireRow) (result : List Row) : Prop where
  | returned {parsed : List Row} {encoded : List WireRow}
      (control : AdmissionStep normalizer source parsed result encoded true (some result)) :
      PythonNormalExecution normalizer source result

theorem parse_rows_call_of_canonical {source : List WireRow}
    (hcanonical : CanonicalWireRows source) :
    ParseRowsCall source (parseRows source) := by
  induction source with
  | nil => exact ParseRowsCall.nil
  | cons row rest ih =>
      have hrow := hcanonical row (by simp)
      have hrest : CanonicalWireRows rest := by
        intro candidate membership
        exact hcanonical candidate (by simp [membership])
      have tail := ih hrest
      exact ParseRowsCall.cons
        (ParseRowCall.accepted row (toGraph row.left) (toGraph row.right)
          row.coefficient
          (ConfigCall.accepted row.left hrow.1)
          (ConfigCall.accepted row.right hrow.2)
          (FractionCall.accepted row.coefficient))
        tail

theorem rows_write_call (rows : List Row) :
    RowsWriteCall rows (serializeRows rows) := by
  induction rows with
  | nil => exact RowsWriteCall.nil
  | cons row rest ih =>
      change RowsWriteCall (row :: rest) (serializeRow row :: serializeRows rest)
      exact RowsWriteCall.cons
        (RowWriteCall.returned row (fromGraph row.left) (fromGraph row.right)
          (GraphWriteCall.returned row.left)
          (GraphWriteCall.returned row.right))
        ih

theorem python_normal_execution_yields_call_derivation
    {normalizer : List Row → List Row} {source : List WireRow}
    {result : List Row}
    (hcanonical : CanonicalWireRows source)
    (run : PythonNormalExecution normalizer source result) :
    NormalReturn normalizer source result := by
  cases run with
  | returned (.evaluated parsed computed encoded hparse hjoint hrows hguard) =>
      have parseCall : ParseRowsCall source parsed := by
        rw [hparse]
        exact parse_rows_call_of_canonical hcanonical
      have jointCall : JointCall normalizer parsed computed := by
        rw [hjoint]
        exact JointCall.returned parsed
      have writeCall : RowsWriteCall computed encoded := by
        rw [hrows]
        exact rows_write_call computed
      have guardEq : encoded = source := of_decide_eq_true hguard
      subst encoded
      exact NormalReturn.returned parseCall jointCall writeCall
        (WireEqualCall.equal source)

theorem python_normal_execution_matches_generated
    {normalizer : List Row → List Row} {source : List WireRow}
    {result : List Row}
    (hcanonical : CanonicalWireRows source)
    (run : PythonNormalExecution normalizer source result) :
    admission normalizer source = some result :=
  normal_return_matches_generated
    (python_normal_execution_yields_call_derivation hcanonical run)

theorem python_normal_execution_exact_rows
    {normalizer : List Row → List Row} {source : List WireRow}
    {result : List Row}
    (hcanonical : CanonicalWireRows source)
    (run : PythonNormalExecution normalizer source result) :
    result = source.map toRow :=
  normal_return_exact_rows
    (python_normal_execution_yields_call_derivation hcanonical run)

theorem changed_rows_cannot_take_normal_return
    {normalizer : List Row → List Row} {source : List WireRow}
    {result : List Row} (changed : serializeRows result ≠ source) :
    ¬ PythonNormalExecution normalizer source result := by
  intro run
  cases run with
  | returned (.evaluated parsed computed encoded hparse hjoint hrows hguard) =>
      apply changed
      have guardEq : encoded = source := of_decide_eq_true hguard
      rw [hrows]
      exact guardEq

end E7CJointAdmissionExecution
