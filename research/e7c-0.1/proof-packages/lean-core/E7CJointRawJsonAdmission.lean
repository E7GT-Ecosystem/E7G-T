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

/-- Recursive JSON equality with dictionary keys compared extensionally.
Unlike `rawJsonEquivalent`, this relation is defined directly over RawJson
constructors: arrays retain position and object fields match by key. The
admission domain supplies unique keys, so each object lookup denotes one
value. -/
inductive rawJsonObjectKeyExtEq : RawJson → RawJson → Prop where
  | null : rawJsonObjectKeyExtEq .null .null
  | boolean (value : Bool) :
      rawJsonObjectKeyExtEq (.boolean value) (.boolean value)
  | integer (value : Int) :
      rawJsonObjectKeyExtEq (.integer value) (.integer value)
  | nonIntegerNumber (lexeme : String) :
      rawJsonObjectKeyExtEq (.nonIntegerNumber lexeme) (.nonIntegerNumber lexeme)
  | string (value : String) :
      rawJsonObjectKeyExtEq (.string value) (.string value)
  | array {left right : List RawJson}
      (length : left.length = right.length)
      (elements : ∀ index (indexLt : index < left.length),
        rawJsonObjectKeyExtEq (left.get ⟨index, indexLt⟩) (right.get ⟨index, by omega⟩)) :
      rawJsonObjectKeyExtEq (.array left) (.array right)
  | object {left right : List (String × RawJson)}
      (keys : ∀ key, key ∈ left.map Prod.fst ↔ key ∈ right.map Prod.fst)
      (values : ∀ key leftValue rightValue,
        lookupField left key = some leftValue →
        lookupField right key = some rightValue →
        rawJsonObjectKeyExtEq leftValue rightValue) :
      rawJsonObjectKeyExtEq (.object left) (.object right)


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

/- Object keys are normalized recursively. Array children, object keys, and
   object values all carry token lengths. The selected raw row-array theorem
   below proves two-way agreement with `rawJsonObjectKeyExtEq` on its
   structural carrier, with fuel and unique-key facts explicit. It recovers
   array children in order and object values under their keys; it does not
   claim injectivity for arbitrary RawJson values. -/
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

def insertTokenField (item : List Nat × List Nat) :
    List (List Nat × List Nat) → List (List Nat × List Nat)
  | [] => [item]
  | head :: tail =>
      if natListLe item.1 head.1 then item :: head :: tail
      else head :: insertTokenField item tail

def sortTokenFields (fields : List (List Nat × List Nat)) :
    List (List Nat × List Nat) :=
  fields.foldr insertTokenField []

theorem sortTokenFields_pair_ordered
    {key₁ key₂ value₁ value₂ : List Nat}
    (h₁₂ : natListLe key₁ key₂ = true)
    (h₂₁ : natListLe key₂ key₁ = false) :
    sortTokenFields [(key₁, value₁), (key₂, value₂)] =
      [(key₁, value₁), (key₂, value₂)] := by
  simp [sortTokenFields, insertTokenField, h₁₂]

theorem sortTokenFields_pair_reversed
    {key₁ key₂ value₁ value₂ : List Nat}
    (h₁₂ : natListLe key₁ key₂ = true)
    (h₂₁ : natListLe key₂ key₁ = false) :
    sortTokenFields [(key₂, value₂), (key₁, value₁)] =
      [(key₁, value₁), (key₂, value₂)] := by
  simp [sortTokenFields, insertTokenField, h₁₂, h₂₁]

/-- The selected row, graph, and fraction objects each have two fixed keys.
Their permitted source field orders sort to the same key order. -/
theorem sortTokenFields_atoms_coefficient (atoms fraction : List Nat) :
    sortTokenFields
      [(stringCodes "atoms", atoms), (stringCodes "coefficient", fraction)] =
        [(stringCodes "atoms", atoms), (stringCodes "coefficient", fraction)] := by
  have h : natListLe (stringCodes "atoms") (stringCodes "coefficient") = true := by
    decide
  simp [sortTokenFields, insertTokenField, h]

theorem sortTokenFields_coefficient_atoms (fraction atoms : List Nat) :
    sortTokenFields
      [(stringCodes "coefficient", fraction), (stringCodes "atoms", atoms)] =
        [(stringCodes "atoms", atoms), (stringCodes "coefficient", fraction)] := by
  have h : natListLe (stringCodes "coefficient") (stringCodes "atoms") = false := by
    decide
  simp [sortTokenFields, insertTokenField, h]

/-- Frame a sequence of token sequences by writing each child's token count
before its payload. -/
def frameTokenChunks : List (List Nat) → List Nat
  | [] => []
  | chunk :: rest => chunk.length :: chunk ++ frameTokenChunks rest

theorem flatMap_frameTokenChunks {α : Type} (f : α → List Nat)
    (values : List α) :
    values.flatMap (fun value => (f value).length :: f value) =
      frameTokenChunks (values.map f) := by
  induction values with
  | nil => rfl
  | cons value rest ih => simp [frameTokenChunks, ih]

/-- Read the sequence of length-prefixed token chunks. -/
def unframeTokenChunks : Nat → List Nat → Option (List (List Nat))
  | 0, _ => none
  | _ + 1, [] => some []
  | fuel + 1, length :: rest =>
      let chunk := rest.take length
      if chunk.length = length then
        match unframeTokenChunks fuel (rest.drop length) with
        | some chunks => some (chunk :: chunks)
        | none => none
      else none

/-- Equal framed streams recover exactly the same number of children, with
the same child token sequence at each position. -/
theorem unframe_frameTokenChunks_of_lt (chunks : List (List Nat)) :
    ∀ fuel, chunks.length < fuel →
      unframeTokenChunks fuel (frameTokenChunks chunks) = some chunks := by
  induction chunks with
  | nil =>
      intro fuel h
      cases fuel with
      | zero => omega
      | succ fuel => simp [frameTokenChunks, unframeTokenChunks]
  | cons chunk rest ih =>
      intro fuel h
      cases fuel with
      | zero => omega
      | succ fuel =>
          have hrest : rest.length < fuel := by simp at h; omega
          simp [frameTokenChunks, unframeTokenChunks, List.take_append,
            List.drop_append, ih fuel hrest]

theorem frameTokenChunks_length_ge (chunks : List (List Nat)) :
    chunks.length ≤ (frameTokenChunks chunks).length := by
  induction chunks with
  | nil => simp [frameTokenChunks]
  | cons chunk rest ih =>
      simp [frameTokenChunks]
      omega

theorem frameTokenChunks_injective {left right : List (List Nat)}
    (h : frameTokenChunks left = frameTokenChunks right) : left = right := by
  let fuel := (frameTokenChunks left).length + 1
  have hl := unframe_frameTokenChunks_of_lt left fuel (by
    exact Nat.lt_succ_of_le (frameTokenChunks_length_ge left))
  have hr := unframe_frameTokenChunks_of_lt right fuel (by
    have hlen := congrArg List.length h
    change right.length < (frameTokenChunks left).length + 1
    rw [hlen]
    exact Nat.lt_succ_of_le (frameTokenChunks_length_ge right))
  have heq := congrArg (unframeTokenChunks fuel) h
  rw [hl, hr] at heq
  exact Option.some.inj heq

def tokenFieldChunks (fields : List (List Nat × List Nat)) : List (List Nat) :=
  fields.flatMap fun (key, value) => [key, value]

def encodeTokenFields (fields : List (List Nat × List Nat)) : List Nat :=
  fields.flatMap fun (key, value) =>
    key.length :: key ++ value.length :: value

theorem encodeTokenFields_eq_frameTokenChunks
    (fields : List (List Nat × List Nat)) :
    encodeTokenFields fields = frameTokenChunks (tokenFieldChunks fields) := by
  calc
    encodeTokenFields fields =
        fields.flatMap (fun (key, value) =>
          [key, value].flatMap (fun chunk => chunk.length :: chunk)) := by
      simp [encodeTokenFields]
    _ = (tokenFieldChunks fields).flatMap
        (fun chunk => chunk.length :: chunk) := by
      symm
      exact List.flatMap_assoc
    _ = frameTokenChunks (tokenFieldChunks fields) := by
      symm
      simpa using (flatMap_frameTokenChunks (fun chunk => chunk)
        (tokenFieldChunks fields)).symm

theorem encodeTokenFields_injective_chunks
    {left right : List (List Nat × List Nat)}
    (h : encodeTokenFields left = encodeTokenFields right) :
    tokenFieldChunks left = tokenFieldChunks right := by
  rw [encodeTokenFields_eq_frameTokenChunks,
    encodeTokenFields_eq_frameTokenChunks] at h
  exact frameTokenChunks_injective h

def normalizeRawJsonFuel : Nat → RawJson → List Nat
  -- Match rawJsonWithinFuel 0: all scalar constructors retain their distinct
  -- values, while an array/object at the boundary is outside the domain.
  | 0, .null => [0]
  | 0, .boolean value => [1, if value then 1 else 0]
  | 0, .integer value =>
      [2, if value < 0 then 1 else 0, value.natAbs]
  | 0, .nonIntegerNumber lexeme => 3 :: encodeStringCodes lexeme
  | 0, .string value => 4 :: encodeStringCodes value
  | 0, .array _ => [99]
  | 0, .object _ => [99]
  | fuel + 1, .null => [0]
  | fuel + 1, .boolean value => [1, if value then 1 else 0]
  | fuel + 1, .integer value =>
      [2, if value < 0 then 1 else 0, value.natAbs]
  | fuel + 1, .nonIntegerNumber lexeme => 3 :: encodeStringCodes lexeme
  | fuel + 1, .string value => 4 :: encodeStringCodes value
  | fuel + 1, .array values =>
      [5, values.length] ++ values.flatMap fun value =>
        let child := normalizeRawJsonFuel fuel value
        child.length :: child
  | fuel + 1, .object fields =>
      let normalizedFields := fields.map fun field =>
        (stringCodes field.1, normalizeRawJsonFuel fuel field.2)
      let ordered := sortTokenFields normalizedFields
      [6, ordered.length] ++ encodeTokenFields ordered

theorem charToNatMap_injective {left right : List Char}
    (h : left.map Char.toNat = right.map Char.toNat) : left = right := by
  induction left generalizing right with
  | nil =>
      cases right with
      | nil => rfl
      | cons c cs => simp at h
  | cons c cs ih =>
      cases right with
      | nil => simp at h
      | cons d ds =>
          simp only [List.map_cons, List.cons.injEq] at h
          have hcd : c = d := Char.toNat_inj.mp h.1
          subst d
          simp [ih h.2]

theorem stringCodes_injective {left right : String}
    (h : stringCodes left = stringCodes right) : left = right := by
  have hchars : left.toList = right.toList := by
    apply charToNatMap_injective
    exact h
  exact String.ext hchars

theorem encodeStringCodes_injective {left right : String}
    (h : encodeStringCodes left = encodeStringCodes right) : left = right := by
  have h' := List.cons.inj h
  exact stringCodes_injective h'.2

theorem normalizeRawJsonFuel_integer_injective {fuel : Nat} {left right : Int}
    (h : normalizeRawJsonFuel fuel (.integer left) =
      normalizeRawJsonFuel fuel (.integer right)) : left = right := by
  cases fuel <;> cases left with
  | ofNat left =>
      cases right with
      | ofNat right =>
          simp [normalizeRawJsonFuel] at h
          exact congrArg Int.ofNat h.2
      | negSucc right => simp [normalizeRawJsonFuel] at h
  | negSucc left =>
      cases right with
      | ofNat right => simp [normalizeRawJsonFuel] at h
      | negSucc right =>
          simp [normalizeRawJsonFuel] at h
          exact congrArg Int.negSucc h

theorem normalizeRawJsonFuel_string_injective {fuel : Nat} {left right : String}
    (h : normalizeRawJsonFuel fuel (.string left) =
      normalizeRawJsonFuel fuel (.string right)) : left = right := by
  cases fuel
  all_goals
    change 4 :: encodeStringCodes left = 4 :: encodeStringCodes right at h
    exact encodeStringCodes_injective (List.cons.inj h).2

theorem normalize_array_children_frame (fuel : Nat) (values : List RawJson) :
    normalizeRawJsonFuel (fuel + 1) (.array values) =
      [5, values.length] ++
        frameTokenChunks (values.map (normalizeRawJsonFuel fuel)) := by
  simp [normalizeRawJsonFuel, flatMap_frameTokenChunks]

/-- Equal array encodings have the same arity and the same normalized child
stream at every index. This extracts child boundaries from the explicit
length frames rather than assuming token normalization is injective. -/
theorem normalize_array_encoding_children_eq {fuel : Nat}
    {left right : List RawJson}
    (h : normalizeRawJsonFuel (fuel + 1) (.array left) =
      normalizeRawJsonFuel (fuel + 1) (.array right)) :
    left.length = right.length ∧
      left.map (normalizeRawJsonFuel fuel) =
        right.map (normalizeRawJsonFuel fuel) := by
  rw [normalize_array_children_frame, normalize_array_children_frame] at h
  rcases List.cons.inj h with ⟨_, h'⟩
  rcases List.cons.inj h' with ⟨hlen, hframes⟩
  constructor
  · exact hlen
  · exact frameTokenChunks_injective hframes

def normalizeRawJson (value : RawJson) : List Nat :=
  normalizeRawJsonFuel 32 value

def rawJsonTwoKeyObject (key₁ key₂ : String) (reverse : Bool)
    (value₁ value₂ : RawJson) : RawJson :=
  if reverse then
    .object [(key₂, value₂), (key₁, value₁)]
  else
    .object [(key₁, value₁), (key₂, value₂)]

theorem rawJsonObjectKeyExtEq_twoKeyObject
    {key₁ key₂ : String} (hkeys : key₁ ≠ key₂)
    {left₁ left₂ right₁ right₂ : RawJson}
    {leftReverse rightReverse : Bool}
    (h₁ : rawJsonObjectKeyExtEq left₁ right₁)
    (h₂ : rawJsonObjectKeyExtEq left₂ right₂) :
    rawJsonObjectKeyExtEq
      (rawJsonTwoKeyObject key₁ key₂ leftReverse left₁ left₂)
      (rawJsonTwoKeyObject key₁ key₂ rightReverse right₁ right₂) := by
  cases leftReverse <;> cases rightReverse
  all_goals
    apply rawJsonObjectKeyExtEq.object
    · intro key
      simp [rawJsonTwoKeyObject, or_comm]
    · intro key leftValue rightValue hleft hright
      by_cases hk₁ : key = key₁
      · subst key
        simp [rawJsonTwoKeyObject, lookupField, hkeys, hkeys.symm] at hleft hright
        cases hleft
        cases hright
        exact h₁
      · by_cases hk₂ : key = key₂
        · subst key
          simp [rawJsonTwoKeyObject, lookupField, hkeys, hkeys.symm] at hleft hright
          cases hleft
          cases hright
          exact h₂
        · have hk₁' : key₁ ≠ key := fun h => hk₁ h.symm
          have hk₂' : key₂ ≠ key := fun h => hk₂ h.symm
          simp [rawJsonTwoKeyObject, lookupField, hk₁', hk₂'] at hleft

theorem rawJsonObjectKeyExtEq_twoKeyObject_iff
    {key₁ key₂ : String} (hkeys : key₁ ≠ key₂)
    {left₁ left₂ right₁ right₂ : RawJson}
    {leftReverse rightReverse : Bool} :
    rawJsonObjectKeyExtEq
      (rawJsonTwoKeyObject key₁ key₂ leftReverse left₁ left₂)
      (rawJsonTwoKeyObject key₁ key₂ rightReverse right₁ right₂) ↔
    rawJsonObjectKeyExtEq left₁ right₁ ∧ rawJsonObjectKeyExtEq left₂ right₂ := by
  cases leftReverse <;> cases rightReverse
  all_goals
    constructor
    · intro h
      cases h with
      | object _ values =>
          exact ⟨
            values key₁ left₁ right₁
              (by simp [rawJsonTwoKeyObject, lookupField, hkeys, hkeys.symm])
              (by simp [rawJsonTwoKeyObject, lookupField, hkeys, hkeys.symm]),
            values key₂ left₂ right₂
              (by simp [rawJsonTwoKeyObject, lookupField, hkeys, hkeys.symm])
              (by simp [rawJsonTwoKeyObject, lookupField, hkeys, hkeys.symm])⟩
    · rintro ⟨h₁, h₂⟩
      exact rawJsonObjectKeyExtEq_twoKeyObject hkeys h₁ h₂

/-- For a selected object with a fixed two-key set, equal normalized streams
recover both child streams under their corresponding keys in either source
field order. -/
theorem normalize_rawJsonTwoKeyObject_children_eq {fuel : Nat}
    {key₁ key₂ : String}
    (h₁₂ : natListLe (stringCodes key₁) (stringCodes key₂) = true)
    (h₂₁ : natListLe (stringCodes key₂) (stringCodes key₁) = false)
    {left₁ left₂ right₁ right₂ : RawJson}
    {leftReverse rightReverse : Bool}
    (h : normalizeRawJsonFuel (fuel + 1)
          (rawJsonTwoKeyObject key₁ key₂ leftReverse left₁ left₂) =
        normalizeRawJsonFuel (fuel + 1)
          (rawJsonTwoKeyObject key₁ key₂ rightReverse right₁ right₂)) :
    normalizeRawJsonFuel fuel left₁ = normalizeRawJsonFuel fuel right₁ ∧
      normalizeRawJsonFuel fuel left₂ = normalizeRawJsonFuel fuel right₂ := by
  have hnorm :
      [6, 2] ++ encodeTokenFields
        [(stringCodes key₁, normalizeRawJsonFuel fuel left₁),
         (stringCodes key₂, normalizeRawJsonFuel fuel left₂)] =
      [6, 2] ++ encodeTokenFields
        [(stringCodes key₁, normalizeRawJsonFuel fuel right₁),
         (stringCodes key₂, normalizeRawJsonFuel fuel right₂)] := by
    cases leftReverse <;> cases rightReverse <;>
      simpa [rawJsonTwoKeyObject, normalizeRawJsonFuel,
        sortTokenFields_pair_ordered h₁₂ h₂₁,
        sortTokenFields_pair_reversed h₁₂ h₂₁] using h
  have hpayload := List.append_cancel_left hnorm
  have hchunks := encodeTokenFields_injective_chunks hpayload
  simp only [tokenFieldChunks, List.flatMap_cons, List.flatMap_nil] at hchunks
  rcases List.cons.inj hchunks with ⟨_, hchunks⟩
  rcases List.cons.inj hchunks with ⟨hvalue₁, hchunks⟩
  rcases List.cons.inj hchunks with ⟨_, hchunks⟩
  rcases List.cons.inj hchunks with ⟨hvalue₂, _⟩
  exact ⟨hvalue₁, hvalue₂⟩

theorem normalize_rawRowObject_children_eq {fuel : Nat}
    {leftAtoms leftCoefficient rightAtoms rightCoefficient : RawJson}
    {leftReverse rightReverse : Bool}
    (h : normalizeRawJsonFuel (fuel + 1)
          (rawJsonTwoKeyObject "atoms" "coefficient" leftReverse
            leftAtoms leftCoefficient) =
        normalizeRawJsonFuel (fuel + 1)
          (rawJsonTwoKeyObject "atoms" "coefficient" rightReverse
            rightAtoms rightCoefficient)) :
    normalizeRawJsonFuel fuel leftAtoms = normalizeRawJsonFuel fuel rightAtoms ∧
      normalizeRawJsonFuel fuel leftCoefficient =
        normalizeRawJsonFuel fuel rightCoefficient :=
  normalize_rawJsonTwoKeyObject_children_eq (by decide) (by decide) h

theorem normalize_rawGraphObject_children_eq {fuel : Nat}
    {leftEdges leftTag rightEdges rightTag : RawJson}
    {leftReverse rightReverse : Bool}
    (h : normalizeRawJsonFuel (fuel + 1)
          (rawJsonTwoKeyObject "edges" "tag" leftReverse leftEdges leftTag) =
        normalizeRawJsonFuel (fuel + 1)
          (rawJsonTwoKeyObject "edges" "tag" rightReverse rightEdges rightTag)) :
    normalizeRawJsonFuel fuel leftEdges = normalizeRawJsonFuel fuel rightEdges ∧
      normalizeRawJsonFuel fuel leftTag = normalizeRawJsonFuel fuel rightTag :=
  normalize_rawJsonTwoKeyObject_children_eq (by decide) (by decide) h

theorem normalize_rawFractionObject_children_eq {fuel : Nat}
    {leftNumerator leftDenominator rightNumerator rightDenominator : RawJson}
    {leftReverse rightReverse : Bool}
    (h : normalizeRawJsonFuel (fuel + 1)
          (rawJsonTwoKeyObject "numerator" "denominator" leftReverse
            leftNumerator leftDenominator) =
        normalizeRawJsonFuel (fuel + 1)
          (rawJsonTwoKeyObject "numerator" "denominator" rightReverse
            rightNumerator rightDenominator)) :
    normalizeRawJsonFuel fuel leftNumerator = normalizeRawJsonFuel fuel rightNumerator ∧
      normalizeRawJsonFuel fuel leftDenominator =
        normalizeRawJsonFuel fuel rightDenominator := by
  have h' : normalizeRawJsonFuel (fuel + 1)
      (rawJsonTwoKeyObject "denominator" "numerator" (!leftReverse)
        leftDenominator leftNumerator) =
    normalizeRawJsonFuel (fuel + 1)
      (rawJsonTwoKeyObject "denominator" "numerator" (!rightReverse)
        rightDenominator rightNumerator) := by
    cases leftReverse <;> cases rightReverse <;>
      simpa [rawJsonTwoKeyObject] using h
  have hparts := normalize_rawJsonTwoKeyObject_children_eq (by decide) (by decide) h'
  exact ⟨hparts.2, hparts.1⟩

/-! ### Selected raw row-array carrier

These structures describe the raw admitted representation rather than its
decoded `WireRow`: fraction numerator and denominator are retained as the
original signed and positive integers. Every two-key object carries its own
field-order bit, while arrays remain ordered. -/

structure SelectedRawGraph where
  edges : List String
  tag : Option String
  reverseFields : Bool
  deriving Repr

structure SelectedRawFraction where
  numerator : Int
  denominator : Int
  denominatorPositive : 0 < denominator
  reverseFields : Bool
  deriving Repr

structure SelectedRawRow where
  firstGraph : SelectedRawGraph
  secondGraph : SelectedRawGraph
  coefficient : SelectedRawFraction
  reverseFields : Bool
  deriving Repr

def rawSelectedGraph (graph : SelectedRawGraph) : RawJson :=
  rawJsonTwoKeyObject "edges" "tag" graph.reverseFields
    (.array (graph.edges.map RawJson.string))
    (match graph.tag with
     | none => .null
     | some value => .string value)

def rawSelectedFraction (fraction : SelectedRawFraction) : RawJson :=
  rawJsonTwoKeyObject "numerator" "denominator" fraction.reverseFields
    (.integer fraction.numerator) (.integer fraction.denominator)

def rawSelectedRow (row : SelectedRawRow) : RawJson :=
  rawJsonTwoKeyObject "atoms" "coefficient" row.reverseFields
    (.array [rawSelectedGraph row.firstGraph, rawSelectedGraph row.secondGraph])
    (rawSelectedFraction row.coefficient)

def rawSelectedRows (rows : List SelectedRawRow) : RawJson :=
  .array (rows.map rawSelectedRow)

theorem map_injective_of_injective {α β : Type} (f : α → β)
    (hf : Function.Injective f) {left right : List α}
    (h : left.map f = right.map f) : left = right := by
  induction left generalizing right with
  | nil => cases right with | nil => rfl | cons x xs => simp at h
  | cons x xs ih =>
      cases right with
      | nil => simp at h
      | cons y ys =>
          simp only [List.map_cons, List.cons.injEq] at h
          have hxy := hf h.1
          subst y
          simp [ih h.2]

def selectedTagRaw : Option String → RawJson
  | none => .null
  | some value => .string value

theorem normalize_selectedTag_eq_iff {fuel : Nat} {left right : Option String}
    (hfuel : 0 < fuel) :
    normalizeRawJsonFuel fuel (selectedTagRaw left) =
      normalizeRawJsonFuel fuel (selectedTagRaw right) ↔ left = right := by
  cases fuel with
  | zero => omega
  | succ fuel =>
      cases left with
      | none =>
          cases right <;> simp [selectedTagRaw, normalizeRawJsonFuel]
      | some left =>
          cases right with
          | none => simp [selectedTagRaw, normalizeRawJsonFuel]
          | some right =>
              constructor
              · intro h
                exact congrArg some (normalizeRawJsonFuel_string_injective h)
              · intro h
                cases h
                rfl

theorem normalize_integer_eq_iff {fuel : Nat} {left right : Int} :
    normalizeRawJsonFuel fuel (.integer left) =
      normalizeRawJsonFuel fuel (.integer right) ↔ left = right := by
  constructor
  · exact normalizeRawJsonFuel_integer_injective
  · intro h
    cases h
    rfl

theorem normalize_string_eq_iff {fuel : Nat} {left right : String} :
    normalizeRawJsonFuel fuel (.string left) =
      normalizeRawJsonFuel fuel (.string right) ↔ left = right := by
  constructor
  · exact normalizeRawJsonFuel_string_injective
  · intro h
    cases h
    rfl

theorem rawJsonObjectKeyExtEq_string_iff {left right : String} :
    rawJsonObjectKeyExtEq (.string left) (.string right) ↔ left = right := by
  constructor
  · intro h
    cases h
    rfl
  · intro h
    cases h
    exact rawJsonObjectKeyExtEq.string left

theorem rawJsonObjectKeyExtEq_integer_iff {left right : Int} :
    rawJsonObjectKeyExtEq (.integer left) (.integer right) ↔ left = right := by
  constructor
  · intro h
    cases h
    rfl
  · intro h
    cases h
    exact rawJsonObjectKeyExtEq.integer left

theorem rawJsonObjectKeyExtEq_stringArray_iff {left right : List String} :
    rawJsonObjectKeyExtEq (.array (left.map RawJson.string))
      (.array (right.map RawJson.string)) ↔ left = right := by
  constructor
  · intro h
    cases h with
    | array hlen hitems =>
        have hmap : left.map RawJson.string = right.map RawJson.string := by
          apply List.ext_getElem
          · simpa using hlen
          · intro index hleft hright
            have hrel := hitems index (by simpa using hleft)
            have hleft' : index < left.length := by simpa using hleft
            have hright' : index < right.length := by simpa using hright
            have hval : left[index]'hleft' = right[index]'hright' :=
              rawJsonObjectKeyExtEq_string_iff.mp
                (by simpa only [List.get_eq_getElem, List.getElem_map] using hrel)
            simpa only [List.getElem_map] using congrArg RawJson.string hval
        exact map_injective_of_injective RawJson.string
          (by intro a b h; cases h; rfl) hmap
  · intro h
    cases h
    apply rawJsonObjectKeyExtEq.array rfl
    intro index hindex
    have hleft : index < left.length := by simpa using hindex
    simpa only [List.get_eq_getElem, List.getElem_map] using
      (rawJsonObjectKeyExtEq.string (left[index]))

theorem normalize_rawEdgeArray_eq_iff {fuel : Nat} {left right : List String} :
    normalizeRawJsonFuel (fuel + 1) (.array (left.map RawJson.string)) =
      normalizeRawJsonFuel (fuel + 1) (.array (right.map RawJson.string)) ↔
    left = right := by
  constructor
  · intro h
    obtain ⟨_, hchildren⟩ := normalize_array_encoding_children_eq h
    simp only [List.map_map] at hchildren
    exact map_injective_of_injective (fun value =>
      normalizeRawJsonFuel fuel (.string value))
      (fun _ _ heq => normalizeRawJsonFuel_string_injective heq) hchildren
  · intro h
    cases h
    rfl

theorem normalize_array_eq_of_children_eq {fuel : Nat}
    {left right : List RawJson}
    (hlen : left.length = right.length)
    (hchildren : left.map (normalizeRawJsonFuel fuel) =
      right.map (normalizeRawJsonFuel fuel)) :
    normalizeRawJsonFuel (fuel + 1) (.array left) =
      normalizeRawJsonFuel (fuel + 1) (.array right) := by
  rw [normalize_array_children_frame, normalize_array_children_frame, hlen]
  have hframes := congrArg frameTokenChunks hchildren
  rw [hframes]

theorem normalize_rawTwoKeyObject_eq_of_children_eq {fuel : Nat}
    {key₁ key₂ : String}
    (hkeys : key₁ ≠ key₂)
    (h₁₂ : natListLe (stringCodes key₁) (stringCodes key₂) = true)
    (h₂₁ : natListLe (stringCodes key₂) (stringCodes key₁) = false)
    {left₁ left₂ right₁ right₂ : RawJson}
    (h₁ : normalizeRawJsonFuel fuel left₁ = normalizeRawJsonFuel fuel right₁)
    (h₂ : normalizeRawJsonFuel fuel left₂ = normalizeRawJsonFuel fuel right₂)
    {leftReverse rightReverse : Bool} :
    normalizeRawJsonFuel (fuel + 1)
      (rawJsonTwoKeyObject key₁ key₂ leftReverse left₁ left₂) =
    normalizeRawJsonFuel (fuel + 1)
      (rawJsonTwoKeyObject key₁ key₂ rightReverse right₁ right₂) := by
  cases leftReverse <;> cases rightReverse <;>
    simp [rawJsonTwoKeyObject, normalizeRawJsonFuel,
      sortTokenFields_pair_ordered h₁₂ h₂₁,
      sortTokenFields_pair_reversed h₁₂ h₂₁, h₁, h₂]

theorem rawJsonObjectKeyExtEq_selectedTag_iff {left right : Option String} :
    rawJsonObjectKeyExtEq (selectedTagRaw left) (selectedTagRaw right) ↔
      left = right := by
  cases left with
  | none =>
      cases right with
      | none =>
          constructor
          · intro _; rfl
          · intro _; exact rawJsonObjectKeyExtEq.null
      | some right =>
          constructor
          · intro h; cases h
          · intro h; cases h
  | some left =>
      cases right with
      | none =>
          constructor
          · intro h; cases h
          · intro h; cases h
      | some right =>
          constructor
          · intro h
            have hs : rawJsonObjectKeyExtEq (.string left) (.string right) := by
              simpa [selectedTagRaw] using h
            exact congrArg some (rawJsonObjectKeyExtEq_string_iff.mp hs)
          · intro h
            cases h
            exact rawJsonObjectKeyExtEq.string left

theorem rawSelectedGraph_relation_iff (left right : SelectedRawGraph) :
    rawJsonObjectKeyExtEq (rawSelectedGraph left) (rawSelectedGraph right) ↔
      left.edges = right.edges ∧ left.tag = right.tag := by
  unfold rawSelectedGraph
  rw [rawJsonObjectKeyExtEq_twoKeyObject_iff (by decide)]
  exact and_congr rawJsonObjectKeyExtEq_stringArray_iff
    rawJsonObjectKeyExtEq_selectedTag_iff

theorem rawSelectedFraction_relation_iff
    (left right : SelectedRawFraction) :
    rawJsonObjectKeyExtEq (rawSelectedFraction left) (rawSelectedFraction right) ↔
      left.numerator = right.numerator ∧ left.denominator = right.denominator := by
  unfold rawSelectedFraction
  rw [rawJsonObjectKeyExtEq_twoKeyObject_iff (by decide)]
  simp [rawSelectedFraction, rawJsonObjectKeyExtEq_integer_iff]

theorem rawJsonObjectKeyExtEq_twoGraphArray_iff
    {leftFirst leftSecond rightFirst rightSecond : RawJson} :
    rawJsonObjectKeyExtEq (.array [leftFirst, leftSecond])
      (.array [rightFirst, rightSecond]) ↔
      rawJsonObjectKeyExtEq leftFirst rightFirst ∧
        rawJsonObjectKeyExtEq leftSecond rightSecond := by
  constructor
  · intro h
    cases h with
    | array _ hitems =>
        have hfirst := hitems 0 (by simp)
        have hsecond := hitems 1 (by simp)
        simpa using And.intro hfirst hsecond
  · rintro ⟨hfirst, hsecond⟩
    apply rawJsonObjectKeyExtEq.array (by simp)
    intro index hindex
    have hindex' : index < 2 := by simpa using hindex
    have hi : index = 0 ∨ index = 1 := by omega
    rcases hi with hi | hi
    · subst index
      simpa using hfirst
    · subst index
      simpa using hsecond

theorem rawSelectedRow_relation_iff (left right : SelectedRawRow) :
    rawJsonObjectKeyExtEq (rawSelectedRow left) (rawSelectedRow right) ↔
      (rawJsonObjectKeyExtEq (rawSelectedGraph left.firstGraph)
          (rawSelectedGraph right.firstGraph) ∧
       rawJsonObjectKeyExtEq (rawSelectedGraph left.secondGraph)
          (rawSelectedGraph right.secondGraph)) ∧
      rawJsonObjectKeyExtEq (rawSelectedFraction left.coefficient)
        (rawSelectedFraction right.coefficient) := by
  unfold rawSelectedRow
  rw [rawJsonObjectKeyExtEq_twoKeyObject_iff (by decide),
    rawJsonObjectKeyExtEq_twoGraphArray_iff]

theorem normalize_rawSelectedGraph_eq_iff (left right : SelectedRawGraph) :
    normalizeRawJsonFuel 29 (rawSelectedGraph left) =
      normalizeRawJsonFuel 29 (rawSelectedGraph right) ↔
      rawJsonObjectKeyExtEq (rawSelectedGraph left) (rawSelectedGraph right) := by
  rw [rawSelectedGraph_relation_iff]
  constructor
  · intro h
    have hparts := normalize_rawGraphObject_children_eq (fuel := 28) h
    exact ⟨(normalize_rawEdgeArray_eq_iff (fuel := 27)).mp hparts.1,
      (normalize_selectedTag_eq_iff (fuel := 28) (by omega)).mp hparts.2⟩
  · rintro ⟨hedges, htag⟩
    exact normalize_rawTwoKeyObject_eq_of_children_eq
      (fuel := 28) (key₁ := "edges") (key₂ := "tag")
      (by decide) (by decide) (by decide)
      ((normalize_rawEdgeArray_eq_iff (fuel := 27)).mpr hedges)
      ((normalize_selectedTag_eq_iff (fuel := 28) (by omega)).mpr htag)

theorem normalize_rawSelectedFraction_eq_iff (left right : SelectedRawFraction) :
    normalizeRawJsonFuel 30 (rawSelectedFraction left) =
      normalizeRawJsonFuel 30 (rawSelectedFraction right) ↔
      rawJsonObjectKeyExtEq (rawSelectedFraction left) (rawSelectedFraction right) := by
  rw [rawSelectedFraction_relation_iff]
  constructor
  · intro h
    have hparts := normalize_rawFractionObject_children_eq (fuel := 29) h
    exact ⟨normalizeRawJsonFuel_integer_injective hparts.1,
      normalizeRawJsonFuel_integer_injective hparts.2⟩
  · rintro ⟨hnum, hden⟩
    cases hL : left.reverseFields <;> cases hR : right.reverseFields
    all_goals
      have hswap := normalize_rawTwoKeyObject_eq_of_children_eq
        (fuel := 29) (key₁ := "denominator") (key₂ := "numerator")
        (by decide) (by decide) (by decide)
        (by simpa using congrArg (fun n : Int => normalizeRawJsonFuel 29 (.integer n)) hden)
        (by simpa using congrArg (fun n : Int => normalizeRawJsonFuel 29 (.integer n)) hnum)
        (leftReverse := !left.reverseFields) (rightReverse := !right.reverseFields)
      simpa [rawSelectedFraction, rawJsonTwoKeyObject, hL, hR] using hswap

theorem normalize_rawSelectedRow_eq_iff (left right : SelectedRawRow) :
    normalizeRawJsonFuel 31 (rawSelectedRow left) =
      normalizeRawJsonFuel 31 (rawSelectedRow right) ↔
      rawJsonObjectKeyExtEq (rawSelectedRow left) (rawSelectedRow right) := by
  rw [rawSelectedRow_relation_iff]
  constructor
  · intro h
    have hparts :
        normalizeRawJsonFuel 30
            (.array [rawSelectedGraph left.firstGraph, rawSelectedGraph left.secondGraph]) =
          normalizeRawJsonFuel 30
            (.array [rawSelectedGraph right.firstGraph, rawSelectedGraph right.secondGraph]) ∧
        normalizeRawJsonFuel 30 (rawSelectedFraction left.coefficient) =
          normalizeRawJsonFuel 30 (rawSelectedFraction right.coefficient) := by
      simpa [rawSelectedRow] using normalize_rawRowObject_children_eq (fuel := 30) h
    have hgraphs := normalize_array_encoding_children_eq (fuel := 29) hparts.1
    have hgraphMap :
        [normalizeRawJsonFuel 29 (rawSelectedGraph left.firstGraph),
         normalizeRawJsonFuel 29 (rawSelectedGraph left.secondGraph)] =
        [normalizeRawJsonFuel 29 (rawSelectedGraph right.firstGraph),
         normalizeRawJsonFuel 29 (rawSelectedGraph right.secondGraph)] := by
      simpa using hgraphs.2
    rcases List.cons.inj hgraphMap with ⟨hfirst, htail⟩
    rcases List.cons.inj htail with ⟨hsecond, _⟩
    exact ⟨⟨(normalize_rawSelectedGraph_eq_iff _ _).mp hfirst,
      (normalize_rawSelectedGraph_eq_iff _ _).mp hsecond⟩,
      (normalize_rawSelectedFraction_eq_iff _ _).mp hparts.2⟩
  · rintro ⟨⟨hfirst, hsecond⟩, hcoefficient⟩
    have hgraphs :
        normalizeRawJsonFuel 29 (rawSelectedGraph left.firstGraph) =
          normalizeRawJsonFuel 29 (rawSelectedGraph right.firstGraph) ∧
        normalizeRawJsonFuel 29 (rawSelectedGraph left.secondGraph) =
          normalizeRawJsonFuel 29 (rawSelectedGraph right.secondGraph) :=
      ⟨(normalize_rawSelectedGraph_eq_iff _ _).mpr hfirst,
       (normalize_rawSelectedGraph_eq_iff _ _).mpr hsecond⟩
    have hatoms :
        normalizeRawJsonFuel 30
            (.array [rawSelectedGraph left.firstGraph, rawSelectedGraph left.secondGraph]) =
          normalizeRawJsonFuel 30
            (.array [rawSelectedGraph right.firstGraph, rawSelectedGraph right.secondGraph]) := by
      apply normalize_array_eq_of_children_eq (fuel := 29) (by simp)
      simpa using hgraphs
    have hfrac := (normalize_rawSelectedFraction_eq_iff _ _).mpr hcoefficient
    have hrow := normalize_rawTwoKeyObject_eq_of_children_eq
      (fuel := 30) (key₁ := "atoms") (key₂ := "coefficient")
      (by decide) (by decide) (by decide) hatoms hfrac
      (leftReverse := left.reverseFields) (rightReverse := right.reverseFields)
    simpa [rawSelectedRow] using hrow

theorem selectedRawRows_encoding_iff_recursiveEquality
    (left right : List SelectedRawRow) :
    normalizeRawJson (rawSelectedRows left) =
      normalizeRawJson (rawSelectedRows right) ↔
    rawJsonObjectKeyExtEq (rawSelectedRows left) (rawSelectedRows right) := by
  change normalizeRawJsonFuel 32 (.array (left.map rawSelectedRow)) =
      normalizeRawJsonFuel 32 (.array (right.map rawSelectedRow)) ↔ _
  constructor
  · intro h
    have hchildren := normalize_array_encoding_children_eq (fuel := 31) h
    have hrowmap :
        (left.map rawSelectedRow).map (normalizeRawJsonFuel 31) =
          (right.map rawSelectedRow).map (normalizeRawJsonFuel 31) := by
      simpa [List.map_map, Function.comp_def] using hchildren.2
    have hlen : left.length = right.length := by
      simpa only [List.length_map] using hchildren.1
    have harray :
        rawJsonObjectKeyExtEq (.array (left.map rawSelectedRow))
          (.array (right.map rawSelectedRow)) := by
      apply rawJsonObjectKeyExtEq.array (by
        simpa only [List.length_map] using hlen)
      intro index hleft
      have hleft' : index < left.length := by simpa only [List.length_map] using hleft
      have hright' : index < right.length := by rw [← hlen]; exact hleft'
      have hindex := congrArg (fun rows : List (List Nat) => rows[index]?) hrowmap
      simp only [List.getElem?_map,
        List.getElem?_eq_getElem hleft', List.getElem?_eq_getElem hright'] at hindex
      have hvalue := Option.some.inj hindex
      have hnorm : normalizeRawJsonFuel 31 (rawSelectedRow (left[index]'hleft')) =
          normalizeRawJsonFuel 31 (rawSelectedRow (right[index]'hright')) := by
        simpa only [List.getElem_map] using hvalue
      have hrowrel := (normalize_rawSelectedRow_eq_iff _ _).mp hnorm
      simpa only [List.get_eq_getElem, List.getElem_map] using hrowrel
    simpa [rawSelectedRows] using harray
  · intro h
    have harray :
        rawJsonObjectKeyExtEq (.array (left.map rawSelectedRow))
          (.array (right.map rawSelectedRow)) := by
      simpa [rawSelectedRows] using h
    cases harray with
    | array hlen hitems =>
        have hrowmap :
            (left.map rawSelectedRow).map (normalizeRawJsonFuel 31) =
              (right.map rawSelectedRow).map (normalizeRawJsonFuel 31) := by
          apply List.ext_getElem (by simpa [List.length_map] using hlen)
          intro index hleft hright
          have hleft' : index < left.length := by simpa only [List.length_map] using hleft
          have hright' : index < right.length := by simpa only [List.length_map] using hright
          have hrel := hitems index (by simpa only [List.length_map] using hleft)
          have hrowrel : rawJsonObjectKeyExtEq
              (rawSelectedRow (left[index]'hleft'))
              (rawSelectedRow (right[index]'hright')) := by
            simpa only [List.get_eq_getElem, List.getElem_map] using hrel
          have hnorm := (normalize_rawSelectedRow_eq_iff _ _).mpr hrowrel
          simpa only [List.getElem_map] using hnorm
        exact normalize_array_eq_of_children_eq (fuel := 31)
          (by simpa [List.length_map] using hlen) hrowmap

/- Fuel-indexed shallow-shape predicate. At fuel zero only scalars are
   safe; each array/object layer consumes one unit, independently of
   collection length. This definition is shared with the statement-trace
   layer so the equality domain is available at its introduction point. -/
def rawJsonWithinFuel : Nat → RawJson → Bool
  | 0, .null => true
  | 0, .boolean _ => true
  | 0, .integer _ => true
  | 0, .nonIntegerNumber _ => true
  | 0, .string _ => true
  | 0, .array _ => false
  | 0, .object _ => false
  | _ + 1, .null => true
  | _ + 1, .boolean _ => true
  | _ + 1, .integer _ => true
  | _ + 1, .nonIntegerNumber _ => true
  | _ + 1, .string _ => true
  | fuel + 1, .array values => values.all (rawJsonWithinFuel fuel)
  | fuel + 1, .object fields =>
      fields.all (fun field => rawJsonWithinFuel fuel field.2)

/-- Check pairwise distinct keys recursively through the declared
32-level comparison domain. The equality relation also requires fuel safety,
so no unchecked object node can lie beyond this predicate's recursion. -/
def rawJsonUniqueObjectKeysFuel : Nat → RawJson → Bool
  | 0, _ => true
  | fuel + 1, .array values =>
      values.all (rawJsonUniqueObjectKeysFuel fuel)
  | fuel + 1, .object fields =>
      distinctObjectKeys fields &&
        fields.all (fun field => rawJsonUniqueObjectKeysFuel fuel field.2)
  | fuel + 1, _ => true

def rawJsonUniqueObjectKeys (value : RawJson) : Bool :=
  rawJsonUniqueObjectKeysFuel 32 value

/-- The bounded equality relation is restricted to unique-key values with
no array/object truncation at normalization fuel 32. -/
def rawJsonEquivalent (left right : RawJson) : Prop :=
  rawJsonWithinFuel 32 left = true ∧
  rawJsonWithinFuel 32 right = true ∧
  rawJsonUniqueObjectKeys left = true ∧
  rawJsonUniqueObjectKeys right = true ∧
  normalizeRawJson left = normalizeRawJson right

/-- On the selected raw row-array carrier, the bounded token guard agrees in
both directions with recursive array/order and object/key equality. The fuel
and unique-key facts are explicit premises for later serializer/admission
trace refinements. The raw fraction numerator and denominator are preserved
independently; this theorem does not quotient them by decoded rational value. -/
theorem selectedRawRows_rawJsonEquivalent_iff_recursiveEquality
    (left right : List SelectedRawRow)
    (leftFuel : rawJsonWithinFuel 32 (rawSelectedRows left) = true)
    (rightFuel : rawJsonWithinFuel 32 (rawSelectedRows right) = true)
    (leftUnique : rawJsonUniqueObjectKeys (rawSelectedRows left) = true)
    (rightUnique : rawJsonUniqueObjectKeys (rawSelectedRows right) = true) :
    rawJsonEquivalent (rawSelectedRows left) (rawSelectedRows right) ↔
      rawJsonObjectKeyExtEq (rawSelectedRows left) (rawSelectedRows right) := by
  unfold rawJsonEquivalent
  simp only [leftFuel, rightFuel, leftUnique, rightUnique, true_and]
  exact selectedRawRows_encoding_iff_recursiveEquality left right

/-- Test fixture nesting a JSON value under an exact number of arrays. -/
def nestRawArrays : Nat → RawJson → RawJson
  | 0, value => value
  | fuel + 1, value => .array [nestRawArrays fuel value]

/-- At depth 33, child length framing still cannot recover a scalar below the
fuel boundary: both children normalize to the same `[99]` token. The bounded
equality relation rejects both values because they exceed its no-truncation
domain. -/
theorem unrestricted_normalization_collapses_beyond_bound :
    normalizeRawJsonFuel 32 (nestRawArrays 33 (.integer 1)) =
      normalizeRawJsonFuel 32 (nestRawArrays 33 (.integer 2)) ∧
    ¬ rawJsonEquivalent (nestRawArrays 33 (.integer 1))
      (nestRawArrays 33 (.integer 2)) := by
  constructor
  · decide
  · intro h
    have hunsafe :
        rawJsonWithinFuel 32 (nestRawArrays 33 (.integer 1)) = false := by
      decide
    have hleft := h.1
    rw [hunsafe] at hleft
    contradiction

def rawObjectForward : RawJson :=
  .object [("atoms", .integer 7), ("coefficient", .integer 11)]

def rawObjectReordered : RawJson :=
  .object [("coefficient", .integer 11), ("atoms", .integer 7)]

theorem rawObjectKeyExtEq_reordered_example :
    rawJsonObjectKeyExtEq rawObjectForward rawObjectReordered := by
  apply rawJsonObjectKeyExtEq.object
  · intro key
    simpa [rawObjectForward, rawObjectReordered] using
      (or_comm : (key = "atoms" ∨ key = "coefficient") ↔
        (key = "coefficient" ∨ key = "atoms"))
  · intro key leftValue rightValue hleft hright
    by_cases hAtoms : ("atoms" == key)
    · have hk : key = "atoms" := ((beq_iff_eq).mp hAtoms).symm
      subst key
      simp [lookupField, rawObjectForward, rawObjectReordered] at hleft hright
      cases hleft
      cases hright
      exact rawJsonObjectKeyExtEq.integer 7
    · by_cases hCoefficient : ("coefficient" == key)
      · have hk : key = "coefficient" := ((beq_iff_eq).mp hCoefficient).symm
        subst key
        simp [lookupField, rawObjectForward, rawObjectReordered] at hleft hright
        cases hleft
        cases hright
        exact rawJsonObjectKeyExtEq.integer 11
      · simp [lookupField, rawObjectForward, hAtoms, hCoefficient] at hleft

theorem raw_object_key_order_is_extensional :
    rawJsonEquivalent rawObjectForward rawObjectReordered  := by
  unfold rawJsonEquivalent rawJsonUniqueObjectKeys
  decide

theorem raw_array_order_remains_significant :
    ¬ rawJsonEquivalent (.array [.integer 1, .integer 2])
      (.array [.integer 2, .integer 1])  := by
  unfold rawJsonEquivalent rawJsonUniqueObjectKeys
  decide

/-- Array normalization now explicitly records each child's token length.
This is a semantic change from the earlier unframed `flatMap` encoding. -/
theorem array_children_are_length_framed :
    normalizeRawJsonFuel 1 (.array [.integer 1, .integer 2]) =
      [5, 2, 3, 2, 0, 1, 3, 2, 0, 2] := by
  decide

theorem raw_null_and_empty_string_remain_distinct :
    ¬ rawJsonEquivalent .null (.string "")  := by
  unfold rawJsonEquivalent rawJsonUniqueObjectKeys
  decide

theorem raw_fraction_pairs_remain_exact :
    ¬ rawJsonEquivalent
      (.object [("numerator", .integer 2), ("denominator", .integer 4)])
      (.object [("numerator", .integer 1), ("denominator", .integer 2)])  := by
  unfold rawJsonEquivalent rawJsonUniqueObjectKeys
  decide

theorem duplicate_object_multiplicity_remains_distinct :
    ¬ rawJsonEquivalent
      (.object [("k", .integer 1), ("k", .integer 1)])
      (.object [("k", .integer 1)])  := by
  unfold rawJsonEquivalent rawJsonUniqueObjectKeys
  decide

theorem rawJsonEquivalent_symmetric {left right : RawJson}
    (h : rawJsonEquivalent left right) : rawJsonEquivalent right left :=
  ⟨h.2.1, h.1, h.2.2.2.1, h.2.2.1, h.2.2.2.2.symm⟩

theorem rawJsonEquivalent_trans {left middle right : RawJson}
    (h₁ : rawJsonEquivalent left middle)
    (h₂ : rawJsonEquivalent middle right) :
    rawJsonEquivalent left right :=
  ⟨h₁.1, h₂.2.1, h₁.2.2.1, h₂.2.2.2.1, h₁.2.2.2.2.trans h₂.2.2.2.2⟩

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
