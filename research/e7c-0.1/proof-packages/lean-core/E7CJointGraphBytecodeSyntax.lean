import E7CJointSerializerSourceSyntax

/- Selected unspecialized CPython-3.12 instruction semantics. The compiler
image is checked separately. This is not a proof of CPython's dispatch engine,
adaptive opcodes, native attribute reads, allocation or exception behavior. -/
namespace E7CJointGraphBytecodeSyntax
open E7CJointSerializerSourceSyntax E7CJointRawJsonAdmission

inductive Instruction where
  | resume (whereFrom : Nat)
  | loadGlobal (name : String) (pushNull : Bool)
  | loadFast (index : Nat)
  | loadAttr (name : String)
  | call (arity : Nat)
  | loadKeys (names : List String)
  | buildConstKeyMap (count : Nat)
  | returnValue
  deriving DecidableEq, Repr

inductive Slot where
  | value (value : Value)
  | nullSentinel
  | listConstructor
  | keys (names : List String)

inductive State where
  | running (stack : List Slot)
  | returned (value : Value)

/-- Ordered tuple-cell visits and append to a fresh modeled list. Actual native
tuple iteration/list allocation following this loop remains an open link. -/
def copyTuple (cells : List Value) : List Value :=
  cells.foldl (fun allocated cell => allocated ++ [cell]) []

theorem copy_tuple_with_prefix (cells prefix : List Value) :
    cells.foldl (fun allocated cell => allocated ++ [cell]) prefix = prefix ++ cells := by
  induction cells generalizing prefix with
  | nil => simp
  | cons cell rest ih => simp [List.foldl_cons, ih, List.append_assoc]

theorem copy_tuple_exact (cells : List Value) : copyTuple cells = cells := by
  simpa [copyTuple] using copy_tuple_with_prefix cells []

/-- Stack is top first. Only the selected non-method CALL convention and
unique two-key object construction are supported. None is modeled rejection;
it is not a classification of a running Python failure or resource limit. -/
def step (read : Value → String → Option Value) (locals : List Value) :
    Instruction → List Slot → Option State
  | .resume 0, stack => some (.running stack)
  | .loadGlobal "list" true, stack =>
      some (.running (.listConstructor :: .nullSentinel :: stack))
  | .loadFast index, stack => do
      let value ← locals[index]?
      pure (.running (.value value :: stack))
  | .loadAttr name, .value base :: rest => do
      let value ← read base name
      pure (.running (.value value :: rest))
  | .call 1, .value (.sequence cells) :: .listConstructor :: .nullSentinel :: rest =>
      some (.running (.value (.sequence (copyTuple cells)) :: rest))
  | .loadKeys names, stack => some (.running (.keys names :: stack))
  | .buildConstKeyMap 2,
      .keys [firstKey, secondKey] :: .value second :: .value first :: rest => do
      if firstKey = secondKey then none else do
        let firstRaw ← toRaw first
        let secondRaw ← toRaw second
        pure (.running (.value (.data (.object
          [(firstKey, firstRaw), (secondKey, secondRaw)])) :: rest))
  | .returnValue, [.value value] => some (.returned value)
  | _, _ => none

/-- A return is accepted only as the final instruction with one value on the
stack. No bytecode instruction or completed result is silently skipped. -/
def execute (read : Value → String → Option Value) (locals : List Value) :
    List Instruction → List Slot → Option Value
  | [], _ => none
  | instruction :: rest, stack => do
      let state ← step read locals instruction stack
      match state with
      | .running next => execute read locals rest next
      | .returned value => if rest.isEmpty then some value else none

end E7CJointGraphBytecodeSyntax
