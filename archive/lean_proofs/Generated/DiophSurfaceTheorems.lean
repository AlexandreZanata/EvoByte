/-
EvoByte Formal Proof Catalog: Unified Diophantine Surface Metatactic Theorems (P100).
Demonstrates automated variable elimination, algebraic normalization, and decision procedures via `dioph_surface`.
-/

import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Data.Rat.Defs
import Tactic.DiophSurface
import Generated.CubicSurfaceFibrations
import Generated.ConicParametrizations
import Generated.QuaternionAlgebraTheorems

/-- Automated proof of cubic surface and conic fiber equivalence via dioph_surface. -/
theorem meta_surface_fiber_equiv (a n x y z : ℚ) :
  cubic_surface_poly a n x y z = conic_fiber_x a n x y z := by
  dioph_surface [cubic_surface_poly, conic_fiber_x]

/-- Automated proof of bilinear hyperbolic factorization via dioph_surface. -/
theorem meta_surface_bilinear_factor (a n x y z : ℚ) :
  conic_bilinear_x a n x y z = (a * x - n) * conic_fiber_x a n x y z := by
  dioph_surface [conic_bilinear_x, conic_fiber_x]

/-- Automated proof of central discriminant expansion via dioph_surface. -/
theorem meta_conic_fibration_discriminant_sq (n x : ℚ) :
  conic_discriminant n x = n^2 * x^2 := by
  dioph_surface [conic_discriminant]

/-- Automated proof of translated hyperbolic expansion via dioph_surface. -/
theorem meta_conic_fiber_translation (a n x y z : ℚ) :
  ((a * x - n) * y - n * x) * ((a * x - n) * z - n * x) =
  (a * x - n)^2 * y * z - n * x * (a * x - n) * (y + z) + (n * x)^2 := by
  dioph_surface

/-- Automated proof of cubic surface S_3 permutation invariance (x, y) via dioph_surface. -/
theorem meta_cubic_surface_symm_xy (a n x y z : ℚ) :
  cubic_surface_poly a n x y z = cubic_surface_poly a n y x z := by
  dioph_surface [cubic_surface_poly]

/-- Automated proof of cubic surface S_3 permutation invariance (y, z) via dioph_surface. -/
theorem meta_cubic_surface_symm_yz (a n x y z : ℚ) :
  cubic_surface_poly a n x y z = cubic_surface_poly a n x z y := by
  dioph_surface [cubic_surface_poly]

/-- Automated proof of cubic surface S_3 permutation invariance (x, z) via dioph_surface. -/
theorem meta_cubic_surface_symm_xz (a n x y z : ℚ) :
  cubic_surface_poly a n x y z = cubic_surface_poly a n z y x := by
  dioph_surface [cubic_surface_poly]
/-- Automated proof of Legendre ternary quadratic form equivalence via dioph_surface. -/
theorem meta_legendre_conic_equiv (a n x y z : ℚ) :
  legendre_conic_form (a * x - n) (n * x) y z 1 = 4 * (a * x - n) * conic_fiber_x a n x y z := by
  dioph_surface [legendre_conic_form, conic_fiber_x]

/-- Automated proof of hyperbolic form factorization via dioph_surface. -/
theorem meta_conic_hyperbolic_equiv (a n x y z : ℚ) :
  conic_hyperbolic_form (a * x - n) (n * x) y z = (a * x - n) * conic_fiber_x a n x y z := by
  dioph_surface [conic_hyperbolic_form, conic_fiber_x]

/-- Automated proof of Euler four-square norm multiplicativity via dioph_surface. -/
theorem meta_euler_four_square (x0 x1 x2 x3 y0 y1 y2 y3 : ℚ) :
  (x0^2 + x1^2 + x2^2 + x3^2) * (y0^2 + y1^2 + y2^2 + y3^2) =
  (x0 * y0 - x1 * y1 - x2 * y2 - x3 * y3)^2 +
  (x0 * y1 + x1 * y0 + x2 * y3 - x3 * y2)^2 +
  (x0 * y2 - x1 * y3 + x2 * y0 + x3 * y1)^2 +
  (x0 * y3 + x1 * y2 - x2 * y1 + x3 * y0)^2 := by
  dioph_surface

/-- Automated proof of generalized quaternion reduced norm multiplicativity via dioph_surface. -/
theorem meta_quat_general_norm_mult (x0 x1 x2 x3 y0 y1 y2 y3 a b : ℚ) :
  quat_nrd x0 x1 x2 x3 a b * quat_nrd y0 y1 y2 y3 a b =
  quat_nrd (x0 * y0 + a * x1 * y1 + b * x2 * y2 - a * b * x3 * y3)
           (x0 * y1 + x1 * y0 - b * x2 * y3 + b * x3 * y2)
           (x0 * y2 + x2 * y0 + a * x1 * y3 - a * x3 * y1)
           (x0 * y3 + x3 * y0 + x1 * y2 - x2 * y1)
           a b := by
  dioph_surface [quat_nrd]

/-- Automated proof of quaternion norm scaling under scalar multiplication via dioph_surface. -/
theorem meta_quat_norm_scale (x0 x1 x2 x3 a b s : ℚ) :
  quat_nrd (s * x0) (s * x1) (s * x2) (s * x3) a b = s^2 * quat_nrd x0 x1 x2 x3 a b := by
  dioph_surface [quat_nrd]

/-- Automated proof of conjugate quaternion norm preservation via dioph_surface. -/
theorem meta_quat_norm_conj (x0 x1 x2 x3 a b : ℚ) :
  quat_nrd x0 (-x1) (-x2) (-x3) a b = quat_nrd x0 x1 x2 x3 a b := by
  dioph_surface [quat_nrd]

/-- Automated proof of Bézout conic factor elimination via dioph_surface. -/
theorem meta_bezout_conic_elimination (nx u v : ℚ) (h : u * v = nx^2) :
  u * v - nx^2 = 0 := by
  dioph_surface

/-- Automated conic fiber vanishing for parametric family es_even via dioph_surface. -/
theorem meta_conic_section_es_even (k : ℚ) :
  conic_fiber_x 4 ((2 : ℚ) + (2 : ℚ) * k) ((2 : ℚ) + (1 : ℚ) * k) ((2 : ℚ) + (3 : ℚ) * k + (1 : ℚ) * k ^ 2) ((1 : ℚ) + (1 : ℚ) * k) = 0 := by
  dioph_surface [conic_fiber_x]

/-- Automated conic fiber vanishing for parametric family es_mod3_r2 via dioph_surface. -/
theorem meta_conic_section_es_mod3_r2 (k : ℚ) :
  conic_fiber_x 4 ((2 : ℚ) + (3 : ℚ) * k) ((1 : ℚ) + (1 : ℚ) * k) ((2 : ℚ) + (3 : ℚ) * k) ((2 : ℚ) + (5 : ℚ) * k + (3 : ℚ) * k ^ 2) = 0 := by
  dioph_surface [conic_fiber_x]

/-- Automated conic fiber vanishing for parametric family es_mod4_r2 via dioph_surface. -/
theorem meta_conic_section_es_mod4_r2 (k : ℚ) :
  conic_fiber_x 4 ((2 : ℚ) + (4 : ℚ) * k) ((1 : ℚ) + (1 : ℚ) * k) ((2 : ℚ) + (6 : ℚ) * k + (4 : ℚ) * k ^ 2) ((2 : ℚ) + (6 : ℚ) * k + (4 : ℚ) * k ^ 2) = 0 := by
  dioph_surface [conic_fiber_x]

/-- Automated conic fiber vanishing for parametric family es_mod4_r3 via dioph_surface. -/
theorem meta_conic_section_es_mod4_r3 (k : ℚ) :
  conic_fiber_x 4 ((3 : ℚ) + (4 : ℚ) * k) ((1 : ℚ) + (1 : ℚ) * k) ((6 : ℚ) + (14 : ℚ) * k + (8 : ℚ) * k ^ 2) ((6 : ℚ) + (14 : ℚ) * k + (8 : ℚ) * k ^ 2) = 0 := by
  dioph_surface [conic_fiber_x]

/-- Automated conic fiber vanishing for parametric family es_mod6_r2 via dioph_surface. -/
theorem meta_conic_section_es_mod6_r2 (k : ℚ) :
  conic_fiber_x 4 ((2 : ℚ) + (6 : ℚ) * k) ((1 : ℚ) + (2 : ℚ) * k) ((2 : ℚ) + (6 : ℚ) * k) ((2 : ℚ) + (10 : ℚ) * k + (12 : ℚ) * k ^ 2) = 0 := by
  dioph_surface [conic_fiber_x]

/-- Automated conic fiber vanishing for parametric family es_mod6_r3 via dioph_surface. -/
theorem meta_conic_section_es_mod6_r3 (k : ℚ) :
  conic_fiber_x 4 ((3 : ℚ) + (6 : ℚ) * k) ((2 : ℚ) + (2 : ℚ) * k) ((2 : ℚ) + (6 : ℚ) * k + (4 : ℚ) * k ^ 2) ((3 : ℚ) + (6 : ℚ) * k) = 0 := by
  dioph_surface [conic_fiber_x]

/-- Automated conic fiber vanishing for parametric family es_mod6_r4 via dioph_surface. -/
theorem meta_conic_section_es_mod6_r4 (k : ℚ) :
  conic_fiber_x 4 ((4 : ℚ) + (6 : ℚ) * k) ((2 : ℚ) + (2 : ℚ) * k) ((4 : ℚ) + (10 : ℚ) * k + (6 : ℚ) * k ^ 2) ((4 : ℚ) + (6 : ℚ) * k) = 0 := by
  dioph_surface [conic_fiber_x]

/-- Automated conic fiber vanishing for parametric family es_mod8_r4 via dioph_surface. -/
theorem meta_conic_section_es_mod8_r4 (k : ℚ) :
  conic_fiber_x 4 ((4 : ℚ) + (8 : ℚ) * k) ((2 : ℚ) + (4 : ℚ) * k) ((3 : ℚ) + (6 : ℚ) * k) ((6 : ℚ) + (12 : ℚ) * k) = 0 := by
  dioph_surface [conic_fiber_x]

/-- Automated conic fiber vanishing for parametric family es_mod12_r6 via dioph_surface. -/
theorem meta_conic_section_es_mod12_r6 (k : ℚ) :
  conic_fiber_x 4 ((6 : ℚ) + (12 : ℚ) * k) ((2 : ℚ) + (3 : ℚ) * k) ((12 : ℚ) + (42 : ℚ) * k + (36 : ℚ) * k ^ 2) ((12 : ℚ) + (42 : ℚ) * k + (36 : ℚ) * k ^ 2) = 0 := by
  dioph_surface [conic_fiber_x]

/-- Automated conic fiber vanishing for parametric family es_mod12_r8 via dioph_surface. -/
theorem meta_conic_section_es_mod12_r8 (k : ℚ) :
  conic_fiber_x 4 ((8 : ℚ) + (12 : ℚ) * k) ((4 : ℚ) + (6 : ℚ) * k) ((6 : ℚ) + (9 : ℚ) * k) ((12 : ℚ) + (18 : ℚ) * k) = 0 := by
  dioph_surface [conic_fiber_x]

/-- Automated conic fiber vanishing for parametric family sierpinski_mod4_r2 via dioph_surface. -/
theorem meta_conic_section_sierpinski_mod4_r2 (k : ℚ) :
  conic_fiber_x 5 ((2 : ℚ) + (4 : ℚ) * k) ((1 : ℚ) + (1 : ℚ) * k) ((1 : ℚ) + (3 : ℚ) * k + (2 : ℚ) * k ^ 2) ((2 : ℚ) + (4 : ℚ) * k) = 0 := by
  dioph_surface [conic_fiber_x]

/-- Automated conic fiber vanishing for parametric family sierpinski_mod5_r0 via dioph_surface. -/
theorem meta_conic_section_sierpinski_mod5_r0 (k : ℚ) :
  conic_fiber_x 5 ((5 : ℚ) + (5 : ℚ) * k) ((2 : ℚ) + (2 : ℚ) * k) ((3 : ℚ) + (3 : ℚ) * k) ((6 : ℚ) + (6 : ℚ) * k) = 0 := by
  dioph_surface [conic_fiber_x]

/-- Automated conic fiber vanishing for parametric family sierpinski_mod6_r2 via dioph_surface. -/
theorem meta_conic_section_sierpinski_mod6_r2 (k : ℚ) :
  conic_fiber_x 5 ((2 : ℚ) + (6 : ℚ) * k) ((1 : ℚ) + (2 : ℚ) * k) ((2 : ℚ) + (10 : ℚ) * k + (12 : ℚ) * k ^ 2) ((1 : ℚ) + (3 : ℚ) * k) = 0 := by
  dioph_surface [conic_fiber_x]

/-- Automated conic fiber vanishing for parametric family sierpinski_mod6_r3 via dioph_surface. -/
theorem meta_conic_section_sierpinski_mod6_r3 (k : ℚ) :
  conic_fiber_x 5 ((3 : ℚ) + (6 : ℚ) * k) ((2 : ℚ) + (3 : ℚ) * k) ((6 : ℚ) + (21 : ℚ) * k + (18 : ℚ) * k ^ 2) ((1 : ℚ) + (2 : ℚ) * k) = 0 := by
  dioph_surface [conic_fiber_x]

/-- Automated conic fiber vanishing for parametric family sierpinski_mod6_r4 via dioph_surface. -/
theorem meta_conic_section_sierpinski_mod6_r4 (k : ℚ) :
  conic_fiber_x 5 ((4 : ℚ) + (6 : ℚ) * k) ((2 : ℚ) + (2 : ℚ) * k) ((4 : ℚ) + (10 : ℚ) * k + (6 : ℚ) * k ^ 2) ((2 : ℚ) + (3 : ℚ) * k) = 0 := by
  dioph_surface [conic_fiber_x]

/-- Automated conic fiber vanishing for parametric family schinzel_a6_mod3_r0 via dioph_surface. -/
theorem meta_conic_section_schinzel_a6_mod3_r0 (k : ℚ) :
  conic_fiber_x 6 ((3 : ℚ) + (3 : ℚ) * k) ((2 : ℚ) + (1 : ℚ) * k) ((2 : ℚ) + (3 : ℚ) * k + (1 : ℚ) * k ^ 2) ((1 : ℚ) + (1 : ℚ) * k) = 0 := by
  dioph_surface [conic_fiber_x]

/-- Automated conic fiber vanishing for parametric family schinzel_a6_mod4_r2 via dioph_surface. -/
theorem meta_conic_section_schinzel_a6_mod4_r2 (k : ℚ) :
  conic_fiber_x 6 ((2 : ℚ) + (4 : ℚ) * k) ((1 : ℚ) + (1 : ℚ) * k) ((1 : ℚ) + (3 : ℚ) * k + (2 : ℚ) * k ^ 2) ((1 : ℚ) + (2 : ℚ) * k) = 0 := by
  dioph_surface [conic_fiber_x]

/-- Automated four-square norm decomposition for u-factor at a = 4, n = 1009 via dioph_surface. -/
theorem meta_four_sq_u_a4_n1009 :
  quat_nrd_std 215 65 0 0 = 50450 := by
  dioph_surface [quat_nrd_std]

/-- Automated four-square norm decomposition for v-factor at a = 4, n = 1009 via dioph_surface. -/
theorem meta_four_sq_v_a4_n1009 :
  quat_nrd_std 1162 118 0 0 = 1364168 := by
  dioph_surface [quat_nrd_std]

/-- Automated certified unit fraction decomposition for a = 4, n = 1009 via dioph_surface. -/
theorem meta_conic_cert_a4_n1009 :
  (4 : ℚ) / 1009 = (1 : ℚ) / 260 + (1 : ℚ) / 10090 + (1 : ℚ) / 52468 := by
  dioph_surface

/-- Automated four-square norm decomposition for u-factor at a = 4, n = 10007 via dioph_surface. -/
theorem meta_four_sq_u_a4_n10007 :
  quat_nrd_std 2814 72 42 0 = 7925544 := by
  dioph_surface [quat_nrd_std]

/-- Automated four-square norm decomposition for v-factor at a = 4, n = 10007 via dioph_surface. -/
theorem meta_four_sq_v_a4_n10007 :
  quat_nrd_std 8913 184 13 0 = 79475594 := by
  dioph_surface [quat_nrd_std]

/-- Automated certified unit fraction decomposition for a = 4, n = 10007 via dioph_surface. -/
theorem meta_conic_cert_a4_n10007 :
  (4 : ℚ) / 10007 = (1 : ℚ) / 2508 + (1 : ℚ) / 1320924 + (1 : ℚ) / 4182926 := by
  dioph_surface

/-- Automated four-square norm decomposition for u-factor at a = 4, n = 841 via dioph_surface. -/
theorem meta_four_sq_u_a4_n841 :
  quat_nrd_std 252 14 10 0 = 63800 := by
  dioph_surface [quat_nrd_std]

/-- Automated four-square norm decomposition for v-factor at a = 4, n = 841 via dioph_surface. -/
theorem meta_four_sq_v_a4_n841 :
  quat_nrd_std 731 46 9 0 = 536558 := by
  dioph_surface [quat_nrd_std]

/-- Automated certified unit fraction decomposition for a = 4, n = 841 via dioph_surface. -/
theorem meta_conic_cert_a4_n841 :
  (4 : ℚ) / 841 = (1 : ℚ) / 220 + (1 : ℚ) / 6380 + (1 : ℚ) / 18502 := by
  dioph_surface

/-- Automated four-square norm decomposition for u-factor at a = 4, n = 1681 via dioph_surface. -/
theorem meta_four_sq_u_a4_n1681 :
  quat_nrd_std 499 9 5 3 = 249116 := by
  dioph_surface [quat_nrd_std]

/-- Automated four-square norm decomposition for v-factor at a = 4, n = 1681 via dioph_surface. -/
theorem meta_four_sq_v_a4_n1681 :
  quat_nrd_std 1461 45 2 1 = 2136551 := by
  dioph_surface [quat_nrd_std]

/-- Automated certified unit fraction decomposition for a = 4, n = 1681 via dioph_surface. -/
theorem meta_conic_cert_a4_n1681 :
  (4 : ℚ) / 1681 = (1 : ℚ) / 434 + (1 : ℚ) / 17794 + (1 : ℚ) / 52111 := by
  dioph_surface

/-- Automated four-square norm decomposition for u-factor at a = 4, n = 2521 via dioph_surface. -/
theorem meta_four_sq_u_a4_n2521 :
  quat_nrd_std 322 78 34 0 = 110924 := by
  dioph_surface [quat_nrd_std]

/-- Automated four-square norm decomposition for v-factor at a = 4, n = 2521 via dioph_surface. -/
theorem meta_four_sq_v_a4_n2521 :
  quat_nrd_std 4819 307 69 0 = 23321771 := by
  dioph_surface [quat_nrd_std]

/-- Automated certified unit fraction decomposition for a = 4, n = 2521 via dioph_surface. -/
theorem meta_conic_cert_a4_n2521 :
  (4 : ℚ) / 2521 = (1 : ℚ) / 638 + (1 : ℚ) / 55462 + (1 : ℚ) / 804199 := by
  dioph_surface

/-- Automated four-square norm decomposition for u-factor at a = 4, n = 3361 via dioph_surface. -/
theorem meta_four_sq_u_a4_n3361 :
  quat_nrd_std 646 53 0 0 = 420125 := by
  dioph_surface [quat_nrd_std]

/-- Automated four-square norm decomposition for v-factor at a = 4, n = 3361 via dioph_surface. -/
theorem meta_four_sq_v_a4_n3361 :
  quat_nrd_std 4318 884 0 0 = 19426580 := by
  dioph_surface [quat_nrd_std]

/-- Automated certified unit fraction decomposition for a = 4, n = 3361 via dioph_surface. -/
theorem meta_conic_cert_a4_n3361 :
  (4 : ℚ) / 3361 = (1 : ℚ) / 850 + (1 : ℚ) / 84025 + (1 : ℚ) / 571370 := by
  dioph_surface

/-- Automated four-square norm decomposition for u-factor at a = 4, n = 4201 via dioph_surface. -/
theorem meta_four_sq_u_a4_n4201 :
  quat_nrd_std 2002 242 0 0 = 4066568 := by
  dioph_surface [quat_nrd_std]

/-- Automated four-square norm decomposition for v-factor at a = 4, n = 4201 via dioph_surface. -/
theorem meta_four_sq_v_a4_n4201 :
  quat_nrd_std 2184 264 0 0 = 4839552 := by
  dioph_surface [quat_nrd_std]

/-- Automated certified unit fraction decomposition for a = 4, n = 4201 via dioph_surface. -/
theorem meta_conic_cert_a4_n4201 :
  (4 : ℚ) / 4201 = (1 : ℚ) / 1056 + (1 : ℚ) / 369688 + (1 : ℚ) / 403296 := by
  dioph_surface

/-- Automated four-square norm decomposition for u-factor at a = 4, n = 5041 via dioph_surface. -/
theorem meta_four_sq_u_a4_n5041 :
  quat_nrd_std 2131 57 15 2 = 4544639 := by
  dioph_surface [quat_nrd_std]

/-- Automated four-square norm decomposition for v-factor at a = 4, n = 5041 via dioph_surface. -/
theorem meta_four_sq_v_a4_n5041 :
  quat_nrd_std 2991 41 3 2 = 8947775 := by
  dioph_surface [quat_nrd_std]

/-- Automated certified unit fraction decomposition for a = 4, n = 5041 via dioph_surface. -/
theorem meta_conic_cert_a4_n5041 :
  (4 : ℚ) / 5041 = (1 : ℚ) / 1265 + (1 : ℚ) / 574816 + (1 : ℚ) / 806560 := by
  dioph_surface

/-- Automated four-square norm decomposition for u-factor at a = 4, n = 121 via dioph_surface. -/
theorem meta_four_sq_u_a4_n121 :
  quat_nrd_std 46 6 2 0 = 2156 := by
  dioph_surface [quat_nrd_std]

/-- Automated four-square norm decomposition for v-factor at a = 4, n = 121 via dioph_surface. -/
theorem meta_four_sq_v_a4_n121 :
  quat_nrd_std 109 7 7 0 = 11979 := by
  dioph_surface [quat_nrd_std]

/-- Automated certified unit fraction decomposition for a = 4, n = 121 via dioph_surface. -/
theorem meta_conic_cert_a4_n121 :
  (4 : ℚ) / 121 = (1 : ℚ) / 42 + (1 : ℚ) / 154 + (1 : ℚ) / 363 := by
  dioph_surface

/-- Automated four-square norm decomposition for u-factor at a = 4, n = 961 via dioph_surface. -/
theorem meta_four_sq_u_a4_n961 :
  quat_nrd_std 367 17 7 3 = 135036 := by
  dioph_surface [quat_nrd_std]

/-- Automated four-square norm decomposition for v-factor at a = 4, n = 961 via dioph_surface. -/
theorem meta_four_sq_v_a4_n961 :
  quat_nrd_std 690 22 6 6 = 476656 := by
  dioph_surface [quat_nrd_std]

/-- Automated certified unit fraction decomposition for a = 4, n = 961 via dioph_surface. -/
theorem meta_conic_cert_a4_n961 :
  (4 : ℚ) / 961 = (1 : ℚ) / 264 + (1 : ℚ) / 4092 + (1 : ℚ) / 7688 := by
  dioph_surface

/-- Automated four-square norm decomposition for u-factor at a = 4, n = 1801 via dioph_surface. -/
theorem meta_four_sq_u_a4_n1801 :
  quat_nrd_std 490 336 0 0 = 352996 := by
  dioph_surface [quat_nrd_std]

/-- Automated four-square norm decomposition for v-factor at a = 4, n = 1801 via dioph_surface. -/
theorem meta_four_sq_v_a4_n1801 :
  quat_nrd_std 1155 792 0 0 = 1961289 := by
  dioph_surface [quat_nrd_std]

/-- Automated certified unit fraction decomposition for a = 4, n = 1801 via dioph_surface. -/
theorem meta_conic_cert_a4_n1801 :
  (4 : ℚ) / 1801 = (1 : ℚ) / 462 + (1 : ℚ) / 25214 + (1 : ℚ) / 59433 := by
  dioph_surface

/-- Automated four-square norm decomposition for u-factor at a = 4, n = 2641 via dioph_surface. -/
theorem meta_four_sq_u_a4_n2641 :
  quat_nrd_std 1206 118 6 0 = 1468396 := by
  dioph_surface [quat_nrd_std]

/-- Automated four-square norm decomposition for v-factor at a = 4, n = 2641 via dioph_surface. -/
theorem meta_four_sq_v_a4_n2641 :
  quat_nrd_std 1490 46 10 0 = 2222316 := by
  dioph_surface [quat_nrd_std]

/-- Automated certified unit fraction decomposition for a = 4, n = 2641 via dioph_surface. -/
theorem meta_conic_cert_a4_n2641 :
  (4 : ℚ) / 2641 = (1 : ℚ) / 684 + (1 : ℚ) / 34472 + (1 : ℚ) / 42408 := by
  dioph_surface

/-- Automated four-square norm decomposition for u-factor at a = 4, n = 3481 via dioph_surface. -/
theorem meta_four_sq_u_a4_n3481 :
  quat_nrd_std 1540 20 6 0 = 2372036 := by
  dioph_surface [quat_nrd_std]

/-- Automated four-square norm decomposition for v-factor at a = 4, n = 3481 via dioph_surface. -/
theorem meta_four_sq_v_a4_n3481 :
  quat_nrd_std 1975 30 26 0 = 3902201 := by
  dioph_surface [quat_nrd_std]

/-- Automated certified unit fraction decomposition for a = 4, n = 3481 via dioph_surface. -/
theorem meta_conic_cert_a4_n3481 :
  (4 : ℚ) / 3481 = (1 : ℚ) / 874 + (1 : ℚ) / 360962 + (1 : ℚ) / 462973 := by
  dioph_surface

/-- Automated four-square norm decomposition for u-factor at a = 4, n = 4321 via dioph_surface. -/
theorem meta_four_sq_u_a4_n4321 :
  quat_nrd_std 1755 75 17 0 = 3085939 := by
  dioph_surface [quat_nrd_std]

/-- Automated four-square norm decomposition for v-factor at a = 4, n = 4321 via dioph_surface. -/
theorem meta_four_sq_v_a4_n4321 :
  quat_nrd_std 2696 456 72 0 = 7481536 := by
  dioph_surface [quat_nrd_std]

/-- Automated certified unit fraction decomposition for a = 4, n = 4321 via dioph_surface. -/
theorem meta_conic_cert_a4_n4321 :
  (4 : ℚ) / 4321 = (1 : ℚ) / 1112 + (1 : ℚ) / 62133 + (1 : ℚ) / 96744 := by
  dioph_surface

/-- Automated four-square norm decomposition for u-factor at a = 4, n = 5161 via dioph_surface. -/
theorem meta_four_sq_u_a4_n5161 :
  quat_nrd_std 2329 55 11 0 = 5427387 := by
  dioph_surface [quat_nrd_std]

/-- Automated four-square norm decomposition for v-factor at a = 4, n = 5161 via dioph_surface. -/
theorem meta_four_sq_v_a4_n5161 :
  quat_nrd_std 2878 162 102 0 = 8319532 := by
  dioph_surface [quat_nrd_std]

/-- Automated certified unit fraction decomposition for a = 4, n = 5161 via dioph_surface. -/
theorem meta_conic_cert_a4_n5161 :
  (4 : ℚ) / 5161 = (1 : ℚ) / 1302 + (1 : ℚ) / 258447 + (1 : ℚ) / 319982 := by
  dioph_surface

/-- Automated four-square norm decomposition for u-factor at a = 4, n = 6001 via dioph_surface. -/
theorem meta_four_sq_u_a4_n6001 :
  quat_nrd_std 2489 656 0 0 = 6625457 := by
  dioph_surface [quat_nrd_std]

/-- Automated four-square norm decomposition for v-factor at a = 4, n = 6001 via dioph_surface. -/
theorem meta_four_sq_v_a4_n6001 :
  quat_nrd_std 3509 176 0 0 = 12344057 := by
  dioph_surface [quat_nrd_std]

/-- Automated certified unit fraction decomposition for a = 4, n = 6001 via dioph_surface. -/
theorem meta_conic_cert_a4_n6001 :
  (4 : ℚ) / 6001 = (1 : ℚ) / 1507 + (1 : ℚ) / 580332 + (1 : ℚ) / 792132 := by
  dioph_surface
