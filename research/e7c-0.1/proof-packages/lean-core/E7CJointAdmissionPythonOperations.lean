import E7CJointAdmissionCPythonBridge

/-!
Operation-level semantics for the pinned FG3 `joint` and `rows` helpers.

The premises correspond to individual CPython operations in the pinned helper
bodies: ordered loop visits, dictionary lookup/add/set, Fraction zero testing,
support filtering, built-in sorting, Joint construction, graph field writes,
Fraction numerator/denominator reads and list-comprehension order. They do not
assume the complete Joint or serializer result equation. CPython adequacy for
each primitive and normal completion is explicit.
-/
namespace E7CJointAdmissionPythonOperations
open E7CEECQTwoStageAllInput
open E7CEECQTwoStageExactCodec
open E7CJointAdmissionGenerated
open E7CJointAdmissionCalls
open E7CJointAdmissionExecution

abbrev JointKey := Graph × Graph

structure JointEntry where
  key : JointKey
  coefficient : Rat
  deriving DecidableEq, Repr

def rowKey (row : Row) : JointKey := (row.left, row.right)

structure CPythonJointPrimitives where
  keyEqual : JointKey → JointKey → Bool
  add : Rat → Rat → Rat
  isZero : Rat → Bool
  keyEqualityRefines : ∀ left right, keyEqual left right = decide (left = right)
  additionRefines : ∀ left right, add left right = left + right
  truthTestRefines : ∀ value, isZero value = decide (value = 0)

def dictLookup (keyEqual : JointKey → JointKey → Bool)
    (entries : List JointEntry) (key : JointKey) : Rat :=
  match entries with
  | [] => 0
  | entry :: rest =>
      if keyEqual entry.key key then entry.coefficient else dictLookup keyEqual rest key

def dictSet (keyEqual : JointKey → JointKey → Bool)
    (entries : List JointEntry) (key : JointKey) (amount : Rat) : List JointEntry :=
  match entries with
  | [] => [⟨key, amount⟩]
  | entry :: rest =>
      if keyEqual entry.key key then ⟨key, amount⟩ :: rest
      else entry :: dictSet keyEqual rest key amount

def jointDictStep (ops : CPythonJointPrimitives)
    (entries : List JointEntry) (row : Row) : List JointEntry :=
  let key := rowKey row
  let old := dictLookup ops.keyEqual entries key
  dictSet ops.keyEqual entries key (ops.add old row.coefficient)

def jointDictRun (ops : CPythonJointPrimitives) :
    List Row → List JointEntry → List JointEntry
  | [], entries => entries
  | row :: rest, entries => jointDictRun ops rest (jointDictStep ops entries row)

inductive JointDictionaryTrace (ops : CPythonJointPrimitives) :
    List Row → List JointEntry → List JointEntry → Prop where
  | nil (entries : List JointEntry) : JointDictionaryTrace ops [] entries entries
  | cons (row : Row) (rows : List Row) (before after final : List JointEntry)
      (step : after = jointDictStep ops before row)
      (tail : JointDictionaryTrace ops rows after final) :
      JointDictionaryTrace ops (row :: rows) before final

theorem dictionaryTrace_computes_run
    {ops : CPythonJointPrimitives} {rows : List Row}
    {before final : List JointEntry}
    (trace : JointDictionaryTrace ops rows before final) :
    final = jointDictRun ops rows before := by
  induction trace with
  | nil entries => rfl
  | @cons row rows before after final step tail ih =>
      simp [jointDictRun, step, ih]

def nonzeroKeys (ops : CPythonJointPrimitives)
    (entries : List JointEntry) : List JointKey :=
  (entries.filter (fun entry => !ops.isZero entry.coefficient)).map
    (fun entry => entry.key)

def compareNatLists : List Nat → List Nat → Ordering
  | [], [] => .eq
  | [], _ :: _ => .lt
  | _ :: _, [] => .gt
  | left :: leftRest, right :: rightRest =>
      let head := compare left right
      if head == .eq then compareNatLists leftRest rightRest else head

def compareText (left right : String) : Ordering :=
  compareNatLists (left.toList.map Char.toNat) (right.toList.map Char.toNat)

def graphEdgesIdentity (graph : Graph) : List Nat :=
  (if graph.ab then [0] else []) ++
  (if graph.ac then [1] else []) ++
  (if graph.bc then [2] else [])

def compareBool (left right : Bool) : Ordering :=
  match left, right with
  | false, false | true, true => .eq
  | false, true => .lt
  | true, false => .gt

def compareGraphIdentity (left right : Graph) : Ordering :=
  let edges := compareNatLists (graphEdgesIdentity left) (graphEdgesIdentity right)
  if edges != .eq then edges
  else
    let marked := compareBool left.tag.isSome right.tag.isSome
    if marked != .eq then marked
    else compareText (left.tag.getD "") (right.tag.getD "")

def compareJointIdentity (left right : JointKey) : Ordering :=
  let first := compareGraphIdentity left.1 right.1
  if first != .eq then first else compareGraphIdentity left.2 right.2

def jointKeyLt (left right : JointKey) : Bool :=
  compareJointIdentity left right == .lt

def insertJointKey (key : JointKey) : List JointKey → List JointKey
  | [] => [key]
  | head :: tail =>
      if jointKeyLt key head then key :: head :: tail
      else head :: insertJointKey key tail

def sortJointKeys : List JointKey → List JointKey
  | [] => []
  | key :: rest => insertJointKey key (sortJointKeys rest)

def entryRow (ops : CPythonJointPrimitives) (entries : List JointEntry)
    (key : JointKey) : Row :=
  ⟨key.1, key.2, dictLookup ops.keyEqual entries key⟩

def jointModelRows (ops : CPythonJointPrimitives)
    (entries : List JointEntry) : List Row :=
  (sortJointKeys (nonzeroKeys ops entries)).map (entryRow ops entries)

def jointNormalizer (ops : CPythonJointPrimitives) (rows : List Row) : List Row :=
  jointModelRows ops (jointDictRun ops rows [])

/- Each member corresponds to a separate operation result in `joint`: the
   dictionary loop, Fraction truth filtering, Python's `sorted` key function
   and comparator, and materialising `(atoms, coefficient)` terms before the
   validating Joint constructor. -/
structure CPythonJointHelperTrace (ops : CPythonJointPrimitives)
    (parsed : List Row) : Type where
  finalDictionary : List JointEntry
  dictionaryLoop : JointDictionaryTrace ops parsed [] finalDictionary
  pythonFilteredKeys : List JointKey
  filterResult : pythonFilteredKeys = nonzeroKeys ops finalDictionary
  pythonSortedKeys : List JointKey
  -- Assumed observation of CPython sorted; its comparator/sort execution is
  -- not derived in this increment.
  sortResult : pythonSortedKeys = sortJointKeys pythonFilteredKeys
  pythonTerms : List Row
  termMaterialisation : pythonTerms = pythonSortedKeys.map
    (entryRow ops finalDictionary)
  constructedTerms : List Row
  -- Assumed observation of Joint construction copying the supplied terms;
  -- constructor validation/acceptance is separately recorded below.
  constructorCopiesTerms : constructedTerms = pythonTerms
  arity : Nat
  binaryArity : arity = 2
  constructorAccepts :
    constructedTerms.all (fun row => decide (row.coefficient ≠ 0)) = true

theorem joint_helper_result_refines
    {ops : CPythonJointPrimitives} {parsed : List Row}
    (trace : CPythonJointHelperTrace ops parsed) :
    trace.constructedTerms = jointNormalizer ops parsed := by
  have hdict : trace.finalDictionary = jointDictRun ops parsed [] :=
    dictionaryTrace_computes_run trace.dictionaryLoop
  rw [trace.constructorCopiesTerms, trace.termMaterialisation,
    trace.sortResult, trace.filterResult, hdict]
  rfl

/- CPython serializer primitive outcomes are recorded at field level. The
   Fraction result is the exact rational denoted by its canonical Python
   numerator/denominator fields; the separate JSON pair decoder is below. -/
structure CPythonRowsHelperTrace (result : List Row) where
  graphEdges : Graph → List String
  graphTag : Graph → Option String
  fractionNumerator : Rat → Int
  fractionDenominator : Rat → Nat
  graphEdgesRefine : ∀ graph, graphEdges graph = (fromGraph graph).edges
  graphTagRefine : ∀ graph, graphTag graph = (fromGraph graph).tag
  fractionNumeratorRefines : ∀ coefficient,
    fractionNumerator coefficient = coefficient.num
  fractionDenominatorRefines : ∀ coefficient,
    fractionDenominator coefficient = coefficient.den
  fractionPairRefines : ∀ coefficient,
    ((fractionNumerator coefficient : Rat) /
      (fractionDenominator coefficient : Rat)) = coefficient
  pythonRows : List WireRow
  listComprehensionOrder : pythonRows = result.map (fun row =>
    ⟨⟨graphEdges row.left, graphTag row.left⟩,
      ⟨graphEdges row.right, graphTag row.right⟩,
      (fractionNumerator row.coefficient : Rat) /
        (fractionDenominator row.coefficient : Rat)⟩)

def pythonGraph (ops : CPythonRowsHelperTrace result) (graph : Graph) : WireGraph :=
  ⟨ops.graphEdges graph, ops.graphTag graph⟩

def pythonRow (ops : CPythonRowsHelperTrace result) (row : Row) : WireRow :=
  ⟨pythonGraph ops row.left, pythonGraph ops row.right,
    (ops.fractionNumerator row.coefficient : Rat) /
      (ops.fractionDenominator row.coefficient : Rat)⟩

theorem graph_helper_result_refines (ops : CPythonRowsHelperTrace result)
    (graph : Graph) : pythonGraph ops graph = fromGraph graph := by
  change ⟨ops.graphEdges graph, ops.graphTag graph⟩ = fromGraph graph
  rw [ops.graphEdgesRefine graph, ops.graphTagRefine graph]

theorem row_helper_result_refines (ops : CPythonRowsHelperTrace result)
    (row : Row) : pythonRow ops row = serializeRow row := by
  cases row with
  | mk left right coefficient =>
      simp [pythonRow, serializeRow, graph_helper_result_refines,
        ops.fractionPairRefines]

theorem rows_helper_result_refines (ops : CPythonRowsHelperTrace result) :
    ops.pythonRows = serializeRows result := by
  rw [ops.listComprehensionOrder]
  unfold serializeRows
  apply List.map_congr_left
  intro row membership
  change pythonRow ops row = serializeRow row
  exact row_helper_result_refines ops row

theorem rows_helper_result_yields_write_call
    (ops : CPythonRowsHelperTrace result) :
    RowsWriteCall result ops.pythonRows := by
  rw [rows_helper_result_refines ops]
  exact rows_write_call result

/- The end-to-end record composes the operation traces with the already
   bounded parser and comparator premises. Joint aggregation and row writing
   are outputs of their helper traces, rather than whole-result premises. -/
structure CPythonAdmissionHelperTrace
    (source : List WireRow) : Type where
  primitives : CPythonJointPrimitives
  parsed : List Row
  canonicalAccepted : ∀ row ∈ source,
    canonicalGraph row.left ∧ canonicalGraph row.right
  parserIteration : parsed = parseRows source
  jointTrace : CPythonJointHelperTrace primitives parsed
  result : List Row
  jointConstructorResult : result = jointTrace.constructedTerms
  rowsTrace : CPythonRowsHelperTrace result
  encoded : List WireRow
  serializerResult : encoded = rowsTrace.pythonRows
  equalityResult : Bool
  builtinEqualityRefines : equalityResult = decide (encoded = source)
  normalReturnBranch : equalityResult = true

theorem helper_trace_joint_result
    {source : List WireRow}
    (ops : CPythonAdmissionHelperTrace source) :
    ops.result = jointNormalizer ops.primitives ops.parsed := by
  rw [ops.jointConstructorResult]
  exact joint_helper_result_refines ops.jointTrace

theorem helper_trace_rows_result
    {source : List WireRow}
    (ops : CPythonAdmissionHelperTrace source) :
    ops.encoded = serializeRows ops.result := by
  rw [ops.serializerResult]
  exact rows_helper_result_refines ops.rowsTrace

def actual_helpers_yield_modeled_trace
    {source : List WireRow}
    (ops : CPythonAdmissionHelperTrace source) :
    ModeledNormalExecution (jointNormalizer ops.primitives) source ops.result := by
  have guard : decide (ops.encoded = source) = true := by
    rw [← ops.builtinEqualityRefines]
    exact ops.normalReturnBranch
  exact ⟨ops.parsed, ops.encoded,
    AdmissionStep.evaluated ops.parsed ops.result ops.encoded
      ops.parserIteration (helper_trace_joint_result ops)
      (helper_trace_rows_result ops) guard⟩

theorem actual_helpers_normal_return_exact_rows
    {source : List WireRow}
    (ops : CPythonAdmissionHelperTrace source) :
    ops.result = source.map toRow :=
  modeled_normal_execution_exact_rows ops.canonicalAccepted
    (actual_helpers_yield_modeled_trace ops)

/- JSON-level rationals retain their numerator and denominator separately.
   This prevents the typed Rat carrier from identifying unreduced raw inputs
   with the canonical Fraction encoding that `rows` emits. -/
inductive RawJsonInteger where
  | integer (value : Int)
  | boolean (value : Bool)
  | other
  deriving DecidableEq, Repr

def exactJsonInteger : RawJsonInteger → Option Int
  | .integer value => some value
  | .boolean _ => none
  | .other => none

theorem pythonBoolIsRejectedAsExactInt (value : Bool) :
    exactJsonInteger (.boolean value) = none := rfl

structure RawCoefficient where
  numerator : RawJsonInteger
  denominator : RawJsonInteger
  deriving DecidableEq, Repr

structure RawJointRow where
  left : WireGraph
  right : WireGraph
  coefficient : RawCoefficient
  deriving DecidableEq, Repr

def rawRowValid (row : RawJointRow) : Prop :=
  (∃ numerator denominator,
    exactJsonInteger row.coefficient.numerator = some numerator ∧
    exactJsonInteger row.coefficient.denominator = some denominator ∧
    denominator > 0 ∧ numerator ≠ 0) ∧
    canonicalGraph row.left ∧ canonicalGraph row.right

/- The raw JSON parser/type checks, exact-int checks (including rejection of
   bool), and Fraction constructor are explicit premises. The value equation
   is not the entire parsed-list result: each row is decoded independently,
   in source order, and the positive denominator is retained. -/
structure CPythonRawDecodeTrace (raw : RawJointRow) where
  numerator : Int
  denominator : Int
  coefficientValue : Rat
  numeratorIsExactInt : exactJsonInteger raw.coefficient.numerator = some numerator
  denominatorIsExactInt : exactJsonInteger raw.coefficient.denominator = some denominator
  denominatorPositive : denominator > 0
  numeratorNonzero : numerator ≠ 0
  fractionValueRefines :
    coefficientValue * (denominator : Rat) = (numerator : Rat)
  leftConfigAccepts : canonicalGraph raw.left
  rightConfigAccepts : canonicalGraph raw.right

def decodedRawRow (raw : RawJointRow) (trace : CPythonRawDecodeTrace raw) : Row :=
  ⟨toGraph raw.left, toGraph raw.right, trace.coefficientValue⟩

def decodedRawWireRow (raw : RawJointRow)
    (trace : CPythonRawDecodeTrace raw) : WireRow :=
  ⟨raw.left, raw.right, trace.coefficientValue⟩

theorem raw_row_decode_is_parser_result (raw : RawJointRow)
    (trace : CPythonRawDecodeTrace raw) :
    decodedRawRow raw trace =
      { left := toGraph raw.left, right := toGraph raw.right,
        coefficient := trace.coefficientValue } := rfl

theorem raw_row_decode_checks_source (raw : RawJointRow)
    (trace : CPythonRawDecodeTrace raw) : rawRowValid raw := by
  refine ⟨⟨trace.numerator, trace.denominator,
    trace.numeratorIsExactInt, trace.denominatorIsExactInt,
    trace.denominatorPositive, trace.numeratorNonzero⟩,
    trace.leftConfigAccepts, trace.rightConfigAccepts⟩

inductive CPythonRawRowsTrace : List RawJointRow → List WireRow → Prop where
  | nil : CPythonRawRowsTrace [] []
  | cons (raw : RawJointRow) (rawRest : List RawJointRow)
      (typedHead : WireRow) (typedRest : List WireRow)
      (headTrace : CPythonRawDecodeTrace raw)
      (headResult : typedHead = decodedRawWireRow raw headTrace)
      (tailTrace : CPythonRawRowsTrace rawRest typedRest) :
      CPythonRawRowsTrace (raw :: rawRest) (typedHead :: typedRest)

structure CPythonRowsAdmissionBound (raw : List RawJointRow) : Prop where
  atMostSixtyFour : raw.length ≤ 64

theorem raw_rows_trace_preserves_order
    {raw : List RawJointRow} {typed : List WireRow}
    (trace : CPythonRawRowsTrace raw typed) : typed.length = raw.length := by
  induction trace with
  | nil => rfl
  | cons raw rawRest typedHead typedRest headTrace headResult tailTrace ih =>
      simp [ih]

theorem raw_rows_count_respects_admission_limit
    {raw : List RawJointRow} {typed : List WireRow}
    (trace : CPythonRawRowsTrace raw typed)
    (bound : CPythonRowsAdmissionBound raw) : typed.length ≤ 64 := by
  calc
    typed.length = raw.length := raw_rows_trace_preserves_order trace
    _ ≤ 64 := bound.atMostSixtyFour

end E7CJointAdmissionPythonOperations
