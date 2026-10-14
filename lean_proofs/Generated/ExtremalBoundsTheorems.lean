/-
EvoByte Formal Proof Catalog: Certified Extremal Coordinate Bounds and Subcubic Minima (P92).
Formal proofs in Lean 4 kernel bounding max(x, y, z) <= C * n^2 < n^3 for Diophantine unit fraction solutions.
-/

import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Data.Rat.Defs

/- Section 1: Parametric Coordinate Bounds across Congruence Families (P92). -/

/-- Parametric coordinate bound for x in n = 4k + 3 family: x(k) ≤ n(k) (P92). -/
theorem param_bound_x_4k3 (k : ℕ) : k + 1 ≤ 4 * k + 3 := by
  omega

/-- Parametric coordinate bound for y, z in n = 4k + 3 family: y(k) ≤ n(k)^2 (P92). -/
theorem param_bound_yz_4k3 (k : ℕ) : (k + 1) * (4 * k + 3) ≤ (4 * k + 3) ^ 2 := by
  have h1 : (k + 1) * (4 * k + 3) = 4 * k ^ 2 + 7 * k + 3 := by ring
  have h2 : (4 * k + 3) ^ 2 = 16 * k ^ 2 + 24 * k + 9 := by ring
  rw [h1, h2]
  omega

/-- Parametric coordinate bound for x in n = 8k + 5 family: x(k) ≤ n(k) (P92). -/
theorem param_bound_x_8k5 (k : ℕ) : 2 * k + 2 ≤ 8 * k + 5 := by
  omega

/-- Parametric coordinate bound for y, z in n = 8k + 5 family: y(k) ≤ n(k)^2 (P92). -/
theorem param_bound_yz_8k5 (k : ℕ) : (k + 1) * (8 * k + 5) ≤ (8 * k + 5) ^ 2 := by
  have h1 : (k + 1) * (8 * k + 5) = 8 * k ^ 2 + 13 * k + 5 := by ring
  have h2 : (8 * k + 5) ^ 2 = 64 * k ^ 2 + 80 * k + 25 := by ring
  rw [h1, h2]
  omega

/-- Parametric coordinate bound for x in n = 12k + 7 family: x(k) ≤ n(k) (P92). -/
theorem param_bound_x_12k7 (k : ℕ) : 3 * k + 2 ≤ 12 * k + 7 := by
  omega

/-- Parametric coordinate bound for y, z in n = 12k + 7 family: y(k) ≤ n(k)^2 (P92). -/
theorem param_bound_yz_12k7 (k : ℕ) : (k + 1) * (12 * k + 7) ≤ (12 * k + 7) ^ 2 := by
  have h1 : (k + 1) * (12 * k + 7) = 12 * k ^ 2 + 19 * k + 7 := by ring
  have h2 : (12 * k + 7) ^ 2 = 144 * k ^ 2 + 168 * k + 49 := by ring
  rw [h1, h2]
  omega

/-- Parametric coordinate bound for x in n = 24k + 11 family: x(k) ≤ n(k) (P92). -/
theorem param_bound_x_24k11 (k : ℕ) : 6 * k + 3 ≤ 24 * k + 11 := by
  omega

/-- Parametric coordinate bound for y, z in n = 24k + 11 family: y(k) ≤ n(k)^2 (P92). -/
theorem param_bound_yz_24k11 (k : ℕ) : (k + 1) * (24 * k + 11) ≤ (24 * k + 11) ^ 2 := by
  have h1 : (k + 1) * (24 * k + 11) = 24 * k ^ 2 + 35 * k + 11 := by ring
  have h2 : (24 * k + 11) ^ 2 = 576 * k ^ 2 + 528 * k + 121 := by ring
  rw [h1, h2]
  omega

/-- Parametric coordinate bound for x in n = 24k + 19 family: x(k) ≤ n(k) (P92). -/
theorem param_bound_x_24k19 (k : ℕ) : 6 * k + 5 ≤ 24 * k + 19 := by
  omega

/-- Parametric coordinate bound for y, z in n = 24k + 19 family: y(k) ≤ n(k)^2 (P92). -/
theorem param_bound_yz_24k19 (k : ℕ) : (k + 1) * (24 * k + 19) ≤ (24 * k + 19) ^ 2 := by
  have h1 : (k + 1) * (24 * k + 19) = 24 * k ^ 2 + 43 * k + 19 := by ring
  have h2 : (24 * k + 19) ^ 2 = 576 * k ^ 2 + 912 * k + 361 := by ring
  rw [h1, h2]
  omega

/-- Parametric coordinate bound for x in n = 24k + 23 family: x(k) ≤ n(k) (P92). -/
theorem param_bound_x_24k23 (k : ℕ) : 6 * k + 6 ≤ 24 * k + 23 := by
  omega

/-- Parametric coordinate bound for y, z in n = 24k + 23 family: y(k) ≤ n(k)^2 (P92). -/
theorem param_bound_yz_24k23 (k : ℕ) : (k + 1) * (24 * k + 23) ≤ (24 * k + 23) ^ 2 := by
  have h1 : (k + 1) * (24 * k + 23) = 24 * k ^ 2 + 47 * k + 23 := by ring
  have h2 : (24 * k + 23) ^ 2 = 576 * k ^ 2 + 1104 * k + 529 := by ring
  rw [h1, h2]
  omega

/- Section 2: Certified Instance Extremal Coordinate Bounds (P92). -/

/-- Certified unit fraction solution for a = 4, n = 73: coordinates (20, 292, 730) (P92). -/
theorem bound_cert_a4_n73_frac : (4 : ℚ) / 73 = (1 : ℚ) / 20 + (1 : ℚ) / 292 + (1 : ℚ) / 730 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 73 (P92). -/
theorem bound_cert_a4_n73_quad : (max 20 (max 292 730) : ℕ) ≤ 1 * 73 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 73 (P92). -/
theorem bound_cert_a4_n73_subcubic : (max 20 (max 292 730) : ℕ) < 73 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 97: coordinates (28, 194, 2716) (P92). -/
theorem bound_cert_a4_n97_frac : (4 : ℚ) / 97 = (1 : ℚ) / 28 + (1 : ℚ) / 194 + (1 : ℚ) / 2716 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 97 (P92). -/
theorem bound_cert_a4_n97_quad : (max 28 (max 194 2716) : ℕ) ≤ 1 * 97 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 97 (P92). -/
theorem bound_cert_a4_n97_subcubic : (max 28 (max 194 2716) : ℕ) < 97 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 193: coordinates (50, 1930, 4825) (P92). -/
theorem bound_cert_a4_n193_frac : (4 : ℚ) / 193 = (1 : ℚ) / 50 + (1 : ℚ) / 1930 + (1 : ℚ) / 4825 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 193 (P92). -/
theorem bound_cert_a4_n193_quad : (max 50 (max 1930 4825) : ℕ) ≤ 1 * 193 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 193 (P92). -/
theorem bound_cert_a4_n193_subcubic : (max 50 (max 1930 4825) : ℕ) < 193 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 241: coordinates (66, 723, 15906) (P92). -/
theorem bound_cert_a4_n241_frac : (4 : ℚ) / 241 = (1 : ℚ) / 66 + (1 : ℚ) / 723 + (1 : ℚ) / 15906 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 241 (P92). -/
theorem bound_cert_a4_n241_quad : (max 66 (max 723 15906) : ℕ) ≤ 1 * 241 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 241 (P92). -/
theorem bound_cert_a4_n241_subcubic : (max 66 (max 723 15906) : ℕ) < 241 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 313: coordinates (80, 5008, 12520) (P92). -/
theorem bound_cert_a4_n313_frac : (4 : ℚ) / 313 = (1 : ℚ) / 80 + (1 : ℚ) / 5008 + (1 : ℚ) / 12520 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 313 (P92). -/
theorem bound_cert_a4_n313_quad : (max 80 (max 5008 12520) : ℕ) ≤ 1 * 313 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 313 (P92). -/
theorem bound_cert_a4_n313_subcubic : (max 80 (max 5008 12520) : ℕ) < 313 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 337: coordinates (90, 1685, 6066) (P92). -/
theorem bound_cert_a4_n337_frac : (4 : ℚ) / 337 = (1 : ℚ) / 90 + (1 : ℚ) / 1685 + (1 : ℚ) / 6066 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 337 (P92). -/
theorem bound_cert_a4_n337_quad : (max 90 (max 1685 6066) : ℕ) ≤ 1 * 337 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 337 (P92). -/
theorem bound_cert_a4_n337_subcubic : (max 90 (max 1685 6066) : ℕ) < 337 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 409: coordinates (105, 5726, 12270) (P92). -/
theorem bound_cert_a4_n409_frac : (4 : ℚ) / 409 = (1 : ℚ) / 105 + (1 : ℚ) / 5726 + (1 : ℚ) / 12270 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 409 (P92). -/
theorem bound_cert_a4_n409_quad : (max 105 (max 5726 12270) : ℕ) ≤ 1 * 409 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 409 (P92). -/
theorem bound_cert_a4_n409_subcubic : (max 105 (max 5726 12270) : ℕ) < 409 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 457: coordinates (120, 3656, 6855) (P92). -/
theorem bound_cert_a4_n457_frac : (4 : ℚ) / 457 = (1 : ℚ) / 120 + (1 : ℚ) / 3656 + (1 : ℚ) / 6855 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 457 (P92). -/
theorem bound_cert_a4_n457_quad : (max 120 (max 3656 6855) : ℕ) ≤ 1 * 457 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 457 (P92). -/
theorem bound_cert_a4_n457_subcubic : (max 120 (max 3656 6855) : ℕ) < 457 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 1009: coordinates (260, 10090, 52468) (P92). -/
theorem bound_cert_a4_n1009_frac : (4 : ℚ) / 1009 = (1 : ℚ) / 260 + (1 : ℚ) / 10090 + (1 : ℚ) / 52468 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 1009 (P92). -/
theorem bound_cert_a4_n1009_quad : (max 260 (max 10090 52468) : ℕ) ≤ 1 * 1009 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 1009 (P92). -/
theorem bound_cert_a4_n1009_subcubic : (max 260 (max 10090 52468) : ℕ) < 1009 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 1129: coordinates (286, 24838, 161447) (P92). -/
theorem bound_cert_a4_n1129_frac : (4 : ℚ) / 1129 = (1 : ℚ) / 286 + (1 : ℚ) / 24838 + (1 : ℚ) / 161447 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 1129 (P92). -/
theorem bound_cert_a4_n1129_quad : (max 286 (max 24838 161447) : ℕ) ≤ 1 * 1129 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 1129 (P92). -/
theorem bound_cert_a4_n1129_subcubic : (max 286 (max 24838 161447) : ℕ) < 1129 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 1201: coordinates (312, 9608, 46839) (P92). -/
theorem bound_cert_a4_n1201_frac : (4 : ℚ) / 1201 = (1 : ℚ) / 312 + (1 : ℚ) / 9608 + (1 : ℚ) / 46839 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 1201 (P92). -/
theorem bound_cert_a4_n1201_quad : (max 312 (max 9608 46839) : ℕ) ≤ 1 * 1201 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 1201 (P92). -/
theorem bound_cert_a4_n1201_subcubic : (max 312 (max 9608 46839) : ℕ) < 1201 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 1369: coordinates (350, 25900, 38332) (P92). -/
theorem bound_cert_a4_n1369_frac : (4 : ℚ) / 1369 = (1 : ℚ) / 350 + (1 : ℚ) / 25900 + (1 : ℚ) / 38332 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 1369 (P92). -/
theorem bound_cert_a4_n1369_quad : (max 350 (max 25900 38332) : ℕ) ≤ 1 * 1369 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 1369 (P92). -/
theorem bound_cert_a4_n1369_subcubic : (max 350 (max 25900 38332) : ℕ) < 1369 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 1681: coordinates (434, 17794, 52111) (P92). -/
theorem bound_cert_a4_n1681_frac : (4 : ℚ) / 1681 = (1 : ℚ) / 434 + (1 : ℚ) / 17794 + (1 : ℚ) / 52111 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 1681 (P92). -/
theorem bound_cert_a4_n1681_quad : (max 434 (max 17794 52111) : ℕ) ≤ 1 * 1681 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 1681 (P92). -/
theorem bound_cert_a4_n1681_subcubic : (max 434 (max 17794 52111) : ℕ) < 1681 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 1801: coordinates (462, 25214, 59433) (P92). -/
theorem bound_cert_a4_n1801_frac : (4 : ℚ) / 1801 = (1 : ℚ) / 462 + (1 : ℚ) / 25214 + (1 : ℚ) / 59433 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 1801 (P92). -/
theorem bound_cert_a4_n1801_quad : (max 462 (max 25214 59433) : ℕ) ≤ 1 * 1801 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 1801 (P92). -/
theorem bound_cert_a4_n1801_subcubic : (max 462 (max 25214 59433) : ℕ) < 1801 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 1849: coordinates (473, 40678, 40678) (P92). -/
theorem bound_cert_a4_n1849_frac : (4 : ℚ) / 1849 = (1 : ℚ) / 473 + (1 : ℚ) / 40678 + (1 : ℚ) / 40678 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 1849 (P92). -/
theorem bound_cert_a4_n1849_quad : (max 473 (max 40678 40678) : ℕ) ≤ 1 * 1849 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 1849 (P92). -/
theorem bound_cert_a4_n1849_subcubic : (max 473 (max 40678 40678) : ℕ) < 1849 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 1969: coordinates (511, 26134, 27566) (P92). -/
theorem bound_cert_a4_n1969_frac : (4 : ℚ) / 1969 = (1 : ℚ) / 511 + (1 : ℚ) / 26134 + (1 : ℚ) / 27566 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 1969 (P92). -/
theorem bound_cert_a4_n1969_quad : (max 511 (max 26134 27566) : ℕ) ≤ 1 * 1969 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 1969 (P92). -/
theorem bound_cert_a4_n1969_subcubic : (max 511 (max 26134 27566) : ℕ) < 1969 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 2003: coordinates (504, 144216, 168252) (P92). -/
theorem bound_cert_a4_n2003_frac : (4 : ℚ) / 2003 = (1 : ℚ) / 504 + (1 : ℚ) / 144216 + (1 : ℚ) / 168252 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 2003 (P92). -/
theorem bound_cert_a4_n2003_quad : (max 504 (max 144216 168252) : ℕ) ≤ 1 * 2003 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 2003 (P92). -/
theorem bound_cert_a4_n2003_subcubic : (max 504 (max 144216 168252) : ℕ) < 2003 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 2041: coordinates (540, 16956, 20410) (P92). -/
theorem bound_cert_a4_n2041_frac : (4 : ℚ) / 2041 = (1 : ℚ) / 540 + (1 : ℚ) / 16956 + (1 : ℚ) / 20410 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 2041 (P92). -/
theorem bound_cert_a4_n2041_quad : (max 540 (max 16956 20410) : ℕ) ≤ 1 * 2041 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 2041 (P92). -/
theorem bound_cert_a4_n2041_subcubic : (max 540 (max 16956 20410) : ℕ) < 2041 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 2209: coordinates (580, 20445, 26508) (P92). -/
theorem bound_cert_a4_n2209_frac : (4 : ℚ) / 2209 = (1 : ℚ) / 580 + (1 : ℚ) / 20445 + (1 : ℚ) / 26508 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 2209 (P92). -/
theorem bound_cert_a4_n2209_quad : (max 580 (max 20445 26508) : ℕ) ≤ 1 * 2209 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 2209 (P92). -/
theorem bound_cert_a4_n2209_subcubic : (max 580 (max 20445 26508) : ℕ) < 2209 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 2521: coordinates (638, 55462, 804199) (P92). -/
theorem bound_cert_a4_n2521_frac : (4 : ℚ) / 2521 = (1 : ℚ) / 638 + (1 : ℚ) / 55462 + (1 : ℚ) / 804199 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 2521 (P92). -/
theorem bound_cert_a4_n2521_quad : (max 638 (max 55462 804199) : ℕ) ≤ 1 * 2521 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 2521 (P92). -/
theorem bound_cert_a4_n2521_subcubic : (max 638 (max 55462 804199) : ℕ) < 2521 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 2641: coordinates (684, 34472, 42408) (P92). -/
theorem bound_cert_a4_n2641_frac : (4 : ℚ) / 2641 = (1 : ℚ) / 684 + (1 : ℚ) / 34472 + (1 : ℚ) / 42408 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 2641 (P92). -/
theorem bound_cert_a4_n2641_quad : (max 684 (max 34472 42408) : ℕ) ≤ 1 * 2641 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 2641 (P92). -/
theorem bound_cert_a4_n2641_subcubic : (max 684 (max 34472 42408) : ℕ) < 2641 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 2689: coordinates (684, 48402, 204364) (P92). -/
theorem bound_cert_a4_n2689_frac : (4 : ℚ) / 2689 = (1 : ℚ) / 684 + (1 : ℚ) / 48402 + (1 : ℚ) / 204364 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 2689 (P92). -/
theorem bound_cert_a4_n2689_quad : (max 684 (max 48402 204364) : ℕ) ≤ 1 * 2689 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 2689 (P92). -/
theorem bound_cert_a4_n2689_subcubic : (max 684 (max 48402 204364) : ℕ) < 2689 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 2809: coordinates (712, 94340, 112360) (P92). -/
theorem bound_cert_a4_n2809_frac : (4 : ℚ) / 2809 = (1 : ℚ) / 712 + (1 : ℚ) / 94340 + (1 : ℚ) / 112360 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 2809 (P92). -/
theorem bound_cert_a4_n2809_quad : (max 712 (max 94340 112360) : ℕ) ≤ 1 * 2809 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 2809 (P92). -/
theorem bound_cert_a4_n2809_subcubic : (max 712 (max 94340 112360) : ℕ) < 2809 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 2881: coordinates (737, 63382, 63382) (P92). -/
theorem bound_cert_a4_n2881_frac : (4 : ℚ) / 2881 = (1 : ℚ) / 737 + (1 : ℚ) / 63382 + (1 : ℚ) / 63382 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 2881 (P92). -/
theorem bound_cert_a4_n2881_quad : (max 737 (max 63382 63382) : ℕ) ≤ 1 * 2881 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 2881 (P92). -/
theorem bound_cert_a4_n2881_subcubic : (max 737 (max 63382 63382) : ℕ) < 2881 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 4, n = 3049: coordinates (780, 36588, 396370) (P92). -/
theorem bound_cert_a4_n3049_frac : (4 : ℚ) / 3049 = (1 : ℚ) / 780 + (1 : ℚ) / 36588 + (1 : ℚ) / 396370 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 4, n = 3049 (P92). -/
theorem bound_cert_a4_n3049_quad : (max 780 (max 36588 396370) : ℕ) ≤ 1 * 3049 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 4, n = 3049 (P92). -/
theorem bound_cert_a4_n3049_subcubic : (max 780 (max 36588 396370) : ℕ) < 3049 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 73: coordinates (15, 1095, 1095) (P92). -/
theorem bound_cert_a5_n73_frac : (5 : ℚ) / 73 = (1 : ℚ) / 15 + (1 : ℚ) / 1095 + (1 : ℚ) / 1095 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 73 (P92). -/
theorem bound_cert_a5_n73_quad : (max 15 (max 1095 1095) : ℕ) ≤ 1 * 73 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 73 (P92). -/
theorem bound_cert_a5_n73_subcubic : (max 15 (max 1095 1095) : ℕ) < 73 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 97: coordinates (22, 194, 1067) (P92). -/
theorem bound_cert_a5_n97_frac : (5 : ℚ) / 97 = (1 : ℚ) / 22 + (1 : ℚ) / 194 + (1 : ℚ) / 1067 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 97 (P92). -/
theorem bound_cert_a5_n97_quad : (max 22 (max 194 1067) : ℕ) ≤ 1 * 97 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 97 (P92). -/
theorem bound_cert_a5_n97_subcubic : (max 22 (max 194 1067) : ℕ) < 97 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 193: coordinates (42, 579, 2702) (P92). -/
theorem bound_cert_a5_n193_frac : (5 : ℚ) / 193 = (1 : ℚ) / 42 + (1 : ℚ) / 579 + (1 : ℚ) / 2702 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 193 (P92). -/
theorem bound_cert_a5_n193_quad : (max 42 (max 579 2702) : ℕ) ≤ 1 * 193 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 193 (P92). -/
theorem bound_cert_a5_n193_subcubic : (max 42 (max 579 2702) : ℕ) < 193 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 241: coordinates (54, 482, 6507) (P92). -/
theorem bound_cert_a5_n241_frac : (5 : ℚ) / 241 = (1 : ℚ) / 54 + (1 : ℚ) / 482 + (1 : ℚ) / 6507 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 241 (P92). -/
theorem bound_cert_a5_n241_quad : (max 54 (max 482 6507) : ℕ) ≤ 1 * 241 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 241 (P92). -/
theorem bound_cert_a5_n241_subcubic : (max 54 (max 482 6507) : ℕ) < 241 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 313: coordinates (66, 1878, 3443) (P92). -/
theorem bound_cert_a5_n313_frac : (5 : ℚ) / 313 = (1 : ℚ) / 66 + (1 : ℚ) / 1878 + (1 : ℚ) / 3443 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 313 (P92). -/
theorem bound_cert_a5_n313_quad : (max 66 (max 1878 3443) : ℕ) ≤ 1 * 313 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 313 (P92). -/
theorem bound_cert_a5_n313_subcubic : (max 66 (max 1878 3443) : ℕ) < 313 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 337: coordinates (68, 11458, 22916) (P92). -/
theorem bound_cert_a5_n337_frac : (5 : ℚ) / 337 = (1 : ℚ) / 68 + (1 : ℚ) / 11458 + (1 : ℚ) / 22916 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 337 (P92). -/
theorem bound_cert_a5_n337_quad : (max 68 (max 11458 22916) : ℕ) ≤ 1 * 337 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 337 (P92). -/
theorem bound_cert_a5_n337_subcubic : (max 68 (max 11458 22916) : ℕ) < 337 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 409: coordinates (84, 4908, 8589) (P92). -/
theorem bound_cert_a5_n409_frac : (5 : ℚ) / 409 = (1 : ℚ) / 84 + (1 : ℚ) / 4908 + (1 : ℚ) / 8589 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 409 (P92). -/
theorem bound_cert_a5_n409_quad : (max 84 (max 4908 8589) : ℕ) ≤ 1 * 409 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 409 (P92). -/
theorem bound_cert_a5_n409_subcubic : (max 84 (max 4908 8589) : ℕ) < 409 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 457: coordinates (102, 914, 23307) (P92). -/
theorem bound_cert_a5_n457_frac : (5 : ℚ) / 457 = (1 : ℚ) / 102 + (1 : ℚ) / 914 + (1 : ℚ) / 23307 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 457 (P92). -/
theorem bound_cert_a5_n457_quad : (max 102 (max 914 23307) : ℕ) ≤ 1 * 457 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 457 (P92). -/
theorem bound_cert_a5_n457_subcubic : (max 102 (max 914 23307) : ℕ) < 457 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 1009: coordinates (210, 6054, 35315) (P92). -/
theorem bound_cert_a5_n1009_frac : (5 : ℚ) / 1009 = (1 : ℚ) / 210 + (1 : ℚ) / 6054 + (1 : ℚ) / 35315 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 1009 (P92). -/
theorem bound_cert_a5_n1009_quad : (max 210 (max 6054 35315) : ℕ) ≤ 1 * 1009 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 1009 (P92). -/
theorem bound_cert_a5_n1009_subcubic : (max 210 (max 6054 35315) : ℕ) < 1009 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 1129: coordinates (232, 9032, 130964) (P92). -/
theorem bound_cert_a5_n1129_frac : (5 : ℚ) / 1129 = (1 : ℚ) / 232 + (1 : ℚ) / 9032 + (1 : ℚ) / 130964 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 1129 (P92). -/
theorem bound_cert_a5_n1129_quad : (max 232 (max 9032 130964) : ℕ) ≤ 1 * 1129 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 1129 (P92). -/
theorem bound_cert_a5_n1129_subcubic : (max 232 (max 9032 130964) : ℕ) < 1129 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 1201: coordinates (248, 9608, 37231) (P92). -/
theorem bound_cert_a5_n1201_frac : (5 : ℚ) / 1201 = (1 : ℚ) / 248 + (1 : ℚ) / 9608 + (1 : ℚ) / 37231 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 1201 (P92). -/
theorem bound_cert_a5_n1201_quad : (max 248 (max 9608 37231) : ℕ) ≤ 1 * 1201 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 1201 (P92). -/
theorem bound_cert_a5_n1201_subcubic : (max 248 (max 9608 37231) : ℕ) < 1201 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 1369: coordinates (282, 17390, 20535) (P92). -/
theorem bound_cert_a5_n1369_frac : (5 : ℚ) / 1369 = (1 : ℚ) / 282 + (1 : ℚ) / 17390 + (1 : ℚ) / 20535 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 1369 (P92). -/
theorem bound_cert_a5_n1369_quad : (max 282 (max 17390 20535) : ℕ) ≤ 1 * 1369 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 1369 (P92). -/
theorem bound_cert_a5_n1369_subcubic : (max 282 (max 17390 20535) : ℕ) < 1369 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 1681: coordinates (341, 41943, 55473) (P92). -/
theorem bound_cert_a5_n1681_frac : (5 : ℚ) / 1681 = (1 : ℚ) / 341 + (1 : ℚ) / 41943 + (1 : ℚ) / 55473 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 1681 (P92). -/
theorem bound_cert_a5_n1681_quad : (max 341 (max 41943 55473) : ℕ) ≤ 1 * 1681 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 1681 (P92). -/
theorem bound_cert_a5_n1681_subcubic : (max 341 (max 41943 55473) : ℕ) < 1681 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 1801: coordinates (368, 28816, 41423) (P92). -/
theorem bound_cert_a5_n1801_frac : (5 : ℚ) / 1801 = (1 : ℚ) / 368 + (1 : ℚ) / 28816 + (1 : ℚ) / 41423 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 1801 (P92). -/
theorem bound_cert_a5_n1801_quad : (max 368 (max 28816 41423) : ℕ) ≤ 1 * 1801 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 1801 (P92). -/
theorem bound_cert_a5_n1801_subcubic : (max 368 (max 28816 41423) : ℕ) < 1801 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 1849: coordinates (387, 16641, 16641) (P92). -/
theorem bound_cert_a5_n1849_frac : (5 : ℚ) / 1849 = (1 : ℚ) / 387 + (1 : ℚ) / 16641 + (1 : ℚ) / 16641 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 1849 (P92). -/
theorem bound_cert_a5_n1849_quad : (max 387 (max 16641 16641) : ℕ) ≤ 1 * 1849 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 1849 (P92). -/
theorem bound_cert_a5_n1849_subcubic : (max 387 (max 16641 16641) : ℕ) < 1849 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 1969: coordinates (403, 31031, 38843) (P92). -/
theorem bound_cert_a5_n1969_frac : (5 : ℚ) / 1969 = (1 : ℚ) / 403 + (1 : ℚ) / 31031 + (1 : ℚ) / 38843 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 1969 (P92). -/
theorem bound_cert_a5_n1969_quad : (max 403 (max 31031 38843) : ℕ) ≤ 1 * 1969 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 1969 (P92). -/
theorem bound_cert_a5_n1969_subcubic : (max 403 (max 31031 38843) : ℕ) < 1969 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 2003: coordinates (408, 24036, 272408) (P92). -/
theorem bound_cert_a5_n2003_frac : (5 : ℚ) / 2003 = (1 : ℚ) / 408 + (1 : ℚ) / 24036 + (1 : ℚ) / 272408 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 2003 (P92). -/
theorem bound_cert_a5_n2003_quad : (max 408 (max 24036 272408) : ℕ) ≤ 1 * 2003 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 2003 (P92). -/
theorem bound_cert_a5_n2003_subcubic : (max 408 (max 24036 272408) : ℕ) < 2003 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 2041: coordinates (429, 15543, 18369) (P92). -/
theorem bound_cert_a5_n2041_frac : (5 : ℚ) / 2041 = (1 : ℚ) / 429 + (1 : ℚ) / 15543 + (1 : ℚ) / 18369 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 2041 (P92). -/
theorem bound_cert_a5_n2041_quad : (max 429 (max 15543 18369) : ℕ) ≤ 1 * 2041 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 2041 (P92). -/
theorem bound_cert_a5_n2041_subcubic : (max 429 (max 15543 18369) : ℕ) < 2041 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 2209: coordinates (444, 145794, 229548) (P92). -/
theorem bound_cert_a5_n2209_frac : (5 : ℚ) / 2209 = (1 : ℚ) / 444 + (1 : ℚ) / 145794 + (1 : ℚ) / 229548 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 2209 (P92). -/
theorem bound_cert_a5_n2209_quad : (max 444 (max 145794 229548) : ℕ) ≤ 1 * 2209 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 2209 (P92). -/
theorem bound_cert_a5_n2209_subcubic : (max 444 (max 145794 229548) : ℕ) < 2209 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 2521: coordinates (506, 277310, 289915) (P92). -/
theorem bound_cert_a5_n2521_frac : (5 : ℚ) / 2521 = (1 : ℚ) / 506 + (1 : ℚ) / 277310 + (1 : ℚ) / 289915 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 2521 (P92). -/
theorem bound_cert_a5_n2521_quad : (max 506 (max 277310 289915) : ℕ) ≤ 1 * 2521 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 2521 (P92). -/
theorem bound_cert_a5_n2521_subcubic : (max 506 (max 277310 289915) : ℕ) < 2521 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 2641: coordinates (536, 71288, 73948) (P92). -/
theorem bound_cert_a5_n2641_frac : (5 : ℚ) / 2641 = (1 : ℚ) / 536 + (1 : ℚ) / 71288 + (1 : ℚ) / 73948 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 2641 (P92). -/
theorem bound_cert_a5_n2641_quad : (max 536 (max 71288 73948) : ℕ) ≤ 1 * 2641 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 2641 (P92). -/
theorem bound_cert_a5_n2641_subcubic : (max 536 (max 71288 73948) : ℕ) < 2641 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 2689: coordinates (550, 29579, 134450) (P92). -/
theorem bound_cert_a5_n2689_frac : (5 : ℚ) / 2689 = (1 : ℚ) / 550 + (1 : ℚ) / 29579 + (1 : ℚ) / 134450 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 2689 (P92). -/
theorem bound_cert_a5_n2689_quad : (max 550 (max 29579 134450) : ℕ) ≤ 1 * 2689 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 2689 (P92). -/
theorem bound_cert_a5_n2689_subcubic : (max 550 (max 29579 134450) : ℕ) < 2689 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 2809: coordinates (583, 30899, 30899) (P92). -/
theorem bound_cert_a5_n2809_frac : (5 : ℚ) / 2809 = (1 : ℚ) / 583 + (1 : ℚ) / 30899 + (1 : ℚ) / 30899 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 2809 (P92). -/
theorem bound_cert_a5_n2809_quad : (max 583 (max 30899 30899) : ℕ) ≤ 1 * 2809 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 2809 (P92). -/
theorem bound_cert_a5_n2809_subcubic : (max 583 (max 30899 30899) : ℕ) < 2809 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 2881: coordinates (603, 25929, 25929) (P92). -/
theorem bound_cert_a5_n2881_frac : (5 : ℚ) / 2881 = (1 : ℚ) / 603 + (1 : ℚ) / 25929 + (1 : ℚ) / 25929 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 2881 (P92). -/
theorem bound_cert_a5_n2881_quad : (max 603 (max 25929 25929) : ℕ) ≤ 1 * 2881 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 2881 (P92). -/
theorem bound_cert_a5_n2881_subcubic : (max 603 (max 25929 25929) : ℕ) < 2881 ^ 3 := by
  decide

/-- Certified unit fraction solution for a = 5, n = 3049: coordinates (620, 60980, 94519) (P92). -/
theorem bound_cert_a5_n3049_frac : (5 : ℚ) / 3049 = (1 : ℚ) / 620 + (1 : ℚ) / 60980 + (1 : ℚ) / 94519 := by
  norm_num

/-- Certified extremal quadratic bound: max(x, y, z) ≤ 1 * n^2 for a = 5, n = 3049 (P92). -/
theorem bound_cert_a5_n3049_quad : (max 620 (max 60980 94519) : ℕ) ≤ 1 * 3049 ^ 2 := by
  decide

/-- Certified subcubic coordinate bound: max(x, y, z) < n^3 for a = 5, n = 3049 (P92). -/
theorem bound_cert_a5_n3049_subcubic : (max 620 (max 60980 94519) : ℕ) < 3049 ^ 3 := by
  decide
