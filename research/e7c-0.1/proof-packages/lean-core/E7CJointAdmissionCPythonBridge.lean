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
    (source : List WireRow) : Type where
  parsed : List Row
  result : List Row
  encoded : List WireRow
  configLeftResult : WireGraph → Graph
  configRightResult : WireGraph → Graph
  fractionResult : Rat → Rat
  configLeftRefines : ∀ graph, configLeftResult graph = toGraph graph
  configRightRefines : ∀ graph, configRightResult graph = toGraph graph
  fractionRefines : ∀ coefficient, fractionResult coefficient = coefficient
  canonicalAccepted : ∀ row ∈ source,
    canonicalGraph row.left ∧ canonicalGraph row.right
  parserIteration :
    parsed = source.map (fun row =>
      ({ left := configLeftResult row.left
         right := configRightResult row.right
         coefficient := fractionResult row.coefficient } : Row))
  jointOutputRefines : result = normalizer parsed
  rowsOutputRefines : encoded = serializeRows result
  equalityResult : Bool
  builtinEqualityRefines : equalityResult = decide (encoded = source)
  normalReturnBranch : equalityResult = true

theorem parser_value_is_model_parse
    {normalizer : List Row → List Row} {source : List WireRow}
    (ops : CPythonOperationRefinements normalizer source) :
    ops.parsed = parseRows source := by
  rw [ops.parserIteration]
  have hleft : ops.configLeftResult = toGraph := funext ops.configLeftRefines
  have hright : ops.configRightResult = toGraph := funext ops.configRightRefines
  have hfraction : ops.fractionResult = id := funext ops.fractionRefines
  simp [parseRows, parseRow, toRow, hleft, hright, hfraction]

theorem parser_results_yield_parse_call
    {normalizer : List Row → List Row} {source : List WireRow}
    (ops : CPythonOperationRefinements normalizer source) :
    ParseRowsCall source ops.parsed := by
  rw [parser_value_is_model_parse ops]
  exact parse_rows_call_of_canonical ops.canonicalAccepted

theorem joint_result_yields_joint_call
    {normalizer : List Row → List Row} {source : List WireRow}
    (ops : CPythonOperationRefinements normalizer source) :
    JointCall normalizer ops.parsed ops.result := by
  rw [ops.jointOutputRefines]
  exact JointCall.returned ops.parsed

theorem serializer_result_yields_write_call
    {normalizer : List Row → List Row} {source : List WireRow}
    (ops : CPythonOperationRefinements normalizer source) :
    RowsWriteCall ops.result ops.encoded := by
  rw [ops.rowsOutputRefines]
  exact rows_write_call ops.result

theorem pinned_normal_return_yields_modeled_trace
    {normalizer : List Row → List Row} {source : List WireRow}
    (ops : CPythonOperationRefinements normalizer source) :
    ModeledNormalExecution normalizer source ops.result := by
  have guard : decide (ops.encoded = source) = true := by
    rw [← ops.builtinEqualityRefines]
    exact ops.normalReturnBranch
  exact ⟨ops.parsed, ops.encoded,
    AdmissionStep.evaluated ops.parsed ops.result ops.encoded
      (parser_value_is_model_parse ops)
      ops.jointOutputRefines
      ops.rowsOutputRefines
      guard⟩

theorem pinned_normal_return_exact_rows
    {normalizer : List Row → List Row} {source : List WireRow}
    (ops : CPythonOperationRefinements normalizer source) :
    ops.result = source.map toRow :=
  modeled_normal_execution_exact_rows ops.canonicalAccepted
    (pinned_normal_return_yields_modeled_trace ops)

theorem different_rows_preclude_normal_return
    {normalizer : List Row → List Row} {source : List WireRow}
    (ops : CPythonOperationRefinements normalizer source)
    (different : serializeRows ops.result ≠ source) : False := by
  exact changed_rows_cannot_take_modeled_normal_return different
    (pinned_normal_return_yields_modeled_trace ops)

end E7CJointAdmissionCPythonBridge
