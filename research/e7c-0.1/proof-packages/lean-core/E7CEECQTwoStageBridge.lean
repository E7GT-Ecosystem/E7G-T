import E7CB2Sequence

/- Finite encoded source/IR observations. No general Python/Lean refinement. -/
namespace E7CEECQTwoStageBridge

theorem vector_success :
    E7CB2Sequence.sequence 20 ({ exit := .success 0, steps := 3, ledger := [8, 0, 2, 4] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .success 2, steps := 2, ledger := [9, 5, 7] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .success 2, steps := 7, ledger := [8, 0, 2, 4, 9, 5, 7] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_same_marginals_alternative :
    E7CB2Sequence.sequence 20 ({ exit := .success 1, steps := 3, ledger := [8, 1, 2, 3] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .success 3, steps := 2, ledger := [9, 5, 6] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .success 3, steps := 7, ledger := [8, 1, 2, 3, 9, 5, 6] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_first_unsupported :
    E7CB2Sequence.sequence 20 ({ exit := .unsupported 0, steps := 0, ledger := [8] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .resourceLimit, steps := 0, ledger := [] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .unsupported 0, steps := 1, ledger := [8] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_second_unsupported :
    E7CB2Sequence.sequence 20 ({ exit := .success 0, steps := 3, ledger := [8, 0, 2, 4] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .unsupported 2, steps := 0, ledger := [9] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .unsupported 2, steps := 5, ledger := [8, 0, 2, 4, 9] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_second_undetermined :
    E7CB2Sequence.sequence 20 ({ exit := .success 0, steps := 3, ledger := [8, 0, 2, 4] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .undetermined 1, steps := 0, ledger := [9] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .undetermined 1, steps := 5, ledger := [8, 0, 2, 4, 9] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_zero_bound :
    E7CB2Sequence.sequence 0 ({ exit := .resourceLimit, steps := 0, ledger := [] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .resourceLimit, steps := 0, ledger := [] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .resourceLimit, steps := 0, ledger := [] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_first_resource_limit :
    E7CB2Sequence.sequence 2 ({ exit := .resourceLimit, steps := 1, ledger := [8, 0] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .resourceLimit, steps := 0, ledger := [] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .resourceLimit, steps := 2, ledger := [8, 0] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_second_pre_step_limit :
    E7CB2Sequence.sequence 4 ({ exit := .success 0, steps := 3, ledger := [8, 0, 2, 4] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .resourceLimit, steps := 0, ledger := [] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .resourceLimit, steps := 4, ledger := [8, 0, 2, 4] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_second_row_limit :
    E7CB2Sequence.sequence 6 ({ exit := .success 0, steps := 3, ledger := [8, 0, 2, 4] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .resourceLimit, steps := 1, ledger := [9, 5] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .resourceLimit, steps := 6, ledger := [8, 0, 2, 4, 9, 5] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_second_ledger_limit :
    E7CB2Sequence.sequence 20 ({ exit := .success 0, steps := 3, ledger := [8, 0, 2, 4] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .resourceLimit, steps := 0, ledger := [] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .resourceLimit, steps := 5, ledger := [8, 0, 2, 4] } : E7CB2Sequence.Trace Nat) := by decide

end E7CEECQTwoStageBridge
