import E7CJointSortConstructorSemantics

/-!
Untyped JSON-value admission for the pinned binary Joint document shape.
Objects model already-decoded JSON objects with unique string keys. JSON-byte
parsing, canonical JSON/hash behavior, CPython exact-type checks, Fraction
construction and raw serialization remain operation-level host links.
-/
namespace E7CJointRawJsonAdmission

open E7CEECQTwoStageAllInput
open E7CEECQTwoStageExactCodec
open E7CJointAdmissionExecution

inductive RawJson where
  | null
  | boolean (value : Bool)
  | integer (value : Int)
  | nonIntegerNumber (lexeme : String)
  | string (value : String)
  | array (values : List RawJson)
  | object (fields : List (String × RawJson))


def lookupField : List (String × RawJson) → String → Option RawJson
  | [], _ => none
  | (key, value) :: rest, wanted =>
      if key == wanted then some value else lookupField rest wanted

def distinctObjectKeys : List (String × RawJson) → Bool
  | [] => true
  | (key, _) :: rest =>
      !(rest.any (fun field => field.1 == key)) && distinctObjectKeys rest

def exactKeys (fields : List (String × RawJson)) (expected : List String) : Bool :=
  distinctObjectKeys fields &&
  decide (fields.length = expected.length) &&
  fields.all (fun field => expected.contains field.1) &&
  expected.all (fun key => fields.any (fun field => field.1 == key))

def exactInteger : RawJson → Option Int
  | .integer value => some value
  | _ => none

def decodeStringList : RawJson → Option (List String)
  | .array values =>
      values.mapM fun value =>
        match value with
        | .string text => some text
        | _ => none
  | _ => none

def edgeRank : String → Option Nat
  | "AB" => some 0
  | "AC" => some 1
  | "BC" => some 2
  | _ => none

def canonicalEdges : List String → Bool
  | [] => true
  | [edge] => (edgeRank edge).isSome
  | edge :: next :: rest =>
      match edgeRank edge, edgeRank next with
      | some leftRank, some rightRank =>
          decide (leftRank < rightRank) && canonicalEdges (next :: rest)
      | _, _ => false

def decodeTag : RawJson → Option (Option String)
  | .null => some none
  | .string value => some (some value)
  | _ => none

def decodeGraph : RawJson → Option WireGraph
  | .object fields => do
      guard (exactKeys fields ["edges", "tag"])
      let rawEdges ← lookupField fields "edges"
      let rawTag ← lookupField fields "tag"
      let edges ← decodeStringList rawEdges
      guard (canonicalEdges edges)
      let tag ← decodeTag rawTag
      pure ⟨edges, tag⟩
  | _ => none

def decodeFractionPair (raw : RawJson) : Option Rat :=
  match raw with
  | .object fields => do
      guard (exactKeys fields ["numerator", "denominator"])
      let rawNumerator ← lookupField fields "numerator"
      let rawDenominator ← lookupField fields "denominator"
      let numerator ← exactInteger rawNumerator
      let denominator ← exactInteger rawDenominator
      guard (decide (denominator > 0))
      guard (decide (numerator ≠ 0))
      pure ((numerator : Rat) / (denominator : Rat))
  | _ => none

def decodeJointRow (raw : RawJson) : Option WireRow :=
  match raw with
  | .object fields => do
      guard (exactKeys fields ["atoms", "coefficient"])
      let rawAtoms ← lookupField fields "atoms"
      let rawCoefficient ← lookupField fields "coefficient"
      match rawAtoms with
      | .array [left, right] => do
          let leftGraph ← decodeGraph left
          let rightGraph ← decodeGraph right
          let coefficient ← decodeFractionPair rawCoefficient
          pure ⟨leftGraph, rightGraph, coefficient⟩
      | _ => none
  | _ => none

def decodeJointRows (raw : RawJson) : Option (List WireRow) :=
  match raw with
  | .array rows =>
      if rows.length ≤ 64 then rows.mapM decodeJointRow else none
  | _ => none

structure DecodedRawDocument where
  rawRows : RawJson
  rows : List WireRow
  stepBound : Nat
  ledgerBound : Nat
  capability : Bool
  obligationResolved : Bool

def expectedDocumentKeys : List String :=
  ["edition", "canonical_source_blob", "model_blob", "predicate_edition",
   "input_type", "output_type", "rows", "resource_policy", "interpretation"]

def fieldIsString (fields : List (String × RawJson)) (key wanted : String) : Bool :=
  match lookupField fields key with
  | some (.string actual) => actual == wanted
  | _ => false

def expectedMetadata (fields : List (String × RawJson)) : Bool :=
  fieldIsString fields "edition" "E7C-EECQ-JOINT-RESTRICT/0.1-provisional" &&
  fieldIsString fields "canonical_source_blob" "a84da2c4de2ada23577cde4512a10c3369aba2b5" &&
  fieldIsString fields "model_blob" "6c624fcd49b95e473a3e80160979183e8d3b58aa" &&
  fieldIsString fields "predicate_edition" "FG3-JOINT-COORD0-ABSENT-AB/0.1-provisional" &&
  fieldIsString fields "input_type" "Joint[FG3,FG3]" &&
  fieldIsString fields "output_type" "Outcome[Partition[Joint[FG3,FG3]],core-1]"

def decodeNonnegativeBound (raw : RawJson) : Option Nat :=
  match exactInteger raw with
  | some value => if decide (value ≥ 0) then some value.toNat else none
  | none => none

def decodeResourcePolicy (raw : RawJson) : Option (Nat × Nat) :=
  match raw with
  | .object fields => do
      guard (exactKeys fields ["step_bound", "ledger_bound"])
      let rawSteps ← lookupField fields "step_bound"
      let rawLedger ← lookupField fields "ledger_bound"
      let steps ← decodeNonnegativeBound rawSteps
      let ledger ← decodeNonnegativeBound rawLedger
      pure (steps, ledger)
  | _ => none

def decodeInterpretation (raw : RawJson) : Option (Bool × Bool) :=
  match raw with
  | .object fields => do
      guard (exactKeys fields ["capability", "obligation"])
      let rawCapability ← lookupField fields "capability"
      let rawObligation ← lookupField fields "obligation"
      match rawCapability, rawObligation with
      | .boolean capability, .string "resolved" => pure (capability, true)
      | .boolean capability, .string "unresolved" => pure (capability, false)
      | _, _ => none
  | _ => none

def decodeRawDocument (raw : RawJson) : Option DecodedRawDocument :=
  match raw with
  | .object fields => do
      guard (exactKeys fields expectedDocumentKeys)
      guard (expectedMetadata fields)
      let rawRows ← lookupField fields "rows"
      let rows ← decodeJointRows rawRows
      let rawPolicy ← lookupField fields "resource_policy"
      let (stepBound, ledgerBound) ← decodeResourcePolicy rawPolicy
      let rawInterpretation ← lookupField fields "interpretation"
      let (capability, obligationResolved) ← decodeInterpretation rawInterpretation
      pure ⟨rawRows, rows, stepBound, ledgerBound, capability, obligationResolved⟩
  | _ => none

/- In the pinned adapter, exceeding the 64-row admission cap raises a
   controlled admission error; it is invalid input, not evaluator exhaustion. -/
inductive RawBoundaryEvent where
  | parsedJson (value : RawJson)
  | jsonSyntaxRejected
  | caughtAdmissionFailure
  | uncaughtHelperException
  | resourceInterruption

inductive RawAdmissionOutcome where
  | accepted (document : DecodedRawDocument)
  | invalidInput
  | exception
  | resource

def classifyRawBoundary : RawBoundaryEvent → RawAdmissionOutcome
  | .parsedJson value =>
      match decodeRawDocument value with
      | some document => .accepted document
      | none => .invalidInput
  | .jsonSyntaxRejected => .invalidInput
  | .caughtAdmissionFailure => .invalidInput
  | .uncaughtHelperException => .exception
  | .resourceInterruption => .resource

theorem exactInteger_rejects_boolean (value : Bool) :
    exactInteger (.boolean value) = none := rfl

theorem exactInteger_rejects_noninteger_json_number (lexeme : String) :
    exactInteger (.nonIntegerNumber lexeme) = none := rfl

theorem null_tag_decodes_distinctly :
    decodeTag .null = some none := rfl

theorem empty_string_tag_decodes_distinctly :
    decodeTag (.string "") = some (some "") := rfl

theorem decodeFractionPair_rejects_boolean_numerator :
    decodeFractionPair (.object
      [("numerator", .boolean true), ("denominator", .integer 2)]) = none := by
  decide

theorem decodeFractionPair_rejects_zero_denominator :
    decodeFractionPair (.object
      [("numerator", .integer 1), ("denominator", .integer 0)]) = none := by
  decide

theorem decodeFractionPair_rejects_zero_numerator :
    decodeFractionPair (.object
      [("numerator", .integer 0), ("denominator", .integer 3)]) = none := by
  decide

def encodeRawGraph (graph : WireGraph) : RawJson :=
  .object
    [("edges", .array (graph.edges.map RawJson.string)),
     ("tag", graph.tag.elim RawJson.null RawJson.string)]

def encodeRawFraction (coefficient : Rat) : RawJson :=
  .object
    [("numerator", .integer coefficient.num),
     ("denominator", .integer (Int.ofNat coefficient.den))]

def encodeRawRow (row : WireRow) : RawJson :=
  .object
    [("atoms", .array [encodeRawGraph row.left, encodeRawGraph row.right]),
     ("coefficient", encodeRawFraction row.coefficient)]

def encodeRawRows (rows : List WireRow) : RawJson :=
  .array (rows.map encodeRawRow)

/- Object keys are normalized recursively. The token encoding is
   self-delimiting: child nodes and strings carry their lengths. It gives a
   recursive extensional comparison without relying on RawJson's field-list
   structural equality. This relation is applied to successfully decoded
   objects, whose every object node has unique keys. -/
def natListLe : List Nat → List Nat → Bool
  | [], _ => true
  | _ :: _, [] => false
  | left :: lefts, right :: rights =>
      if left == right then natListLe lefts rights else left < right

def stringCodes (value : String) : List Nat :=
  value.toList.map Char.toNat

def encodeStringCodes (value : String) : List Nat :=
  let codes := stringCodes value
  codes.length :: codes

def insertRawField (item : String × RawJson) : List (String × RawJson) →
    List (String × RawJson)
  | [] => [item]
  | head :: tail =>
      if natListLe (stringCodes item.1) (stringCodes head.1) then item :: head :: tail
      else head :: insertRawField item tail

def sortRawFields (fields : List (String × RawJson)) : List (String × RawJson) :=
  fields.foldr insertRawField []

def normalizeRawJson : RawJson → List Nat
  | .null => [0]
  | .boolean value => [1, if value then 1 else 0]
  | .integer value =>
      [2, if value < 0 then 1 else 0, value.natAbs]
  | .nonIntegerNumber lexeme => 3 :: encodeStringCodes lexeme
  | .string value => 4 :: encodeStringCodes value
  | .array values =>
      [5, values.length] ++ values.flatMap normalizeRawJson
  | .object fields =>
      let ordered := sortRawFields fields
      [6, ordered.length] ++ ordered.flatMap fun (key, fieldValue) =>
        encodeStringCodes key ++ normalizeRawJson fieldValue
termination_by value => sizeOf value
decreasing_by all_goals simp_wf; simp_all; omega

def rawJsonEquivalent (left right : RawJson) : Prop :=
  normalizeRawJson left = normalizeRawJson right

def rawObjectForward : RawJson :=
  .object [("atoms", .integer 7), ("coefficient", .integer 11)]

def rawObjectReordered : RawJson :=
  .object [("coefficient", .integer 11), ("atoms", .integer 7)]

theorem raw_object_key_order_is_extensional :
    rawJsonEquivalent rawObjectForward rawObjectReordered := by
  decide

theorem raw_array_order_remains_significant :
    ¬ rawJsonEquivalent (.array [.integer 1, .integer 2])
      (.array [.integer 2, .integer 1]) := by
  decide

theorem raw_null_and_empty_string_remain_distinct :
    ¬ rawJsonEquivalent .null (.string "") := by
  decide

theorem raw_fraction_pairs_remain_exact :
    ¬ rawJsonEquivalent
      (.object [("numerator", .integer 2), ("denominator", .integer 4)])
      (.object [("numerator", .integer 1), ("denominator", .integer 2)]) := by
  decide

theorem duplicate_object_multiplicity_remains_distinct :
    ¬ rawJsonEquivalent
      (.object [("k", .integer 1), ("k", .integer 1)])
      (.object [("k", .integer 1)]) := by
  decide

theorem rawJsonEquivalent_symmetric {left right : RawJson}
    (h : rawJsonEquivalent left right) : rawJsonEquivalent right left :=
  h.symm

theorem rawJsonEquivalent_trans {left middle right : RawJson}
    (h₁ : rawJsonEquivalent left middle)
    (h₂ : rawJsonEquivalent middle right) :
    rawJsonEquivalent left right :=
  h₁.trans h₂

/- The raw serializer and equality link remain operation-level host premises.
   This theorem composes them using Python-shaped recursive equality rather
   than order-sensitive equality on the RawJson object-field lists. -/
structure RawTypedNormalReturnTrace
    (source : RawJson) (normalizer : List Row → List Row) (result : List Row) : Type where
  document : DecodedRawDocument
  rawAdmission : decodeRawDocument source = some document
  canonicalGraphs : CanonicalWireRows document.rows
  typedRun : ModeledNormalExecution normalizer document.rows result
  rawRowsOutput : RawJson
  rawRowsSerializerRefines : rawJsonEquivalent rawRowsOutput
    (encodeRawRows (result.map fromRow))
  rawRowsEqualityGuard : rawJsonEquivalent rawRowsOutput document.rawRows

theorem raw_rows_equal_canonical_return
    {source : RawJson} {normalizer : List Row → List Row} {result : List Row}
    (trace : RawTypedNormalReturnTrace source normalizer result) :
    rawJsonEquivalent trace.document.rawRows (encodeRawRows (result.map fromRow)) :=
  rawJsonEquivalent_trans
    (rawJsonEquivalent_symmetric trace.rawRowsEqualityGuard)
    trace.rawRowsSerializerRefines

theorem raw_typed_normal_return_exact
    {source : RawJson} {normalizer : List Row → List Row} {result : List Row}
    (trace : RawTypedNormalReturnTrace source normalizer result) :
    result = trace.document.rows.map toRow ∧
      rawJsonEquivalent trace.document.rawRows (encodeRawRows (result.map fromRow)) :=
  ⟨modeled_normal_execution_exact_rows trace.canonicalGraphs trace.typedRun,
    raw_rows_equal_canonical_return trace⟩

theorem boundary_outcomes_remain_distinct :
    classifyRawBoundary .jsonSyntaxRejected ≠
      classifyRawBoundary .uncaughtHelperException ∧
    classifyRawBoundary .uncaughtHelperException ≠
      classifyRawBoundary .resourceInterruption ∧
    classifyRawBoundary .resourceInterruption ≠
      classifyRawBoundary .jsonSyntaxRejected := by
  constructor <;> simp [classifyRawBoundary]

end E7CJointRawJsonAdmission
