import E7CEECQTwoStageImplementationPath

/- A total checker for decoded observation streams. Native trace production,
wire decoding and package parse correctness are separate trusted/open links. -/
namespace E7CEECQIRObservationChecker
open E7CEECQTwoStageAllInput E7CEECQTwoStageOperational
open E7CEECQTwoStageExactCodec E7CEECQTwoStageImplementationPath

inductive Packet where
  | charge (steps : Nat) (secondStarted : Bool)
  | append (event : Event) (entries : Nat)
  | terminal (result : Observation)
  deriving DecidableEq, Repr

/-- Only a single final terminal packet is accepted; trailing, missing or
changed terminal observations are rejected. -/
def finishChecked {path first second fuel capacity machine}
    (expected : Observation)
    (proof : Trace path first second fuel capacity machine expected) :
    List Packet → Option { result // Trace path first second fuel capacity machine result }
  | [.terminal reported] =>
      if reported = expected then some ⟨expected, proof⟩ else none
  | _ => none

/-- Successful checking constructs its Trace proof. It does not take a
completed Trace or output agreement theorem as an input. Charge and append
are separate, so failed append still consumes the charged step. -/
def certify (path : Path) (first second : Policy) :
    (fuel capacity : Nat) → (machine : Machine) → List Packet →
      Option { result // Trace path first second fuel capacity machine result }
  | fuel, capacity, machine, packets =>
      match hf : finished machine.cursor with
      | some terminal =>
          finishChecked (observe machine terminal) (.terminal fuel capacity machine terminal hf) packets
      | none =>
          match fuel with
          | 0 =>
              finishChecked (observe machine (.resourceLimit (snapshot machine)))
                (.noFuel capacity machine hf) packets
          | fuel + 1 =>
              match packets with
              | .charge steps started :: rest =>
                  if steps = (charge machine).steps ∧ started = (charge machine).secondStarted then
                    match capacity with
                    | 0 =>
                        finishChecked (observe (charge machine)
                          (.resourceLimit (snapshot (charge machine))))
                          (.noLedger fuel machine hf) rest
                    | capacity + 1 =>
                        match rest with
                        | .append event entries :: tail =>
                            if event = (advance first second machine.cursor).1 ∧
                                entries = machine.ledgerRev.length + 1 then do
                              let checked ← certify path first second fuel capacity
                                (append first second machine) tail
                              pure ⟨checked.val, .visited fuel capacity machine checked.val hf checked.property⟩
                            else none
                        | _ => none
                  else none
              | _ => none

def checkStream (path : Path) (first second : Policy) (fuel capacity : Nat)
    (machine : Machine) (packets : List Packet) : Option Observation :=
  (certify path first second fuel capacity machine packets).map Subtype.val

theorem checked_refines_drive {path first second fuel capacity machine packets out}
    (accepted : checkStream path first second fuel capacity machine packets = some out) :
    out = drive fuel capacity first second machine := by
  unfold checkStream at accepted
  cases hc : certify path first second fuel capacity machine packets with
  | none => simp [hc] at accepted
  | some checked =>
      have same : checked.val = out := by simpa [hc] using accepted
      exact same.symm.trans (trace_refines_drive checked.property)

theorem checked_source_ir_agree (rs : List WireRow)
    (first second : Policy) (budget : Budget)
    (sourcePackets irPackets : List Packet)
    (sourceResult irResult : Observation)
    (sourceAccepted : checkStream .source first second budget.stepBound budget.ledgerBound
      (initial (rs.map toRow)) sourcePackets = some sourceResult)
    (irAccepted : checkStream .ir first second budget.stepBound budget.ledgerBound
      (initial (rs.map toRow)) irPackets = some irResult) :
    sourceResult = irResult ∧
    sourceResult.orderedLedger = (wirePlan rs first second).take
      (min budget.stepBound budget.ledgerBound) := by
  have hs : sourceResult = run (rs.map toRow) first second budget := by
    simpa [run, initial] using checked_refines_drive sourceAccepted
  have hi : irResult = run (rs.map toRow) first second budget := by
    simpa [run, initial] using checked_refines_drive irAccepted
  constructor
  · exact hs.trans hi.symm
  · rw [hs]
    exact wire_budgeted_event_simulation rs first second budget

inductive PackageGate where
  | nestedLimit | outerLimit | admitted
  deriving DecidableEq, Repr

/-- Measured serialized lengths, not lengths inferred from source admission.
The two checks remain separate and their order matches nested lowering. -/
def packageGate (nestedBytes outerBytes : Nat) : PackageGate :=
  if nestedBytes ≤ 1000000 then
    if outerBytes ≤ 1000000 then .admitted else .outerLimit
  else .nestedLimit

theorem package_gate_admitted_iff (nested outer : Nat) :
    packageGate nested outer = .admitted ↔ nested ≤ 1000000 ∧ outer ≤ 1000000 := by
  unfold packageGate
  split
  · rename_i nestedWithin
    split
    · rename_i outerWithin
      exact ⟨fun _ => ⟨nestedWithin, outerWithin⟩, fun _ => rfl⟩
    · rename_i outerExceeded
      constructor
      · intro impossible
        cases impossible
      · intro bounds
        exact False.elim (outerExceeded bounds.2)
  · rename_i nestedExceeded
    constructor
    · intro impossible
      cases impossible
    · intro bounds
      exact False.elim (nestedExceeded bounds.1)

def checkIR (nestedBytes outerBytes : Nat) (first second : Policy)
    (rs : List WireRow) (budget : Budget) (packets : List Packet) : Option Observation :=
  match packageGate nestedBytes outerBytes with
  | .admitted => checkStream .ir first second budget.stepBound budget.ledgerBound
      (initial (rs.map toRow)) packets
  | _ => none

theorem check_ir_requires_both_bounds (nested outer : Nat) (first second : Policy)
    (rs : List WireRow) (budget : Budget) (packets : List Packet) (out : Observation)
    (accepted : checkIR nested outer first second rs budget packets = some out) :
    nested ≤ 1000000 ∧ outer ≤ 1000000 := by
  have gate : packageGate nested outer = .admitted := by
    cases hg : packageGate nested outer <;> simp [checkIR, hg] at accepted ⊢
  exact (package_gate_admitted_iff nested outer).mp gate

theorem check_ir_refines_run (nested outer : Nat) (first second : Policy)
    (rs : List WireRow) (budget : Budget) (packets : List Packet) (out : Observation)
    (accepted : checkIR nested outer first second rs budget packets = some out) :
    out = run (rs.map toRow) first second budget := by
  cases hg : packageGate nested outer with
  | nestedLimit => simp [checkIR, hg] at accepted
  | outerLimit => simp [checkIR, hg] at accepted
  | admitted =>
      have stream : checkStream .ir first second budget.stepBound budget.ledgerBound
          (initial (rs.map toRow)) packets = some out := by
        simpa [checkIR, hg] using accepted
      simpa [run, initial] using checked_refines_drive stream

example : packageGate 1000001 1 = .nestedLimit := rfl
example : packageGate 1 1000001 = .outerLimit := rfl
example : packageGate 1000000 1000000 = .admitted := rfl

example : checkStream .ir .ready .ready 1 0 (initial [])
    [.charge 1 true] = none := by decide
example : checkStream .ir .ready .ready 1 1 (initial [])
    [.append (.attempt .first) 1] = none := rfl

/-- Failed second append from any selected retained/excluded lists: a charged
step is required, the ledger cannot grow, and secondStarted is true. -/
theorem failed_second_append_checked (kept excluded : List Row) (steps fuel : Nat)
    (ledger : List Event) :
    let machine : Machine := ⟨.secondAttempt kept excluded, steps, ledger, false⟩
    let out := observe (charge machine) (.resourceLimit (snapshot (charge machine)))
    (certify .ir .ready .ready (fuel + 1) 0 machine
      [.charge (steps + 1) true, .terminal out]).map Subtype.val = some out := by
  simp [certify, finished, charge, attemptingSecond, finishChecked, observe]

/- Selected structural transport carrier. Native JSON parsing and terminal
observation decoding are still outside Lean. Row payloads are carried from
the emitted event, never recovered by indexing the expected input table. -/
inductive WireEvent where
  | attempt (stage : Stage)
  | row (stage : Stage) (index : Nat) (value : WireRow) (excluded : Bool)
  deriving DecidableEq, Repr

def decodeEvent : WireEvent → Event
  | .attempt stage => .attempt stage
  | .row stage index value excluded => .row stage index (toRow value) excluded

def encodeEvent : Event → WireEvent
  | .attempt stage => .attempt stage
  | .row stage index value excluded => .row stage index (fromRow value) excluded

theorem event_roundtrip (event : Event) : decodeEvent (encodeEvent event) = event := by
  cases event <;> simp [decodeEvent, encodeEvent, row_roundtrip]

theorem row_event_transport (stage : Stage) (index : Nat) (value : WireRow)
    (excluded : Bool) :
    decodeEvent (.row stage index value excluded) =
      .row stage index ⟨toGraph value.left, toGraph value.right, value.coefficient⟩ excluded := rfl

theorem canonical_row_event_recovered (stage : Stage) (index : Nat) (value : WireRow)
    (excluded : Bool) (hl : canonicalGraph value.left) (hr : canonicalGraph value.right) :
    encodeEvent (decodeEvent (.row stage index value excluded)) =
      .row stage index value excluded := by
  simp [decodeEvent, encodeEvent, canonical_row_roundtrip value hl hr]

inductive WirePacket where
  | charge (steps : Nat) (secondStarted : Bool)
  | append (event : WireEvent) (entries : Nat)
  | terminal (result : Observation)
  deriving DecidableEq, Repr

def decodePacket : WirePacket → Packet
  | .charge steps started => .charge steps started
  | .append event entries => .append (decodeEvent event) entries
  | .terminal result => .terminal result

def checkTransport (path : Path) (first second : Policy) (fuel capacity : Nat)
    (machine : Machine) (packets : List WirePacket) : Option Observation :=
  checkStream path first second fuel capacity machine (packets.map decodePacket)

theorem accepted_transport_refines_drive {path first second fuel capacity machine packets out}
    (accepted : checkTransport path first second fuel capacity machine packets = some out) :
    out = drive fuel capacity first second machine :=
  checked_refines_drive accepted

def checkTransportIR (nested outer : Nat) (first second : Policy)
    (rs : List WireRow) (budget : Budget) (packets : List WirePacket) : Option Observation :=
  checkIR nested outer first second rs budget (packets.map decodePacket)

theorem accepted_ir_transport (nested outer : Nat) (first second : Policy)
    (rs : List WireRow) (budget : Budget) (packets : List WirePacket) (out : Observation)
    (accepted : checkTransportIR nested outer first second rs budget packets = some out) :
    nested ≤ 1000000 ∧ outer ≤ 1000000 ∧ out = run (rs.map toRow) first second budget :=
  ⟨(check_ir_requires_both_bounds nested outer first second rs budget
      (packets.map decodePacket) out accepted).1,
    (check_ir_requires_both_bounds nested outer first second rs budget
      (packets.map decodePacket) out accepted).2,
    check_ir_refines_run nested outer first second rs budget
      (packets.map decodePacket) out accepted⟩

/- Terminal observations now retain their own wire rows and event payloads.
Resource progress is decoded independently of the top-level progress. -/
structure WireProgress where
  completedSteps : Nat
  ledgerPrefix : List WireEvent
  firstExcluded : Option (List WireRow)
  secondExcludedPrefix : List WireRow
  deriving DecidableEq, Repr

def decodeProgress (p : WireProgress) : Progress :=
  ⟨p.completedSteps, p.ledgerPrefix.map decodeEvent,
    p.firstExcluded.map (List.map toRow), p.secondExcludedPrefix.map toRow⟩

def encodeProgress (p : Progress) : WireProgress :=
  ⟨p.completedSteps, p.ledgerPrefix.map encodeEvent,
    p.firstExcluded.map (List.map fromRow), p.secondExcludedPrefix.map fromRow⟩

theorem rows_transport_roundtrip (rs : List Row) :
    (rs.map fromRow).map toRow = rs := by
  induction rs with
  | nil => rfl
  | cons r rs ih => simp [row_roundtrip, ih]

theorem events_transport_roundtrip (es : List Event) :
    (es.map encodeEvent).map decodeEvent = es := by
  induction es with
  | nil => rfl
  | cons e es ih => simp [event_roundtrip, ih]

theorem progress_transport_roundtrip (p : Progress) :
    decodeProgress (encodeProgress p) = p := by
  cases p with
  | mk steps ledger first second =>
      cases first <;>
        simp [decodeProgress, encodeProgress, rows_transport_roundtrip,
          events_transport_roundtrip]

inductive WireTerminal where
  | success (retained firstExcluded secondExcluded : List WireRow)
  | resourceLimit (progress : WireProgress)
  | unsupported (stage : Stage)
  | undetermined (stage : Stage)
  deriving DecidableEq, Repr

def decodeTerminal : WireTerminal → Terminal
  | .success retained first second =>
      .success ⟨retained.map toRow, first.map toRow, second.map toRow⟩
  | .resourceLimit progress => .resourceLimit (decodeProgress progress)
  | .unsupported stage => .unsupported stage
  | .undetermined stage => .undetermined stage

def encodeTerminal : Terminal → WireTerminal
  | .success p => .success (p.retained.map fromRow) (p.firstExcluded.map fromRow)
      (p.secondExcluded.map fromRow)
  | .resourceLimit progress => .resourceLimit (encodeProgress progress)
  | .unsupported stage => .unsupported stage
  | .undetermined stage => .undetermined stage

theorem terminal_transport_roundtrip (t : Terminal) :
    decodeTerminal (encodeTerminal t) = t := by
  cases t with
  | success p => cases p; simp [decodeTerminal, encodeTerminal, rows_transport_roundtrip]
  | resourceLimit p => simp [decodeTerminal, encodeTerminal, progress_transport_roundtrip]
  | unsupported stage => rfl
  | undetermined stage => rfl

structure WireObservation where
  terminal : WireTerminal
  orderedLedger : List WireEvent
  progress : WireProgress
  secondStarted : Bool
  deriving DecidableEq, Repr

def decodeObservation (o : WireObservation) : Observation :=
  ⟨decodeTerminal o.terminal, o.orderedLedger.map decodeEvent,
    decodeProgress o.progress, o.secondStarted⟩

def encodeObservation (o : Observation) : WireObservation :=
  ⟨encodeTerminal o.terminal, o.orderedLedger.map encodeEvent,
    encodeProgress o.progress, o.secondStarted⟩

theorem observation_transport_roundtrip (o : Observation) :
    decodeObservation (encodeObservation o) = o := by
  cases o
  simp [decodeObservation, encodeObservation, terminal_transport_roundtrip,
    events_transport_roundtrip, progress_transport_roundtrip]

inductive TerminalPacket where
  | charge (steps : Nat) (secondStarted : Bool)
  | append (event : WireEvent) (entries : Nat)
  | terminal (result : WireObservation)
  deriving DecidableEq, Repr

def decodeTerminalPacket : TerminalPacket → Packet
  | .charge steps started => .charge steps started
  | .append event entries => .append (decodeEvent event) entries
  | .terminal result => .terminal (decodeObservation result)

def checkTerminalTransport (path : Path) (first second : Policy) (fuel capacity : Nat)
    (machine : Machine) (packets : List TerminalPacket) : Option Observation :=
  checkStream path first second fuel capacity machine (packets.map decodeTerminalPacket)

theorem accepted_terminal_transport_refines_drive
    {path first second fuel capacity machine packets out}
    (accepted : checkTerminalTransport path first second fuel capacity machine packets = some out) :
    out = drive fuel capacity first second machine := checked_refines_drive accepted

def checkTerminalTransportIR (nested outer : Nat) (first second : Policy)
    (rs : List WireRow) (budget : Budget) (packets : List TerminalPacket) : Option Observation :=
  checkIR nested outer first second rs budget (packets.map decodeTerminalPacket)

theorem accepted_terminal_ir_transport (nested outer : Nat) (first second : Policy)
    (rs : List WireRow) (budget : Budget) (packets : List TerminalPacket) (out : Observation)
    (accepted : checkTerminalTransportIR nested outer first second rs budget packets = some out) :
    nested ≤ 1000000 ∧ outer ≤ 1000000 ∧ out = run (rs.map toRow) first second budget :=
  ⟨(check_ir_requires_both_bounds nested outer first second rs budget
      (packets.map decodeTerminalPacket) out accepted).1,
    (check_ir_requires_both_bounds nested outer first second rs budget
      (packets.map decodeTerminalPacket) out accepted).2,
    check_ir_refines_run nested outer first second rs budget
      (packets.map decodeTerminalPacket) out accepted⟩

end E7CEECQIRObservationChecker
