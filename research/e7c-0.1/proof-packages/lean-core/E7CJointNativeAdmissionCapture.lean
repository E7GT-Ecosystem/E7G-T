import E7CJointRawJsonAdmission

/- Local constructor-result receipts. The evidence is data, not a completed
admission trace. Its native origin, dispatch, object denotation and stability
remain trusted. In particular these theorems do not classify host exits. -/
namespace E7CJointNativeAdmissionCapture
open E7CJointRawJsonAdmission

/-- A strict integer check for observed Fraction fields. This layer does not
invoke the legacy Rat division primitive used by the raw decoder. -/
def fractionFieldsChecked (inputNumerator inputDenominator outputNumerator : Int)
    (outputDenominator : Nat) : Bool :=
  decide (inputDenominator > 0) && (decide (inputNumerator ≠ 0) &&
    (decide (outputDenominator > 0) && decide
      (outputNumerator * inputDenominator = inputNumerator * Int.ofNat outputDenominator)))

theorem checked_fraction_fields (inputNumerator inputDenominator outputNumerator : Int)
    (outputDenominator : Nat)
    (checked : fractionFieldsChecked inputNumerator inputDenominator outputNumerator
      outputDenominator = true) :
    inputDenominator > 0 ∧ inputNumerator ≠ 0 ∧ outputDenominator > 0 ∧
      outputNumerator * inputDenominator = inputNumerator * Int.ofNat outputDenominator := by
  simpa [fractionFieldsChecked, Bool.and_eq_true] using checked

theorem exact_integer_kind_excludes_boolean (value : Bool) :
    exactInteger (.boolean value) = none := rfl

end E7CJointNativeAdmissionCapture

