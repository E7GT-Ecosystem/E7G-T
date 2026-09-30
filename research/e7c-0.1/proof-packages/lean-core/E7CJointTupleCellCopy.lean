import E7CJointGraphBytecodeSemantics

/- Selected exact-tuple fast-path copy loop from CPython 3.12.3/3.12.14.
This relation denotes cell reads, NewRef results and writes. It does not
establish that native C memory or the installed runtime supplies those steps. -/
namespace E7CJointTupleCellCopy
open E7CJointSerializerSourceSyntax E7CJointGraphBytecodeSyntax

/-- Logical non-null object identifiers, not machine addresses or C NULL. -/
abbrev Pointer := Nat

inductive Event where
  | read (index : Nat) (pointer : Pointer)
  | newRef (pointer : Pointer) (result : Pointer)
  | write (index : Nat) (pointer : Pointer)
  deriving DecidableEq, Repr

/-- The output is derived cell by cell, never supplied as a copy-result premise.
Indices denote the fresh destination, so both source and destination start at 0.
Allocation and the source/destination representation are outside this relation. -/
inductive CopyRun (newRef : Pointer → Option Pointer) :
    Nat → List Pointer → List Event → List Pointer → Prop where
  | nil (index) : CopyRun newRef index [] [] []
  | cons {index pointer result cells events output}
      (reference : newRef pointer = some result)
      (remaining : CopyRun newRef (index + 1) cells events output) :
      CopyRun newRef index (pointer :: cells)
        (.read index pointer :: .newRef pointer result ::
          .write index result :: events) (result :: output)

def cellPlan : Nat → List Pointer → List Event
  | _, [] => []
  | index, pointer :: rest =>
      .read index pointer :: .newRef pointer pointer ::
        .write index pointer :: cellPlan (index + 1) rest

/-- Operation-local pointer identity, not equality of completed lists. Native
Py_NewRef ownership/refcount and memory safety remain separate premises. -/
def RefIdentity (newRef : Pointer → Option Pointer) : Prop :=
  ∀ pointer, newRef pointer = some pointer

theorem copy_run_exact {newRef : Pointer → Option Pointer}
    (identity : RefIdentity newRef) {index cells events output}
    (run : CopyRun newRef index cells events output) :
    output = cells ∧ events = cellPlan index cells := by
  induction run with
  | nil index => exact ⟨rfl, rfl⟩
  | @cons index pointer result cells events output reference remaining ih =>
      have same : pointer = result :=
        Option.some.inj ((identity pointer).symm.trans reference)
      cases same
      rcases ih with ⟨hout, hevents⟩
      cases hout
      cases hevents
      exact ⟨rfl, rfl⟩

theorem copy_run_exists {newRef : Pointer → Option Pointer}
    (identity : RefIdentity newRef) (cells : List Pointer) (index : Nat) :
    CopyRun newRef index cells (cellPlan index cells) cells := by
  induction cells generalizing index with
  | nil => exact .nil index
  | cons pointer rest ih =>
      exact .cons (identity pointer) (ih (index + 1))

theorem plan_length (cells : List Pointer) (index : Nat) :
    (cellPlan index cells).length = 3 * cells.length := by
  induction cells generalizing index with
  | nil => rfl
  | cons pointer rest ih =>
      simp only [cellPlan, List.length_cons, ih, Nat.mul_add, Nat.mul_one] <;> omega

/-- Denotation uses one stable pointer interpretation for both containers.
Duplicate pointers, order and every cell's complete value are retained. -/
theorem copy_run_denotation {newRef : Pointer → Option Pointer}
    (identity : RefIdentity newRef) {index cells events output}
    (run : CopyRun newRef index cells events output)
    (denote : Pointer → Value) :
    output.map denote = copyTuple (cells.map denote) := by
  rw [(copy_run_exact identity run).1, copy_tuple_exact]

theorem changed_cells_rejected {newRef : Pointer → Option Pointer}
    (identity : RefIdentity newRef) {index cells events output}
    (changed : output ≠ cells) : ¬ CopyRun newRef index cells events output := by
  intro run
  exact changed (copy_run_exact identity run).1

example : CopyRun (fun pointer => some pointer) 0 [7, 7, 2]
    (cellPlan 0 [7, 7, 2]) [7, 7, 2] :=
  copy_run_exists (by intro; rfl) _ _

end E7CJointTupleCellCopy
