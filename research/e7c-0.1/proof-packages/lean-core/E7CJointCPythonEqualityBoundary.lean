import E7CJointRawJsonAdmission

/-
A normal-return correspondence audit for the exact pinned admit path.
This increment records the Python-object equality boundary encountered when
trying to derive #146's structural RawJson equality from the running helper.
-/
namespace E7CJointCPythonEqualityBoundary

open E7CJointRawJsonAdmission

/- Exact source pins at base commit 0b14219...; normalized AST digests are
   also enforced by e7c_joint_first_helper_sites.checked_sites. -/
def pinnedAdmissionFileBlob : String := "8937d64dbc2ec4fc71884073dac50904dd016ff6"
def pinnedJointAdapterFileBlob : String := "58092143cbbd6d13cedae7bcaca0b08c5f673811"
def pinnedGraphAdapterFileBlob : String := "3f10f9cb8b0edf027a552dbc336634438d9dbeba"
def pinnedCanonicalFileBlob : String := "9be6966af22d6fd1f381e724f82adb34ef12014d"
def pinnedAdmissionAst : String := "02686f71546ef8d328c32e5321a7eec0d08628b50281cdbc7ebc4b4ee9900408"
def pinnedRowsAst : String := "d398cd44f71be111bfb0598805813a89d445ad09c2eb6fe3b2c3e535a8ab68a0"
def pinnedRowAst : String := "93d2971bdcf3796b7e688cd1ccff45a3d4ed7934b9b7ef9d1c22cdd7b28d386f"
def pinnedGraphAst : String := "e24060d0457a10f3cf155f49966203d9eb1a4e658417fc739f243d78daa1d295"
def pinnedJointAst : String := "895a144ef2ed8c98c6c436cee9c4591cc07bb7a68d2e7cb9ff69a89f2100231f"
def pinnedJointConstructorAst : String := "bf054e3ee0a2271a49a122b1350a54afc8a9f77685f81796cc93fe19e0778b27"
def pinnedConfigConstructorAst : String := "ba7d6085689cebeaffb4a5d46dbf5a15c09e405c54e34f4e97381178ee967d65"
def pinnedConfigIdentityAst : String := "226291c923dd5694adb2898c8fde025d2f3d4cda7e51048cbd1c32452c7a6133"
def pinnedCanonicalJsonGuardAst : String := "201c5a74316b65b26508d120ed3801a15b9bb3d0dfbe8e02b25181ac9342405d"

/- Python dictionary equality compares key/value mappings; insertion order is
   not part of equality. This finite integer-valued fragment is enough to
   check whether #146's ordered RawJson object representation can stand for
   that primitive operation. -/
def lookupIntField : List (String × Int) → String → Option Int
  | [], _ => none
  | (key, value) :: rest, wanted =>
      if key == wanted then some value else lookupIntField rest wanted

def pythonDictEqIntFields (left right : List (String × Int)) : Bool :=
  (left.length == right.length) &&
    left.all (fun (key, value) => lookupIntField right key == some value) &&
    right.all (fun (key, value) => lookupIntField left key == some value)

/- The list-backed AST comparison used by #146 is ordered at the object-field
   level. This function makes that representational equality explicit without
   requiring a DecidableEq instance for recursive RawJson. -/
def orderedIntFieldListsEqual : List (String × Int) → List (String × Int) → Bool
  | [], [] => true
  | (key, value) :: left, (key', value') :: right =>
      key == key' && value == value' && orderedIntFieldListsEqual left right
  | _, _ => false

def canonicalRowsObjectFields : List (String × Int) :=
  [("atoms", 7), ("coefficient", 11)]

def permutedRowsObjectFields : List (String × Int) :=
  [("coefficient", 11), ("atoms", 7)]

theorem python_dict_equality_ignores_row_object_key_order :
    pythonDictEqIntFields canonicalRowsObjectFields permutedRowsObjectFields = true := by
  decide

theorem rawjson_field_sequence_model_distinguishes_same_objects :
    orderedIntFieldListsEqual canonicalRowsObjectFields permutedRowsObjectFields = false := by
  decide

theorem normal_python_dict_equality_does_not_imply_rawjson_field_sequence_equality :
    pythonDictEqIntFields canonicalRowsObjectFields permutedRowsObjectFields = true ∧
    orderedIntFieldListsEqual canonicalRowsObjectFields permutedRowsObjectFields = false :=
  ⟨python_dict_equality_ignores_row_object_key_order,
    rawjson_field_sequence_model_distinguishes_same_objects⟩

/- An admitted normal execution of the pinned source may take the final
   fall-through branch when the two Python row lists compare equal as mappings.
   That fact alone cannot provide the ordered-field equality required by
   RawTypedNormalReturnTrace.rawRowsEqualityGuard. -/
theorem e146_structural_guard_is_stronger_than_python_mapping_equality :
    ¬ (pythonDictEqIntFields canonicalRowsObjectFields permutedRowsObjectFields = true →
       orderedIntFieldListsEqual canonicalRowsObjectFields permutedRowsObjectFields = true) := by
  intro implication
  have h := implication python_dict_equality_ignores_row_object_key_order
  rw [rawjson_field_sequence_model_distinguishes_same_objects] at h
  contradiction

end E7CJointCPythonEqualityBoundary
