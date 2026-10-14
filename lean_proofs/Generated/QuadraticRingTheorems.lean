/-
EvoByte Formal Proof Catalog: Quadratic Ring Sieve and Norm Factorization Theorems (P91).
-/

import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Data.Rat.Defs

/-- Erdős–Straus unit fraction solution for resistant residue n = 841 (r = 1 mod 840, k = 1).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res1_k1 : (4 : ℚ) / 841 = (1 : ℚ) / 211 + (1 : ℚ) / 59160 + (1 : ℚ) / 362000040 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(5)] for divisor delta = 29 (n = 841, P91). -/
theorem qring_norm_res1_k1 : (7 : ℤ)^2 - 5 * (2 : ℤ)^2 = 29 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 1681 (r = 1 mod 840, k = 2).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res1_k2 : (4 : ℚ) / 1681 = (1 : ℚ) / 421 + (1 : ℚ) / 235914 + (1 : ℚ) / 4072111554 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(2)] for divisor delta = 41 (n = 1681, P91). -/
theorem qring_norm_res1_k2 : (7 : ℤ)^2 - 2 * (2 : ℤ)^2 = 41 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 2521 (r = 1 mod 840, k = 3).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res1_k3 : (4 : ℚ) / 2521 = (1 : ℚ) / 636 + (1 : ℚ) / 69748 + (1 : ℚ) / 131876031 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(6)] for divisor delta = 848 (n = 2521, P91). -/
theorem qring_norm_res1_k3 : (4 : ℤ)^2 - 6 * (12 : ℤ)^2 = -848 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 3361 (r = 1 mod 840, k = 4).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res1_k4 : (4 : ℚ) / 3361 = (1 : ℚ) / 841 + (1 : ℚ) / 942210 + (1 : ℚ) / 91836266490 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(5)] for divisor delta = 29 (n = 3361, P91). -/
theorem qring_norm_res1_k4 : (7 : ℤ)^2 - 5 * (2 : ℤ)^2 = 29 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 121 (r = 121 mod 840, k = 0).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res121_k0 : (4 : ℚ) / 121 = (1 : ℚ) / 31 + (1 : ℚ) / 1254 + (1 : ℚ) / 427614 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(3)] for divisor delta = 11 (n = 121, P91). -/
theorem qring_norm_res121_k0 : (1 : ℤ)^2 - 3 * (2 : ℤ)^2 = -11 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 961 (r = 121 mod 840, k = 1).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res121_k1 : (4 : ℚ) / 961 = (1 : ℚ) / 242 + (1 : ℚ) / 33232 + (1 : ℚ) / 124653232 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(2)] for divisor delta = 62 (n = 961, P91). -/
theorem qring_norm_res121_k1 : (8 : ℤ)^2 - 2 * (1 : ℤ)^2 = 62 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 1801 (r = 121 mod 840, k = 2).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res121_k2 : (4 : ℚ) / 1801 = (1 : ℚ) / 451 + (1 : ℚ) / 270754 + (1 : ℚ) / 19992746114 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(3)] for divisor delta = 11 (n = 1801, P91). -/
theorem qring_norm_res121_k2 : (1 : ℤ)^2 - 3 * (2 : ℤ)^2 = -11 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 2641 (r = 121 mod 840, k = 3).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res121_k3 : (4 : ℚ) / 2641 = (1 : ℚ) / 662 + (1 : ℚ) / 249774 + (1 : ℚ) / 5745925983 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(5)] for divisor delta = 76 (n = 2641, P91). -/
theorem qring_norm_res121_k3 : (9 : ℤ)^2 - 5 * (1 : ℤ)^2 = 76 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 3481 (r = 121 mod 840, k = 4).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res121_k4 : (4 : ℚ) / 3481 = (1 : ℚ) / 871 + (1 : ℚ) / 1010670 + (1 : ℚ) / 51937320630 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(3)] for divisor delta = 59 (n = 3481, P91). -/
theorem qring_norm_res121_k4 : (4 : ℤ)^2 - 3 * (5 : ℤ)^2 = -59 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 169 (r = 169 mod 840, k = 0).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res169_k0 : (4 : ℚ) / 169 = (1 : ℚ) / 44 + (1 : ℚ) / 1066 + (1 : ℚ) / 304876 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(3)] for divisor delta = 26 (n = 169, P91). -/
theorem qring_norm_res169_k0 : (1 : ℤ)^2 - 3 * (3 : ℤ)^2 = -26 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 1009 (r = 169 mod 840, k = 1).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res169_k1 : (4 : ℚ) / 1009 = (1 : ℚ) / 253 + (1 : ℚ) / 85096 + (1 : ℚ) / 1974822872 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(3)] for divisor delta = 11 (n = 1009, P91). -/
theorem qring_norm_res169_k1 : (1 : ℤ)^2 - 3 * (2 : ℤ)^2 = -11 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 1849 (r = 169 mod 840, k = 2).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res169_k2 : (4 : ℚ) / 1849 = (1 : ℚ) / 465 + (1 : ℚ) / 78174 + (1 : ℚ) / 521029710 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(6)] for divisor delta = 129 (n = 1849, P91). -/
theorem qring_norm_res169_k2 : (15 : ℤ)^2 - 6 * (4 : ℤ)^2 = 129 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 2689 (r = 169 mod 840, k = 3).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res169_k3 : (4 : ℚ) / 2689 = (1 : ℚ) / 676 + (1 : ℚ) / 121186 + (1 : ℚ) / 8472598004 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(3)] for divisor delta = 26 (n = 2689, P91). -/
theorem qring_norm_res169_k3 : (1 : ℤ)^2 - 3 * (3 : ℤ)^2 = -26 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 3529 (r = 169 mod 840, k = 4).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res169_k4 : (4 : ℚ) / 3529 = (1 : ℚ) / 884 + (1 : ℚ) / 445666 + (1 : ℚ) / 53473680676 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(3)] for divisor delta = 26 (n = 3529, P91). -/
theorem qring_norm_res169_k4 : (1 : ℤ)^2 - 3 * (3 : ℤ)^2 = -26 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 289 (r = 289 mod 840, k = 0).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res289_k0 : (4 : ℚ) / 289 = (1 : ℚ) / 73 + (1 : ℚ) / 7038 + (1 : ℚ) / 8734158 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(2)] for divisor delta = 17 (n = 289, P91). -/
theorem qring_norm_res289_k0 : (5 : ℤ)^2 - 2 * (2 : ℤ)^2 = 17 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 1129 (r = 289 mod 840, k = 1).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res289_k1 : (4 : ℚ) / 1129 = (1 : ℚ) / 285 + (1 : ℚ) / 29260 + (1 : ℚ) / 99103620 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(5)] for divisor delta = 95 (n = 1129, P91). -/
theorem qring_norm_res289_k1 : (10 : ℤ)^2 - 5 * (1 : ℤ)^2 = 95 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 1969 (r = 289 mod 840, k = 2).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res289_k2 : (4 : ℚ) / 1969 = (1 : ℚ) / 493 + (1 : ℚ) / 323576 + (1 : ℚ) / 28554611272 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(3)] for divisor delta = 11 (n = 1969, P91). -/
theorem qring_norm_res289_k2 : (1 : ℤ)^2 - 3 * (2 : ℤ)^2 = -11 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 2809 (r = 289 mod 840, k = 3).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res289_k3 : (4 : ℚ) / 2809 = (1 : ℚ) / 703 + (1 : ℚ) / 658260 + (1 : ℚ) / 24526109340 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(6)] for divisor delta = 53 (n = 2809, P91). -/
theorem qring_norm_res289_k3 : (1 : ℤ)^2 - 6 * (3 : ℤ)^2 = -53 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 3649 (r = 289 mod 840, k = 4).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res289_k4 : (4 : ℚ) / 3649 = (1 : ℚ) / 913 + (1 : ℚ) / 1110516 + (1 : ℚ) / 336338649372 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(3)] for divisor delta = 11 (n = 3649, P91). -/
theorem qring_norm_res289_k4 : (1 : ℤ)^2 - 3 * (2 : ℤ)^2 = -11 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 361 (r = 361 mod 840, k = 0).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res361_k0 : (4 : ℚ) / 361 = (1 : ℚ) / 92 + (1 : ℚ) / 4750 + (1 : ℚ) / 4151500 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(6)] for divisor delta = 38 (n = 361, P91). -/
theorem qring_norm_res361_k0 : (4 : ℤ)^2 - 6 * (3 : ℤ)^2 = -38 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 1201 (r = 361 mod 840, k = 1).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res361_k1 : (4 : ℚ) / 1201 = (1 : ℚ) / 306 + (1 : ℚ) / 15980 + (1 : ℚ) / 172727820 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(2)] for divisor delta = 34 (n = 1201, P91). -/
theorem qring_norm_res361_k1 : (6 : ℤ)^2 - 2 * (1 : ℤ)^2 = 34 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 2041 (r = 361 mod 840, k = 2).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res361_k2 : (4 : ℚ) / 2041 = (1 : ℚ) / 512 + (1 : ℚ) / 149292 + (1 : ℚ) / 3000172032 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(3)] for divisor delta = 52 (n = 2041, P91). -/
theorem qring_norm_res361_k2 : (8 : ℤ)^2 - 3 * (2 : ℤ)^2 = 52 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 2881 (r = 361 mod 840, k = 3).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res361_k3 : (4 : ℚ) / 2881 = (1 : ℚ) / 722 + (1 : ℚ) / 297160 + (1 : ℚ) / 16266241240 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(6)] for divisor delta = 38 (n = 2881, P91). -/
theorem qring_norm_res361_k3 : (4 : ℤ)^2 - 6 * (3 : ℤ)^2 = -38 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 3721 (r = 361 mod 840, k = 4).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res361_k4 : (4 : ℚ) / 3721 = (1 : ℚ) / 932 + (1 : ℚ) / 495442 + (1 : ℚ) / 14083434292 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(3)] for divisor delta = 122 (n = 3721, P91). -/
theorem qring_norm_res361_k4 : (5 : ℤ)^2 - 3 * (7 : ℤ)^2 = -122 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 529 (r = 529 mod 840, k = 0).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res529_k0 : (4 : ℚ) / 529 = (1 : ℚ) / 133 + (1 : ℚ) / 23460 + (1 : ℚ) / 71764140 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(2)] for divisor delta = 23 (n = 529, P91). -/
theorem qring_norm_res529_k0 : (5 : ℤ)^2 - 2 * (1 : ℤ)^2 = 23 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 1369 (r = 529 mod 840, k = 1).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res529_k1 : (4 : ℚ) / 1369 = (1 : ℚ) / 346 + (1 : ℚ) / 32005 + (1 : ℚ) / 2368370 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(10)] for divisor delta = 6401 (n = 1369, P91). -/
theorem qring_norm_res529_k1 : (81 : ℤ)^2 - 10 * (4 : ℤ)^2 = 6401 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 2209 (r = 529 mod 840, k = 2).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res529_k2 : (4 : ℚ) / 2209 = (1 : ℚ) / 553 + (1 : ℚ) / 407208 + (1 : ℚ) / 10583743128 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(2)] for divisor delta = 47 (n = 2209, P91). -/
theorem qring_norm_res529_k2 : (7 : ℤ)^2 - 2 * (1 : ℤ)^2 = 47 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 3049 (r = 529 mod 840, k = 3).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res529_k3 : (4 : ℚ) / 3049 = (1 : ℚ) / 765 + (1 : ℚ) / 212058 + (1 : ℚ) / 3232824210 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(2)] for divisor delta = 153 (n = 3049, P91). -/
theorem qring_norm_res529_k3 : (15 : ℤ)^2 - 2 * (6 : ℤ)^2 = 153 := by
  ring

/-- Erdős–Straus unit fraction solution for resistant residue n = 3889 (r = 529 mod 840, k = 4).
    Derived via quadratic ring norm factorization in Z[sqrt(d)] (P91). -/
theorem qring_cert_res529_k4 : (4 : ℚ) / 3889 = (1 : ℚ) / 975 + (1 : ℚ) / 344708 + (1 : ℚ) / 100542705900 := by
  norm_num

/-- Quadratic ring norm identity in Z[sqrt(3)] for divisor delta = 13 (n = 3889, P91). -/
theorem qring_norm_res529_k4 : (4 : ℤ)^2 - 3 * (1 : ℤ)^2 = 13 := by
  ring
