import E7CJointRawJsonAdmission

/-!
Statement-level model of row serialization and the final raw equality guard
for the pinned `admit` normal branch. It constructs serialized values from
field-read/write events and derives the final raw-row relation from branch
execution plus one CPython equality adequacy contract.
-/
namespace E7CJointCPythonNormalReturnTrace

open E7CEECQTwoStageAllInput
open E7CEECQTwoStageExactCodec
open E7CJointAdmissionExecution
open E7CJointRawJsonAdmission

structure GraphFieldStatementTrace (graph : WireGraph) (output : RawJson) : Type where
  edgesRead : List String
  edgesAttributeRead : edgesRead = graph.edges
  tagRead : Option String
  tagAttributeRead : tagRead = graph.tag
  dictionaryWrite : output = .object
    [("edges", .array (edgesRead.map RawJson.string)),
     ("tag", tagRead.elim RawJson.null RawJson.string)]

structure FractionFieldStatementTrace (coefficient : Rat) (output : RawJson) : Type where
  numeratorRead : Int
  numeratorAttributeRead : numeratorRead = coefficient.num
  denominatorRead : Nat
  denominatorAttributeRead : denominatorRead = coefficient.den
  dictionaryWrite : output = .object
    [("numerator", .integer numeratorRead),
     ("denominator", .integer (Int.ofNat denominatorRead))]

structure RowStatementTrace (row : WireRow) (output : RawJson) : Type where
  leftOutput : RawJson
  leftGraphReadWrite : GraphFieldStatementTrace row.left leftOutput
  rightOutput : RawJson
  rightGraphReadWrite : GraphFieldStatementTrace row.right rightOutput
  coefficientOutput : RawJson
  fractionReadWrite : FractionFieldStatementTrace row.coefficient coefficientOutput
  atomListWrite : RawJson
  atomsWritten : outputAtoms = .array [leftOutput, rightOutput]
  rowDictionaryWrite : output = .object
    [("atoms", outputAtoms), ("coefficient", coefficientOutput)]

inductive RowsStatementTrace : List WireRow → RawJson → Prop where
  | nil : RowsStatementTrace [] (.array [])
  | cons {row : WireRow} {rows : List WireRow}
      {rowOutput : RawJson} {tailRows : List RawJson}
      (rowTrace : RowStatementTrace row rowOutput)
      (tailTrace : RowsStatementTrace rows (.array tailRows)) :
      RowsStatementTrace (row :: rows) (.array (rowOutput :: tailRows))

theorem graph_statement_output_exact
    {graph : WireGraph} {output : RawJson}
    (trace : GraphFieldStatementTrace graph output) :
    output = encodeRawGraph graph := by
  rw [trace.dictionaryWrite, trace.edgesAttributeRead, trace.tagAttributeRead]

theorem fraction_statement_output_exact
    {coefficient : Rat} {output : RawJson}
    (trace : FractionFieldStatementTrace coefficient output) :
    output = encodeRawFraction coefficient := by
  rw [trace.dictionaryWrite, trace.numeratorAttributeRead,
    trace.denominatorAttributeRead]

theorem row_statement_output_exact
    {row : WireRow} {output : RawJson}
    (trace : RowStatementTrace row output) :
    output = encodeRawRow row := by
  rw [trace.rowDictionaryWrite, trace.atomsWritten,
    graph_statement_output_exact trace.leftGraphReadWrite,
    graph_statement_output_exact trace.rightGraphReadWrite,
    fraction_statement_output_exact trace.fractionReadWrite]

theorem rows_statement_output_exact
    {rows : List WireRow} {output : RawJson}
    (trace : RowsStatementTrace rows output) :
    output = encodeRawRows rows := by
  induction trace with
  | nil => rfl
  | @cons row rows rowOutput rowsOutput rowTrace rowsTrace ih =>
      simp [encodeRawRows, row_statement_output_exact rowTrace, ih]

inductive FinalGuardOutcome where
  | returnedNormally
  | rejected
  deriving DecidableEq, Repr

def finalRowsGuard (pythonEqual : RawJson → RawJson → Bool)
    (serializedRows originalRows : RawJson) : FinalGuardOutcome :=
  if pythonEqual serializedRows originalRows then
    .returnedNormally
  else
    .rejected

structure CPythonJsonEqualityContract where
  pythonEqual : RawJson → RawJson → Bool
  equalityRefinesExtensionalModel : ∀ left right,
    pythonEqual left right = decide (rawJsonEquivalent left right)

theorem normal_guard_execution_yields_extensional_equality
    (contract : CPythonJsonEqualityContract)
    {serializedRows originalRows : RawJson}
    (branch : finalRowsGuard contract.pythonEqual serializedRows originalRows =
      .returnedNormally) :
    rawJsonEquivalent serializedRows originalRows := by
  have hCompare : contract.pythonEqual serializedRows originalRows = true := by
    unfold finalRowsGuard at branch
    split at branch <;> simp_all
  rw [contract.equalityRefinesExtensionalModel] at hCompare
  exact of_decide_eq_true hCompare

theorem rawJsonEquivalent_of_structural_eq
    {left right : RawJson} (h : left = right) :
    rawJsonEquivalent left right := by
  unfold rawJsonEquivalent
  subst right
  rfl

/-- The serializer result and equality result are derived from statement traces.
The only equality adequacy premise is the operation-level CPython contract; the
theorem does not take a serialized result, equality boolean, or #146 raw trace
as a premise. -/
theorem pinned_statement_suffix_yields_canonical_raw_rows
    {normalizer : List Row → List Row} {source : List WireRow}
    {result : List Row} {originalRows output : RawJson}
    (canonical : CanonicalWireRows source)
    (typedExecution : ModeledNormalExecution normalizer source result)
    (serializer : RowsStatementTrace (result.map fromRow) output)
    (contract : CPythonJsonEqualityContract)
    (returned : finalRowsGuard contract.pythonEqual output originalRows =
      .returnedNormally) :
    result = source.map toRow ∧
      rawJsonEquivalent originalRows
        (encodeRawRows (result.map fromRow)) := by
  have hExactRows := modeled_normal_execution_exact_rows canonical typedExecution
  have hSerialized : output = encodeRawRows (result.map fromRow) :=
    rows_statement_output_exact serializer
  have hGuard : rawJsonEquivalent output originalRows :=
    normal_guard_execution_yields_extensional_equality contract returned
  have hCanonical : rawJsonEquivalent output
      (encodeRawRows (result.map fromRow)) :=
    rawJsonEquivalent_of_structural_eq hSerialized
  exact ⟨hExactRows,
    rawJsonEquivalent_trans (rawJsonEquivalent_symmetric hGuard) hCanonical⟩

end E7CJointCPythonNormalReturnTrace
