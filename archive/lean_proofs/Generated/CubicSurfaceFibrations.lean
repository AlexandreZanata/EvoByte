/-
EvoByte Formal Proof Catalog: Diophantine Cubic Surface Conic Fibrations (P97).
Varietal formulation a*x*y*z = n*(y*z + x*z + x*y) and conic bundle C_x(y, z) over Q(x).
-/

import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Data.Rat.Defs

def cubic_surface_poly (a n x y z : ℚ) : ℚ :=
  a * x * y * z - n * (y * z + x * z + x * y)

def conic_fiber_x (a n x y z : ℚ) : ℚ :=
  (a * x - n) * y * z - n * x * (y + z)

def conic_bilinear_x (a n x y z : ℚ) : ℚ :=
  ((a * x - n) * y - n * x) * ((a * x - n) * z - n * x) - (n * x)^2

def conic_discriminant (n x : ℚ) : ℚ :=
  (n * x)^2

/-- Equivalence between cubic surface equation and affine conic fibration fiber at x. -/
theorem cubic_surface_fiber_x_equiv (a n x y z : ℚ) :
  cubic_surface_poly a n x y z = conic_fiber_x a n x y z := by
  dsimp [cubic_surface_poly, conic_fiber_x]
  ring

/-- Bilinear factorization of affine conic fiber into translated hyperbolic components. -/
theorem cubic_surface_bilinear_factorization (a n x y z : ℚ) :
  conic_bilinear_x a n x y z = (a * x - n) * conic_fiber_x a n x y z := by
  dsimp [conic_bilinear_x, conic_fiber_x]
  ring

/-- Central discriminant expansion of affine conic fibration at x. -/
theorem conic_fibration_discriminant_sq (n x : ℚ) :
  conic_discriminant n x = n^2 * x^2 := by
  dsimp [conic_discriminant]
  ring

/-- Translated hyperbolic expansion of conic fiber at x. -/
theorem conic_fiber_translation_identity (a n x y z : ℚ) :
  ((a * x - n) * y - n * x) * ((a * x - n) * z - n * x) =
  (a * x - n)^2 * y * z - n * x * (a * x - n) * (y + z) + (n * x)^2 := by
  ring

/-- S_3 permutation invariance of cubic surface under (x, y) swap. -/
theorem cubic_surface_symm_xy (a n x y z : ℚ) :
  cubic_surface_poly a n x y z = cubic_surface_poly a n y x z := by
  dsimp [cubic_surface_poly]
  ring

/-- S_3 permutation invariance of cubic surface under (y, z) swap. -/
theorem cubic_surface_symm_yz (a n x y z : ℚ) :
  cubic_surface_poly a n x y z = cubic_surface_poly a n x z y := by
  dsimp [cubic_surface_poly]
  ring

/-- S_3 permutation invariance of cubic surface under (x, z) swap. -/
theorem cubic_surface_symm_xz (a n x y z : ℚ) :
  cubic_surface_poly a n x y z = cubic_surface_poly a n z y x := by
  dsimp [cubic_surface_poly]
  ring

/-- S_3 cyclic permutation invariance of cubic surface. -/
theorem cubic_surface_cyclic_perm (a n x y z : ℚ) :
  cubic_surface_poly a n x y z = cubic_surface_poly a n y z x := by
  dsimp [cubic_surface_poly]
  ring

/-- Parametric rational section on cubic surface for family es_even (a = 4). -/
theorem cubic_surface_section_es_even (k : ℚ) :
  cubic_surface_poly 4 ((2 : ℚ) + (2 : ℚ) * k) ((2 : ℚ) + (1 : ℚ) * k) ((2 : ℚ) + (3 : ℚ) * k + (1 : ℚ) * k ^ 2) ((1 : ℚ) + (1 : ℚ) * k) = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Parametric rational section on cubic surface for family es_mod3_r2 (a = 4). -/
theorem cubic_surface_section_es_mod3_r2 (k : ℚ) :
  cubic_surface_poly 4 ((2 : ℚ) + (3 : ℚ) * k) ((1 : ℚ) + (1 : ℚ) * k) ((2 : ℚ) + (3 : ℚ) * k) ((2 : ℚ) + (5 : ℚ) * k + (3 : ℚ) * k ^ 2) = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Parametric rational section on cubic surface for family es_mod4_r2 (a = 4). -/
theorem cubic_surface_section_es_mod4_r2 (k : ℚ) :
  cubic_surface_poly 4 ((2 : ℚ) + (4 : ℚ) * k) ((1 : ℚ) + (1 : ℚ) * k) ((2 : ℚ) + (6 : ℚ) * k + (4 : ℚ) * k ^ 2) ((2 : ℚ) + (6 : ℚ) * k + (4 : ℚ) * k ^ 2) = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Parametric rational section on cubic surface for family es_mod4_r3 (a = 4). -/
theorem cubic_surface_section_es_mod4_r3 (k : ℚ) :
  cubic_surface_poly 4 ((3 : ℚ) + (4 : ℚ) * k) ((1 : ℚ) + (1 : ℚ) * k) ((6 : ℚ) + (14 : ℚ) * k + (8 : ℚ) * k ^ 2) ((6 : ℚ) + (14 : ℚ) * k + (8 : ℚ) * k ^ 2) = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Parametric rational section on cubic surface for family es_mod6_r2 (a = 4). -/
theorem cubic_surface_section_es_mod6_r2 (k : ℚ) :
  cubic_surface_poly 4 ((2 : ℚ) + (6 : ℚ) * k) ((1 : ℚ) + (2 : ℚ) * k) ((2 : ℚ) + (6 : ℚ) * k) ((2 : ℚ) + (10 : ℚ) * k + (12 : ℚ) * k ^ 2) = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Parametric rational section on cubic surface for family es_mod6_r3 (a = 4). -/
theorem cubic_surface_section_es_mod6_r3 (k : ℚ) :
  cubic_surface_poly 4 ((3 : ℚ) + (6 : ℚ) * k) ((2 : ℚ) + (2 : ℚ) * k) ((2 : ℚ) + (6 : ℚ) * k + (4 : ℚ) * k ^ 2) ((3 : ℚ) + (6 : ℚ) * k) = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Parametric rational section on cubic surface for family es_mod6_r4 (a = 4). -/
theorem cubic_surface_section_es_mod6_r4 (k : ℚ) :
  cubic_surface_poly 4 ((4 : ℚ) + (6 : ℚ) * k) ((2 : ℚ) + (2 : ℚ) * k) ((4 : ℚ) + (10 : ℚ) * k + (6 : ℚ) * k ^ 2) ((4 : ℚ) + (6 : ℚ) * k) = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Parametric rational section on cubic surface for family es_mod8_r4 (a = 4). -/
theorem cubic_surface_section_es_mod8_r4 (k : ℚ) :
  cubic_surface_poly 4 ((4 : ℚ) + (8 : ℚ) * k) ((2 : ℚ) + (4 : ℚ) * k) ((3 : ℚ) + (6 : ℚ) * k) ((6 : ℚ) + (12 : ℚ) * k) = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Parametric rational section on cubic surface for family es_mod12_r6 (a = 4). -/
theorem cubic_surface_section_es_mod12_r6 (k : ℚ) :
  cubic_surface_poly 4 ((6 : ℚ) + (12 : ℚ) * k) ((2 : ℚ) + (3 : ℚ) * k) ((12 : ℚ) + (42 : ℚ) * k + (36 : ℚ) * k ^ 2) ((12 : ℚ) + (42 : ℚ) * k + (36 : ℚ) * k ^ 2) = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Parametric rational section on cubic surface for family es_mod12_r8 (a = 4). -/
theorem cubic_surface_section_es_mod12_r8 (k : ℚ) :
  cubic_surface_poly 4 ((8 : ℚ) + (12 : ℚ) * k) ((4 : ℚ) + (6 : ℚ) * k) ((6 : ℚ) + (9 : ℚ) * k) ((12 : ℚ) + (18 : ℚ) * k) = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Parametric rational section on cubic surface for family sierpinski_mod4_r2 (a = 5). -/
theorem cubic_surface_section_sierpinski_mod4_r2 (k : ℚ) :
  cubic_surface_poly 5 ((2 : ℚ) + (4 : ℚ) * k) ((1 : ℚ) + (1 : ℚ) * k) ((1 : ℚ) + (3 : ℚ) * k + (2 : ℚ) * k ^ 2) ((2 : ℚ) + (4 : ℚ) * k) = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Parametric rational section on cubic surface for family sierpinski_mod5_r0 (a = 5). -/
theorem cubic_surface_section_sierpinski_mod5_r0 (k : ℚ) :
  cubic_surface_poly 5 ((5 : ℚ) + (5 : ℚ) * k) ((2 : ℚ) + (2 : ℚ) * k) ((3 : ℚ) + (3 : ℚ) * k) ((6 : ℚ) + (6 : ℚ) * k) = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Parametric rational section on cubic surface for family sierpinski_mod6_r2 (a = 5). -/
theorem cubic_surface_section_sierpinski_mod6_r2 (k : ℚ) :
  cubic_surface_poly 5 ((2 : ℚ) + (6 : ℚ) * k) ((1 : ℚ) + (2 : ℚ) * k) ((2 : ℚ) + (10 : ℚ) * k + (12 : ℚ) * k ^ 2) ((1 : ℚ) + (3 : ℚ) * k) = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Parametric rational section on cubic surface for family sierpinski_mod6_r3 (a = 5). -/
theorem cubic_surface_section_sierpinski_mod6_r3 (k : ℚ) :
  cubic_surface_poly 5 ((3 : ℚ) + (6 : ℚ) * k) ((2 : ℚ) + (3 : ℚ) * k) ((6 : ℚ) + (21 : ℚ) * k + (18 : ℚ) * k ^ 2) ((1 : ℚ) + (2 : ℚ) * k) = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Parametric rational section on cubic surface for family sierpinski_mod6_r4 (a = 5). -/
theorem cubic_surface_section_sierpinski_mod6_r4 (k : ℚ) :
  cubic_surface_poly 5 ((4 : ℚ) + (6 : ℚ) * k) ((2 : ℚ) + (2 : ℚ) * k) ((4 : ℚ) + (10 : ℚ) * k + (6 : ℚ) * k ^ 2) ((2 : ℚ) + (3 : ℚ) * k) = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Parametric rational section on cubic surface for family schinzel_a6_mod3_r0 (a = 6). -/
theorem cubic_surface_section_schinzel_a6_mod3_r0 (k : ℚ) :
  cubic_surface_poly 6 ((3 : ℚ) + (3 : ℚ) * k) ((2 : ℚ) + (1 : ℚ) * k) ((2 : ℚ) + (3 : ℚ) * k + (1 : ℚ) * k ^ 2) ((1 : ℚ) + (1 : ℚ) * k) = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Parametric rational section on cubic surface for family schinzel_a6_mod4_r2 (a = 6). -/
theorem cubic_surface_section_schinzel_a6_mod4_r2 (k : ℚ) :
  cubic_surface_poly 6 ((2 : ℚ) + (4 : ℚ) * k) ((1 : ℚ) + (1 : ℚ) * k) ((1 : ℚ) + (3 : ℚ) * k + (2 : ℚ) * k ^ 2) ((1 : ℚ) + (2 : ℚ) * k) = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Certified unit fraction decomposition on cubic surface for a = 4, n = 1009. -/
theorem cubic_surface_cert_a4_n1009 :
  (4 : ℚ) / 1009 = (1 : ℚ) / 260 + (1 : ℚ) / 10090 + (1 : ℚ) / 52468 := by
  norm_num

/-- Vanishing of cubic surface polynomial at rational point a = 4, n = 1009. -/
theorem cubic_surface_point_zero_a4_n1009 :
  cubic_surface_poly 4 1009 260 10090 52468 = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Certified unit fraction decomposition on cubic surface for a = 4, n = 10007. -/
theorem cubic_surface_cert_a4_n10007 :
  (4 : ℚ) / 10007 = (1 : ℚ) / 2508 + (1 : ℚ) / 1320924 + (1 : ℚ) / 4182926 := by
  norm_num

/-- Vanishing of cubic surface polynomial at rational point a = 4, n = 10007. -/
theorem cubic_surface_point_zero_a4_n10007 :
  cubic_surface_poly 4 10007 2508 1320924 4182926 = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Certified unit fraction decomposition on cubic surface for a = 4, n = 841. -/
theorem cubic_surface_cert_a4_n841 :
  (4 : ℚ) / 841 = (1 : ℚ) / 220 + (1 : ℚ) / 6380 + (1 : ℚ) / 18502 := by
  norm_num

/-- Vanishing of cubic surface polynomial at rational point a = 4, n = 841. -/
theorem cubic_surface_point_zero_a4_n841 :
  cubic_surface_poly 4 841 220 6380 18502 = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Certified unit fraction decomposition on cubic surface for a = 4, n = 1681. -/
theorem cubic_surface_cert_a4_n1681 :
  (4 : ℚ) / 1681 = (1 : ℚ) / 434 + (1 : ℚ) / 17794 + (1 : ℚ) / 52111 := by
  norm_num

/-- Vanishing of cubic surface polynomial at rational point a = 4, n = 1681. -/
theorem cubic_surface_point_zero_a4_n1681 :
  cubic_surface_poly 4 1681 434 17794 52111 = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Certified unit fraction decomposition on cubic surface for a = 4, n = 2521. -/
theorem cubic_surface_cert_a4_n2521 :
  (4 : ℚ) / 2521 = (1 : ℚ) / 638 + (1 : ℚ) / 55462 + (1 : ℚ) / 804199 := by
  norm_num

/-- Vanishing of cubic surface polynomial at rational point a = 4, n = 2521. -/
theorem cubic_surface_point_zero_a4_n2521 :
  cubic_surface_poly 4 2521 638 55462 804199 = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Certified unit fraction decomposition on cubic surface for a = 4, n = 3361. -/
theorem cubic_surface_cert_a4_n3361 :
  (4 : ℚ) / 3361 = (1 : ℚ) / 850 + (1 : ℚ) / 84025 + (1 : ℚ) / 571370 := by
  norm_num

/-- Vanishing of cubic surface polynomial at rational point a = 4, n = 3361. -/
theorem cubic_surface_point_zero_a4_n3361 :
  cubic_surface_poly 4 3361 850 84025 571370 = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Certified unit fraction decomposition on cubic surface for a = 4, n = 4201. -/
theorem cubic_surface_cert_a4_n4201 :
  (4 : ℚ) / 4201 = (1 : ℚ) / 1056 + (1 : ℚ) / 369688 + (1 : ℚ) / 403296 := by
  norm_num

/-- Vanishing of cubic surface polynomial at rational point a = 4, n = 4201. -/
theorem cubic_surface_point_zero_a4_n4201 :
  cubic_surface_poly 4 4201 1056 369688 403296 = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Certified unit fraction decomposition on cubic surface for a = 4, n = 5041. -/
theorem cubic_surface_cert_a4_n5041 :
  (4 : ℚ) / 5041 = (1 : ℚ) / 1265 + (1 : ℚ) / 574816 + (1 : ℚ) / 806560 := by
  norm_num

/-- Vanishing of cubic surface polynomial at rational point a = 4, n = 5041. -/
theorem cubic_surface_point_zero_a4_n5041 :
  cubic_surface_poly 4 5041 1265 574816 806560 = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Certified unit fraction decomposition on cubic surface for a = 4, n = 121. -/
theorem cubic_surface_cert_a4_n121 :
  (4 : ℚ) / 121 = (1 : ℚ) / 42 + (1 : ℚ) / 154 + (1 : ℚ) / 363 := by
  norm_num

/-- Vanishing of cubic surface polynomial at rational point a = 4, n = 121. -/
theorem cubic_surface_point_zero_a4_n121 :
  cubic_surface_poly 4 121 42 154 363 = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Certified unit fraction decomposition on cubic surface for a = 4, n = 961. -/
theorem cubic_surface_cert_a4_n961 :
  (4 : ℚ) / 961 = (1 : ℚ) / 264 + (1 : ℚ) / 4092 + (1 : ℚ) / 7688 := by
  norm_num

/-- Vanishing of cubic surface polynomial at rational point a = 4, n = 961. -/
theorem cubic_surface_point_zero_a4_n961 :
  cubic_surface_poly 4 961 264 4092 7688 = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Certified unit fraction decomposition on cubic surface for a = 4, n = 1801. -/
theorem cubic_surface_cert_a4_n1801 :
  (4 : ℚ) / 1801 = (1 : ℚ) / 462 + (1 : ℚ) / 25214 + (1 : ℚ) / 59433 := by
  norm_num

/-- Vanishing of cubic surface polynomial at rational point a = 4, n = 1801. -/
theorem cubic_surface_point_zero_a4_n1801 :
  cubic_surface_poly 4 1801 462 25214 59433 = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Certified unit fraction decomposition on cubic surface for a = 4, n = 2641. -/
theorem cubic_surface_cert_a4_n2641 :
  (4 : ℚ) / 2641 = (1 : ℚ) / 684 + (1 : ℚ) / 34472 + (1 : ℚ) / 42408 := by
  norm_num

/-- Vanishing of cubic surface polynomial at rational point a = 4, n = 2641. -/
theorem cubic_surface_point_zero_a4_n2641 :
  cubic_surface_poly 4 2641 684 34472 42408 = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Certified unit fraction decomposition on cubic surface for a = 4, n = 3481. -/
theorem cubic_surface_cert_a4_n3481 :
  (4 : ℚ) / 3481 = (1 : ℚ) / 874 + (1 : ℚ) / 360962 + (1 : ℚ) / 462973 := by
  norm_num

/-- Vanishing of cubic surface polynomial at rational point a = 4, n = 3481. -/
theorem cubic_surface_point_zero_a4_n3481 :
  cubic_surface_poly 4 3481 874 360962 462973 = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Certified unit fraction decomposition on cubic surface for a = 4, n = 4321. -/
theorem cubic_surface_cert_a4_n4321 :
  (4 : ℚ) / 4321 = (1 : ℚ) / 1112 + (1 : ℚ) / 62133 + (1 : ℚ) / 96744 := by
  norm_num

/-- Vanishing of cubic surface polynomial at rational point a = 4, n = 4321. -/
theorem cubic_surface_point_zero_a4_n4321 :
  cubic_surface_poly 4 4321 1112 62133 96744 = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Certified unit fraction decomposition on cubic surface for a = 4, n = 5161. -/
theorem cubic_surface_cert_a4_n5161 :
  (4 : ℚ) / 5161 = (1 : ℚ) / 1302 + (1 : ℚ) / 258447 + (1 : ℚ) / 319982 := by
  norm_num

/-- Vanishing of cubic surface polynomial at rational point a = 4, n = 5161. -/
theorem cubic_surface_point_zero_a4_n5161 :
  cubic_surface_poly 4 5161 1302 258447 319982 = 0 := by
  dsimp [cubic_surface_poly]
  ring

/-- Certified unit fraction decomposition on cubic surface for a = 4, n = 6001. -/
theorem cubic_surface_cert_a4_n6001 :
  (4 : ℚ) / 6001 = (1 : ℚ) / 1507 + (1 : ℚ) / 580332 + (1 : ℚ) / 792132 := by
  norm_num

/-- Vanishing of cubic surface polynomial at rational point a = 4, n = 6001. -/
theorem cubic_surface_point_zero_a4_n6001 :
  cubic_surface_poly 4 6001 1507 580332 792132 = 0 := by
  dsimp [cubic_surface_poly]
  ring
