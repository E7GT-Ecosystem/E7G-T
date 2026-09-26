import E7CJointAdmissionExecution

/-!
Conditional operation-by-operation bridge from the selected, pinned Python
normal-return path to #138's modeled trace. This module derives the #135 call
judgments from operation-result equations; it does not take ParseRowsCall,
JointCall or RowsWriteCall as premises.

The CPython result equations remain explicit adequacy premises. In particular,
the source is already a typed WireRow list, Fraction is modeled after exact
numerator/denominator decoding, and normalizer abstracts the exact
aggregation result of the pinned joint helper. This module does not prove
that CPython or the helper implements these equations.
-/
namespace E7CJointAdmissionCPythonBridge
open E7CEECQTwoStageAllInput
open E7CEECQTwoStageExactCodec
open E7CJointAdmissionGenerated
open E7CJointAdmissionCalls
open E7CJointAdmissionExecution

/- Operation-level outcomes for the selected parser, Joint, rows and equality
   path. These premises describe individual computed values. None assumes the
   final serialized-row equality; that follows from the comparator result and
   the normal-return branch. -/
structure CPythonOperationRefinements
    (normalizer : List Row → List Row)
    (source : List WireRow) (result : List Row) : Type where
  parsed : List Row
  encoded : List WireRow
  configResult : WireGraph → Graph
  fractionResult : Rat → Rat
  configLeftRefines : ∀ graph, configResult graph = toGraph graph
  configRightRefines : ∀ graph, configResult graph = toGraph graph
  fractionRefines : ∀ coefficient, fractionResult coefficient = coefficient
  canonicalAccepted : ∀ row ∈ source,
    canonicalGraph row.left ∧ canonicalGraph row.right
  parserIteration :
    parsed = source.map (fun row =>
      ({ left := configResult row.left
         right := configResult row.right
         coefficient := fractionResult row.coefficient } : Row))
  jointOutputRefines : result = normalizer parsed
  rowsOutputRefines : encoded = serializeRows result
  equalityResult : Bool
  builtinEqualityRefines : equalityResult = decide (encoded = source)
  normalReturnBranch : equalityResult = true

theorem parser_value_is_model_parse
    {normalizer : List Row → List Row} {source : List WireRow}
    {result : List Row}
    (ops : CPythonOperationRefinements normalizer source result) :
    ops.parsed = parseRows source := by
  rw [ops.parserIteration]
  have hleft : ops.configResult = toGraph := funext ops.configLeftRefines
  have hright : ops.configResult = toGraph := funext ops.configRightRefines
  have hfraction : ops.fractionResult = id := funext ops.fractionRefines
  simp [parseRows, parseRow, toRow, hleft, hright, hfraction]

theorem parser_results_yield_parse_call
    {normalizer : List Row → List Row} {source : List WireRow}
    {result : List Row}
    (ops : CPythonOperationRefinements normalizer source result) :
    ParseRowsCall source ops.parsed := by
  rw [parser_value_is_model_parse ops]
  exact parse_rows_call_of_canonical ops.canonicalAccepted

theorem joint_result_yields_joint_call
    {normalizer : List Row → List Row} {source : List WireRow}
    {result : List Row}
    (ops : CPythonOperationRefinements normalizer source result) :
    JointCall normalizer ops.parsed result := by
  rw [ops.jointOutputRefines]
  exact JointCall.returned ops.parsed

theorem serializer_result_yields_write_call
    {normalizer : List Row → List Row} {source : List WireRow}
    {result : List Row}
    (ops : CPythonOperationRefinements normalizer source result) :
    RowsWriteCall result ops.encoded := by
  rw [ops.rowsOutputRefines]
  exact rows_write_call result

theorem pinned_normal_return_yields_modeled_trace
    {normalizer : List Row → List Row} {source : List WireRow}
    {result : List Row}
    (ops : CPythonOperationRefinements normalizer source result) :
    ModeledNormalExecution normalizer source result := by
  have guard : decide (ops.encoded = source) = true := by
    rw [← ops.builtinEqualityRefines]
    exact ops.normalReturnBranch
  exact ⟨ops.parsed, ops.encoded,
    AdmissionStep.evaluated ops.parsed result ops.encoded
      (parser_value_is_model_parse ops)
      ops.jointOutputRefines
      ops.rowsOutputRefines
      guard⟩

theorem pinned_normal_return_exact_rows
    {normalizer : List Row → List Row} {source : List WireRow}
    {result : List Row}
    (ops : CPythonOperationRefinements normalizer source result) :
    result = source.map toRow :=
  modeled_normal_execution_exact_rows ops.canonicalAccepted
    (pinned_normal_return_yields_modeled_trace ops)

theorem different_rows_preclude_normal_return
    {normalizer : List Row → List Row} {source : List WireRow}
    {result : List Row}
    (ops : CPythonOperationRefinements normalizer source result)
    (different : serializeRows result ≠ source) : False := by
  exact changed_rows_cannot_take_modeled_normal_return different
    (pinned_normal_return_yields_modeled_trace ops)

end E7CJointAdmissionCPythonBridge
