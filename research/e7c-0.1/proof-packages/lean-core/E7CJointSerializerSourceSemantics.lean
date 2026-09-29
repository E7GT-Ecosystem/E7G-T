import E7CJointSerializerSourceGenerated
import E7CJointFirstStageNormalReturnComposition

/- Execute the checked helper source trees and derive their existing serializer
trace. Attribute contracts are operation-local assumptions; no serializer
result equation or completed RowsStatementTrace is assumed. CPython's execution
of this selected grammar and its native object representation remain open. -/
namespace E7CJointSerializerSourceSemantics
open E7CEECQTwoStageExactCodec E7CJointRawJsonAdmission
open E7CJointSerializerSourceSyntax E7CJointSerializerSourceGenerated
open E7CJointCPythonNormalReturnTrace

def runGraph (read : Value → String → Option Value) (value : Value) : Option Value :=
  eval read listCall 16 graphExpr [value]

def graphCall (read : Value → String → Option Value) :
    String → List Value → Option Value
  | "_graph", [value] => runGraph read value
  | _, _ => none

def runRow (read : Value → String → Option Value)
    (atoms coefficient : Value) : Option Value :=
  eval read (graphCall read) 16 rowExpr [atoms, coefficient]

def rowCall (read : Value → String → Option Value) :
    String → List Value → Option Value
  | "_row", [atoms, coefficient] => runRow read atoms coefficient
  | _, _ => none

/-- The selected normal evaluator for rows: the source translator checks the
exact native-Joint and arity guard. None includes modeled rejection and failed
evaluation; it does not classify a running Python exception or resource limit. -/
def runRows (read : Value → String → Option Value) (value : Value) : Option RawJson :=
  match value with
  | .joint _ _ => do
      let .data (.integer 2) ← read value "arity" | none
      let result ← eval read (rowCall read) 16 rowsExpr [value]
      toRaw result
  | _ => none

theorem mapM_of_some {α β : Type} (f : α → Option β) (g : α → β)
    (pointwise : ∀ value, f value = some (g value)) (values : List α) :
    values.mapM f = some (values.map g) := by
  induction values with
  | nil => rfl
  | cons value rest ih => simp [List.mapM_cons, pointwise, ih]

theorem toRaw_data_sequence (values : List RawJson) :
    toRaw (.sequence (values.map Value.data)) = some (.array values) := by
  have h := mapM_of_some (toRaw ∘ Value.data) id (by intro; simp [toRaw]) values
  simp only [toRaw, List.mapM_map]
  rw [h]
  simp

theorem graph_source_run_exact
    {read : Value → String → Option Value} (attributes : AttributeContracts read)
    (graph : WireGraph) :
    runGraph read (.graph graph) = some (.data (encodeRawGraph graph)) := by
  have hedge : toRaw (graphItems graph) =
      some (.array (graph.edges.map RawJson.string)) := by
    simpa [graphItems, List.map_map, Function.comp_def] using
      toRaw_data_sequence (graph.edges.map RawJson.string)
  have hlist : listCall "list" [graphItems graph] = some (graphItems graph) := rfl
  simp [runGraph, graphExpr, eval, attributes.edges,
    attributes.tag, hlist, hedge, encodeRawGraph, toRaw]

theorem row_source_run_exact
    {read : Value → String → Option Value} (attributes : AttributeContracts read)
    (row : WireRow) :
    runRow read (.sequence [.graph row.left, .graph row.right])
      (.fraction row.coefficient) = some (.data (encodeRawRow row)) := by
  simp [runRow, rowExpr, eval, bindItems, graphCall,
    graph_source_run_exact attributes, attributes.numerator,
    attributes.denominator, toRaw, encodeRawRow, encodeRawFraction]

theorem rows_source_expression_exact
    {read : Value → String → Option Value} (attributes : AttributeContracts read)
    (rows : List WireRow) :
    eval read (rowCall read) 16 rowsExpr [.joint 2 rows] =
      some (.sequence (rows.map (fun row => .data (encodeRawRow row)))) := by
  have each : ∀ row : WireRow,
      (do
        let scope ← bindItems 2 (rowItems row) [.joint 2 rows]
        eval read (rowCall read) 15
          (.call "_row" [.variable 0, .variable 1]) scope) =
      some (.data (encodeRawRow row)) := by
    intro row
    simpa [rowItems, bindItems, eval, rowCall] using row_source_run_exact attributes row
  have iteration := mapM_of_some _ _ each rows
  simpa [rowsExpr, eval, attributes.terms, List.mapM_map, Function.comp_def] using
    congrArg (fun output => output.bind (fun values => some (Value.sequence values))) iteration

theorem rows_source_run_exact
    {read : Value → String → Option Value} (attributes : AttributeContracts read)
    (rows : List WireRow) :
    runRows read (.joint 2 rows) = some (encodeRawRows rows) := by
  have expression := rows_source_expression_exact attributes rows
  have output := toRaw_data_sequence (rows.map encodeRawRow)
  simpa [runRows, attributes.arity, expression, List.map_map,
    encodeRawRows, Function.comp_def] using output

def graph_encoder_trace (graph : WireGraph) :
    GraphFieldStatementTrace graph (encodeRawGraph graph) :=
  ⟨graph.edges, rfl, graph.tag, rfl, rfl⟩

def fraction_encoder_trace (coefficient : Rat) :
    FractionFieldStatementTrace coefficient (encodeRawFraction coefficient) :=
  ⟨coefficient.num, rfl, coefficient.den, rfl, rfl⟩

def row_encoder_trace (row : WireRow) :
    RowStatementTrace row (encodeRawRow row) :=
  ⟨encodeRawGraph row.left, graph_encoder_trace row.left,
   encodeRawGraph row.right, graph_encoder_trace row.right,
   encodeRawFraction row.coefficient, fraction_encoder_trace row.coefficient,
   .array [encodeRawGraph row.left, encodeRawGraph row.right], rfl, rfl⟩

theorem rows_encoder_trace (rows : List WireRow) :
    RowsStatementTrace rows (encodeRawRows rows) := by
  induction rows with
  | nil => exact .nil
  | cons row rest ih => exact .cons (row_encoder_trace row) ih

/-- This is an all-list source-interpreter result under local read contracts.
The normal-run premise is about runRows, not an observation of CPython. -/
theorem normal_source_run_yields_rows_statement_trace
    {read : Value → String → Option Value} (attributes : AttributeContracts read)
    {rows : List WireRow} {output : RawJson}
    (normal : runRows read (.joint 2 rows) = some output) :
    RowsStatementTrace rows output := by
  have exactOutput := rows_source_run_exact attributes rows
  rw [exactOutput] at normal
  cases normal
  exact rows_encoder_trace rows

theorem normal_source_run_derives_domain
    {read : Value → String → Option Value} (attributes : AttributeContracts read)
    {rows : List WireRow} {output : RawJson}
    (normal : runRows read (.joint 2 rows) = some output) :
    rawJsonWithinFuel 32 output = true ∧ rawJsonUniqueObjectKeys output = true := by
  have trace := normal_source_run_yields_rows_statement_trace attributes normal
  exact ⟨rows_statement_within_fuel trace, rows_statement_unique_keys trace⟩

theorem nonbinary_native_joint_rejected (arity : Nat) (rows : List WireRow)
    (different : arity ≠ 2) : runRows nativeAttributes (.joint arity rows) = none := by
  simp [runRows, nativeAttributes]
  split <;> simp_all <;> omega

end E7CJointSerializerSourceSemantics

namespace E7CJointSerializerSourceGuardBridge
open E7CEECQTwoStageExactCodec E7CJointRawJsonAdmission
open E7CJointSerializerSourceSyntax E7CJointSerializerSourceSemantics
open E7CJointCPythonNormalReturnTrace

/- The serializer premise of #157 is supplied by source-expression execution.
Admission, Joint, final comparison, and running-host adequacy remain separate. -/
open E7CJointAdmissionGenerated E7CJointAdmissionPythonOperations
open E7CJointSortConstructorSemantics E7CJointAdmissionStatementTrace
open E7CJointFirstStageNormalReturnComposition

theorem source_serializer_guard_recursive_equality
    {read : Value → String → Option Value} (attributes : AttributeContracts read)
    {rawDocument : RawJson} {ops : CPythonJointPrimitives}
    (admission : CompleteAdmissionStatementTrace rawDocument)
    (joint : JointNormalizerStatementTrace ops
      (parseRows admission.rowsAdmission.rows))
    {output : RawJson}
    (helperRun : runRows read (.joint 2
      ((jointNormalizer ops (parseRows admission.rowsAdmission.rows)).map fromRow)) =
      some output)
    (contract : CPythonJsonEqualityContract output admission.rawRows)
    (returned : finalRowsGuard contract.pythonEqual output admission.rawRows =
      .returnedNormally) :
    rawJsonObjectKeyExtEq output admission.rawRows :=
  first_stage_guard_recursive_equality admission joint
    (normal_source_run_yields_rows_statement_trace attributes helperRun)
    contract returned

end E7CJointSerializerSourceGuardBridge
