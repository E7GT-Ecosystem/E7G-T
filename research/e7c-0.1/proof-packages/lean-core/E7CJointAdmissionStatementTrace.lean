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

private theorem unique_string (fuel : Nat) (value : String) :
    rawJsonUniqueObjectKeysFuel fuel (.string value) = true := by
  cases fuel <;> rfl

private theorem unique_integer (fuel : Nat) (value : Int) :
    rawJsonUniqueObjectKeysFuel fuel (.integer value) = true := by
  cases fuel <;> rfl

theorem graph_decoder_follows_statement_trace
    {raw : RawJson} (trace : GraphAdmissionStatementTrace raw) :
    decodeGraph raw = some trace.output := by
  simp [guard, Option.guard, decodeGraph, trace.objectRead, trace.keyCheck, trace.edgesFieldRead,
    trace.tagFieldRead, trace.stringArrayDecode,
    trace.edgeOrderCheck, trace.tagDecode, GraphAdmissionStatementTrace.output]

theorem graph_trace_canonical
    {raw : RawJson} (trace : GraphAdmissionStatementTrace raw) :
    canonicalGraph trace.output := by
  exact canonicalEdges_implies_canonicalGraph trace.edgeOrderCheck

theorem graph_trace_within_fuel
    {raw : RawJson} (trace : GraphAdmissionStatementTrace raw) :
    rawJsonWithinFuel 2 raw = true := by
  have layout := exactKeys_two_layout trace.keyCheck (by decide)
    trace.edgesFieldRead trace.tagFieldRead
  have hStringDecode := trace.stringArrayDecode
  have edgesFuel : rawJsonWithinFuel 1 trace.rawEdges = true := by
    cases hEdges : trace.rawEdges with
    | array values =>
        have hstrings : ∀ value ∈ values, ∃ text, value = .string text := by
          simpa [decodeStringList, hEdges] using
            decodeStringList_members_are_strings hStringDecode
        change values.all (rawJsonWithinFuel 0) = true
        rw [List.all_eq_true]
        intro value membership
        rcases hstrings value membership with ⟨text, hvalue⟩
        rw [hvalue]
        rfl
    | null => simp [decodeStringList, hEdges] at hStringDecode
    | boolean value => simp [decodeStringList, hEdges] at hStringDecode
    | integer value => simp [decodeStringList, hEdges] at hStringDecode
    | nonIntegerNumber lexeme => simp [decodeStringList, hEdges] at hStringDecode
    | string value => simp [decodeStringList, hEdges] at hStringDecode
    | object fields => simp [decodeStringList, hEdges] at hStringDecode
  have tagFuel : rawJsonWithinFuel 1 trace.rawTag = true := by
    cases hTag : trace.rawTag with
    | null => rfl
    | string value => rfl
    | boolean value =>
        have hDecode := trace.tagDecode
        simp [decodeTag, hTag] at hDecode
    | integer value =>
        have hDecode := trace.tagDecode
        simp [decodeTag, hTag] at hDecode
    | nonIntegerNumber lexeme =>
        have hDecode := trace.tagDecode
        simp [decodeTag, hTag] at hDecode
    | array values =>
        have hDecode := trace.tagDecode
        simp [decodeTag, hTag] at hDecode
    | object fields =>
        have hDecode := trace.tagDecode
        simp [decodeTag, hTag] at hDecode
  rcases layout with layout | layout
  · rw [trace.objectRead, layout]
    simp [rawJsonWithinFuel, edgesFuel, tagFuel]
  · rw [trace.objectRead, layout]
    simp [rawJsonWithinFuel, edgesFuel, tagFuel]

theorem graph_trace_unique_keys
    {raw : RawJson} (trace : GraphAdmissionStatementTrace raw) (fuel : Nat) :
    rawJsonUniqueObjectKeysFuel (fuel + 2) raw = true := by
  have layout := exactKeys_two_layout trace.keyCheck (by decide)
    trace.edgesFieldRead trace.tagFieldRead
  have edgesUnique : rawJsonUniqueObjectKeysFuel (fuel + 1) trace.rawEdges = true := by
    have hdecode := trace.stringArrayDecode
    cases hEdges : trace.rawEdges with
    | array values =>
        have hstrings : ∀ value ∈ values, ∃ text, value = .string text := by
          simpa [decodeStringList, hEdges] using
            decodeStringList_members_are_strings trace.stringArrayDecode
        change values.all (rawJsonUniqueObjectKeysFuel fuel) = true
        rw [List.all_eq_true]
        intro value membership
        rcases hstrings value membership with ⟨text, hvalue⟩
        rw [hvalue]
        exact unique_string fuel text
    | null => simp [decodeStringList, hEdges] at hdecode
    | boolean value => simp [decodeStringList, hEdges] at hdecode
    | integer value => simp [decodeStringList, hEdges] at hdecode
    | nonIntegerNumber lexeme => simp [decodeStringList, hEdges] at hdecode
    | string value => simp [decodeStringList, hEdges] at hdecode
    | object fields => simp [decodeStringList, hEdges] at hdecode
  have tagUnique : rawJsonUniqueObjectKeysFuel (fuel + 1) trace.rawTag = true := by
    have hdecode := trace.tagDecode
    cases hTag : trace.rawTag with
    | null => rfl
    | string value => exact unique_string (fuel + 1) value
    | boolean value => simp [decodeTag, hTag] at hdecode
    | integer value => simp [decodeTag, hTag] at hdecode
    | nonIntegerNumber lexeme => simp [decodeTag, hTag] at hdecode
    | array values => simp [decodeTag, hTag] at hdecode
    | object fields => simp [decodeTag, hTag] at hdecode
  rcases layout with layout | layout
  · rw [trace.objectRead, layout]
    simp [rawJsonUniqueObjectKeysFuel, distinctObjectKeys, edgesUnique, tagUnique]
  · rw [trace.objectRead, layout]
    simp [rawJsonUniqueObjectKeysFuel, distinctObjectKeys, edgesUnique, tagUnique]

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

theorem fraction_trace_within_fuel
    {raw : RawJson} (trace : FractionAdmissionStatementTrace raw) :
    rawJsonWithinFuel 2 raw = true := by
  have layout := exactKeys_two_layout trace.keyCheck (by decide)
    trace.numeratorFieldRead trace.denominatorFieldRead
  have numeratorFuel : rawJsonWithinFuel 1 trace.rawNumerator = true := by
    have hnum := trace.numeratorExactInt
    cases rawNum : trace.rawNumerator with
    | integer value => rfl
    | null => simp [exactInteger, rawNum] at hnum
    | boolean value => simp [exactInteger, rawNum] at hnum
    | nonIntegerNumber lexeme => simp [exactInteger, rawNum] at hnum
    | string value => simp [exactInteger, rawNum] at hnum
    | array values => simp [exactInteger, rawNum] at hnum
    | object fields => simp [exactInteger, rawNum] at hnum
  have denominatorFuel : rawJsonWithinFuel 1 trace.rawDenominator = true := by
    have hden := trace.denominatorExactInt
    cases rawDen : trace.rawDenominator with
    | integer value => rfl
    | null => simp [exactInteger, rawDen] at hden
    | boolean value => simp [exactInteger, rawDen] at hden
    | nonIntegerNumber lexeme => simp [exactInteger, rawDen] at hden
    | string value => simp [exactInteger, rawDen] at hden
    | array values => simp [exactInteger, rawDen] at hden
    | object fields => simp [exactInteger, rawDen] at hden
  rcases layout with layout | layout
  · rw [trace.objectRead, layout]
    simp [rawJsonWithinFuel, numeratorFuel, denominatorFuel]
  · rw [trace.objectRead, layout]
    simp [rawJsonWithinFuel, numeratorFuel, denominatorFuel]

theorem fraction_trace_unique_keys
    {raw : RawJson} (trace : FractionAdmissionStatementTrace raw) (fuel : Nat) :
    rawJsonUniqueObjectKeysFuel (fuel + 1) raw = true := by
  have layout := exactKeys_two_layout trace.keyCheck (by decide)
    trace.numeratorFieldRead trace.denominatorFieldRead
  have numeratorUnique : rawJsonUniqueObjectKeysFuel fuel trace.rawNumerator = true := by
    have hnum := trace.numeratorExactInt
    cases h : trace.rawNumerator with
    | integer value => exact unique_integer fuel value
    | null => simp [exactInteger, h] at hnum
    | boolean value => simp [exactInteger, h] at hnum
    | nonIntegerNumber lexeme => simp [exactInteger, h] at hnum
    | string value => simp [exactInteger, h] at hnum
    | array values => simp [exactInteger, h] at hnum
    | object fields => simp [exactInteger, h] at hnum
  have denominatorUnique : rawJsonUniqueObjectKeysFuel fuel trace.rawDenominator = true := by
    have hden := trace.denominatorExactInt
    cases h : trace.rawDenominator with
    | integer value => exact unique_integer fuel value
    | null => simp [exactInteger, h] at hden
    | boolean value => simp [exactInteger, h] at hden
    | nonIntegerNumber lexeme => simp [exactInteger, h] at hden
    | string value => simp [exactInteger, h] at hden
    | array values => simp [exactInteger, h] at hden
    | object fields => simp [exactInteger, h] at hden
  rcases layout with layout | layout
  · rw [trace.objectRead, layout]
    simp [rawJsonUniqueObjectKeysFuel, distinctObjectKeys,
      numeratorUnique, denominatorUnique]
  · rw [trace.objectRead, layout]
    simp [rawJsonUniqueObjectKeysFuel, distinctObjectKeys,
      numeratorUnique, denominatorUnique]

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

theorem joint_row_trace_within_fuel
    {raw : RawJson} (trace : JointRowAdmissionStatementTrace raw) :
    rawJsonWithinFuel 4 raw = true := by
  have layout := exactKeys_two_layout trace.keyCheck (by decide)
    trace.atomsFieldRead trace.coefficientFieldRead
  have leftFuel := graph_trace_within_fuel trace.leftGraph
  have rightFuel := graph_trace_within_fuel trace.rightGraph
  have atomsFuel : rawJsonWithinFuel 3 trace.rawAtoms = true := by
    rw [trace.twoCoordinateArrayRead]
    simp [rawJsonWithinFuel, leftFuel, rightFuel]
  have coefficientFuel2 := fraction_trace_within_fuel trace.coefficient
  have coefficientFuel3 : rawJsonWithinFuel 3 trace.rawCoefficient = true := by
    exact rawJsonWithinFuel_mono (fuel := 2) coefficientFuel2
  rcases layout with layout | layout
  · rw [trace.objectRead, layout]
    simp [rawJsonWithinFuel, atomsFuel, coefficientFuel3]
  · rw [trace.objectRead, layout]
    simp [rawJsonWithinFuel, atomsFuel, coefficientFuel3]

theorem joint_row_trace_unique_keys
    {raw : RawJson} (trace : JointRowAdmissionStatementTrace raw) (fuel : Nat) :
    rawJsonUniqueObjectKeysFuel (fuel + 4) raw = true := by
  have layout := exactKeys_two_layout trace.keyCheck (by decide)
    trace.atomsFieldRead trace.coefficientFieldRead
  have hleft := graph_trace_unique_keys trace.leftGraph fuel
  have hright := graph_trace_unique_keys trace.rightGraph fuel
  have atomsUnique : rawJsonUniqueObjectKeysFuel (fuel + 3) trace.rawAtoms = true := by
    rw [trace.twoCoordinateArrayRead]
    simp [rawJsonUniqueObjectKeysFuel, hleft, hright]
  have hcoeff := fraction_trace_unique_keys trace.coefficient (fuel + 2)
  rcases layout with layout | layout
  · rw [trace.objectRead, layout]
    simp [rawJsonUniqueObjectKeysFuel, distinctObjectKeys, atomsUnique, hcoeff]
  · rw [trace.objectRead, layout]
    simp [rawJsonUniqueObjectKeysFuel, distinctObjectKeys, atomsUnique, hcoeff]

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

theorem joint_row_trace_canonical
    {raw : RawJson} (trace : JointRowAdmissionStatementTrace raw) :
    canonicalGraph trace.output.left ∧ canonicalGraph trace.output.right := by
  exact ⟨graph_trace_canonical trace.leftGraph,
    graph_trace_canonical trace.rightGraph⟩

theorem raw_rows_visits_canonical
    {rawRows : List RawJson} {rows : List WireRow}
    (visits : RawRowsVisitTrace rawRows rows) : CanonicalWireRows rows := by
  induction visits with
  | nil =>
      intro row membership
      simp at membership
  | @cons rawRow rawTail tail rowVisit tailVisits ih =>
      intro row membership
      simp at membership
      rcases membership with rfl | membership
      · exact joint_row_trace_canonical rowVisit
      · exact ih row membership

structure RawRowsAdmissionStatementTrace (raw : RawJson) where
  rawRows : List RawJson
  arrayRead : raw = .array rawRows
  rows : List WireRow
  visits : RawRowsVisitTrace rawRows rows
  capCheck : rawRows.length ≤ 64

theorem raw_rows_visits_within_fuel
    {rawRows : List RawJson} {rows : List WireRow}
    (visits : RawRowsVisitTrace rawRows rows) :
    rawJsonWithinFuel 5 (.array rawRows) = true := by
  induction visits with
  | nil => rfl
  | @cons rawRow rawTail tail rowVisit tailVisits ih =>
      have hrow := joint_row_trace_within_fuel rowVisit
      have htail : rawTail.all (rawJsonWithinFuel 4) = true := by
        simpa [rawJsonWithinFuel] using ih
      simp [rawJsonWithinFuel, hrow, htail]

theorem rows_statement_trace_within_fuel
    {raw : RawJson} (trace : RawRowsAdmissionStatementTrace raw) :
    rawJsonWithinFuel 32 raw = true := by
  have hFive := raw_rows_visits_within_fuel trace.visits
  have hThirtyTwo : rawJsonWithinFuel 32 (.array trace.rawRows) = true := by
    exact E7CJointCPythonNormalReturnTrace.rawJsonWithinFuel_mono_of_le
      (by omega) hFive
  simpa [trace.arrayRead] using hThirtyTwo

theorem raw_rows_visits_unique_keys
    {rawRows : List RawJson} {rows : List WireRow}
    (visits : RawRowsVisitTrace rawRows rows) :
    rawJsonUniqueObjectKeysFuel 32 (.array rawRows) = true := by
  induction visits with
  | nil => rfl
  | @cons rawRow rawTail tail rowVisit tailVisits ih =>
      have hrow := joint_row_trace_unique_keys rowVisit 27
      have htail : rawTail.all (rawJsonUniqueObjectKeysFuel 31) = true := by
        simpa [rawJsonUniqueObjectKeysFuel] using ih
      simp [rawJsonUniqueObjectKeysFuel, hrow, htail]

theorem rows_statement_trace_unique_keys
    {raw : RawJson} (trace : RawRowsAdmissionStatementTrace raw) :
    rawJsonUniqueObjectKeys raw = true := by
  rw [trace.arrayRead]
  exact raw_rows_visits_unique_keys trace.visits

/- The selected carrier retains the original raw integer pair. In particular,
   these witnesses do not pass through the decoded Rat coefficient. -/
theorem decoded_string_values_exact
    {values : List RawJson} {strings : List String}
    (decoded : decodeStringValues values = some strings) :
    values = strings.map RawJson.string := by
  induction values generalizing strings with
  | nil =>
      simp [decodeStringValues] at decoded
      cases decoded
      rfl
  | cons value rest ih =>
      cases value with
      | string text =>
          cases hrest : decodeStringValues rest with
          | none => simp [decodeStringValues, hrest] at decoded
          | some tail =>
              simp [decodeStringValues, hrest] at decoded
              cases decoded
              simp [ih hrest]
      | null => simp [decodeStringValues] at decoded
      | boolean value => simp [decodeStringValues] at decoded
      | integer value => simp [decodeStringValues] at decoded
      | nonIntegerNumber lexeme => simp [decodeStringValues] at decoded
      | array values => simp [decodeStringValues] at decoded
      | object fields => simp [decodeStringValues] at decoded

theorem decoded_string_list_exact
    {raw : RawJson} {strings : List String}
    (decoded : decodeStringList raw = some strings) :
    raw = .array (strings.map RawJson.string) := by
  cases raw with
  | array values =>
      have h := decoded_string_values_exact (by simpa [decodeStringList] using decoded)
      simpa using congrArg RawJson.array h
  | null => simp [decodeStringList] at decoded
  | boolean value => simp [decodeStringList] at decoded
  | integer value => simp [decodeStringList] at decoded
  | nonIntegerNumber lexeme => simp [decodeStringList] at decoded
  | string value => simp [decodeStringList] at decoded
  | object fields => simp [decodeStringList] at decoded

theorem decoded_tag_exact
    {raw : RawJson} {tag : Option String}
    (decoded : decodeTag raw = some tag) :
    raw = tag.elim RawJson.null RawJson.string := by
  cases raw with
  | null =>
      simp [decodeTag] at decoded
      cases decoded
      rfl
  | string value =>
      simp [decodeTag] at decoded
      cases decoded
      rfl
  | boolean value => simp [decodeTag] at decoded
  | integer value => simp [decodeTag] at decoded
  | nonIntegerNumber lexeme => simp [decodeTag] at decoded
  | array values => simp [decodeTag] at decoded
  | object fields => simp [decodeTag] at decoded

theorem exact_integer_raw
    {raw : RawJson} {value : Int}
    (decoded : exactInteger raw = some value) : raw = .integer value := by
  cases raw with
  | integer actual =>
      simp [exactInteger] at decoded
      cases decoded
      rfl
  | null => simp [exactInteger] at decoded
  | boolean actual => simp [exactInteger] at decoded
  | nonIntegerNumber lexeme => simp [exactInteger] at decoded
  | string actual => simp [exactInteger] at decoded
  | array values => simp [exactInteger] at decoded
  | object fields => simp [exactInteger] at decoded

theorem graph_trace_selected_raw
    {raw : RawJson} (trace : GraphAdmissionStatementTrace raw) :
    ∃ selected : SelectedRawGraph, raw = rawSelectedGraph selected := by
  have hEdges := decoded_string_list_exact trace.stringArrayDecode
  have hTag := decoded_tag_exact trace.tagDecode
  have layout := exactKeys_two_layout trace.keyCheck (by decide)
    trace.edgesFieldRead trace.tagFieldRead
  rcases layout with layout | layout
  · refine ⟨⟨trace.edges, trace.tag, false⟩, ?_⟩
    rw [trace.objectRead, layout, hEdges, hTag]
    cases trace.tag <;> rfl
  · refine ⟨⟨trace.edges, trace.tag, true⟩, ?_⟩
    rw [trace.objectRead, layout, hEdges, hTag]
    cases trace.tag <;> rfl

theorem fraction_trace_selected_raw
    {raw : RawJson} (trace : FractionAdmissionStatementTrace raw) :
    ∃ selected : SelectedRawFraction, raw = rawSelectedFraction selected := by
  have hNumerator := exact_integer_raw trace.numeratorExactInt
  have hDenominator := exact_integer_raw trace.denominatorExactInt
  have layout := exactKeys_two_layout trace.keyCheck (by decide)
    trace.numeratorFieldRead trace.denominatorFieldRead
  rcases layout with layout | layout
  · refine ⟨⟨trace.numerator, trace.denominator,
        trace.positiveDenominator, false⟩, ?_⟩
    rw [trace.objectRead, layout, hNumerator, hDenominator]
    rfl
  · refine ⟨⟨trace.numerator, trace.denominator,
        trace.positiveDenominator, true⟩, ?_⟩
    rw [trace.objectRead, layout, hNumerator, hDenominator]
    rfl

theorem row_trace_selected_raw
    {raw : RawJson} (trace : JointRowAdmissionStatementTrace raw) :
    ∃ selected : SelectedRawRow, raw = rawSelectedRow selected := by
  rcases graph_trace_selected_raw trace.leftGraph with ⟨left, hleft⟩
  rcases graph_trace_selected_raw trace.rightGraph with ⟨right, hright⟩
  rcases fraction_trace_selected_raw trace.coefficient with ⟨fraction, hfraction⟩
  have layout := exactKeys_two_layout trace.keyCheck (by decide)
    trace.atomsFieldRead trace.coefficientFieldRead
  rcases layout with layout | layout
  · refine ⟨⟨left, right, fraction, false⟩, ?_⟩
    rw [trace.objectRead, layout, trace.twoCoordinateArrayRead,
      hleft, hright, hfraction]
    rfl
  · refine ⟨⟨left, right, fraction, true⟩, ?_⟩
    rw [trace.objectRead, layout, trace.twoCoordinateArrayRead,
      hleft, hright, hfraction]
    rfl

theorem raw_rows_visits_selected_raw
    {rawRows : List RawJson} {rows : List WireRow}
    (visits : RawRowsVisitTrace rawRows rows) :
    ∃ selected : List SelectedRawRow,
      rawRows = selected.map rawSelectedRow := by
  induction visits with
  | nil => exact ⟨[], rfl⟩
  | @cons rawRow rawTail tail rowVisit tailVisits ih =>
      rcases row_trace_selected_raw rowVisit with ⟨row, hrow⟩
      rcases ih with ⟨selectedTail, htail⟩
      exact ⟨row :: selectedTail, by simp [hrow, htail]⟩

theorem rows_statement_trace_selected_raw
    {raw : RawJson} (trace : RawRowsAdmissionStatementTrace raw) :
    ∃ selected : List SelectedRawRow,
      raw = rawSelectedRows selected := by
  rcases raw_rows_visits_selected_raw trace.visits with ⟨selected, hselected⟩
  exact ⟨selected, by rw [trace.arrayRead, hselected]; rfl⟩

theorem rows_decoder_follows_statement_trace
    {raw : RawJson} (trace : RawRowsAdmissionStatementTrace raw) :
    decodeJointRows raw = some trace.rows := by
  have hfuel := rows_statement_trace_within_fuel trace
  have hfuelRows : rawJsonWithinFuel 32 (.array trace.rawRows) = true := by
    simpa [trace.arrayRead] using hfuel
  simp [decodeJointRows, trace.arrayRead, trace.capCheck, hfuelRows,
    raw_rows_mapM_follows_visits trace.visits]

theorem rows_statement_trace_canonical
    {raw : RawJson} (trace : RawRowsAdmissionStatementTrace raw) :
    CanonicalWireRows trace.rows :=
  raw_rows_visits_canonical trace.visits

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
