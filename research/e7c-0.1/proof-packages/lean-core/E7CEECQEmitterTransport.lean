import E7CEECQIRObservationChecker

/- Constructive emitter-to-checker completeness. The hypotheses are local
operation equations, not a completed Trace, checker acceptance, or final
source/IR output equality. Native code/control and raw parser correspondence
to these functions remain explicit host boundaries. -/
namespace E7CEECQEmitterTransport
open E7CEECQTwoStageAllInput E7CEECQTwoStageOperational
open E7CEECQTwoStageExactCodec E7CEECQTwoStageImplementationPath
open E7CEECQIRObservationChecker

structure HostOps where
  stop : Cursor → Option Terminal
  charged : Machine → Machine
  appended : Policy → Policy → Machine → Machine
  event : Policy → Policy → Cursor → Event
  observed : Machine → Terminal → Observation

def modelOps : HostOps :=
  ⟨finished, charge, append, fun first second cursor => (advance first second cursor).1,
    observe⟩

structure LocalContract (ops : HostOps) : Prop where
  stop : ∀ cursor, ops.stop cursor = finished cursor
  charged : ∀ machine, ops.charged machine = charge machine
  appended : ∀ first second machine, ops.appended first second machine = append first second machine
  event : ∀ first second cursor, ops.event first second cursor = (advance first second cursor).1
  observed : ∀ machine terminal, ops.observed machine terminal = observe machine terminal

/-- Execute finite control and emit actual local primitive returns in order.
No complete plan or expected final partition is an input to this function. -/
def emit (ops : HostOps) (first second : Policy) : Nat → Nat → Machine → List Packet
  | fuel, capacity, machine =>
      match ops.stop machine.cursor with
      | some terminal => [.terminal (ops.observed machine terminal)]
      | none =>
          match fuel with
          | 0 => [.terminal (ops.observed machine (.resourceLimit (snapshot machine)))]
          | fuel + 1 =>
              let charged := ops.charged machine
              let packet := Packet.charge charged.steps charged.secondStarted
              match capacity with
              | 0 => [packet, .terminal
                  (ops.observed charged (.resourceLimit (snapshot charged)))]
              | capacity + 1 =>
                  packet :: .append (ops.event first second machine.cursor)
                    (machine.ledgerRev.length + 1) ::
                    emit ops first second fuel capacity (ops.appended first second machine)

theorem operations_identified (ops : HostOps) (law : LocalContract ops) : ops = modelOps := by
  cases ops with
  | mk stop charged appended event observed =>
      have hs : stop = finished := funext law.stop
      have hc : charged = charge := funext law.charged
      have ha : appended = append := funext fun first => funext fun second =>
        funext (law.appended first second)
      have he : event = (fun first second cursor => (advance first second cursor).1) :=
        funext fun first => funext fun second => funext (law.event first second)
      have ho : observed = observe := funext fun machine => funext (law.observed machine)
      subst stop; subst charged; subst appended; subst event; subst observed
      rfl

/-- The certificate is constructed from finite execution, never supplied as
an assumption about a native run. -/
theorem emitted_certificate (path : Path) (first second : Policy)
    (fuel capacity : Nat) (machine : Machine) :
    ∃ checked, certify path first second fuel capacity machine
      (emit modelOps first second fuel capacity machine) = some checked := by
  induction fuel generalizing capacity machine with
  | zero =>
      cases hf : finished machine.cursor with
      | none =>
          refine ⟨⟨observe machine (.resourceLimit (snapshot machine)),
            Trace.noFuel capacity machine hf⟩, ?_⟩
          rw [emit]
          simp only [modelOps, hf]
          unfold certify
          split <;> simp_all [finishChecked]
      | some terminal =>
          refine ⟨⟨observe machine terminal, Trace.terminal 0 capacity machine terminal hf⟩, ?_⟩
          rw [emit]
          simp only [modelOps, hf]
          unfold certify
          split <;> simp_all [finishChecked]
  | succ fuel ih =>
      cases hf : finished machine.cursor with
      | some terminal =>
          refine ⟨⟨observe machine terminal,
            Trace.terminal (fuel + 1) capacity machine terminal hf⟩, ?_⟩
          rw [emit]
          simp only [modelOps, hf]
          unfold certify
          split <;> simp_all [finishChecked]
      | none =>
          cases capacity with
          | zero =>
              refine ⟨⟨observe (charge machine) (.resourceLimit (snapshot (charge machine))),
                Trace.noLedger fuel machine hf⟩, ?_⟩
              rw [emit]
              simp only [modelOps, hf]
              unfold certify
              split <;> simp_all [finishChecked]
          | succ capacity =>
              obtain ⟨checked, hc⟩ := ih capacity (append first second machine)
              refine ⟨⟨checked.val,
                Trace.visited fuel capacity machine checked.val hf checked.property⟩, ?_⟩
              rw [emit]
              simp only [modelOps, hf]
              unfold certify
              split <;> simp_all [finishChecked]

theorem emitted_stream_accepted (path : Path) (first second : Policy)
    (fuel capacity : Nat) (machine : Machine) :
    checkStream path first second fuel capacity machine
      (emit modelOps first second fuel capacity machine) =
      some (drive fuel capacity first second machine) := by
  obtain ⟨checked, hc⟩ := emitted_certificate path first second fuel capacity machine
  have ho := trace_refines_drive checked.property
  simp [checkStream, hc, ho]

def encodePacket : Packet → TerminalPacket
  | .charge steps started => .charge steps started
  | .append event entries => .append (encodeEvent event) entries
  | .terminal result => .terminal (encodeObservation result)

theorem packet_roundtrip (packet : Packet) :
    decodeTerminalPacket (encodePacket packet) = packet := by
  cases packet <;> simp [encodePacket, decodeTerminalPacket, event_roundtrip,
    observation_transport_roundtrip]

theorem packets_roundtrip (packets : List Packet) :
    (packets.map encodePacket).map decodeTerminalPacket = packets := by
  induction packets with
  | nil => rfl
  | cons packet packets ih => simp [packet_roundtrip, ih]

def wireEmission (ops : HostOps) (first second : Policy) (fuel capacity : Nat)
    (machine : Machine) : List TerminalPacket :=
  (emit ops first second fuel capacity machine).map encodePacket

/-- All finite budgets, policies and typed machine states, under local
primitive contracts. Checker acceptance is a conclusion. -/
theorem local_operations_supply_accepted_transport (ops : HostOps) (law : LocalContract ops)
    (path : Path) (first second : Policy) (fuel capacity : Nat) (machine : Machine) :
    checkTerminalTransport path first second fuel capacity machine
      (wireEmission ops first second fuel capacity machine) =
      some (drive fuel capacity first second machine) := by
  rw [operations_identified ops law]
  unfold checkTerminalTransport wireEmission
  rw [packets_roundtrip]
  exact emitted_stream_accepted path first second fuel capacity machine

theorem emitted_ir_with_separate_captured_bounds (ops : HostOps) (law : LocalContract ops)
    (capture : CapturedPackages) (nestedBound : capture.nested.size ≤ 1000000)
    (outerBound : capture.outer.size ≤ 1000000) (first second : Policy)
    (rows : List WireRow) (budget : Budget) :
    checkCapturedIR capture first second rows budget
      (wireEmission ops first second budget.stepBound budget.ledgerBound
        (initial (rows.map toRow))) = some (run (rows.map toRow) first second budget) := by
  have gate := (package_gate_admitted_iff capture.nested.size capture.outer.size).mpr
    ⟨nestedBound, outerBound⟩
  simp only [checkCapturedIR, checkTerminalTransportIR, checkIR, gate]
  simpa [checkTerminalTransport, run, initial] using
    local_operations_supply_accepted_transport ops law .ir first second
      budget.stepBound budget.ledgerBound (initial (rows.map toRow))

theorem independently_bound_source_ir (sourceOps irOps : HostOps)
    (sourceLaw : LocalContract sourceOps) (irLaw : LocalContract irOps)
    (first second : Policy) (rows : List WireRow) (budget : Budget) :
    checkTerminalTransport .source first second budget.stepBound budget.ledgerBound
      (initial (rows.map toRow))
      (wireEmission sourceOps first second budget.stepBound budget.ledgerBound
        (initial (rows.map toRow))) =
    checkTerminalTransport .ir first second budget.stepBound budget.ledgerBound
      (initial (rows.map toRow))
      (wireEmission irOps first second budget.stepBound budget.ledgerBound
        (initial (rows.map toRow))) := by
  rw [local_operations_supply_accepted_transport sourceOps sourceLaw,
    local_operations_supply_accepted_transport irOps irLaw]

example : emit modelOps .ready .ready 1 0 (initial []) =
    [.charge 1 false, .terminal
      (observe (charge (initial [])) (.resourceLimit (snapshot (charge (initial [])))))] := rfl

example (kept excluded : List Row) (steps fuel : Nat) (ledger : List Event) :
    emit modelOps .ready .ready (fuel + 1) 0
      ⟨.secondAttempt kept excluded, steps, ledger, false⟩ =
      [.charge (steps + 1) true, .terminal
        (observe (charge ⟨.secondAttempt kept excluded, steps, ledger, false⟩)
          (.resourceLimit (snapshot (charge
            ⟨.secondAttempt kept excluded, steps, ledger, false⟩))))] := rfl

end E7CEECQEmitterTransport
