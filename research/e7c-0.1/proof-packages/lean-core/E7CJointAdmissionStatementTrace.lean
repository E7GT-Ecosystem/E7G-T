import E7CJointCPythonNormalReturnTrace

/-!
Separate statement-trace increment for the pinned Joint admission prefix.
It records object/key reads and nested row decoder operations individually,
then derives the raw rows decoder result and the typed parser call. It does
not claim full top-level document acceptance or CPython operation adequacy.
-/
namespace E7CJointAdmissionStatementTrace

open E7CEECQTwoStageAllInput
open E7CEECQTwoStageExactCodec
open E7CJointAdmissionExecution
open E7CJointRawJsonAdmission
open E7CJointCPythonNormalReturnTrace
open E7CJointAdmissionPythonOperations
open E7CJointAdmissionCalls
open E7CJointAdmissionGenerated
open E7CJointSortConstructorSemantics

structure GraphAdmissionStatementTrace (raw : RawJson) where
  fields : List (String × RawJson)
  objectRead : raw = .object fields
  keyCheck : exactKeys fields ["edges", "tag"] = true
  rawEdges : RawJson
  rawTag : RawJson
  edgesFieldRead : lookupField fields "edges" = some rawEdges
  tagFieldRead : lookupField fields "tag" = some rawTag
  edges : List String
  stringArrayDecode : decodeStringList rawEdges = some edges
  edgeOrderCheck : canonicalEdges edges = true
  tag : Option String
  tagDecode : decodeTag rawTag = some tag

def GraphAdmissionStatementTrace.output
    {raw : RawJson} (trace : GraphAdmissionStatementTrace raw) : WireGraph :=
  ⟨trace.edges, trace.tag⟩

theorem graph_decoder_follows_statement_trace
    {raw : RawJson} (trace : GraphAdmissionStatementTrace raw) :
    decodeGraph raw = some trace.output := by
  simp [guard, Option.guard, decodeGraph, trace.objectRead, trace.keyCheck, trace.edgesFieldRead,
    trace.tagFieldRead, trace.stringArrayDecode,
    trace.edgeOrderCheck, trace.tagDecode, GraphAdmissionStatementTrace.output]

structure FractionAdmissionStatementTrace (raw : RawJson) where
  fields : List (String × RawJson)
  objectRead : raw = .object fields
  keyCheck : exactKeys fields ["numerator", "denominator"] = true
  rawNumerator : RawJson
  rawDenominator : RawJson
  numeratorFieldRead : lookupField fields "numerator" = some rawNumerator
  denominatorFieldRead : lookupField fields "denominator" = some rawDenominator
  numerator : Int
  numeratorExactInt : exactInteger rawNumerator = some numerator
  denominator : Int
  denominatorExactInt : exactInteger rawDenominator = some denominator
  positiveDenominator : denominator > 0
  nonzeroNumerator : numerator ≠ 0

def FractionAdmissionStatementTrace.output
    {raw : RawJson} (trace : FractionAdmissionStatementTrace raw) : Rat :=
  (trace.numerator : Rat) / (trace.denominator : Rat)

theorem fraction_decoder_follows_statement_trace
    {raw : RawJson} (trace : FractionAdmissionStatementTrace raw) :
    decodeFractionPair raw = some trace.output := by
  simp [guard, Option.guard, decodeFractionPair, trace.objectRead, trace.keyCheck, trace.numeratorFieldRead,
    trace.denominatorFieldRead, trace.numeratorExactInt,
    trace.denominatorExactInt, trace.positiveDenominator,
    trace.nonzeroNumerator, FractionAdmissionStatementTrace.output]

structure JointRowAdmissionStatementTrace (raw : RawJson) where
  fields : List (String × RawJson)
  objectRead : raw = .object fields
  keyCheck : exactKeys fields ["atoms", "coefficient"] = true
  rawAtoms : RawJson
  rawCoefficient : RawJson
  atomsFieldRead : lookupField fields "atoms" = some rawAtoms
  coefficientFieldRead : lookupField fields "coefficient" = some rawCoefficient
  rawLeft : RawJson
  rawRight : RawJson
  twoCoordinateArrayRead : rawAtoms = .array [rawLeft, rawRight]
  leftGraph : GraphAdmissionStatementTrace rawLeft
  rightGraph : GraphAdmissionStatementTrace rawRight
  coefficient : FractionAdmissionStatementTrace rawCoefficient

def JointRowAdmissionStatementTrace.output
    {raw : RawJson} (trace : JointRowAdmissionStatementTrace raw) : WireRow :=
  ⟨trace.leftGraph.output, trace.rightGraph.output, trace.coefficient.output⟩

theorem row_decoder_follows_statement_trace
    {raw : RawJson} (trace : JointRowAdmissionStatementTrace raw) :
    decodeJointRow raw = some trace.output := by
  simp [guard, Option.guard, decodeJointRow, trace.objectRead, trace.keyCheck, trace.atomsFieldRead,
    trace.coefficientFieldRead, trace.twoCoordinateArrayRead,
    graph_decoder_follows_statement_trace trace.leftGraph,
    graph_decoder_follows_statement_trace trace.rightGraph,
    fraction_decoder_follows_statement_trace trace.coefficient,
    JointRowAdmissionStatementTrace.output]

inductive RawRowsVisitTrace : List RawJson → List WireRow → Prop where
  | nil : RawRowsVisitTrace [] []
  | cons {rawRow : RawJson} {rawTail : List RawJson}
      {tail : List WireRow}
      (rowVisit : JointRowAdmissionStatementTrace rawRow)
      (tailVisits : RawRowsVisitTrace rawTail tail) :
      RawRowsVisitTrace (rawRow :: rawTail) (rowVisit.output :: tail)

theorem raw_rows_mapM_follows_visits
    {rawRows : List RawJson} {rows : List WireRow}
    (visits : RawRowsVisitTrace rawRows rows) :
    rawRows.mapM decodeJointRow = some rows := by
  induction visits with
  | nil => rfl
  | @cons rawRow rawTail tail rowVisit tailVisits ih =>
      simp [row_decoder_follows_statement_trace rowVisit, ih]

structure RawRowsAdmissionStatementTrace (raw : RawJson) where
  rawRows : List RawJson
  arrayRead : raw = .array rawRows
  rows : List WireRow
  visits : RawRowsVisitTrace rawRows rows
  capCheck : rawRows.length ≤ 64
  fuelCheck : rawJsonWithinFuel 32 raw = true

theorem rows_decoder_follows_statement_trace
    {raw : RawJson} (trace : RawRowsAdmissionStatementTrace raw) :
    decodeJointRows raw = some trace.rows := by
  have hfuel : rawJsonWithinFuel 32 (.array trace.rawRows) = true := by
    simpa [trace.arrayRead] using trace.fuelCheck
  simp [decodeJointRows, trace.arrayRead, trace.capCheck, hfuel,
    raw_rows_mapM_follows_visits trace.visits]

/-- The prefix pins the top-level document object, exact top-level keys,
metadata checks and rows field read, then derives nested row admission from
individual statement events. Policy and interpretation statement traces are
not part of this increment. -/
structure PinnedAdmissionRowsStatementTrace (rawDocument : RawJson) where
  fields : List (String × RawJson)
  documentObjectRead : rawDocument = .object fields
  documentKeyCheck : exactKeys fields expectedDocumentKeys = true
  metadataCheck : expectedMetadata fields = true
  rawRows : RawJson
  rowsFieldRead : lookupField fields "rows" = some rawRows
  rowsAdmission : RawRowsAdmissionStatementTrace rawRows

theorem pinned_document_rows_decoder_result
    {rawDocument : RawJson}
    (trace : PinnedAdmissionRowsStatementTrace rawDocument) :
    decodeJointRows trace.rawRows = some trace.rowsAdmission.rows :=
  rows_decoder_follows_statement_trace trace.rowsAdmission

/-- With the independently proved canonical graph invariant, each decoded
row's Config and Fraction calls are supplied by the existing typed parser
rules. This composes the raw statement events into the parser call derivation,
without assuming a completed decoded document or Joint result. -/
theorem raw_statement_rows_supply_typed_parse_call
    {rawDocument : RawJson}
    (trace : PinnedAdmissionRowsStatementTrace rawDocument)
    (canonical : CanonicalWireRows trace.rowsAdmission.rows) :
    ParseRowsCall trace.rowsAdmission.rows
      (parseRows trace.rowsAdmission.rows) :=
  parse_rows_call_of_canonical canonical


/- The Joint operation is composed from the admitted typed parser rows,
   pre-sort dictionary/filter visits, abstract identity-sort visits, and
   per-row constructor validation. These remain abstract operation semantics;
   actual CPython sort/constructor adequacy is not asserted here. -/
structure JointNormalizerStatementTrace
    (ops : CPythonJointPrimitives) (parsed : List Row) where
  preSort : PreSortJointHelperTrace ops parsed
  sortedKeys : List E7CJointAdmissionPythonOperations.JointKey
  sortVisits : AbstractIdentitySortTrace cpythonIdentityCompare
    preSort.pythonFilteredKeys sortedKeys
  constructorOps : CPythonJointConstructorOps
  constructorVisits : CPythonJointConstructorTrace constructorOps 2
    (materializeJointRows ops preSort.finalDictionary sortedKeys)

theorem joint_statement_trace_returns_model_rows
    {ops : CPythonJointPrimitives} {parsed : List Row}
    (trace : JointNormalizerStatementTrace ops parsed) :
    runConstructorRows trace.constructorOps 2
      (materializeJointRows ops trace.preSort.finalDictionary trace.sortedKeys) =
      some (jointNormalizer ops parsed) :=
  joint_constructor_trace_builds_normalizer trace.preSort trace.sortedKeys
    trace.sortVisits trace.constructorOps trace.constructorVisits

theorem raw_statement_admission_reaches_typed_joint_operation
    {rawDocument : RawJson} {ops : CPythonJointPrimitives}
    (admission : PinnedAdmissionRowsStatementTrace rawDocument)
    (canonical : CanonicalWireRows admission.rowsAdmission.rows)
    (jointTrace : JointNormalizerStatementTrace ops
      (parseRows admission.rowsAdmission.rows)) :
    decodeJointRows admission.rawRows = some admission.rowsAdmission.rows ∧
    ParseRowsCall admission.rowsAdmission.rows
      (parseRows admission.rowsAdmission.rows) ∧
    runConstructorRows jointTrace.constructorOps 2
      (materializeJointRows ops jointTrace.preSort.finalDictionary
        jointTrace.sortedKeys) =
      some (jointNormalizer ops (parseRows admission.rowsAdmission.rows)) ∧
    parseRows admission.rowsAdmission.rows =
      admission.rowsAdmission.rows.map toRow := by
  have hDecoded := pinned_document_rows_decoder_result admission
  have hParser := parse_rows_call_of_canonical canonical
  have hJoint := joint_statement_trace_returns_model_rows jointTrace
  exact ⟨hDecoded, hParser, hJoint, rfl⟩

end E7CJointAdmissionStatementTrace
