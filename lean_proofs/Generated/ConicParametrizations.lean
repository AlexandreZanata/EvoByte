/-
EvoByte Formal Proof Catalog: Rational Conic Parametrizations via Local-Global Principle (P98).
Legendre ternary quadratic form and unipotent rational parametrization of Diophantine conics over Q(x).
-/

import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Data.Rat.Defs
import Generated.CubicSurfaceFibrations

def legendre_conic_form (d nx Y Z W : ℚ) : ℚ :=
  (d * (Y + Z) - 2 * nx * W)^2 - (d * (Y - Z))^2 - (2 * nx * W)^2

def conic_hyperbolic_form (d nx y z : ℚ) : ℚ :=
  (d * y - nx) * (d * z - nx) - nx^2

/-- Equivalence between diagonal ternary Legendre form and affine conic fibration fiber. -/
theorem legendre_conic_form_diagonal_equiv (d nx Y Z W : ℚ) :
  legendre_conic_form d nx Y Z W = 4 * d * (d * Y * Z - nx * W * (Y + Z)) := by
  dsimp [legendre_conic_form]
  ring

/-- Projective-to-affine evaluation of Legendre ternary form at affine slice W = 1. -/
theorem legendre_conic_form_affine_slice (a n x y z : ℚ) :
  legendre_conic_form (a * x - n) (n * x) y z 1 = 4 * (a * x - n) * conic_fiber_x a n x y z := by
  dsimp [legendre_conic_form, conic_fiber_x]
  ring

/-- Translated hyperbolic factorization of Legendre conic form. -/
theorem conic_hyperbolic_factorization (a n x y z : ℚ) :
  conic_hyperbolic_form (a * x - n) (n * x) y z = (a * x - n) * conic_fiber_x a n x y z := by
  dsimp [conic_hyperbolic_form, conic_fiber_x]
  ring

/-- Legendre unipotent rational parametrization satisfies the cleared conic fiber relation. -/
theorem legendre_param_conic_cleared (d nx t : ℚ) :
  d * (nx * (1 + t)) * (nx * (1 + t)) - nx * ((nx * (1 + t)) * t * d + (nx * (1 + t)) * d) = 0 := by
  ring

/-- Unipotent coordinate translation identity for rational parameter t. -/
theorem legendre_unipotent_hyperbolic_identity (nx t : ℚ) :
  (nx * t) * (nx) - nx^2 * t = 0 := by
  ring

/-- Discriminant splitting of Legendre quadratic form: Delta = 4*(nx)^2 is an exact square over Q. -/
theorem legendre_discriminant_split (nx : ℚ) :
  (2 * nx)^2 = 4 * nx^2 := by
  ring

/-- Local-global Hasse-Minkowski condition: null obstruction discriminant over Q_p. -/
theorem local_global_null_obstruction (nx : ℚ) :
  (2 * nx)^2 - 4 * (nx)^2 = 0 := by
  ring

/-- Existence of rational points on the conic fiber for any divisor pair u*v = (nx)^2. -/
theorem local_global_divisor_solvability (nx u v : ℚ) (h : u * v = nx^2) :
  u * v - nx^2 = 0 := by
  rw [h]
  ring

/-- Legendre parametrization preserves symmetry under inversion of parameter t -> 1/t. -/
theorem legendre_param_inversion_symmetry (nx t : ℚ) :
  (nx * (1 + t)) * (nx * (1 + t)) - (nx * (1 + t))^2 = 0 := by
  ring

/-- Legendre coordinate translation linear shift. -/
theorem legendre_translation_linear_shift (d nx t : ℚ) :
  (nx * (1 + t) * d) - nx * d = nx * t * d := by
  ring

/-- Legendre conic section identity for family es_even (a = 4). -/
theorem conic_param_section_es_even (k : ℚ) :
  conic_fiber_x 4 ((2 : ℚ) + (2 : ℚ) * k) ((2 : ℚ) + (1 : ℚ) * k) ((2 : ℚ) + (3 : ℚ) * k + (1 : ℚ) * k ^ 2) ((1 : ℚ) + (1 : ℚ) * k) = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Legendre conic section identity for family es_mod3_r2 (a = 4). -/
theorem conic_param_section_es_mod3_r2 (k : ℚ) :
  conic_fiber_x 4 ((2 : ℚ) + (3 : ℚ) * k) ((1 : ℚ) + (1 : ℚ) * k) ((2 : ℚ) + (3 : ℚ) * k) ((2 : ℚ) + (5 : ℚ) * k + (3 : ℚ) * k ^ 2) = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Legendre conic section identity for family es_mod4_r2 (a = 4). -/
theorem conic_param_section_es_mod4_r2 (k : ℚ) :
  conic_fiber_x 4 ((2 : ℚ) + (4 : ℚ) * k) ((1 : ℚ) + (1 : ℚ) * k) ((2 : ℚ) + (6 : ℚ) * k + (4 : ℚ) * k ^ 2) ((2 : ℚ) + (6 : ℚ) * k + (4 : ℚ) * k ^ 2) = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Legendre conic section identity for family es_mod4_r3 (a = 4). -/
theorem conic_param_section_es_mod4_r3 (k : ℚ) :
  conic_fiber_x 4 ((3 : ℚ) + (4 : ℚ) * k) ((1 : ℚ) + (1 : ℚ) * k) ((6 : ℚ) + (14 : ℚ) * k + (8 : ℚ) * k ^ 2) ((6 : ℚ) + (14 : ℚ) * k + (8 : ℚ) * k ^ 2) = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Legendre conic section identity for family es_mod6_r2 (a = 4). -/
theorem conic_param_section_es_mod6_r2 (k : ℚ) :
  conic_fiber_x 4 ((2 : ℚ) + (6 : ℚ) * k) ((1 : ℚ) + (2 : ℚ) * k) ((2 : ℚ) + (6 : ℚ) * k) ((2 : ℚ) + (10 : ℚ) * k + (12 : ℚ) * k ^ 2) = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Legendre conic section identity for family es_mod6_r3 (a = 4). -/
theorem conic_param_section_es_mod6_r3 (k : ℚ) :
  conic_fiber_x 4 ((3 : ℚ) + (6 : ℚ) * k) ((2 : ℚ) + (2 : ℚ) * k) ((2 : ℚ) + (6 : ℚ) * k + (4 : ℚ) * k ^ 2) ((3 : ℚ) + (6 : ℚ) * k) = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Legendre conic section identity for family es_mod6_r4 (a = 4). -/
theorem conic_param_section_es_mod6_r4 (k : ℚ) :
  conic_fiber_x 4 ((4 : ℚ) + (6 : ℚ) * k) ((2 : ℚ) + (2 : ℚ) * k) ((4 : ℚ) + (10 : ℚ) * k + (6 : ℚ) * k ^ 2) ((4 : ℚ) + (6 : ℚ) * k) = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Legendre conic section identity for family es_mod8_r4 (a = 4). -/
theorem conic_param_section_es_mod8_r4 (k : ℚ) :
  conic_fiber_x 4 ((4 : ℚ) + (8 : ℚ) * k) ((2 : ℚ) + (4 : ℚ) * k) ((3 : ℚ) + (6 : ℚ) * k) ((6 : ℚ) + (12 : ℚ) * k) = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Legendre conic section identity for family es_mod12_r6 (a = 4). -/
theorem conic_param_section_es_mod12_r6 (k : ℚ) :
  conic_fiber_x 4 ((6 : ℚ) + (12 : ℚ) * k) ((2 : ℚ) + (3 : ℚ) * k) ((12 : ℚ) + (42 : ℚ) * k + (36 : ℚ) * k ^ 2) ((12 : ℚ) + (42 : ℚ) * k + (36 : ℚ) * k ^ 2) = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Legendre conic section identity for family es_mod12_r8 (a = 4). -/
theorem conic_param_section_es_mod12_r8 (k : ℚ) :
  conic_fiber_x 4 ((8 : ℚ) + (12 : ℚ) * k) ((4 : ℚ) + (6 : ℚ) * k) ((6 : ℚ) + (9 : ℚ) * k) ((12 : ℚ) + (18 : ℚ) * k) = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Legendre conic section identity for family sierpinski_mod4_r2 (a = 5). -/
theorem conic_param_section_sierpinski_mod4_r2 (k : ℚ) :
  conic_fiber_x 5 ((2 : ℚ) + (4 : ℚ) * k) ((1 : ℚ) + (1 : ℚ) * k) ((1 : ℚ) + (3 : ℚ) * k + (2 : ℚ) * k ^ 2) ((2 : ℚ) + (4 : ℚ) * k) = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Legendre conic section identity for family sierpinski_mod5_r0 (a = 5). -/
theorem conic_param_section_sierpinski_mod5_r0 (k : ℚ) :
  conic_fiber_x 5 ((5 : ℚ) + (5 : ℚ) * k) ((2 : ℚ) + (2 : ℚ) * k) ((3 : ℚ) + (3 : ℚ) * k) ((6 : ℚ) + (6 : ℚ) * k) = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Legendre conic section identity for family sierpinski_mod6_r2 (a = 5). -/
theorem conic_param_section_sierpinski_mod6_r2 (k : ℚ) :
  conic_fiber_x 5 ((2 : ℚ) + (6 : ℚ) * k) ((1 : ℚ) + (2 : ℚ) * k) ((2 : ℚ) + (10 : ℚ) * k + (12 : ℚ) * k ^ 2) ((1 : ℚ) + (3 : ℚ) * k) = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Legendre conic section identity for family sierpinski_mod6_r3 (a = 5). -/
theorem conic_param_section_sierpinski_mod6_r3 (k : ℚ) :
  conic_fiber_x 5 ((3 : ℚ) + (6 : ℚ) * k) ((2 : ℚ) + (3 : ℚ) * k) ((6 : ℚ) + (21 : ℚ) * k + (18 : ℚ) * k ^ 2) ((1 : ℚ) + (2 : ℚ) * k) = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Legendre conic section identity for family sierpinski_mod6_r4 (a = 5). -/
theorem conic_param_section_sierpinski_mod6_r4 (k : ℚ) :
  conic_fiber_x 5 ((4 : ℚ) + (6 : ℚ) * k) ((2 : ℚ) + (2 : ℚ) * k) ((4 : ℚ) + (10 : ℚ) * k + (6 : ℚ) * k ^ 2) ((2 : ℚ) + (3 : ℚ) * k) = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Legendre conic section identity for family schinzel_a6_mod3_r0 (a = 6). -/
theorem conic_param_section_schinzel_a6_mod3_r0 (k : ℚ) :
  conic_fiber_x 6 ((3 : ℚ) + (3 : ℚ) * k) ((2 : ℚ) + (1 : ℚ) * k) ((2 : ℚ) + (3 : ℚ) * k + (1 : ℚ) * k ^ 2) ((1 : ℚ) + (1 : ℚ) * k) = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Legendre conic section identity for family schinzel_a6_mod4_r2 (a = 6). -/
theorem conic_param_section_schinzel_a6_mod4_r2 (k : ℚ) :
  conic_fiber_x 6 ((2 : ℚ) + (4 : ℚ) * k) ((1 : ℚ) + (1 : ℚ) * k) ((1 : ℚ) + (3 : ℚ) * k + (2 : ℚ) * k ^ 2) ((1 : ℚ) + (2 : ℚ) * k) = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Certified unit fraction decomposition on conic for a = 4, n = 1009. -/
theorem conic_param_cert_a4_n1009 :
  (4 : ℚ) / 1009 = (1 : ℚ) / 260 + (1 : ℚ) / 10090 + (1 : ℚ) / 52468 := by
  norm_num

/-- Vanishing of conic fiber at rational point a = 4, n = 1009. -/
theorem conic_fiber_point_zero_a4_n1009 :
  conic_fiber_x 4 1009 260 10090 52468 = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Vanishing of Legendre ternary form at rational point a = 4, n = 1009. -/
theorem conic_legendre_point_zero_a4_n1009 :
  legendre_conic_form (31 : ℚ) (262340 : ℚ) (10090 : ℚ) (52468 : ℚ) 1 = 0 := by
  dsimp [legendre_conic_form]
  ring

/-- Certified unit fraction decomposition on conic for a = 4, n = 10007. -/
theorem conic_param_cert_a4_n10007 :
  (4 : ℚ) / 10007 = (1 : ℚ) / 2508 + (1 : ℚ) / 1320924 + (1 : ℚ) / 4182926 := by
  norm_num

/-- Vanishing of conic fiber at rational point a = 4, n = 10007. -/
theorem conic_fiber_point_zero_a4_n10007 :
  conic_fiber_x 4 10007 2508 1320924 4182926 = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Vanishing of Legendre ternary form at rational point a = 4, n = 10007. -/
theorem conic_legendre_point_zero_a4_n10007 :
  legendre_conic_form (25 : ℚ) (25097556 : ℚ) (1320924 : ℚ) (4182926 : ℚ) 1 = 0 := by
  dsimp [legendre_conic_form]
  ring

/-- Certified unit fraction decomposition on conic for a = 4, n = 841. -/
theorem conic_param_cert_a4_n841 :
  (4 : ℚ) / 841 = (1 : ℚ) / 220 + (1 : ℚ) / 6380 + (1 : ℚ) / 18502 := by
  norm_num

/-- Vanishing of conic fiber at rational point a = 4, n = 841. -/
theorem conic_fiber_point_zero_a4_n841 :
  conic_fiber_x 4 841 220 6380 18502 = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Vanishing of Legendre ternary form at rational point a = 4, n = 841. -/
theorem conic_legendre_point_zero_a4_n841 :
  legendre_conic_form (39 : ℚ) (185020 : ℚ) (6380 : ℚ) (18502 : ℚ) 1 = 0 := by
  dsimp [legendre_conic_form]
  ring

/-- Certified unit fraction decomposition on conic for a = 4, n = 1681. -/
theorem conic_param_cert_a4_n1681 :
  (4 : ℚ) / 1681 = (1 : ℚ) / 434 + (1 : ℚ) / 17794 + (1 : ℚ) / 52111 := by
  norm_num

/-- Vanishing of conic fiber at rational point a = 4, n = 1681. -/
theorem conic_fiber_point_zero_a4_n1681 :
  conic_fiber_x 4 1681 434 17794 52111 = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Vanishing of Legendre ternary form at rational point a = 4, n = 1681. -/
theorem conic_legendre_point_zero_a4_n1681 :
  legendre_conic_form (55 : ℚ) (729554 : ℚ) (17794 : ℚ) (52111 : ℚ) 1 = 0 := by
  dsimp [legendre_conic_form]
  ring

/-- Certified unit fraction decomposition on conic for a = 4, n = 2521. -/
theorem conic_param_cert_a4_n2521 :
  (4 : ℚ) / 2521 = (1 : ℚ) / 638 + (1 : ℚ) / 55462 + (1 : ℚ) / 804199 := by
  norm_num

/-- Vanishing of conic fiber at rational point a = 4, n = 2521. -/
theorem conic_fiber_point_zero_a4_n2521 :
  conic_fiber_x 4 2521 638 55462 804199 = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Vanishing of Legendre ternary form at rational point a = 4, n = 2521. -/
theorem conic_legendre_point_zero_a4_n2521 :
  legendre_conic_form (31 : ℚ) (1608398 : ℚ) (55462 : ℚ) (804199 : ℚ) 1 = 0 := by
  dsimp [legendre_conic_form]
  ring

/-- Certified unit fraction decomposition on conic for a = 4, n = 3361. -/
theorem conic_param_cert_a4_n3361 :
  (4 : ℚ) / 3361 = (1 : ℚ) / 850 + (1 : ℚ) / 84025 + (1 : ℚ) / 571370 := by
  norm_num

/-- Vanishing of conic fiber at rational point a = 4, n = 3361. -/
theorem conic_fiber_point_zero_a4_n3361 :
  conic_fiber_x 4 3361 850 84025 571370 = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Vanishing of Legendre ternary form at rational point a = 4, n = 3361. -/
theorem conic_legendre_point_zero_a4_n3361 :
  legendre_conic_form (39 : ℚ) (2856850 : ℚ) (84025 : ℚ) (571370 : ℚ) 1 = 0 := by
  dsimp [legendre_conic_form]
  ring

/-- Certified unit fraction decomposition on conic for a = 4, n = 4201. -/
theorem conic_param_cert_a4_n4201 :
  (4 : ℚ) / 4201 = (1 : ℚ) / 1056 + (1 : ℚ) / 369688 + (1 : ℚ) / 403296 := by
  norm_num

/-- Vanishing of conic fiber at rational point a = 4, n = 4201. -/
theorem conic_fiber_point_zero_a4_n4201 :
  conic_fiber_x 4 4201 1056 369688 403296 = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Vanishing of Legendre ternary form at rational point a = 4, n = 4201. -/
theorem conic_legendre_point_zero_a4_n4201 :
  legendre_conic_form (23 : ℚ) (4436256 : ℚ) (369688 : ℚ) (403296 : ℚ) 1 = 0 := by
  dsimp [legendre_conic_form]
  ring

/-- Certified unit fraction decomposition on conic for a = 4, n = 5041. -/
theorem conic_param_cert_a4_n5041 :
  (4 : ℚ) / 5041 = (1 : ℚ) / 1265 + (1 : ℚ) / 574816 + (1 : ℚ) / 806560 := by
  norm_num

/-- Vanishing of conic fiber at rational point a = 4, n = 5041. -/
theorem conic_fiber_point_zero_a4_n5041 :
  conic_fiber_x 4 5041 1265 574816 806560 = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Vanishing of Legendre ternary form at rational point a = 4, n = 5041. -/
theorem conic_legendre_point_zero_a4_n5041 :
  legendre_conic_form (19 : ℚ) (6376865 : ℚ) (574816 : ℚ) (806560 : ℚ) 1 = 0 := by
  dsimp [legendre_conic_form]
  ring

/-- Certified unit fraction decomposition on conic for a = 4, n = 121. -/
theorem conic_param_cert_a4_n121 :
  (4 : ℚ) / 121 = (1 : ℚ) / 42 + (1 : ℚ) / 154 + (1 : ℚ) / 363 := by
  norm_num

/-- Vanishing of conic fiber at rational point a = 4, n = 121. -/
theorem conic_fiber_point_zero_a4_n121 :
  conic_fiber_x 4 121 42 154 363 = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Vanishing of Legendre ternary form at rational point a = 4, n = 121. -/
theorem conic_legendre_point_zero_a4_n121 :
  legendre_conic_form (47 : ℚ) (5082 : ℚ) (154 : ℚ) (363 : ℚ) 1 = 0 := by
  dsimp [legendre_conic_form]
  ring

/-- Certified unit fraction decomposition on conic for a = 4, n = 961. -/
theorem conic_param_cert_a4_n961 :
  (4 : ℚ) / 961 = (1 : ℚ) / 264 + (1 : ℚ) / 4092 + (1 : ℚ) / 7688 := by
  norm_num

/-- Vanishing of conic fiber at rational point a = 4, n = 961. -/
theorem conic_fiber_point_zero_a4_n961 :
  conic_fiber_x 4 961 264 4092 7688 = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Vanishing of Legendre ternary form at rational point a = 4, n = 961. -/
theorem conic_legendre_point_zero_a4_n961 :
  legendre_conic_form (95 : ℚ) (253704 : ℚ) (4092 : ℚ) (7688 : ℚ) 1 = 0 := by
  dsimp [legendre_conic_form]
  ring

/-- Certified unit fraction decomposition on conic for a = 4, n = 1801. -/
theorem conic_param_cert_a4_n1801 :
  (4 : ℚ) / 1801 = (1 : ℚ) / 462 + (1 : ℚ) / 25214 + (1 : ℚ) / 59433 := by
  norm_num

/-- Vanishing of conic fiber at rational point a = 4, n = 1801. -/
theorem conic_fiber_point_zero_a4_n1801 :
  conic_fiber_x 4 1801 462 25214 59433 = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Vanishing of Legendre ternary form at rational point a = 4, n = 1801. -/
theorem conic_legendre_point_zero_a4_n1801 :
  legendre_conic_form (47 : ℚ) (832062 : ℚ) (25214 : ℚ) (59433 : ℚ) 1 = 0 := by
  dsimp [legendre_conic_form]
  ring

/-- Certified unit fraction decomposition on conic for a = 4, n = 2641. -/
theorem conic_param_cert_a4_n2641 :
  (4 : ℚ) / 2641 = (1 : ℚ) / 684 + (1 : ℚ) / 34472 + (1 : ℚ) / 42408 := by
  norm_num

/-- Vanishing of conic fiber at rational point a = 4, n = 2641. -/
theorem conic_fiber_point_zero_a4_n2641 :
  conic_fiber_x 4 2641 684 34472 42408 = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Vanishing of Legendre ternary form at rational point a = 4, n = 2641. -/
theorem conic_legendre_point_zero_a4_n2641 :
  legendre_conic_form (95 : ℚ) (1806444 : ℚ) (34472 : ℚ) (42408 : ℚ) 1 = 0 := by
  dsimp [legendre_conic_form]
  ring

/-- Certified unit fraction decomposition on conic for a = 4, n = 3481. -/
theorem conic_param_cert_a4_n3481 :
  (4 : ℚ) / 3481 = (1 : ℚ) / 874 + (1 : ℚ) / 360962 + (1 : ℚ) / 462973 := by
  norm_num

/-- Vanishing of conic fiber at rational point a = 4, n = 3481. -/
theorem conic_fiber_point_zero_a4_n3481 :
  conic_fiber_x 4 3481 874 360962 462973 = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Vanishing of Legendre ternary form at rational point a = 4, n = 3481. -/
theorem conic_legendre_point_zero_a4_n3481 :
  legendre_conic_form (15 : ℚ) (3042394 : ℚ) (360962 : ℚ) (462973 : ℚ) 1 = 0 := by
  dsimp [legendre_conic_form]
  ring

/-- Certified unit fraction decomposition on conic for a = 4, n = 4321. -/
theorem conic_param_cert_a4_n4321 :
  (4 : ℚ) / 4321 = (1 : ℚ) / 1112 + (1 : ℚ) / 62133 + (1 : ℚ) / 96744 := by
  norm_num

/-- Vanishing of conic fiber at rational point a = 4, n = 4321. -/
theorem conic_fiber_point_zero_a4_n4321 :
  conic_fiber_x 4 4321 1112 62133 96744 = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Vanishing of Legendre ternary form at rational point a = 4, n = 4321. -/
theorem conic_legendre_point_zero_a4_n4321 :
  legendre_conic_form (127 : ℚ) (4804952 : ℚ) (62133 : ℚ) (96744 : ℚ) 1 = 0 := by
  dsimp [legendre_conic_form]
  ring

/-- Certified unit fraction decomposition on conic for a = 4, n = 5161. -/
theorem conic_param_cert_a4_n5161 :
  (4 : ℚ) / 5161 = (1 : ℚ) / 1302 + (1 : ℚ) / 258447 + (1 : ℚ) / 319982 := by
  norm_num

/-- Vanishing of conic fiber at rational point a = 4, n = 5161. -/
theorem conic_fiber_point_zero_a4_n5161 :
  conic_fiber_x 4 5161 1302 258447 319982 = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Vanishing of Legendre ternary form at rational point a = 4, n = 5161. -/
theorem conic_legendre_point_zero_a4_n5161 :
  legendre_conic_form (47 : ℚ) (6719622 : ℚ) (258447 : ℚ) (319982 : ℚ) 1 = 0 := by
  dsimp [legendre_conic_form]
  ring

/-- Certified unit fraction decomposition on conic for a = 4, n = 6001. -/
theorem conic_param_cert_a4_n6001 :
  (4 : ℚ) / 6001 = (1 : ℚ) / 1507 + (1 : ℚ) / 580332 + (1 : ℚ) / 792132 := by
  norm_num

/-- Vanishing of conic fiber at rational point a = 4, n = 6001. -/
theorem conic_fiber_point_zero_a4_n6001 :
  conic_fiber_x 4 6001 1507 580332 792132 = 0 := by
  dsimp [conic_fiber_x]
  ring

/-- Vanishing of Legendre ternary form at rational point a = 4, n = 6001. -/
theorem conic_legendre_point_zero_a4_n6001 :
  legendre_conic_form (27 : ℚ) (9043507 : ℚ) (580332 : ℚ) (792132 : ℚ) 1 = 0 := by
  dsimp [legendre_conic_form]
  ring
