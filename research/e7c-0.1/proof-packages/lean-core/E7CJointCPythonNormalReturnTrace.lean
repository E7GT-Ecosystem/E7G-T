import E7CJointRawJsonAdmission

/-!
Bounded statement-level model of row serialization and the final raw equality
guard for the pinned `admit` normal branch. It constructs serialized values from
field-read/write events and derives the final raw-row relation from branch
execution plus one CPython equality adequacy contract.
-/
namespace E7CJointCPythonNormalReturnTrace

open E7CEECQTwoStageAllInput
open E7CEECQTwoStageExactCodec
open E7CJointAdmissionExecution
open E7CJointRawJsonAdmission

noncomputable instance rawJsonEquivalentDecidable (left right : RawJson) :
    Decidable (rawJsonEquivalent left right) := by
  unfold rawJsonEquivalent
  infer_instance

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
  outputAtoms : RawJson
  atomListWrite : outputAtoms = .array [leftOutput, rightOutput]
  rowDictionaryWrite : output = .object
    [("atoms", outputAtoms), ("coefficient", coefficientOutput)]

inductive RowsStatementTrace : List WireRow → RawJson → Prop where
  | nil : RowsStatementTrace [] (.array [])
  | cons {row : WireRow} {rows : List WireRow}
      {rowOutput : RawJson} {tailRows : List RawJson}
      (rowTrace : RowStatementTrace row rowOutput)
      (tailTrace : RowsStatementTrace rows (.array tailRows)) :
      RowsStatementTrace (row :: rows) (.array (rowOutput :: tailRows))

theorem rawJsonDepthList_string (values : List String) :
    rawJsonDepthList (values.map RawJson.string) = 0 := by
  induction values with
  | nil => rfl
  | cons value rest ih =>
      simp [rawJsonDepthList, rawJsonDepth, ih]

theorem encodeRawGraph_depth (graph : WireGraph) :
    rawJsonDepth (encodeRawGraph graph) = 2 := by
  cases graph with
  | mk edges tag =>
      cases tag <;>
        simp [encodeRawGraph, rawJsonDepth, rawJsonDepthFields,
          rawJsonDepthList_string, rawJsonDepthList]

theorem encodeRawFraction_depth (coefficient : Rat) :
    rawJsonDepth (encodeRawFraction coefficient) = 1 := by
  simp [encodeRawFraction, rawJsonDepth, rawJsonDepthFields]

theorem encodeRawRow_depth (row : WireRow) :
    rawJsonDepth (encodeRawRow row) = 4 := by
  cases row with
  | mk left right coefficient =>
      simp [encodeRawRow, rawJsonDepth, rawJsonDepthFields, rawJsonDepthList,
        encodeRawGraph_depth, encodeRawFraction_depth]

theorem encodeRawRows_depth_le (rows : List WireRow) :
    rawJsonDepth (encodeRawRows rows) ≤ 5 := by
  induction rows with
  | nil => simp [encodeRawRows, rawJsonDepth, rawJsonDepthList]
  | cons row rest ih =>
      simp [encodeRawRows, rawJsonDepth, rawJsonDepthList,
        encodeRawRow_depth, ih]
      omega

theorem graph_statement_output_exact
    {graph : WireGraph} {output : RawJson}
    (trace : GraphFieldStatementTrace graph output) :
    output = encodeRawGraph graph := by
  rw [trace.dictionaryWrite, trace.edgesAttributeRead, trace.tagAttributeRead]
  rfl

theorem fraction_statement_output_exact
    {coefficient : Rat} {output : RawJson}
    (trace : FractionFieldStatementTrace coefficient output) :
    output = encodeRawFraction coefficient := by
  rw [trace.dictionaryWrite, trace.numeratorAttributeRead,
    trace.denominatorAttributeRead]
  rfl

theorem row_statement_output_exact
    {row : WireRow} {output : RawJson}
    (trace : RowStatementTrace row output) :
    output = encodeRawRow row := by
  rw [trace.rowDictionaryWrite, trace.atomListWrite]
  have hleft := graph_statement_output_exact trace.leftGraphReadWrite
  have hright := graph_statement_output_exact trace.rightGraphReadWrite
  have hcoeff := fraction_statement_output_exact trace.fractionReadWrite
  simp [encodeRawRow, hleft, hright, hcoeff]

theorem rows_statement_output_exact
    {rows : List WireRow} {output : RawJson}
    (trace : RowsStatementTrace rows output) :
    output = encodeRawRows rows := by
  induction trace with
  | nil => rfl
  | @cons row rows rowOutput rowsOutput rowTrace rowsTrace ih =>
      have htail : rowsOutput = rows.map encodeRawRow := by
        change RawJson.array rowsOutput = RawJson.array (rows.map encodeRawRow) at ih
        injection ih with htail
      simp [encodeRawRows, row_statement_output_exact rowTrace, htail]

theorem rows_statement_depth_le
    {rows : List WireRow} {output : RawJson}
    (trace : RowsStatementTrace rows output) :
    rawJsonDepth output ≤ 5 := by
  rw [rows_statement_output_exact trace]
  exact encodeRawRows_depth_le rows

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

/- Host adequacy is restricted to the one pair compared by the pinned final
guard. The fuel-safety proofs are separate premises derived below from row
admission and the serializer trace, not folded into this contract. -/
structure CPythonJsonEqualityContract
    (serialized original : RawJson) where
  pythonEqual : RawJson → RawJson → Bool
  equalityAtComparedPair :
    ∀ (serializedFuelSafe : rawJsonDepth serialized ≤ 32)
      (originalFuelSafe : rawJsonDepth original ≤ 32),
      pythonEqual serialized original =
        decide (rawJsonEquivalent serialized original)

theorem normal_guard_execution_yields_extensional_equality
    {serializedRows originalRows : RawJson}
    (contract : CPythonJsonEqualityContract serializedRows originalRows)
    (serializedFuelSafe : rawJsonDepth serializedRows ≤ 32)
    (originalFuelSafe : rawJsonDepth originalRows ≤ 32)
    (branch : finalRowsGuard contract.pythonEqual serializedRows originalRows =
      .returnedNormally) :
    rawJsonEquivalent serializedRows originalRows := by
  have hCompare : contract.pythonEqual serializedRows originalRows = true := by
    unfold finalRowsGuard at branch
    split at branch <;> simp_all
  rw [contract.equalityAtComparedPair serializedFuelSafe originalFuelSafe] at hCompare
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
    (admittedRows : decodeJointRows originalRows = some source)
    (typedExecution : ModeledNormalExecution normalizer source result)
    (serializer : RowsStatementTrace (result.map fromRow) output)
    (contract : CPythonJsonEqualityContract output originalRows)
    (returned : finalRowsGuard contract.pythonEqual output originalRows =
      .returnedNormally) :
    result = source.map toRow ∧
      rawJsonEquivalent originalRows
        (encodeRawRows (result.map fromRow)) := by
  have hExactRows := modeled_normal_execution_exact_rows canonical typedExecution
  have hSerialized : output = encodeRawRows (result.map fromRow) :=
    rows_statement_output_exact serializer
  have hOutputDepth : rawJsonDepth output ≤ 5 :=
    rows_statement_depth_le serializer
  have hOutputFuel : rawJsonDepth output ≤ 32 := by omega
  have hOriginalFuel : rawJsonDepth originalRows ≤ 32 :=
    decodeJointRows_depth_below_fuel admittedRows
  have hGuard : rawJsonEquivalent output originalRows :=
    normal_guard_execution_yields_extensional_equality contract
      (by omega) hOriginalFuel returned
  have hCanonical : rawJsonEquivalent output
      (encodeRawRows (result.map fromRow)) :=
    rawJsonEquivalent_of_structural_eq hSerialized
  exact ⟨hExactRows,
    rawJsonEquivalent_trans (rawJsonEquivalent_symmetric hGuard) hCanonical⟩

end E7CJointCPythonNormalReturnTrace
