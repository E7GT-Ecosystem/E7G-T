import E7CS1FG3Codec

/-!
Value-level bridge between Lean's normalized Rat and the collector's
unreduced positive-denominator fractions. It does not interpret Python
Fraction or admit external FG3 source payloads.
-/

namespace E7CS1RatArithmetic

open E7CS1ExactCollect E7CS1FG3Codec

theorem fromRat_add (left right : Rat) :
    Equivalent (fromRat (left + right))
      (add (fromRat left) (fromRat right)) := by
  let numerator : Int :=
    left.num * (right.den : Int) + right.num * (left.den : Int)
  let denominator : Nat := left.den * right.den
  have positive : 0 < denominator :=
    Nat.mul_pos left.den_pos right.den_pos
  have nonzero : denominator ≠ 0 := Nat.ne_of_gt positive
  have normalized :
      Rat.normalize numerator denominator nonzero = left + right := by
    simpa [numerator, denominator] using (Rat.add_def left right).symm
  have sameValue :
      numerator * ((left + right).den : Int) =
        (left + right).num * (denominator : Int) := by
    exact (Rat.normalize_eq_iff nonzero
      (Nat.ne_of_gt (left + right).den_pos)).mp
      (normalized.trans (Rat.normalize_self (left + right)).symm)
  change (left + right).num * (denominator : Int) =
    numerator * ((left + right).den : Int)
  exact sameValue.symm

theorem fromRat_zero (value : Rat) :
    isZero (fromRat value) = decide (value = 0) := by
  have h : value.num = 0 ↔ value = 0 := by
    rw [Rat.eq_iff_mul_eq_mul]
    simp
  simp only [isZero, fromRat, h]

theorem fromRat_add_zero (left right : Rat) :
    isZero (add (fromRat left) (fromRat right)) =
      decide (left + right = 0) := by
  rw [← equivalent_isZero (fromRat_add left right), fromRat_zero]

end E7CS1RatArithmetic
