import E7CB2Sequence

/- Generated finite vectors from complete B2/B1/IR replay.
   Equality here is for the encoded abstract traces only. -/

namespace E7CB2FiniteBridge

theorem vector_success_strict :
    E7CB2Sequence.sequence 20 ({ exit := .success 0, steps := 2, ledger := [2] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .success 1, steps := 0, ledger := [0, 1] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .success 1, steps := 4, ledger := [2, 0, 1] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_success_total :
    E7CB2Sequence.sequence 20 ({ exit := .success 0, steps := 2, ledger := [2] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .success 0, steps := 0, ledger := [2] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .success 0, steps := 4, ledger := [2, 2] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_continuation_domain_error :
    E7CB2Sequence.sequence 20 ({ exit := .success 2, steps := 2, ledger := [2] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .domainError 4, steps := 0, ledger := [0, 1] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .domainError 4, steps := 4, ledger := [2, 0, 1] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_first_unsupported :
    E7CB2Sequence.sequence 20 ({ exit := .unsupported 3, steps := 2, ledger := [2] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .resourceLimit, steps := 0, ledger := [] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .unsupported 3, steps := 3, ledger := [2] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_first_undetermined :
    E7CB2Sequence.sequence 20 ({ exit := .undetermined 1, steps := 2, ledger := [2] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .resourceLimit, steps := 0, ledger := [] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .undetermined 1, steps := 3, ledger := [2] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_child_step_limit :
    E7CB2Sequence.sequence 2 ({ exit := .resourceLimit, steps := 1, ledger := [] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .resourceLimit, steps := 0, ledger := [] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .resourceLimit, steps := 2, ledger := [] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_continuation_step_limit :
    E7CB2Sequence.sequence 3 ({ exit := .success 0, steps := 2, ledger := [2] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .resourceLimit, steps := 0, ledger := [] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .resourceLimit, steps := 3, ledger := [2] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_zero_bound :
    E7CB2Sequence.sequence 0 ({ exit := .resourceLimit, steps := 0, ledger := [] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .resourceLimit, steps := 0, ledger := [] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .resourceLimit, steps := 0, ledger := [] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_first_ledger_limit :
    E7CB2Sequence.sequence 20 ({ exit := .resourceLimit, steps := 2, ledger := [] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .resourceLimit, steps := 0, ledger := [] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .resourceLimit, steps := 3, ledger := [] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_continuation_ledger_limit :
    E7CB2Sequence.sequence 20 ({ exit := .success 0, steps := 2, ledger := [2] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .resourceLimit, steps := 0, ledger := [] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .resourceLimit, steps := 4, ledger := [2] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_partiality_ledger_limit :
    E7CB2Sequence.sequence 20 ({ exit := .success 0, steps := 2, ledger := [2] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .resourceLimit, steps := 0, ledger := [0] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .resourceLimit, steps := 4, ledger := [2, 0] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_continuation_unsupported :
    E7CB2Sequence.sequence 20 ({ exit := .success 0, steps := 2, ledger := [2] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .unsupported 2, steps := 0, ledger := [0, 1] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .unsupported 2, steps := 4, ledger := [2, 0, 1] } : E7CB2Sequence.Trace Nat) := by decide

theorem vector_continuation_undetermined :
    E7CB2Sequence.sequence 20 ({ exit := .success 0, steps := 2, ledger := [2] } : E7CB2Sequence.Trace Nat)
      (fun _ => ({ exit := .undetermined 0, steps := 0, ledger := [0, 1] } : E7CB2Sequence.Trace Nat)) =
    ({ exit := .undetermined 0, steps := 4, ledger := [2, 0, 1] } : E7CB2Sequence.Trace Nat) := by decide

end E7CB2FiniteBridge