import E7CS1FG3Rows

/-!
Constructive, unreduced exact rational collection of finite FG3 images.
Positive denominators and integer arithmetic avoid classical choice in the
executable collector. A canonical reduced wire encoding is not proved here.
-/

namespace E7CS1ExactCollect

open E7CS1FG3Single

structure Fraction where
  numerator : Int
  denominator : Nat
  positive : 0 < denominator

def opposite (value : Fraction) : Fraction :=
  ⟨-value.numerator, value.denominator, value.positive⟩

/- Cross multiplication represents exact addition. The output fraction may
be unreduced; its denominator remains strictly positive. -/
def add (left right : Fraction) : Fraction :=
  ⟨left.numerator * (right.denominator : Int) +
     right.numerator * (left.denominator : Int),
   left.denominator * right.denominator,
   Nat.mul_pos left.positive right.positive⟩

def isZero (value : Fraction) : Bool := decide (value.numerator = 0)

/- Equality of values is cross multiplication, independent of the particular
positive denominator chosen for an internal fraction. -/
def Equivalent (left right : Fraction) : Prop :=
  left.numerator * (right.denominator : Int) =
    right.numerator * (left.denominator : Int)

theorem equivalent_refl (value : Fraction) : Equivalent value value := rfl

theorem equivalent_symm {left right : Fraction}
    (h : Equivalent left right) : Equivalent right left := h.symm

theorem equivalent_trans {left middle right : Fraction}
    (first : Equivalent left middle)
    (second : Equivalent middle right) : Equivalent left right := by
  have middleDenominatorNonzero : (middle.denominator : Int) ≠ 0 :=
    Int.ofNat_ne_zero.mpr (Nat.ne_of_gt middle.positive)
  apply Int.eq_of_mul_eq_mul_left middleDenominatorNonzero
  calc
    (middle.denominator : Int) *
        (left.numerator * (right.denominator : Int)) =
        (left.numerator * (middle.denominator : Int)) *
          (right.denominator : Int) := by ac_rfl
    _ = (middle.numerator * (left.denominator : Int)) *
          (right.denominator : Int) :=
            congrArg (fun x : Int => x * (right.denominator : Int)) first
    _ = (middle.numerator * (right.denominator : Int)) *
          (left.denominator : Int) := by ac_rfl
    _ = (right.numerator * (middle.denominator : Int)) *
          (left.denominator : Int) :=
            congrArg (fun x : Int => x * (left.denominator : Int)) second
    _ = (middle.denominator : Int) *
          (right.numerator * (left.denominator : Int)) := by ac_rfl

theorem add_comm_equivalent (left right : Fraction) :
    Equivalent (add left right) (add right left) := by
  simp [Equivalent, add, Int.add_comm, Int.mul_comm, Nat.mul_comm]

private theorem add_congr_left_int
    (an ad bn bd cn cd : Int) (hab : an * bd = bn * ad) :
    (an * cd + cn * ad) * (bd * cd) =
      (bn * cd + cn * bd) * (ad * cd) := by
  have first : (an * cd) * (bd * cd) = (an * bd) * (cd * cd) := by ac_rfl
  have second : (cn * ad) * (bd * cd) = cn * (ad * bd * cd) := by ac_rfl
  have third : (bn * cd) * (ad * cd) = (bn * ad) * (cd * cd) := by ac_rfl
  have fourth : (cn * bd) * (ad * cd) = cn * (ad * bd * cd) := by ac_rfl
  simp only [Int.add_mul, first, second, third, fourth, hab]

theorem add_congr_left {left alternate : Fraction}
    (h : Equivalent left alternate) (right : Fraction) :
    Equivalent (add left right) (add alternate right) := by
  unfold Equivalent add at *
  simp only [Int.natCast_mul]
  exact add_congr_left_int left.numerator (left.denominator : Int)
    alternate.numerator (alternate.denominator : Int)
    right.numerator (right.denominator : Int) h

theorem add_congr_right (left : Fraction) {right alternate : Fraction}
    (h : Equivalent right alternate) :
    Equivalent (add left right) (add left alternate) :=
  equivalent_trans (add_comm_equivalent left right)
    (equivalent_trans (add_congr_left h left)
      (equivalent_symm (add_comm_equivalent left alternate)))

theorem add_congr {left alternate right replacement : Fraction}
    (hl : Equivalent left alternate) (hr : Equivalent right replacement) :
    Equivalent (add left right) (add alternate replacement) :=
  equivalent_trans (add_congr_left hl right)
    (add_congr_right alternate hr)

theorem add_assoc_numerator (left middle right : Fraction) :
    (add (add left middle) right).numerator =
      (add left (add middle right)).numerator := by
  simp [add, Int.natCast_mul, Int.add_mul, Int.mul_add,
    Int.mul_assoc, Int.mul_comm, Int.mul_left_comm,
    Int.add_assoc, Int.add_comm, Int.add_left_comm]

theorem add_assoc_denominator (left middle right : Fraction) :
    (add (add left middle) right).denominator =
      (add left (add middle right)).denominator := by
  simp [add, Nat.mul_assoc]

theorem add_assoc_equivalent (left middle right : Fraction) :
    Equivalent (add (add left middle) right)
      (add left (add middle right)) := by
  unfold Equivalent
  rw [add_assoc_numerator, add_assoc_denominator]

theorem equivalent_numerator_zero {left right : Fraction}
    (h : Equivalent left right) :
    left.numerator = 0 ↔ right.numerator = 0 := by
  have leftDenominatorNonzero : (left.denominator : Int) ≠ 0 :=
    Int.ofNat_ne_zero.mpr (Nat.ne_of_gt left.positive)
  have rightDenominatorNonzero : (right.denominator : Int) ≠ 0 :=
    Int.ofNat_ne_zero.mpr (Nat.ne_of_gt right.positive)
  constructor
  · intro hl
    have hp : right.numerator * (left.denominator : Int) = 0 := by
      rw [← h, hl, Int.zero_mul]
    exact (Int.mul_eq_zero.mp hp).resolve_right leftDenominatorNonzero
  · intro hr
    have hp : left.numerator * (right.denominator : Int) = 0 := by
      rw [h, hr, Int.zero_mul]
    exact (Int.mul_eq_zero.mp hp).resolve_right rightDenominatorNonzero

theorem equivalent_isZero {left right : Fraction}
    (h : Equivalent left right) : isZero left = isZero right := by
  by_cases hl : left.numerator = 0
  · have hr := (equivalent_numerator_zero h).mp hl
    simp [isZero, hl, hr]
  · have hr : right.numerator ≠ 0 :=
      fun hzero => hl ((equivalent_numerator_zero h).mpr hzero)
    simp [isZero, hl, hr]

theorem opposite_sum_has_zero_numerator (value : Fraction) :
    (add value (opposite value)).numerator = 0 := by
  simpa [add, opposite, Int.neg_mul] using
    (Int.add_neg_cancel_right 0
      (value.numerator * (value.denominator : Int)))

theorem opposite_sum_is_zero (value : Fraction) :
    isZero (add value (opposite value)) = true := by
  unfold isZero
  rw [opposite_sum_has_zero_numerator]
  rfl

abbrev Collected := List (Graph × Fraction)

/- Store each exact target graph once. On a collision add coefficients and
remove the target if their sum is zero. Input admission precedes this step. -/
def insert (graph : Graph) (amount : Fraction) : Collected → Collected
  | [] => if isZero amount then [] else [(graph, amount)]
  | (existing, coefficient) :: rest =>
      if graph = existing then
        let total := add coefficient amount
        if isZero total then rest else (existing, total) :: rest
      else (existing, coefficient) :: insert graph amount rest

def collect (rows : List (Graph × Fraction)) : Collected :=
  rows.foldl (fun state row => insert row.1 row.2 state) []

/- Every entry retained by an arbitrary finite collection has a nonzero
coefficient, even after intermediate cancellations. -/
def zeroFree : Collected → Prop
  | [] => True
  | (_, amount) :: rest => isZero amount = false ∧ zeroFree rest

theorem insert_zeroFree (graph : Graph) (amount : Fraction)
    (state : Collected) (h : zeroFree state) :
    zeroFree (insert graph amount state) := by
  induction state with
  | nil =>
      cases hz : isZero amount <;> simp [insert, hz, zeroFree]
  | cons head rest ih =>
      rcases head with ⟨existing, coefficient⟩
      change isZero coefficient = false ∧ zeroFree rest at h
      obtain ⟨hcoeff, hrest⟩ := h
      by_cases heq : graph = existing
      · cases hz : isZero (add coefficient amount) <;>
          simp [insert, heq, hz, zeroFree, hrest]
      · simp [insert, heq, zeroFree, hcoeff, ih hrest]

theorem foldl_zeroFree (rows : List (Graph × Fraction))
    (state : Collected) (h : zeroFree state) :
    zeroFree (rows.foldl (fun acc row => insert row.1 row.2 acc) state) := by
  induction rows generalizing state with
  | nil => simpa using h
  | cons row rest ih =>
      simp only [List.foldl_cons]
      exact ih _ (insert_zeroFree row.1 row.2 state h)

theorem collect_zeroFree (rows : List (Graph × Fraction)) :
    zeroFree (collect rows) := by
  exact foldl_zeroFree rows [] trivial

/- keyAbsent and uniqueKeys express the support invariant without imposing
an ordering on graph keys. -/
def keyAbsent (graph : Graph) : Collected → Prop
  | [] => True
  | (existing, _) :: rest => existing ≠ graph ∧ keyAbsent graph rest

def uniqueKeys : Collected → Prop
  | [] => True
  | (existing, _) :: rest => keyAbsent existing rest ∧ uniqueKeys rest

theorem insert_keeps_absent (forbidden graph : Graph) (amount : Fraction)
    (state : Collected) (h : keyAbsent forbidden state)
    (different : graph ≠ forbidden) :
    keyAbsent forbidden (insert graph amount state) := by
  induction state with
  | nil =>
      cases hz : isZero amount <;>
        simp [insert, hz, keyAbsent, different]
  | cons head rest ih =>
      rcases head with ⟨existing, coefficient⟩
      change existing ≠ forbidden ∧ keyAbsent forbidden rest at h
      obtain ⟨hhead, hrest⟩ := h
      by_cases heq : graph = existing
      · cases hz : isZero (add coefficient amount) <;>
          simp [insert, heq, hz, keyAbsent, hhead, hrest]
      · simp [insert, heq, keyAbsent, hhead, ih hrest]

theorem insert_uniqueKeys (graph : Graph) (amount : Fraction)
    (state : Collected) (h : uniqueKeys state) :
    uniqueKeys (insert graph amount state) := by
  induction state with
  | nil =>
      cases hz : isZero amount <;>
        simp [insert, hz, uniqueKeys, keyAbsent]
  | cons head rest ih =>
      rcases head with ⟨existing, coefficient⟩
      change keyAbsent existing rest ∧ uniqueKeys rest at h
      obtain ⟨habsent, hrest⟩ := h
      by_cases heq : graph = existing
      · cases hz : isZero (add coefficient amount) <;>
          simp [insert, heq, hz, uniqueKeys, habsent, hrest]
      · have hkept := insert_keeps_absent existing graph amount rest habsent heq
        simp [insert, heq, uniqueKeys, hkept, ih hrest]

theorem foldl_uniqueKeys (rows : List (Graph × Fraction))
    (state : Collected) (h : uniqueKeys state) :
    uniqueKeys (rows.foldl (fun acc row => insert row.1 row.2 acc) state) := by
  induction rows generalizing state with
  | nil => simpa using h
  | cons row rest ih =>
      simp only [List.foldl_cons]
      exact ih _ (insert_uniqueKeys row.1 row.2 state h)

theorem collect_uniqueKeys (rows : List (Graph × Fraction)) :
    uniqueKeys (collect rows) := by
  exact foldl_uniqueKeys rows [] trivial

/- A graph is observed by its first retained coefficient, or exact zero
when absent. The collector invariants make that observation unambiguous. -/
def zero : Fraction := ⟨0, 1, by decide⟩

def lookup (graph : Graph) : Collected → Option Fraction
  | [] => none
  | (existing, amount) :: rest =>
      if existing = graph then some amount else lookup graph rest

def observed (graph : Graph) (state : Collected) : Fraction :=
  (lookup graph state).getD zero

def contribution (graph : Graph) (row : Graph × Fraction) : Fraction :=
  if row.1 = graph then row.2 else zero

def foldValue (graph : Graph) (rows : List (Graph × Fraction))
    (initial : Fraction) : Fraction :=
  rows.foldl (fun acc row => add acc (contribution graph row)) initial

theorem add_zero_right (value : Fraction) :
    Equivalent (add value zero) value := by
  simp [Equivalent, add, zero]

theorem add_zero_left (value : Fraction) :
    Equivalent (add zero value) value := by
  simp [Equivalent, add, zero]

theorem zero_of_isZero (value : Fraction) (h : isZero value = true) :
    Equivalent value zero := by
  have hn : value.numerator = 0 := by simpa [isZero] using h
  simp [Equivalent, zero, hn]

theorem lookup_none_of_absent (graph : Graph) (state : Collected)
    (h : keyAbsent graph state) : lookup graph state = none := by
  induction state with
  | nil => rfl
  | cons head rest ih =>
      rcases head with ⟨existing, amount⟩
      change existing ≠ graph ∧ keyAbsent graph rest at h
      simp [lookup, h.1, ih h.2]

theorem observed_insert (target key : Graph) (amount : Fraction)
    (state : Collected) (h : uniqueKeys state) :
    Equivalent (observed target (insert key amount state))
      (add (observed target state) (contribution target (key, amount))) := by
  induction state with
  | nil =>
      by_cases hkey : key = target
      · subst target
        cases hz : isZero amount with
        | true =>
            have hzero := zero_of_isZero amount hz
            simpa [observed, lookup, insert, contribution, hz] using
              (equivalent_symm
                (equivalent_trans (add_zero_left amount) hzero))
        | false =>
            simpa [observed, lookup, insert, contribution, hz] using
              (equivalent_symm (add_zero_left amount))
      · simpa [observed, lookup, insert, contribution, hkey,
          add_zero_right] using
          (equivalent_symm (add_zero_right zero))
  | cons head rest ih =>
      rcases head with ⟨existing, coefficient⟩
      change keyAbsent existing rest ∧ uniqueKeys rest at h
      obtain ⟨habsent, hrest⟩ := h
      by_cases hkey : key = existing
      · subst key
        by_cases htarget : existing = target
        · subst target
          have hnone := lookup_none_of_absent existing rest habsent
          cases hz : isZero (add coefficient amount) with
          | true =>
              simpa [observed, lookup, insert, contribution, hnone, hz] using
                (equivalent_symm (zero_of_isZero (add coefficient amount) hz))
          | false =>
              simp [observed, lookup, insert, contribution, hz,
                Equivalent]
        · cases hz : isZero (add coefficient amount) <;>
            simpa [observed, lookup, insert, contribution, htarget, hz]
              using (equivalent_symm (add_zero_right (observed target rest)))
      · by_cases htarget : existing = target
        · subst target
          have hdistinct : key ≠ existing := hkey
          simpa [observed, lookup, insert, contribution, hkey,
            hdistinct] using
            (equivalent_symm (add_zero_right coefficient))
        · simpa [observed, lookup, insert, hkey, htarget]
            using ih hrest

theorem same_graph_opposites_cancel (graph : Graph) (amount : Fraction)
    (nonzero : isZero amount = false) :
    collect [(graph, amount), (graph, opposite amount)] = [] := by
  simp [collect, insert, nonzero, opposite_sum_is_zero]

/- The same rational value can arrive with different unreduced denominators. -/
def half : Fraction := ⟨1, 2, by decide⟩
def negativeHalfUnreduced : Fraction := ⟨-2, 4, by decide⟩

theorem negative_half_equivalent_to_opposite :
    Equivalent negativeHalfUnreduced (opposite half) := by
  unfold Equivalent negativeHalfUnreduced half opposite
  decide

theorem cross_denominator_cancellation (graph : Graph) :
    collect [(graph, half), (graph, negativeHalfUnreduced)] = [] := by
  have firstNonzero : isZero half = false := rfl
  have exactCancel : isZero (add half negativeHalfUnreduced) = true := rfl
  simp [collect, insert, firstNonzero, exactCancel]

theorem colliding_nonzero_pair (graph : Graph) (left right : Fraction)
    (leftNonzero : left.numerator ≠ 0)
    (sumNonzero : (add left right).numerator ≠ 0) :
    collect [(graph, left), (graph, right)] =
      [(graph, add left right)] := by
  simp [collect, insert, isZero, leftNonzero, sumNonzero]

end E7CS1ExactCollect
