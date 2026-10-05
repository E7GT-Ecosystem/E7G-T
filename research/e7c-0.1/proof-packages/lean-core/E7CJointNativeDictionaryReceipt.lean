import E7CJointNativeDictionaryTrace
import E7CJointRawJsonAdmission

/-!
Decode the dictionary-transition portion of the finite CPython capture packet
into the Lean event relation. This proves that any accepted decoded packet
matches the abstract dictionary step at each listed row. It does not prove
that a profiler callback faithfully denotes CPython execution, nor that a
JSON parser produced the RawJson value supplied here.
-/
namespace E7CJointNativeDictionaryReceipt
open E7CEECQTwoStageAllInput
open E7CEECQTwoStageExactCodec
open E7CJointAdmissionExecution
open E7CJointAdmissionPythonOperations
open E7CJointNativeDictionaryTrace
open E7CJointRawJsonAdmission

def nativeFraction (raw : RawJson) : Option Rat :=
  match raw with
  | .object fields => do
      guard (exactKeys fields ["fraction"])
      let rawPair ← lookupField fields "fraction"
      match rawPair with
      | .array [.integer numerator, .integer denominator] =>
          if decide (denominator > 0) then
            pure ((numerator : Rat) / (denominator : Rat))
          else none
      | _ => none
  | _ => none

def nativeConfig (raw : RawJson) : Option Graph :=
  match raw with
  | .object fields => do
      guard (exactKeys fields ["config"])
      let rawConfig ← lookupField fields "config"
      let wire ← decodeGraph rawConfig
      pure (toGraph wire)
  | _ => none

def nativeJointKey (raw : RawJson) : Option JointKey :=
  match raw with
  | .object fields => do
      guard (exactKeys fields ["tuple"])
      let rawPair ← lookupField fields "tuple"
      match rawPair with
      | .array [left, right] => do
          let leftGraph ← nativeConfig left
          let rightGraph ← nativeConfig right
          pure (leftGraph, rightGraph)
      | _ => none
  | _ => none

def nativeRow (raw : RawJson) : Option Row :=
  match raw with
  | .object fields => do
      guard (exactKeys fields ["coefficient", "key"])
      let rawCoefficient ← lookupField fields "coefficient"
      let rawKey ← lookupField fields "key"
      let coefficient ← nativeFraction rawCoefficient
      let key ← nativeJointKey rawKey
      pure ⟨key.1, key.2, coefficient⟩
  | _ => none

def nativeEntry (raw : RawJson) : Option JointEntry :=
  match raw with
  | .object fields => do
      guard (exactKeys fields ["key", "coefficient"])
      let rawKey ← lookupField fields "key"
      let rawCoefficient ← lookupField fields "coefficient"
      let key ← nativeJointKey rawKey
      let coefficient ← nativeFraction rawCoefficient
      pure ⟨key, coefficient⟩
  | _ => none

def nativeEntries (raw : RawJson) : Option (List JointEntry) :=
  match raw with
  | .array entries => entries.mapM nativeEntry
  | _ => none

structure DecodedNativeTransition (ops : CPythonJointPrimitives) where
  index : Nat
  before : List JointEntry
  row : Row
  lookupResult : Rat
  additionResult : Rat
  after : List JointEntry
  dictGetObserved : Bool
  refines : JointDictionaryRowEvent ops before row after

def nativeNat (raw : RawJson) : Option Nat :=
  match exactInteger raw with
  | some value => if decide (value ≥ 0) then some value.toNat else none
  | none => none

def decodeNativeTransition (ops : CPythonJointPrimitives)
    (raw : RawJson) : Option (DecodedNativeTransition ops) := do
  let fields ← match raw with
    | .object fields => some fields
    | _ => none
  guard (exactKeys fields
    ["site", "index", "row", "before", "lookup_result",
     "addition_result", "dict_get_call", "after"])
  let site ← lookupField fields "site"
  guard (match site with
    | .string name => name == "dictionary-transition"
    | _ => false)
  let rawIndex ← lookupField fields "index"
  let index ← nativeNat rawIndex
  let rawRow ← lookupField fields "row"
  let row ← nativeRow rawRow
  let rawBefore ← lookupField fields "before"
  let before ← nativeEntries rawBefore
  let rawLookup ← lookupField fields "lookup_result"
  let lookupResult ← nativeFraction rawLookup
  let rawAddition ← lookupField fields "addition_result"
  let additionResult ← nativeFraction rawAddition
  let rawGetObserved ← lookupField fields "dict_get_call"
  let dictGetObserved ← match rawGetObserved with
    | .boolean value => some value
    | _ => none
  guard dictGetObserved
  let rawAfter ← lookupField fields "after"
  let after ← nativeEntries rawAfter
  if hLookup : lookupResult = dictLookup ops.keyEqual before (rowKey row) then
    if hAdd : additionResult = ops.add lookupResult row.coefficient then
      if hUpdate : after = dictSet ops.keyEqual before (rowKey row) additionResult then
        some {
          index := index
          before := before
          row := row
          lookupResult := lookupResult
          additionResult := additionResult
          after := after
          dictGetObserved := dictGetObserved
          refines := ⟨lookupResult, additionResult, hLookup, hAdd, hUpdate⟩
        }
      else none
    else none
  else none

def decodeNativeTransitionTrace (ops : CPythonJointPrimitives) :
    (expected : Nat) → (initial : List JointEntry) → (events : List RawJson) →
      Option (Σ rows : List Row, Σ final : List JointEntry,
        JointDictionaryEventTrace ops rows initial final)
  | _, initial, [] => some ⟨[], initial, .nil initial⟩
  | expected, initial, raw :: rest => do
      let event ← decodeNativeTransition ops raw
      if hIndex : event.index = expected then
        if hBefore : event.before = initial then
          match decodeNativeTransitionTrace ops (expected + 1) event.after rest with
          | some ⟨rows, final, tail⟩ =>
              let eventRefines :
                  JointDictionaryRowEvent ops initial event.row event.after := by
                cases hBefore
                exact event.refines
              some ⟨event.row :: rows, final,
                .cons event.row rows initial event.after final eventRefines tail⟩
          | none => none
        else none
      else none

def decodeNativeDictionaryPacket (ops : CPythonJointPrimitives)
    (packet : RawJson) :
      Option (Σ rows : List Row, Σ final : List JointEntry,
        JointDictionaryEventTrace ops rows [] final) := do
  let fields ← match packet with
    | .object fields => some fields
    | _ => none
  guard (exactKeys fields
    ["edition", "python", "input", "events", "dictionary_transitions",
     "returned", "adequacy"])
  let rawEdition ← lookupField fields "edition"
  guard (match rawEdition with
    | .string edition => edition == "E7C-native-joint-dictionary-trace/0.2-provisional"
    | _ => false)
  let rawTransitions ← lookupField fields "dictionary_transitions"
  match rawTransitions with
  | .array transitions => decodeNativeTransitionTrace ops 0 [] transitions
  | _ => none

def exactJointPrimitives : CPythonJointPrimitives where
  keyEqual := fun left right => decide (left = right)
  add := fun left right => left + right
  isZero := fun value => decide (value = 0)
  keyEqualityRefines := by intro left right; rfl
  additionRefines := by intro left right; rfl
  truthTestRefines := by intro value; rfl

theorem nativeFraction_rejects_boolean_numerator :
    nativeFraction (.object [("fraction", .array [.boolean true, .integer 2])]) =
      none := by
  decide

theorem nativeConfig_rejects_noncanonical_edges :
    nativeConfig (.object [("config", .object
      [("edges", .array [.string "AC", .string "AB"]), ("tag", .null)])]) =
      none := by
  decide

theorem nativeConfig_preserves_null_vs_empty_tag :
    nativeConfig (.object [("config", .object
      [("edges", .array []), ("tag", .null)])]) ≠
    nativeConfig (.object [("config", .object
      [("edges", .array []), ("tag", .string "")])]) := by
  decide

theorem nativeFraction_normalizes_exact_pair :
    nativeFraction (.object [("fraction", .array [.integer 2, .integer 4])]) =
      some ((1 : Rat) / 2) := by
  decide

theorem acceptedPacket_has_modelled_final_dictionary
    {packet : RawJson} {rows : List Row} {final : List JointEntry}
    {trace : JointDictionaryEventTrace exactJointPrimitives rows [] final}
    (accepted : decodeNativeDictionaryPacket exactJointPrimitives packet =
      some ⟨rows, final, trace⟩) :
    final = jointDictRun exactJointPrimitives rows [] := by
  exact eventTrace_final_is_run trace

end E7CJointNativeDictionaryReceipt
