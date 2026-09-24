/-!
An abstract trace algebra for the opt-in E7C-B2 selected success sequence.
The child trace is supplied after B1 evaluation with the residual bound.
This does not encode Python admission, map tables, ledger capacity or replay.
-/

namespace E7CB2Sequence

inductive Exit (α : Type) where
  | success (value : α)
  | unsupported (diagnostic : Nat)
  | undetermined (diagnostic : Nat)
  | domainError (diagnostic : Nat)
  | resourceLimit
  deriving DecidableEq, Repr

structure Trace (α : Type) where
  exit : Exit α
  steps : Nat
  ledger : List Nat
  deriving DecidableEq, Repr

/- One outer step is charged. The continuation is called only after child
success and with room for its own entry step. Its result is a trace for that
remaining budget; this abstract algebra does not establish the premise. -/
def sequence {α β : Type} (bound : Nat) (child : Trace α)
    (continuation : α → Trace β) : Trace β :=
  if bound = 0 then
    { exit := .resourceLimit, steps := 0, ledger := [] }
  else
    match child.exit with
    | .success value =>
        if 1 + child.steps >= bound then
          { exit := .resourceLimit, steps := 1 + child.steps, ledger := child.ledger }
        else
          let tail := continuation value
          { exit := tail.exit, steps := 2 + child.steps + tail.steps,
            ledger := child.ledger ++ tail.ledger }
    | .unsupported diagnostic =>
        { exit := .unsupported diagnostic, steps := 1 + child.steps,
          ledger := child.ledger }
    | .undetermined diagnostic =>
        { exit := .undetermined diagnostic, steps := 1 + child.steps,
          ledger := child.ledger }
    | .domainError diagnostic =>
        { exit := .domainError diagnostic, steps := 1 + child.steps,
          ledger := child.ledger }
    | .resourceLimit =>
        { exit := .resourceLimit, steps := 1 + child.steps,
          ledger := child.ledger }

theorem zero_bound_ignores_child {α β : Type} (child : Trace α)
    (continuation : α → Trace β) :
    sequence 0 child continuation =
      { exit := .resourceLimit, steps := 0, ledger := [] } := by
  rfl

theorem unsupported_does_not_call_continuation {α β : Type}
    (n steps diagnostic : Nat) (ledger : List Nat)
    (left right : α → Trace β) :
    sequence (Nat.succ n)
        { exit := .unsupported diagnostic, steps := steps, ledger := ledger } left =
    sequence (Nat.succ n)
        { exit := .unsupported diagnostic, steps := steps, ledger := ledger } right := by
  rfl

theorem undetermined_does_not_call_continuation {α β : Type}
    (n steps diagnostic : Nat) (ledger : List Nat)
    (left right : α → Trace β) :
    sequence (Nat.succ n)
        { exit := .undetermined diagnostic, steps := steps, ledger := ledger } left =
    sequence (Nat.succ n)
        { exit := .undetermined diagnostic, steps := steps, ledger := ledger } right := by
  rfl

theorem resource_limit_preserves_prefix {α β : Type}
    (n steps : Nat) (ledger : List Nat) (continuation : α → Trace β) :
    sequence (Nat.succ n)
        { exit := .resourceLimit, steps := steps, ledger := ledger } continuation =
      { exit := .resourceLimit, steps := 1 + steps, ledger := ledger } := by
  rfl

theorem unsupported_preserves_payload_and_prefix {α β : Type}
    (n steps diagnostic : Nat) (ledger : List Nat)
    (continuation : α → Trace β) :
    sequence (Nat.succ n)
        { exit := .unsupported diagnostic, steps := steps, ledger := ledger } continuation =
      { exit := .unsupported diagnostic, steps := 1 + steps, ledger := ledger } := by
  rfl

theorem undetermined_preserves_payload_and_prefix {α β : Type}
    (n steps diagnostic : Nat) (ledger : List Nat)
    (continuation : α → Trace β) :
    sequence (Nat.succ n)
        { exit := .undetermined diagnostic, steps := steps, ledger := ledger } continuation =
      { exit := .undetermined diagnostic, steps := 1 + steps, ledger := ledger } := by
  rfl

theorem success_trace_appends_continuation {α β : Type}
    (bound steps : Nat) (value : α) (ledger : List Nat)
    (continuation : α → Trace β)
    (nonzero : bound ≠ 0) (room : ¬ 1 + steps >= bound) :
    sequence bound
        { exit := .success value, steps := steps, ledger := ledger } continuation =
      { exit := (continuation value).exit,
        steps := 2 + steps + (continuation value).steps,
        ledger := ledger ++ (continuation value).ledger } := by
  simp [sequence, nonzero, room]

theorem success_without_continuation_step_is_resource_limit {α β : Type}
    (bound steps : Nat) (value : α) (ledger : List Nat)
    (continuation : α → Trace β)
    (nonzero : bound ≠ 0) (exhausted : 1 + steps >= bound) :
    sequence bound
        { exit := .success value, steps := steps, ledger := ledger } continuation =
      { exit := .resourceLimit, steps := 1 + steps, ledger := ledger } := by
  simp [sequence, nonzero, exhausted]

end E7CB2Sequence
