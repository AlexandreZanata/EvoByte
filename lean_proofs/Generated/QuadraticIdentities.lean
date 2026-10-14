/-
EvoByte Formal Proof Catalog: Certified Multiparameter Quadratic Identities in Q[u, v].
-/

import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Data.Rat.Defs

/-- Erdős–Straus bilinear factor identity: n(u, v) = (4u - 1)(4v - 1)
    Verified exact in Q[u, v]: a*X*Y*Z = n*(Y*Z + X*Z + X*Y). -/
theorem erdos_quadratic_bilinear_4u1_4v1 : ∀ (u v : ℚ),
    (4 : ℚ) * (u * (4 * v - 1)) * (u * (4 * u - 1) * (4 * v - 1) + 1) * (u * (4 * u - 1) * (4 * v - 1) * (u * (4 * u - 1) * (4 * v - 1) + 1)) =
    ((4 * u - 1) * (4 * v - 1)) * ((u * (4 * u - 1) * (4 * v - 1) + 1) * (u * (4 * u - 1) * (4 * v - 1) * (u * (4 * u - 1) * (4 * v - 1) + 1)) + (u * (4 * v - 1)) * (u * (4 * u - 1) * (4 * v - 1) * (u * (4 * u - 1) * (4 * v - 1) + 1)) + (u * (4 * v - 1)) * (u * (4 * u - 1) * (4 * v - 1) + 1)) := by
  intro u v
  ring

/-- Erdős–Straus pure square identity: n(u) = (4u - 1)^2 = 16u^2 - 8u + 1
    Verified exact in Q[u]: a*X*Y*Z = n*(Y*Z + X*Z + X*Y). -/
theorem erdos_quadratic_square_4u1 : ∀ (u : ℚ),
    (4 : ℚ) * (u * (4 * u - 1)) * (u * (4 * u - 1)^2 + 1) * (u * (4 * u - 1)^2 * (u * (4 * u - 1)^2 + 1)) =
    ((4 * u - 1)^2) * ((u * (4 * u - 1)^2 + 1) * (u * (4 * u - 1)^2 * (u * (4 * u - 1)^2 + 1)) + (u * (4 * u - 1)) * (u * (4 * u - 1)^2 * (u * (4 * u - 1)^2 + 1)) + (u * (4 * u - 1)) * (u * (4 * u - 1)^2 + 1)) := by
  intro u
  ring

/-- Erdős–Straus bilinear factor identity: n(u, v) = (3u - 1)(3v - 1)
    Verified exact in Q[u, v]: a*X*Y*Z = n*(Y*Z + X*Z + X*Y). -/
theorem erdos_bilinear_3u1_3v1 : ∀ (u v : ℚ),
    (4 : ℚ) * (u * (3 * v - 1)) * ((3 * u - 1) * (3 * v - 1)) * (u * (3 * u - 1) * (3 * v - 1)) =
    ((3 * u - 1) * (3 * v - 1)) * (((3 * u - 1) * (3 * v - 1)) * (u * (3 * u - 1) * (3 * v - 1)) + (u * (3 * v - 1)) * (u * (3 * u - 1) * (3 * v - 1)) + (u * (3 * v - 1)) * ((3 * u - 1) * (3 * v - 1))) := by
  intro u v
  ring

/-- Erdős–Straus pure square identity: n(u) = (3u - 1)^2 = 9u^2 - 6u + 1
    Verified exact in Q[u]: a*X*Y*Z = n*(Y*Z + X*Z + X*Y). -/
theorem erdos_quadratic_square_3u1 : ∀ (u : ℚ),
    (4 : ℚ) * (u * (3 * u - 1)) * ((3 * u - 1)^2) * (u * (3 * u - 1)^2) =
    ((3 * u - 1)^2) * (((3 * u - 1)^2) * (u * (3 * u - 1)^2) + (u * (3 * u - 1)) * (u * (3 * u - 1)^2) + (u * (3 * u - 1)) * ((3 * u - 1)^2)) := by
  intro u
  ring

/-- Erdős–Straus bilinear factor identity: n(u, v) = (7u - 1) v
    Verified exact in Q[u, v]: a*X*Y*Z = n*(Y*Z + X*Z + X*Y). -/
theorem erdos_bilinear_7u1_v : ∀ (u v : ℚ),
    (4 : ℚ) * (2 * u * v) * (2 * (7 * u - 1) * v) * (2 * u * (7 * u - 1) * v) =
    ((7 * u - 1) * v) * ((2 * (7 * u - 1) * v) * (2 * u * (7 * u - 1) * v) + (2 * u * v) * (2 * u * (7 * u - 1) * v) + (2 * u * v) * (2 * (7 * u - 1) * v)) := by
  intro u v
  ring

/-- Erdős–Straus pure square identity: n(u) = (7u - 1)^2 = 49u^2 - 14u + 1
    Verified exact in Q[u]: a*X*Y*Z = n*(Y*Z + X*Z + X*Y). -/
theorem erdos_quadratic_square_7u1 : ∀ (u : ℚ),
    (4 : ℚ) * (2 * u * (7 * u - 1)) * (2 * (7 * u - 1)^2) * (2 * u * (7 * u - 1)^2) =
    ((7 * u - 1)^2) * ((2 * (7 * u - 1)^2) * (2 * u * (7 * u - 1)^2) + (2 * u * (7 * u - 1)) * (2 * u * (7 * u - 1)^2) + (2 * u * (7 * u - 1)) * (2 * (7 * u - 1)^2)) := by
  intro u
  ring

/-- Sierpiński bilinear factor identity: n(u, v) = (5u - 1)(5v - 1)
    Verified exact in Q[u, v]: a*X*Y*Z = n*(Y*Z + X*Z + X*Y). -/
theorem sierpinski_bilinear_5u1_5v1 : ∀ (u v : ℚ),
    (5 : ℚ) * (u * (5 * v - 1)) * (u * (5 * u - 1) * (5 * v - 1) + 1) * (u * (5 * u - 1) * (5 * v - 1) * (u * (5 * u - 1) * (5 * v - 1) + 1)) =
    ((5 * u - 1) * (5 * v - 1)) * ((u * (5 * u - 1) * (5 * v - 1) + 1) * (u * (5 * u - 1) * (5 * v - 1) * (u * (5 * u - 1) * (5 * v - 1) + 1)) + (u * (5 * v - 1)) * (u * (5 * u - 1) * (5 * v - 1) * (u * (5 * u - 1) * (5 * v - 1) + 1)) + (u * (5 * v - 1)) * (u * (5 * u - 1) * (5 * v - 1) + 1)) := by
  intro u v
  ring

/-- Sierpiński pure square identity: n(u) = (5u - 1)^2 = 25u^2 - 10u + 1
    Verified exact in Q[u]: a*X*Y*Z = n*(Y*Z + X*Z + X*Y). -/
theorem sierpinski_quadratic_square_5u1 : ∀ (u : ℚ),
    (5 : ℚ) * (u * (5 * u - 1)) * (u * (5 * u - 1)^2 + 1) * (u * (5 * u - 1)^2 * (u * (5 * u - 1)^2 + 1)) =
    ((5 * u - 1)^2) * ((u * (5 * u - 1)^2 + 1) * (u * (5 * u - 1)^2 * (u * (5 * u - 1)^2 + 1)) + (u * (5 * u - 1)) * (u * (5 * u - 1)^2 * (u * (5 * u - 1)^2 + 1)) + (u * (5 * u - 1)) * (u * (5 * u - 1)^2 + 1)) := by
  intro u
  ring

/-- Sierpiński bilinear factor identity: n(u, v) = (4u - 1)(4v - 1)
    Verified exact in Q[u, v]: a*X*Y*Z = n*(Y*Z + X*Z + X*Y). -/
theorem sierpinski_bilinear_4u1_4v1 : ∀ (u v : ℚ),
    (5 : ℚ) * (u * (4 * v - 1)) * ((4 * u - 1) * (4 * v - 1)) * (u * (4 * u - 1) * (4 * v - 1)) =
    ((4 * u - 1) * (4 * v - 1)) * (((4 * u - 1) * (4 * v - 1)) * (u * (4 * u - 1) * (4 * v - 1)) + (u * (4 * v - 1)) * (u * (4 * u - 1) * (4 * v - 1)) + (u * (4 * v - 1)) * ((4 * u - 1) * (4 * v - 1))) := by
  intro u v
  ring

/-- Sierpiński pure square identity: n(u) = (4u - 1)^2 = 16u^2 - 8u + 1
    Verified exact in Q[u]: a*X*Y*Z = n*(Y*Z + X*Z + X*Y). -/
theorem sierpinski_quadratic_square_4u1 : ∀ (u : ℚ),
    (5 : ℚ) * (u * (4 * u - 1)) * ((4 * u - 1)^2) * (u * (4 * u - 1)^2) =
    ((4 * u - 1)^2) * (((4 * u - 1)^2) * (u * (4 * u - 1)^2) + (u * (4 * u - 1)) * (u * (4 * u - 1)^2) + (u * (4 * u - 1)) * ((4 * u - 1)^2)) := by
  intro u
  ring

/-- Sierpiński bilinear factor identity: n(u, v) = (5u - 2)(5v - 2)
    Verified exact in Q[u, v]: a*X*Y*Z = n*(Y*Z + X*Z + X*Y). -/
theorem sierpinski_bilinear_5u2_5v2 : ∀ (u v : ℚ),
    (5 : ℚ) * (u * (5 * v - 2)) * ((u * (5 * u - 2) * (5 * v - 2) + 1) / 2) * ((u * (5 * u - 2) * (5 * v - 2) * (u * (5 * u - 2) * (5 * v - 2) + 1)) / 2) =
    ((5 * u - 2) * (5 * v - 2)) * (((u * (5 * u - 2) * (5 * v - 2) + 1) / 2) * ((u * (5 * u - 2) * (5 * v - 2) * (u * (5 * u - 2) * (5 * v - 2) + 1)) / 2) + (u * (5 * v - 2)) * ((u * (5 * u - 2) * (5 * v - 2) * (u * (5 * u - 2) * (5 * v - 2) + 1)) / 2) + (u * (5 * v - 2)) * ((u * (5 * u - 2) * (5 * v - 2) + 1) / 2)) := by
  intro u v
  ring

/-- Sierpiński pure square identity: n(u) = (5u - 2)^2 = 25u^2 - 20u + 4
    Verified exact in Q[u]: a*X*Y*Z = n*(Y*Z + X*Z + X*Y). -/
theorem sierpinski_quadratic_square_5u2 : ∀ (u : ℚ),
    (5 : ℚ) * (u * (5 * u - 2)) * ((u * (5 * u - 2)^2 + 1) / 2) * ((u * (5 * u - 2)^2 * (u * (5 * u - 2)^2 + 1)) / 2) =
    ((5 * u - 2)^2) * (((u * (5 * u - 2)^2 + 1) / 2) * ((u * (5 * u - 2)^2 * (u * (5 * u - 2)^2 + 1)) / 2) + (u * (5 * u - 2)) * ((u * (5 * u - 2)^2 * (u * (5 * u - 2)^2 + 1)) / 2) + (u * (5 * u - 2)) * ((u * (5 * u - 2)^2 + 1) / 2)) := by
  intro u
  ring

/-- Certified Diophantine solution for resistant residue n = 121 (P84).
    Verified exact: 4/121 = 1/44 + 1/121 + 1/484 with pairwise distinct positive integers. -/
theorem erdos_straus_cert_res121 :
    (4 : ℚ) / 121 = 1 / 44 + 1 / 121 + 1 / 484 := by
  norm_num

/-- Certified Diophantine solution for resistant residue n = 169 (P84).
    Verified exact: 4/169 = 1/52 + 1/338 + 1/676 with pairwise distinct positive integers. -/
theorem erdos_straus_cert_res169 :
    (4 : ℚ) / 169 = 1 / 52 + 1 / 338 + 1 / 676 := by
  norm_num

/-- Certified Diophantine solution for resistant residue n = 289 (P84).
    Verified exact: 4/289 = 1/102 + 1/289 + 1/1734 with pairwise distinct positive integers. -/
theorem erdos_straus_cert_res289 :
    (4 : ℚ) / 289 = 1 / 102 + 1 / 289 + 1 / 1734 := by
  norm_num

/-- Certified Diophantine solution for resistant residue n = 361 (P84).
    Verified exact: 4/361 = 1/95 + 1/1806 + 1/3259830 with pairwise distinct positive integers. -/
theorem erdos_straus_cert_res361 :
    (4 : ℚ) / 361 = 1 / 95 + 1 / 1806 + 1 / 3259830 := by
  norm_num

/-- Certified Diophantine solution for resistant residue n = 529 (P84).
    Verified exact: 4/529 = 1/138 + 1/3175 + 1/10077450 with pairwise distinct positive integers. -/
theorem erdos_straus_cert_res529 :
    (4 : ℚ) / 529 = 1 / 138 + 1 / 3175 + 1 / 10077450 := by
  norm_num

/-- Certified Diophantine solution for resistant residue n = 9 (P84).
    Verified exact: 5/9 = 1/3 + 1/5 + 1/45 with pairwise distinct positive integers. -/
theorem sierpinski_cert_res9 :
    (5 : ℚ) / 9 = 1 / 3 + 1 / 5 + 1 / 45 := by
  norm_num

/-- Certified Diophantine solution for resistant residue n = 49 (P84).
    Verified exact: 5/49 = 1/14 + 1/49 + 1/98 with pairwise distinct positive integers. -/
theorem sierpinski_cert_res49 :
    (5 : ℚ) / 49 = 1 / 14 + 1 / 49 + 1 / 98 := by
  norm_num

/-- Certified Diophantine solution for resistant residue n = 121 (P84).
    Verified exact: 5/121 = 1/33 + 1/121 + 1/363 with pairwise distinct positive integers. -/
theorem sierpinski_cert_res121 :
    (5 : ℚ) / 121 = 1 / 33 + 1 / 121 + 1 / 363 := by
  norm_num

/-- Certified Diophantine solution for resistant residue n = 169 (P84).
    Verified exact: 5/169 = 1/39 + 1/254 + 1/128778 with pairwise distinct positive integers. -/
theorem sierpinski_cert_res169 :
    (5 : ℚ) / 169 = 1 / 39 + 1 / 254 + 1 / 128778 := by
  norm_num

/-- Certified Diophantine solution for resistant residue n = 529 (P84).
    Verified exact: 5/529 = 1/115 + 1/1323 + 1/3499335 with pairwise distinct positive integers. -/
theorem sierpinski_cert_res529 :
    (5 : ℚ) / 529 = 1 / 115 + 1 / 1323 + 1 / 3499335 := by
  norm_num
