/-
EvoByte Formal Proof Catalog: Multiterm and Coprime Egyptian Fraction Theorems (P86).
-/

import Mathlib.Tactic.NormNum
import Mathlib.Data.Rat.Defs

/-- Multiterm Egyptian fraction for erdos_straus 4/5 with 3 terms (P86).
    Guarantees exact rational balance 4/5 = ∑ 1/x_i without unproven axioms or holes. -/
theorem multiterm_frac_es_5_3t : (4 : ℚ) / 5 = 1 / 2 + 1 / 5 + 1 / 10 := by
  norm_num

/-- Multiterm Egyptian fraction exact Diophantine integer balance for 4/5 (P86).
    Guarantees 4 * ∏ x_i = 5 * ∑ (∏_{j≠i} x_j) without unproven axioms or holes. -/
theorem multiterm_int_es_5_3t : 4 * (2 * 5 * 10 : ℤ) = 5 * ((5 * 10 : ℤ) + (2 * 10 : ℤ) + (2 * 5 : ℤ)) := by
  norm_num

/-- Multiterm Egyptian fraction strict coprimality constraint gcd(2, 5, 10) = 1 (P86).
    Verified by kernel decision procedure without unproven axioms or holes. -/
theorem multiterm_coprime_es_5_3t : Nat.gcd (Nat.gcd 2 5) 10 = 1 := by
  decide

/-- Multiterm Egyptian fraction for erdos_straus 4/7 with 3 terms (P86).
    Guarantees exact rational balance 4/7 = ∑ 1/x_i without unproven axioms or holes. -/
theorem multiterm_frac_es_7_3t : (4 : ℚ) / 7 = 1 / 2 + 1 / 21 + 1 / 42 := by
  norm_num

/-- Multiterm Egyptian fraction exact Diophantine integer balance for 4/7 (P86).
    Guarantees 4 * ∏ x_i = 7 * ∑ (∏_{j≠i} x_j) without unproven axioms or holes. -/
theorem multiterm_int_es_7_3t : 4 * (2 * 21 * 42 : ℤ) = 7 * ((21 * 42 : ℤ) + (2 * 42 : ℤ) + (2 * 21 : ℤ)) := by
  norm_num

/-- Multiterm Egyptian fraction strict coprimality constraint gcd(2, 21, 42) = 1 (P86).
    Verified by kernel decision procedure without unproven axioms or holes. -/
theorem multiterm_coprime_es_7_3t : Nat.gcd (Nat.gcd 2 21) 42 = 1 := by
  decide

/-- Multiterm Egyptian fraction for erdos_straus 4/11 with 3 terms (P86).
    Guarantees exact rational balance 4/11 = ∑ 1/x_i without unproven axioms or holes. -/
theorem multiterm_frac_es_11_3t : (4 : ℚ) / 11 = 1 / 3 + 1 / 44 + 1 / 132 := by
  norm_num

/-- Multiterm Egyptian fraction exact Diophantine integer balance for 4/11 (P86).
    Guarantees 4 * ∏ x_i = 11 * ∑ (∏_{j≠i} x_j) without unproven axioms or holes. -/
theorem multiterm_int_es_11_3t : 4 * (3 * 44 * 132 : ℤ) = 11 * ((44 * 132 : ℤ) + (3 * 132 : ℤ) + (3 * 44 : ℤ)) := by
  norm_num

/-- Multiterm Egyptian fraction strict coprimality constraint gcd(3, 44, 132) = 1 (P86).
    Verified by kernel decision procedure without unproven axioms or holes. -/
theorem multiterm_coprime_es_11_3t : Nat.gcd (Nat.gcd 3 44) 132 = 1 := by
  decide

/-- Multiterm Egyptian fraction for erdos_straus 4/29 with 3 terms (P86).
    Guarantees exact rational balance 4/29 = ∑ 1/x_i without unproven axioms or holes. -/
theorem multiterm_frac_es_29_3t : (4 : ℚ) / 29 = 1 / 8 + 1 / 87 + 1 / 696 := by
  norm_num

/-- Multiterm Egyptian fraction exact Diophantine integer balance for 4/29 (P86).
    Guarantees 4 * ∏ x_i = 29 * ∑ (∏_{j≠i} x_j) without unproven axioms or holes. -/
theorem multiterm_int_es_29_3t : 4 * (8 * 87 * 696 : ℤ) = 29 * ((87 * 696 : ℤ) + (8 * 696 : ℤ) + (8 * 87 : ℤ)) := by
  norm_num

/-- Multiterm Egyptian fraction strict coprimality constraint gcd(8, 87, 696) = 1 (P86).
    Verified by kernel decision procedure without unproven axioms or holes. -/
theorem multiterm_coprime_es_29_3t : Nat.gcd (Nat.gcd 8 87) 696 = 1 := by
  decide

/-- Multiterm Egyptian fraction for erdos_straus 4/121 with 3 terms (P86).
    Guarantees exact rational balance 4/121 = ∑ 1/x_i without unproven axioms or holes. -/
theorem multiterm_frac_es_121_3t : (4 : ℚ) / 121 = 1 / 31 + 1 / 1694 + 1 / 4774 := by
  norm_num

/-- Multiterm Egyptian fraction exact Diophantine integer balance for 4/121 (P86).
    Guarantees 4 * ∏ x_i = 121 * ∑ (∏_{j≠i} x_j) without unproven axioms or holes. -/
theorem multiterm_int_es_121_3t : 4 * (31 * 1694 * 4774 : ℤ) = 121 * ((1694 * 4774 : ℤ) + (31 * 4774 : ℤ) + (31 * 1694 : ℤ)) := by
  norm_num

/-- Multiterm Egyptian fraction strict coprimality constraint gcd(31, 1694, 4774) = 1 (P86).
    Verified by kernel decision procedure without unproven axioms or holes. -/
theorem multiterm_coprime_es_121_3t : Nat.gcd (Nat.gcd 31 1694) 4774 = 1 := by
  decide

/-- Multiterm Egyptian fraction for sierpinski 5/9 with 3 terms (P86).
    Guarantees exact rational balance 5/9 = ∑ 1/x_i without unproven axioms or holes. -/
theorem multiterm_frac_sier_9_3t : (5 : ℚ) / 9 = 1 / 2 + 1 / 30 + 1 / 45 := by
  norm_num

/-- Multiterm Egyptian fraction exact Diophantine integer balance for 5/9 (P86).
    Guarantees 5 * ∏ x_i = 9 * ∑ (∏_{j≠i} x_j) without unproven axioms or holes. -/
theorem multiterm_int_sier_9_3t : 5 * (2 * 30 * 45 : ℤ) = 9 * ((30 * 45 : ℤ) + (2 * 45 : ℤ) + (2 * 30 : ℤ)) := by
  norm_num

/-- Multiterm Egyptian fraction strict coprimality constraint gcd(2, 30, 45) = 1 (P86).
    Verified by kernel decision procedure without unproven axioms or holes. -/
theorem multiterm_coprime_sier_9_3t : Nat.gcd (Nat.gcd 2 30) 45 = 1 := by
  decide

/-- Multiterm Egyptian fraction for erdos_straus 4/5 with 4 terms (P86).
    Guarantees exact rational balance 4/5 = ∑ 1/x_i without unproven axioms or holes. -/
theorem multiterm_frac_es_5_4t : (4 : ℚ) / 5 = 1 / 2 + 1 / 4 + 1 / 36 + 1 / 45 := by
  norm_num

/-- Multiterm Egyptian fraction exact Diophantine integer balance for 4/5 (P86).
    Guarantees 4 * ∏ x_i = 5 * ∑ (∏_{j≠i} x_j) without unproven axioms or holes. -/
theorem multiterm_int_es_5_4t : 4 * (2 * 4 * 36 * 45 : ℤ) = 5 * ((4 * 36 * 45 : ℤ) + (2 * 36 * 45 : ℤ) + (2 * 4 * 45 : ℤ) + (2 * 4 * 36 : ℤ)) := by
  norm_num

/-- Multiterm Egyptian fraction strict coprimality constraint gcd(2, 4, 36, 45) = 1 (P86).
    Verified by kernel decision procedure without unproven axioms or holes. -/
theorem multiterm_coprime_es_5_4t : Nat.gcd (Nat.gcd (Nat.gcd 2 4) 36) 45 = 1 := by
  decide

/-- Multiterm Egyptian fraction for erdos_straus 4/13 with 4 terms (P86).
    Guarantees exact rational balance 4/13 = ∑ 1/x_i without unproven axioms or holes. -/
theorem multiterm_frac_es_13_4t : (4 : ℚ) / 13 = 1 / 4 + 1 / 18 + 1 / 900 + 1 / 975 := by
  norm_num

/-- Multiterm Egyptian fraction exact Diophantine integer balance for 4/13 (P86).
    Guarantees 4 * ∏ x_i = 13 * ∑ (∏_{j≠i} x_j) without unproven axioms or holes. -/
theorem multiterm_int_es_13_4t : 4 * (4 * 18 * 900 * 975 : ℤ) = 13 * ((18 * 900 * 975 : ℤ) + (4 * 900 * 975 : ℤ) + (4 * 18 * 975 : ℤ) + (4 * 18 * 900 : ℤ)) := by
  norm_num

/-- Multiterm Egyptian fraction strict coprimality constraint gcd(4, 18, 900, 975) = 1 (P86).
    Verified by kernel decision procedure without unproven axioms or holes. -/
theorem multiterm_coprime_es_13_4t : Nat.gcd (Nat.gcd (Nat.gcd 4 18) 900) 975 = 1 := by
  decide

/-- Multiterm Egyptian fraction for erdos_straus 4/169 with 4 terms (P86).
    Guarantees exact rational balance 4/169 = ∑ 1/x_i without unproven axioms or holes. -/
theorem multiterm_frac_es_169_4t : (4 : ℚ) / 169 = 1 / 43 + 1 / 2423 + 1 / 11739435 + 1 / 35208615 := by
  norm_num

/-- Multiterm Egyptian fraction exact Diophantine integer balance for 4/169 (P86).
    Guarantees 4 * ∏ x_i = 169 * ∑ (∏_{j≠i} x_j) without unproven axioms or holes. -/
theorem multiterm_int_es_169_4t : 4 * (43 * 2423 * 11739435 * 35208615 : ℤ) = 169 * ((2423 * 11739435 * 35208615 : ℤ) + (43 * 11739435 * 35208615 : ℤ) + (43 * 2423 * 35208615 : ℤ) + (43 * 2423 * 11739435 : ℤ)) := by
  norm_num

/-- Multiterm Egyptian fraction strict coprimality constraint gcd(43, 2423, 11739435, 35208615) = 1 (P86).
    Verified by kernel decision procedure without unproven axioms or holes. -/
theorem multiterm_coprime_es_169_4t : Nat.gcd (Nat.gcd (Nat.gcd 43 2423) 11739435) 35208615 = 1 := by
  decide

/-- Multiterm Egyptian fraction for erdos_straus 4/289 with 4 terms (P86).
    Guarantees exact rational balance 4/289 = ∑ 1/x_i without unproven axioms or holes. -/
theorem multiterm_frac_es_289_4t : (4 : ℚ) / 289 = 1 / 73 + 1 / 7033 + 1 / 130919295 + 1 / 171202155 := by
  norm_num

/-- Multiterm Egyptian fraction exact Diophantine integer balance for 4/289 (P86).
    Guarantees 4 * ∏ x_i = 289 * ∑ (∏_{j≠i} x_j) without unproven axioms or holes. -/
theorem multiterm_int_es_289_4t : 4 * (73 * 7033 * 130919295 * 171202155 : ℤ) = 289 * ((7033 * 130919295 * 171202155 : ℤ) + (73 * 130919295 * 171202155 : ℤ) + (73 * 7033 * 171202155 : ℤ) + (73 * 7033 * 130919295 : ℤ)) := by
  norm_num

/-- Multiterm Egyptian fraction strict coprimality constraint gcd(73, 7033, 130919295, 171202155) = 1 (P86).
    Verified by kernel decision procedure without unproven axioms or holes. -/
theorem multiterm_coprime_es_289_4t : Nat.gcd (Nat.gcd (Nat.gcd 73 7033) 130919295) 171202155 = 1 := by
  decide

/-- Multiterm Egyptian fraction for sierpinski 5/7 with 4 terms (P86).
    Guarantees exact rational balance 5/7 = ∑ 1/x_i without unproven axioms or holes. -/
theorem multiterm_frac_sier_7_4t : (5 : ℚ) / 7 = 1 / 2 + 1 / 5 + 1 / 120 + 1 / 168 := by
  norm_num

/-- Multiterm Egyptian fraction exact Diophantine integer balance for 5/7 (P86).
    Guarantees 5 * ∏ x_i = 7 * ∑ (∏_{j≠i} x_j) without unproven axioms or holes. -/
theorem multiterm_int_sier_7_4t : 5 * (2 * 5 * 120 * 168 : ℤ) = 7 * ((5 * 120 * 168 : ℤ) + (2 * 120 * 168 : ℤ) + (2 * 5 * 168 : ℤ) + (2 * 5 * 120 : ℤ)) := by
  norm_num

/-- Multiterm Egyptian fraction strict coprimality constraint gcd(2, 5, 120, 168) = 1 (P86).
    Verified by kernel decision procedure without unproven axioms or holes. -/
theorem multiterm_coprime_sier_7_4t : Nat.gcd (Nat.gcd (Nat.gcd 2 5) 120) 168 = 1 := by
  decide

/-- Multiterm Egyptian fraction for sierpinski 5/49 with 4 terms (P86).
    Guarantees exact rational balance 5/49 = ∑ 1/x_i without unproven axioms or holes. -/
theorem multiterm_frac_sier_49_4t : (5 : ℚ) / 49 = 1 / 10 + 1 / 491 + 1 / 480690 + 1 / 481671 := by
  norm_num

/-- Multiterm Egyptian fraction exact Diophantine integer balance for 5/49 (P86).
    Guarantees 5 * ∏ x_i = 49 * ∑ (∏_{j≠i} x_j) without unproven axioms or holes. -/
theorem multiterm_int_sier_49_4t : 5 * (10 * 491 * 480690 * 481671 : ℤ) = 49 * ((491 * 480690 * 481671 : ℤ) + (10 * 480690 * 481671 : ℤ) + (10 * 491 * 481671 : ℤ) + (10 * 491 * 480690 : ℤ)) := by
  norm_num

/-- Multiterm Egyptian fraction strict coprimality constraint gcd(10, 491, 480690, 481671) = 1 (P86).
    Verified by kernel decision procedure without unproven axioms or holes. -/
theorem multiterm_coprime_sier_49_4t : Nat.gcd (Nat.gcd (Nat.gcd 10 491) 480690) 481671 = 1 := by
  decide
