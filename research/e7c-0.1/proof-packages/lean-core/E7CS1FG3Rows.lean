import E7CS1FG3Single

/-!
Finite ordered traversal of admitted FG3 support rows before collision
collection. This retains rational coefficients without performing rational
arithmetic. It does not prove a canonical State or Python correspondence.
-/

namespace E7CS1FG3Rows

open E7CS1FG3Single

def image (row : AdmittedRow) : Graph × Rat :=
  (unionGraph row.left row.right, row.coefficient)

structure Scan where
  terminal : Terminal
  visits : Nat
  offendingIndex : Option Nat
  deriving DecidableEq, Repr

/- Consume one visit before examining the next tag pair. Successful images
are retained in input order; failures never contain a partial image list. -/
def scan : Nat → List AdmittedRow → Scan
  | _, [] => ⟨.success [], 0, none⟩
  | 0, _ :: _ => ⟨.resourceLimit, 0, none⟩
  | fuel + 1, row :: rest =>
      if row.left.tag = row.right.tag then
        let tail := scan fuel rest
        match tail.terminal with
        | .success images =>
            ⟨.success (image row :: images), tail.visits + 1, none⟩
        | .domainError =>
            ⟨.domainError, tail.visits + 1,
             tail.offendingIndex.map Nat.succ⟩
        | .resourceLimit =>
            ⟨.resourceLimit, tail.visits + 1, none⟩
      else ⟨.domainError, 1, some 0⟩

/- Independent finite source-side scan of canonical input support. The
first incompatible index is measured in ordered support, not raw rows. -/
def firstBad : List AdmittedRow → Option Nat
  | [] => none
  | row :: rest =>
      if row.left.tag = row.right.tag then (firstBad rest).map Nat.succ
      else some 0

def expected (rows : List AdmittedRow) : Scan :=
  match firstBad rows with
  | none => ⟨.success (rows.map image), rows.length, none⟩
  | some index => ⟨.domainError, index + 1, some index⟩

theorem sufficient_visits_match_source :
    (rows : List AdmittedRow) → scan rows.length rows = expected rows
  | [] => rfl
  | row :: rest => by
      by_cases compatible : row.left.tag = row.right.tag
      · cases sourceTail : firstBad rest with
        | none =>
            simp [scan, expected, firstBad, compatible, sourceTail,
              sufficient_visits_match_source rest, expected]
        | some index =>
            simp [scan, expected, firstBad, compatible, sourceTail,
              sufficient_visits_match_source rest, expected]
      · simp [scan, expected, firstBad, compatible]

theorem zero_visits_before_first_pair (row : AdmittedRow)
    (rest : List AdmittedRow) :
    scan 0 (row :: rest) = ⟨.resourceLimit, 0, none⟩ := rfl

theorem incompatible_first_pair (fuel : Nat) (row : AdmittedRow)
    (rest : List AdmittedRow) (bad : row.left.tag ≠ row.right.tag) :
    scan (fuel + 1) (row :: rest) =
      ⟨.domainError, 1, some 0⟩ := by
  simp [scan, bad]

/- For a variable operand, two term entries are charged before this scan.
There is one terminal strict-union ledger entry on success or domain failure,
and none when a bound stops traversal. -/
def runRows (rows : List AdmittedRow) (maxSteps maxVisits : Nat) : Observation :=
  if maxSteps < 2 then
    ⟨.resourceLimit, maxSteps, 0, []⟩
  else
    let result := scan maxVisits rows
    match result.terminal with
    | .success images =>
        ⟨.success images, 2, result.visits,
         [.strictSuccess result.visits images.length]⟩
    | .domainError =>
        ⟨.domainError, 2, result.visits,
         [.strictDomain result.visits (result.offendingIndex.getD 0)]⟩
    | .resourceLimit =>
        ⟨.resourceLimit, 2, result.visits, []⟩

theorem term_step_bound_precedes_scan (rows : List AdmittedRow)
    (maxSteps maxVisits : Nat) (short : maxSteps < 2) :
    runRows rows maxSteps maxVisits =
      ⟨.resourceLimit, maxSteps, 0, []⟩ := by
  simp [runRows, short]

end E7CS1FG3Rows
