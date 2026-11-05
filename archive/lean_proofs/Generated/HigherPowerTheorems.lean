/-
EvoByte Formal Proof Catalog: Higher Power Diophantine Fractions (P102).
Formalized algebraic varietal fibrations, homogeneous scaling identities,
and certified unit fraction decompositions for a / n^k = 1/x + 1/y + 1/z (k >= 2).
-/

import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Data.Rat.Defs
import Tactic.DiophSurface

def higher_power_surface (a n : ℚ) (k : ℕ) (x y z : ℚ) : ℚ :=
  a * x * y * z - (n^k) * (x * y + y * z + z * x)

def higher_power_surface_sq (a n x y z : ℚ) : ℚ :=
  a * x * y * z - (n^2) * (x * y + y * z + z * x)

def higher_power_surface_cube (a n x y z : ℚ) : ℚ :=
  a * x * y * z - (n^3) * (x * y + y * z + z * x)

def higher_power_surface_quartic (a n x y z : ℚ) : ℚ :=
  a * x * y * z - (n^4) * (x * y + y * z + z * x)

/- Section 1: Varietal Fibration Symmetries and Hyperbolic Factorizations. -/

/-- Surface symmetry under (x, y) swap for k = 2. -/
theorem higher_power_surface_sq_symm_xy : ∀ a n x y z : ℚ,
    higher_power_surface_sq a n x y z = higher_power_surface_sq a n y x z := by
  intro a n x y z; dsimp [higher_power_surface_sq]; ring

/-- Surface symmetry under (y, z) swap for k = 2. -/
theorem higher_power_surface_sq_symm_yz : ∀ a n x y z : ℚ,
    higher_power_surface_sq a n x y z = higher_power_surface_sq a n x z y := by
  intro a n x y z; dsimp [higher_power_surface_sq]; ring

/-- Surface cyclic symmetry for k = 2. -/
theorem higher_power_surface_sq_cyclic : ∀ a n x y z : ℚ,
    higher_power_surface_sq a n x y z = higher_power_surface_sq a n y z x := by
  intro a n x y z; dsimp [higher_power_surface_sq]; ring

/-- Surface symmetry under (x, y) swap for k = 3. -/
theorem higher_power_surface_cube_symm_xy : ∀ a n x y z : ℚ,
    higher_power_surface_cube a n x y z = higher_power_surface_cube a n y x z := by
  intro a n x y z; dsimp [higher_power_surface_cube]; ring

/-- Surface symmetry under (y, z) swap for k = 3. -/
theorem higher_power_surface_cube_symm_yz : ∀ a n x y z : ℚ,
    higher_power_surface_cube a n x y z = higher_power_surface_cube a n x z y := by
  intro a n x y z; dsimp [higher_power_surface_cube]; ring

/-- Surface cyclic symmetry for k = 3. -/
theorem higher_power_surface_cube_cyclic : ∀ a n x y z : ℚ,
    higher_power_surface_cube a n x y z = higher_power_surface_cube a n y z x := by
  intro a n x y z; dsimp [higher_power_surface_cube]; ring

/-- Surface symmetry under (x, y) swap for k = 4. -/
theorem higher_power_surface_quartic_symm_xy : ∀ a n x y z : ℚ,
    higher_power_surface_quartic a n x y z = higher_power_surface_quartic a n y x z := by
  intro a n x y z; dsimp [higher_power_surface_quartic]; ring

/-- Surface symmetry under (y, z) swap for k = 4. -/
theorem higher_power_surface_quartic_symm_yz : ∀ a n x y z : ℚ,
    higher_power_surface_quartic a n x y z = higher_power_surface_quartic a n x z y := by
  intro a n x y z; dsimp [higher_power_surface_quartic]; ring

/-- Surface cyclic symmetry for k = 4. -/
theorem higher_power_surface_quartic_cyclic : ∀ a n x y z : ℚ,
    higher_power_surface_quartic a n x y z = higher_power_surface_quartic a n y z x := by
  intro a n x y z; dsimp [higher_power_surface_quartic]; ring

/-- Hyperbolic factorization for quadratic denominator n^2. -/
theorem hyperbolic_factorization_power2 : ∀ n x y : ℚ,
    (4 * x - n^2) * (4 * y - n^2) - n^4 = 16 * x * y - 4 * n^2 * (x + y) := by
  intro n x y; ring

/-- Hyperbolic factorization for cubic denominator n^3. -/
theorem hyperbolic_factorization_power3 : ∀ n x y : ℚ,
    (4 * x - n^3) * (4 * y - n^3) - n^6 = 16 * x * y - 4 * n^3 * (x + y) := by
  intro n x y; ring

/-- Hyperbolic factorization for quartic denominator n^4. -/
theorem hyperbolic_factorization_power4 : ∀ n x y : ℚ,
    (4 * x - n^4) * (4 * y - n^4) - n^8 = 16 * x * y - 4 * n^4 * (x + y) := by
  intro n x y; ring

/-- Higher power identity decomposition for n^2. -/
theorem higher_power_identity_sq : ∀ n x y z : ℚ,
    4 * (x * y * z) - n^2 * (y * z + x * z + x * y) = x * ((4 * y - n^2) * z - n^2 * y) - n^2 * y * z := by
  intro n x y z; ring

/-- Higher power identity decomposition for n^3. -/
theorem higher_power_identity_cube : ∀ n x y z : ℚ,
    4 * (x * y * z) - n^3 * (y * z + x * z + x * y) = x * ((4 * y - n^3) * z - n^3 * y) - n^3 * y * z := by
  intro n x y z; ring

/-- Higher power identity decomposition for n^4. -/
theorem higher_power_identity_quartic : ∀ n x y z : ℚ,
    4 * (x * y * z) - n^4 * (y * z + x * z + x * y) = x * ((4 * y - n^4) * z - n^4 * y) - n^4 * y * z := by
  intro n x y z; ring

/- Section 2: Homogeneous Power Scaling Transfer Identities. -/

/-- Polynomial homogeneous scaling equivalence for k = 2. -/
theorem power_scaling_poly_identity_sq : ∀ a n x y z : ℚ,
    a * (n * x) * (n * y) * (n * z) - (n^2) * ((n * x) * (n * y) + (n * y) * (n * z) + (n * z) * (n * x)) =
    n^3 * (a * x * y * z - n * (x * y + y * z + z * x)) := by
  intro a n x y z; ring

/-- Polynomial homogeneous scaling equivalence for k = 3. -/
theorem power_scaling_poly_identity_cube : ∀ a n x y z : ℚ,
    a * (n^2 * x) * (n^2 * y) * (n^2 * z) - (n^3) * ((n^2 * x) * (n^2 * y) + (n^2 * y) * (n^2 * z) + (n^2 * z) * (n^2 * x)) =
    n^6 * (a * x * y * z - n * (x * y + y * z + z * x)) := by
  intro a n x y z; ring

/-- Polynomial homogeneous scaling equivalence for k = 4. -/
theorem power_scaling_poly_identity_quartic : ∀ a n x y z : ℚ,
    a * (n^3 * x) * (n^3 * y) * (n^3 * z) - (n^4) * ((n^3 * x) * (n^3 * y) + (n^3 * y) * (n^3 * z) + (n^3 * z) * (n^3 * x)) =
    n^9 * (a * x * y * z - n * (x * y + y * z + z * x)) := by
  intro a n x y z; ring

/-- Polynomial homogeneous scaling equivalence for k = 5. -/
theorem power_scaling_poly_identity_quintic : ∀ a n x y z : ℚ,
    a * (n^4 * x) * (n^4 * y) * (n^4 * z) - (n^5) * ((n^4 * x) * (n^4 * y) + (n^4 * y) * (n^4 * z) + (n^4 * z) * (n^4 * x)) =
    n^12 * (a * x * y * z - n * (x * y + y * z + z * x)) := by
  intro a n x y z; ring

/-- Polynomial homogeneous scaling equivalence for k = 6. -/
theorem power_scaling_poly_identity_sextic : ∀ a n x y z : ℚ,
    a * (n^5 * x) * (n^5 * y) * (n^5 * z) - (n^6) * ((n^5 * x) * (n^5 * y) + (n^5 * y) * (n^5 * z) + (n^5 * z) * (n^5 * x)) =
    n^15 * (a * x * y * z - n * (x * y + y * z + z * x)) := by
  intro a n x y z; ring

/-- Transfer theorem from linear base solution to quadratic denominator n^2. -/
theorem power_scaling_transfer_sq : ∀ a n x y z : ℚ,
    a * x * y * z = n * (x * y + y * z + z * x) →
    a * (n * x) * (n * y) * (n * z) = (n^2) * ((n * x) * (n * y) + (n * y) * (n * z) + (n * z) * (n * x)) := by
  intro a n x y z h
  calc
    a * (n * x) * (n * y) * (n * z) = n^3 * (a * x * y * z) := by ring
    _ = n^3 * (n * (x * y + y * z + z * x)) := by rw [h]
    _ = (n^2) * ((n * x) * (n * y) + (n * y) * (n * z) + (n * z) * (n * x)) := by ring

/-- Transfer theorem from linear base solution to cubic denominator n^3. -/
theorem power_scaling_transfer_cube : ∀ a n x y z : ℚ,
    a * x * y * z = n * (x * y + y * z + z * x) →
    a * (n^2 * x) * (n^2 * y) * (n^2 * z) = (n^3) * ((n^2 * x) * (n^2 * y) + (n^2 * y) * (n^2 * z) + (n^2 * z) * (n^2 * x)) := by
  intro a n x y z h
  calc
    a * (n^2 * x) * (n^2 * y) * (n^2 * z) = n^6 * (a * x * y * z) := by ring
    _ = n^6 * (n * (x * y + y * z + z * x)) := by rw [h]
    _ = (n^3) * ((n^2 * x) * (n^2 * y) + (n^2 * y) * (n^2 * z) + (n^2 * z) * (n^2 * x)) := by ring

/-- Transfer theorem from linear base solution to quartic denominator n^4. -/
theorem power_scaling_transfer_quartic : ∀ a n x y z : ℚ,
    a * x * y * z = n * (x * y + y * z + z * x) →
    a * (n^3 * x) * (n^3 * y) * (n^3 * z) = (n^4) * ((n^3 * x) * (n^3 * y) + (n^3 * y) * (n^3 * z) + (n^3 * z) * (n^3 * x)) := by
  intro a n x y z h
  calc
    a * (n^3 * x) * (n^3 * y) * (n^3 * z) = n^9 * (a * x * y * z) := by ring
    _ = n^9 * (n * (x * y + y * z + z * x)) := by rw [h]
    _ = (n^4) * ((n^3 * x) * (n^3 * y) + (n^3 * y) * (n^3 * z) + (n^3 * z) * (n^3 * x)) := by ring

/-- Transfer theorem from linear base solution to quintic denominator n^5. -/
theorem power_scaling_transfer_quintic : ∀ a n x y z : ℚ,
    a * x * y * z = n * (x * y + y * z + z * x) →
    a * (n^4 * x) * (n^4 * y) * (n^4 * z) = (n^5) * ((n^4 * x) * (n^4 * y) + (n^4 * y) * (n^4 * z) + (n^4 * z) * (n^4 * x)) := by
  intro a n x y z h
  calc
    a * (n^4 * x) * (n^4 * y) * (n^4 * z) = n^12 * (a * x * y * z) := by ring
    _ = n^12 * (n * (x * y + y * z + z * x)) := by rw [h]
    _ = (n^5) * ((n^4 * x) * (n^4 * y) + (n^4 * y) * (n^4 * z) + (n^4 * z) * (n^4 * x)) := by ring

/-- Transfer theorem from linear base solution to sextic denominator n^6. -/
theorem power_scaling_transfer_sextic : ∀ a n x y z : ℚ,
    a * x * y * z = n * (x * y + y * z + z * x) →
    a * (n^5 * x) * (n^5 * y) * (n^5 * z) = (n^6) * ((n^5 * x) * (n^5 * y) + (n^5 * y) * (n^5 * z) + (n^5 * z) * (n^5 * x)) := by
  intro a n x y z h
  calc
    a * (n^5 * x) * (n^5 * y) * (n^5 * z) = n^15 * (a * x * y * z) := by ring
    _ = n^15 * (n * (x * y + y * z + z * x)) := by rw [h]
    _ = (n^6) * ((n^5 * x) * (n^5 * y) + (n^5 * y) * (n^5 * z) + (n^5 * z) * (n^5 * x)) := by ring

/-- Transfer theorem from quadratic solution to quartic denominator n^4. -/
theorem power_scaling_transfer_sq_to_quartic : ∀ a n x y z : ℚ,
    a * x * y * z = (n^2) * (x * y + y * z + z * x) →
    a * (n^2 * x) * (n^2 * y) * (n^2 * z) = (n^4) * ((n^2 * x) * (n^2 * y) + (n^2 * y) * (n^2 * z) + (n^2 * z) * (n^2 * x)) := by
  intro a n x y z h
  calc
    a * (n^2 * x) * (n^2 * y) * (n^2 * z) = n^6 * (a * x * y * z) := by ring
    _ = n^6 * ((n^2) * (x * y + y * z + z * x)) := by rw [h]
    _ = (n^4) * ((n^2 * x) * (n^2 * y) + (n^2 * y) * (n^2 * z) + (n^2 * z) * (n^2 * x)) := by ring

/-- Transfer theorem from cubic solution to sextic denominator n^6. -/
theorem power_scaling_transfer_cube_to_sextic : ∀ a n x y z : ℚ,
    a * x * y * z = (n^3) * (x * y + y * z + z * x) →
    a * (n^3 * x) * (n^3 * y) * (n^3 * z) = (n^6) * ((n^3 * x) * (n^3 * y) + (n^3 * y) * (n^3 * z) + (n^3 * z) * (n^3 * x)) := by
  intro a n x y z h
  calc
    a * (n^3 * x) * (n^3 * y) * (n^3 * z) = n^9 * (a * x * y * z) := by ring
    _ = n^9 * ((n^3) * (x * y + y * z + z * x)) := by rw [h]
    _ = (n^6) * ((n^3 * x) * (n^3 * y) + (n^3 * y) * (n^3 * z) + (n^3 * z) * (n^3 * x)) := by ring

/-- Transfer theorem from quadratic solution to sextic denominator n^6. -/
theorem power_scaling_transfer_sq_to_sextic : ∀ a n x y z : ℚ,
    a * x * y * z = (n^2) * (x * y + y * z + z * x) →
    a * (n^4 * x) * (n^4 * y) * (n^4 * z) = (n^6) * ((n^4 * x) * (n^4 * y) + (n^4 * y) * (n^4 * z) + (n^4 * z) * (n^4 * x)) := by
  intro a n x y z h
  calc
    a * (n^4 * x) * (n^4 * y) * (n^4 * z) = n^12 * (a * x * y * z) := by ring
    _ = n^12 * ((n^2) * (x * y + y * z + z * x)) := by rw [h]
    _ = (n^6) * ((n^4 * x) * (n^4 * y) + (n^4 * y) * (n^4 * z) + (n^4 * z) * (n^4 * x)) := by ring

/- Section 3: Parametric Rational Sections in Q[k] for n^2 and n^3. -/

/-- Parametric quadratic section on higher power surface for family es_even. -/
theorem higher_power_section_sq_es_even : ∀ k : ℚ,
    higher_power_surface_sq 4 (((2 : ℚ) + (2 : ℚ) * k)) ((((2 : ℚ) + (2 : ℚ) * k)) * (((2 : ℚ) + (1 : ℚ) * k))) ((((2 : ℚ) + (2 : ℚ) * k)) * (((2 : ℚ) + (3 : ℚ) * k + (1 : ℚ) * k ^ 2))) ((((2 : ℚ) + (2 : ℚ) * k)) * (((1 : ℚ) + (1 : ℚ) * k))) = 0 := by
  intro k
  dsimp [higher_power_surface_sq]
  ring

/-- Parametric cubic section on higher power surface for family es_even. -/
theorem higher_power_section_cube_es_even : ∀ k : ℚ,
    higher_power_surface_cube 4 (((2 : ℚ) + (2 : ℚ) * k)) ((((2 : ℚ) + (2 : ℚ) * k))^2 * (((2 : ℚ) + (1 : ℚ) * k))) ((((2 : ℚ) + (2 : ℚ) * k))^2 * (((2 : ℚ) + (3 : ℚ) * k + (1 : ℚ) * k ^ 2))) ((((2 : ℚ) + (2 : ℚ) * k))^2 * (((1 : ℚ) + (1 : ℚ) * k))) = 0 := by
  intro k
  dsimp [higher_power_surface_cube]
  ring

/-- Parametric quadratic section on higher power surface for family es_mod3_r2. -/
theorem higher_power_section_sq_es_mod3_r2 : ∀ k : ℚ,
    higher_power_surface_sq 4 (((2 : ℚ) + (3 : ℚ) * k)) ((((2 : ℚ) + (3 : ℚ) * k)) * (((1 : ℚ) + (1 : ℚ) * k))) ((((2 : ℚ) + (3 : ℚ) * k)) * (((2 : ℚ) + (3 : ℚ) * k))) ((((2 : ℚ) + (3 : ℚ) * k)) * (((2 : ℚ) + (5 : ℚ) * k + (3 : ℚ) * k ^ 2))) = 0 := by
  intro k
  dsimp [higher_power_surface_sq]
  ring

/-- Parametric cubic section on higher power surface for family es_mod3_r2. -/
theorem higher_power_section_cube_es_mod3_r2 : ∀ k : ℚ,
    higher_power_surface_cube 4 (((2 : ℚ) + (3 : ℚ) * k)) ((((2 : ℚ) + (3 : ℚ) * k))^2 * (((1 : ℚ) + (1 : ℚ) * k))) ((((2 : ℚ) + (3 : ℚ) * k))^2 * (((2 : ℚ) + (3 : ℚ) * k))) ((((2 : ℚ) + (3 : ℚ) * k))^2 * (((2 : ℚ) + (5 : ℚ) * k + (3 : ℚ) * k ^ 2))) = 0 := by
  intro k
  dsimp [higher_power_surface_cube]
  ring

/-- Parametric quadratic section on higher power surface for family es_mod4_r2. -/
theorem higher_power_section_sq_es_mod4_r2 : ∀ k : ℚ,
    higher_power_surface_sq 4 (((2 : ℚ) + (4 : ℚ) * k)) ((((2 : ℚ) + (4 : ℚ) * k)) * (((1 : ℚ) + (1 : ℚ) * k))) ((((2 : ℚ) + (4 : ℚ) * k)) * (((2 : ℚ) + (6 : ℚ) * k + (4 : ℚ) * k ^ 2))) ((((2 : ℚ) + (4 : ℚ) * k)) * (((2 : ℚ) + (6 : ℚ) * k + (4 : ℚ) * k ^ 2))) = 0 := by
  intro k
  dsimp [higher_power_surface_sq]
  ring

/-- Parametric cubic section on higher power surface for family es_mod4_r2. -/
theorem higher_power_section_cube_es_mod4_r2 : ∀ k : ℚ,
    higher_power_surface_cube 4 (((2 : ℚ) + (4 : ℚ) * k)) ((((2 : ℚ) + (4 : ℚ) * k))^2 * (((1 : ℚ) + (1 : ℚ) * k))) ((((2 : ℚ) + (4 : ℚ) * k))^2 * (((2 : ℚ) + (6 : ℚ) * k + (4 : ℚ) * k ^ 2))) ((((2 : ℚ) + (4 : ℚ) * k))^2 * (((2 : ℚ) + (6 : ℚ) * k + (4 : ℚ) * k ^ 2))) = 0 := by
  intro k
  dsimp [higher_power_surface_cube]
  ring

/-- Parametric quadratic section on higher power surface for family es_mod4_r3. -/
theorem higher_power_section_sq_es_mod4_r3 : ∀ k : ℚ,
    higher_power_surface_sq 4 (((3 : ℚ) + (4 : ℚ) * k)) ((((3 : ℚ) + (4 : ℚ) * k)) * (((1 : ℚ) + (1 : ℚ) * k))) ((((3 : ℚ) + (4 : ℚ) * k)) * (((6 : ℚ) + (14 : ℚ) * k + (8 : ℚ) * k ^ 2))) ((((3 : ℚ) + (4 : ℚ) * k)) * (((6 : ℚ) + (14 : ℚ) * k + (8 : ℚ) * k ^ 2))) = 0 := by
  intro k
  dsimp [higher_power_surface_sq]
  ring

/-- Parametric cubic section on higher power surface for family es_mod4_r3. -/
theorem higher_power_section_cube_es_mod4_r3 : ∀ k : ℚ,
    higher_power_surface_cube 4 (((3 : ℚ) + (4 : ℚ) * k)) ((((3 : ℚ) + (4 : ℚ) * k))^2 * (((1 : ℚ) + (1 : ℚ) * k))) ((((3 : ℚ) + (4 : ℚ) * k))^2 * (((6 : ℚ) + (14 : ℚ) * k + (8 : ℚ) * k ^ 2))) ((((3 : ℚ) + (4 : ℚ) * k))^2 * (((6 : ℚ) + (14 : ℚ) * k + (8 : ℚ) * k ^ 2))) = 0 := by
  intro k
  dsimp [higher_power_surface_cube]
  ring

/-- Parametric quadratic section on higher power surface for family es_mod6_r2. -/
theorem higher_power_section_sq_es_mod6_r2 : ∀ k : ℚ,
    higher_power_surface_sq 4 (((2 : ℚ) + (6 : ℚ) * k)) ((((2 : ℚ) + (6 : ℚ) * k)) * (((1 : ℚ) + (2 : ℚ) * k))) ((((2 : ℚ) + (6 : ℚ) * k)) * (((2 : ℚ) + (6 : ℚ) * k))) ((((2 : ℚ) + (6 : ℚ) * k)) * (((2 : ℚ) + (10 : ℚ) * k + (12 : ℚ) * k ^ 2))) = 0 := by
  intro k
  dsimp [higher_power_surface_sq]
  ring

/-- Parametric cubic section on higher power surface for family es_mod6_r2. -/
theorem higher_power_section_cube_es_mod6_r2 : ∀ k : ℚ,
    higher_power_surface_cube 4 (((2 : ℚ) + (6 : ℚ) * k)) ((((2 : ℚ) + (6 : ℚ) * k))^2 * (((1 : ℚ) + (2 : ℚ) * k))) ((((2 : ℚ) + (6 : ℚ) * k))^2 * (((2 : ℚ) + (6 : ℚ) * k))) ((((2 : ℚ) + (6 : ℚ) * k))^2 * (((2 : ℚ) + (10 : ℚ) * k + (12 : ℚ) * k ^ 2))) = 0 := by
  intro k
  dsimp [higher_power_surface_cube]
  ring

/-- Parametric quadratic section on higher power surface for family es_mod6_r3. -/
theorem higher_power_section_sq_es_mod6_r3 : ∀ k : ℚ,
    higher_power_surface_sq 4 (((3 : ℚ) + (6 : ℚ) * k)) ((((3 : ℚ) + (6 : ℚ) * k)) * (((2 : ℚ) + (2 : ℚ) * k))) ((((3 : ℚ) + (6 : ℚ) * k)) * (((2 : ℚ) + (6 : ℚ) * k + (4 : ℚ) * k ^ 2))) ((((3 : ℚ) + (6 : ℚ) * k)) * (((3 : ℚ) + (6 : ℚ) * k))) = 0 := by
  intro k
  dsimp [higher_power_surface_sq]
  ring

/-- Parametric cubic section on higher power surface for family es_mod6_r3. -/
theorem higher_power_section_cube_es_mod6_r3 : ∀ k : ℚ,
    higher_power_surface_cube 4 (((3 : ℚ) + (6 : ℚ) * k)) ((((3 : ℚ) + (6 : ℚ) * k))^2 * (((2 : ℚ) + (2 : ℚ) * k))) ((((3 : ℚ) + (6 : ℚ) * k))^2 * (((2 : ℚ) + (6 : ℚ) * k + (4 : ℚ) * k ^ 2))) ((((3 : ℚ) + (6 : ℚ) * k))^2 * (((3 : ℚ) + (6 : ℚ) * k))) = 0 := by
  intro k
  dsimp [higher_power_surface_cube]
  ring

/-- Parametric quadratic section on higher power surface for family es_mod6_r4. -/
theorem higher_power_section_sq_es_mod6_r4 : ∀ k : ℚ,
    higher_power_surface_sq 4 (((4 : ℚ) + (6 : ℚ) * k)) ((((4 : ℚ) + (6 : ℚ) * k)) * (((2 : ℚ) + (2 : ℚ) * k))) ((((4 : ℚ) + (6 : ℚ) * k)) * (((4 : ℚ) + (10 : ℚ) * k + (6 : ℚ) * k ^ 2))) ((((4 : ℚ) + (6 : ℚ) * k)) * (((4 : ℚ) + (6 : ℚ) * k))) = 0 := by
  intro k
  dsimp [higher_power_surface_sq]
  ring

/-- Parametric cubic section on higher power surface for family es_mod6_r4. -/
theorem higher_power_section_cube_es_mod6_r4 : ∀ k : ℚ,
    higher_power_surface_cube 4 (((4 : ℚ) + (6 : ℚ) * k)) ((((4 : ℚ) + (6 : ℚ) * k))^2 * (((2 : ℚ) + (2 : ℚ) * k))) ((((4 : ℚ) + (6 : ℚ) * k))^2 * (((4 : ℚ) + (10 : ℚ) * k + (6 : ℚ) * k ^ 2))) ((((4 : ℚ) + (6 : ℚ) * k))^2 * (((4 : ℚ) + (6 : ℚ) * k))) = 0 := by
  intro k
  dsimp [higher_power_surface_cube]
  ring

/-- Parametric quadratic section on higher power surface for family es_mod8_r4. -/
theorem higher_power_section_sq_es_mod8_r4 : ∀ k : ℚ,
    higher_power_surface_sq 4 (((4 : ℚ) + (8 : ℚ) * k)) ((((4 : ℚ) + (8 : ℚ) * k)) * (((2 : ℚ) + (4 : ℚ) * k))) ((((4 : ℚ) + (8 : ℚ) * k)) * (((3 : ℚ) + (6 : ℚ) * k))) ((((4 : ℚ) + (8 : ℚ) * k)) * (((6 : ℚ) + (12 : ℚ) * k))) = 0 := by
  intro k
  dsimp [higher_power_surface_sq]
  ring

/-- Parametric cubic section on higher power surface for family es_mod8_r4. -/
theorem higher_power_section_cube_es_mod8_r4 : ∀ k : ℚ,
    higher_power_surface_cube 4 (((4 : ℚ) + (8 : ℚ) * k)) ((((4 : ℚ) + (8 : ℚ) * k))^2 * (((2 : ℚ) + (4 : ℚ) * k))) ((((4 : ℚ) + (8 : ℚ) * k))^2 * (((3 : ℚ) + (6 : ℚ) * k))) ((((4 : ℚ) + (8 : ℚ) * k))^2 * (((6 : ℚ) + (12 : ℚ) * k))) = 0 := by
  intro k
  dsimp [higher_power_surface_cube]
  ring

/-- Parametric quadratic section on higher power surface for family es_mod12_r6. -/
theorem higher_power_section_sq_es_mod12_r6 : ∀ k : ℚ,
    higher_power_surface_sq 4 (((6 : ℚ) + (12 : ℚ) * k)) ((((6 : ℚ) + (12 : ℚ) * k)) * (((2 : ℚ) + (3 : ℚ) * k))) ((((6 : ℚ) + (12 : ℚ) * k)) * (((12 : ℚ) + (42 : ℚ) * k + (36 : ℚ) * k ^ 2))) ((((6 : ℚ) + (12 : ℚ) * k)) * (((12 : ℚ) + (42 : ℚ) * k + (36 : ℚ) * k ^ 2))) = 0 := by
  intro k
  dsimp [higher_power_surface_sq]
  ring

/-- Parametric cubic section on higher power surface for family es_mod12_r6. -/
theorem higher_power_section_cube_es_mod12_r6 : ∀ k : ℚ,
    higher_power_surface_cube 4 (((6 : ℚ) + (12 : ℚ) * k)) ((((6 : ℚ) + (12 : ℚ) * k))^2 * (((2 : ℚ) + (3 : ℚ) * k))) ((((6 : ℚ) + (12 : ℚ) * k))^2 * (((12 : ℚ) + (42 : ℚ) * k + (36 : ℚ) * k ^ 2))) ((((6 : ℚ) + (12 : ℚ) * k))^2 * (((12 : ℚ) + (42 : ℚ) * k + (36 : ℚ) * k ^ 2))) = 0 := by
  intro k
  dsimp [higher_power_surface_cube]
  ring

/-- Parametric quadratic section on higher power surface for family es_mod12_r8. -/
theorem higher_power_section_sq_es_mod12_r8 : ∀ k : ℚ,
    higher_power_surface_sq 4 (((8 : ℚ) + (12 : ℚ) * k)) ((((8 : ℚ) + (12 : ℚ) * k)) * (((4 : ℚ) + (6 : ℚ) * k))) ((((8 : ℚ) + (12 : ℚ) * k)) * (((6 : ℚ) + (9 : ℚ) * k))) ((((8 : ℚ) + (12 : ℚ) * k)) * (((12 : ℚ) + (18 : ℚ) * k))) = 0 := by
  intro k
  dsimp [higher_power_surface_sq]
  ring

/-- Parametric cubic section on higher power surface for family es_mod12_r8. -/
theorem higher_power_section_cube_es_mod12_r8 : ∀ k : ℚ,
    higher_power_surface_cube 4 (((8 : ℚ) + (12 : ℚ) * k)) ((((8 : ℚ) + (12 : ℚ) * k))^2 * (((4 : ℚ) + (6 : ℚ) * k))) ((((8 : ℚ) + (12 : ℚ) * k))^2 * (((6 : ℚ) + (9 : ℚ) * k))) ((((8 : ℚ) + (12 : ℚ) * k))^2 * (((12 : ℚ) + (18 : ℚ) * k))) = 0 := by
  intro k
  dsimp [higher_power_surface_cube]
  ring

/-- Parametric quadratic section on higher power surface for family sierpinski_mod4_r2. -/
theorem higher_power_section_sq_sierpinski_mod4_r2 : ∀ k : ℚ,
    higher_power_surface_sq 5 (((2 : ℚ) + (4 : ℚ) * k)) ((((2 : ℚ) + (4 : ℚ) * k)) * (((1 : ℚ) + (1 : ℚ) * k))) ((((2 : ℚ) + (4 : ℚ) * k)) * (((1 : ℚ) + (3 : ℚ) * k + (2 : ℚ) * k ^ 2))) ((((2 : ℚ) + (4 : ℚ) * k)) * (((2 : ℚ) + (4 : ℚ) * k))) = 0 := by
  intro k
  dsimp [higher_power_surface_sq]
  ring

/-- Parametric cubic section on higher power surface for family sierpinski_mod4_r2. -/
theorem higher_power_section_cube_sierpinski_mod4_r2 : ∀ k : ℚ,
    higher_power_surface_cube 5 (((2 : ℚ) + (4 : ℚ) * k)) ((((2 : ℚ) + (4 : ℚ) * k))^2 * (((1 : ℚ) + (1 : ℚ) * k))) ((((2 : ℚ) + (4 : ℚ) * k))^2 * (((1 : ℚ) + (3 : ℚ) * k + (2 : ℚ) * k ^ 2))) ((((2 : ℚ) + (4 : ℚ) * k))^2 * (((2 : ℚ) + (4 : ℚ) * k))) = 0 := by
  intro k
  dsimp [higher_power_surface_cube]
  ring

/-- Parametric quadratic section on higher power surface for family sierpinski_mod5_r0. -/
theorem higher_power_section_sq_sierpinski_mod5_r0 : ∀ k : ℚ,
    higher_power_surface_sq 5 (((5 : ℚ) + (5 : ℚ) * k)) ((((5 : ℚ) + (5 : ℚ) * k)) * (((2 : ℚ) + (2 : ℚ) * k))) ((((5 : ℚ) + (5 : ℚ) * k)) * (((3 : ℚ) + (3 : ℚ) * k))) ((((5 : ℚ) + (5 : ℚ) * k)) * (((6 : ℚ) + (6 : ℚ) * k))) = 0 := by
  intro k
  dsimp [higher_power_surface_sq]
  ring

/-- Parametric cubic section on higher power surface for family sierpinski_mod5_r0. -/
theorem higher_power_section_cube_sierpinski_mod5_r0 : ∀ k : ℚ,
    higher_power_surface_cube 5 (((5 : ℚ) + (5 : ℚ) * k)) ((((5 : ℚ) + (5 : ℚ) * k))^2 * (((2 : ℚ) + (2 : ℚ) * k))) ((((5 : ℚ) + (5 : ℚ) * k))^2 * (((3 : ℚ) + (3 : ℚ) * k))) ((((5 : ℚ) + (5 : ℚ) * k))^2 * (((6 : ℚ) + (6 : ℚ) * k))) = 0 := by
  intro k
  dsimp [higher_power_surface_cube]
  ring

/- Section 4: Exact Rational Unit Fraction Certificates for k = 2 (n^2). -/

/-- Certified unit fraction decomposition for 4 / 2^2 (k = 2). -/
theorem higher_power_cert_k2_n2 :
    (4 : ℚ) / 4 = 1 / 3 + 1 / 3 + 1 / 3 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 3^2 (k = 2). -/
theorem higher_power_cert_k2_n3 :
    (4 : ℚ) / 9 = 1 / 6 + 1 / 6 + 1 / 9 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 5^2 (k = 2). -/
theorem higher_power_cert_k2_n5 :
    (4 : ℚ) / 25 = 1 / 10 + 1 / 25 + 1 / 50 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 7^2 (k = 2). -/
theorem higher_power_cert_k2_n7 :
    (4 : ℚ) / 49 = 1 / 18 + 1 / 63 + 1 / 98 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 11^2 (k = 2). -/
theorem higher_power_cert_k2_n11 :
    (4 : ℚ) / 121 = 1 / 42 + 1 / 154 + 1 / 363 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 13^2 (k = 2). -/
theorem higher_power_cert_k2_n13 :
    (4 : ℚ) / 169 = 1 / 52 + 1 / 338 + 1 / 676 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 17^2 (k = 2). -/
theorem higher_power_cert_k2_n17 :
    (4 : ℚ) / 289 = 1 / 85 + 1 / 578 + 1 / 2890 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 19^2 (k = 2). -/
theorem higher_power_cert_k2_n19 :
    (4 : ℚ) / 361 = 1 / 100 + 1 / 1805 + 1 / 1900 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 23^2 (k = 2). -/
theorem higher_power_cert_k2_n23 :
    (4 : ℚ) / 529 = 1 / 147 + 1 / 2254 + 1 / 3174 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 29^2 (k = 2). -/
theorem higher_power_cert_k2_n29 :
    (4 : ℚ) / 841 = 1 / 220 + 1 / 6380 + 1 / 18502 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 31^2 (k = 2). -/
theorem higher_power_cert_k2_n31 :
    (4 : ℚ) / 961 = 1 / 264 + 1 / 4092 + 1 / 7688 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 37^2 (k = 2). -/
theorem higher_power_cert_k2_n37 :
    (4 : ℚ) / 1369 = 1 / 350 + 1 / 25900 + 1 / 38332 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 41^2 (k = 2). -/
theorem higher_power_cert_k2_n41 :
    (4 : ℚ) / 1681 = 1 / 434 + 1 / 17794 + 1 / 52111 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 43^2 (k = 2). -/
theorem higher_power_cert_k2_n43 :
    (4 : ℚ) / 1849 = 1 / 473 + 1 / 40678 + 1 / 40678 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 47^2 (k = 2). -/
theorem higher_power_cert_k2_n47 :
    (4 : ℚ) / 2209 = 1 / 580 + 1 / 20445 + 1 / 26508 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 53^2 (k = 2). -/
theorem higher_power_cert_k2_n53 :
    (4 : ℚ) / 2809 = 1 / 712 + 1 / 94340 + 1 / 112360 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 59^2 (k = 2). -/
theorem higher_power_cert_k2_n59 :
    (4 : ℚ) / 3481 = 1 / 874 + 1 / 360962 + 1 / 462973 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 61^2 (k = 2). -/
theorem higher_power_cert_k2_n61 :
    (4 : ℚ) / 3721 = 1 / 943 + 1 / 115046 + 1 / 171166 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 67^2 (k = 2). -/
theorem higher_power_cert_k2_n67 :
    (4 : ℚ) / 4489 = 1 / 1139 + 1 / 152626 + 1 / 152626 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 71^2 (k = 2). -/
theorem higher_power_cert_k2_n71 :
    (4 : ℚ) / 5041 = 1 / 1265 + 1 / 574816 + 1 / 806560 := by
  norm_num

/- Section 5: Exact Rational Unit Fraction Certificates for k = 3 (n^3). -/

/-- Certified unit fraction decomposition for 4 / 2^3 (k = 3). -/
theorem higher_power_cert_k3_n2 :
    (4 : ℚ) / 8 = 1 / 6 + 1 / 6 + 1 / 6 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 3^3 (k = 3). -/
theorem higher_power_cert_k3_n3 :
    (4 : ℚ) / 27 = 1 / 18 + 1 / 18 + 1 / 27 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 4^3 (k = 3). -/
theorem higher_power_cert_k3_n4 :
    (4 : ℚ) / 64 = 1 / 48 + 1 / 48 + 1 / 48 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 5^3 (k = 3). -/
theorem higher_power_cert_k3_n5 :
    (4 : ℚ) / 125 = 1 / 36 + 1 / 450 + 1 / 500 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 6^3 (k = 3). -/
theorem higher_power_cert_k3_n6 :
    (4 : ℚ) / 216 = 1 / 108 + 1 / 216 + 1 / 216 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 7^3 (k = 3). -/
theorem higher_power_cert_k3_n7 :
    (4 : ℚ) / 343 = 1 / 98 + 1 / 1372 + 1 / 1372 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 8^3 (k = 3). -/
theorem higher_power_cert_k3_n8 :
    (4 : ℚ) / 512 = 1 / 168 + 1 / 1008 + 1 / 1152 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 9^3 (k = 3). -/
theorem higher_power_cert_k3_n9 :
    (4 : ℚ) / 729 = 1 / 204 + 1 / 2916 + 1 / 4131 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 10^3 (k = 3). -/
theorem higher_power_cert_k3_n10 :
    (4 : ℚ) / 1000 = 1 / 300 + 1 / 3000 + 1 / 3000 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 11^3 (k = 3). -/
theorem higher_power_cert_k3_n11 :
    (4 : ℚ) / 1331 = 1 / 342 + 1 / 23958 + 1 / 25289 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 12^3 (k = 3). -/
theorem higher_power_cert_k3_n12 :
    (4 : ℚ) / 1728 = 1 / 513 + 1 / 5472 + 1 / 5472 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 13^3 (k = 3). -/
theorem higher_power_cert_k3_n13 :
    (4 : ℚ) / 2197 = 1 / 558 + 1 / 62868 + 1 / 79092 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 14^3 (k = 3). -/
theorem higher_power_cert_k3_n14 :
    (4 : ℚ) / 2744 = 1 / 756 + 1 / 14553 + 1 / 15092 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 15^3 (k = 3). -/
theorem higher_power_cert_k3_n15 :
    (4 : ℚ) / 3375 = 1 / 888 + 1 / 31968 + 1 / 36000 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 16^3 (k = 3). -/
theorem higher_power_cert_k3_n16 :
    (4 : ℚ) / 4096 = 1 / 1064 + 1 / 51072 + 1 / 58368 := by
  norm_num

/- Section 6: Exact Rational Unit Fraction Certificates for k = 4 (n^4). -/

/-- Certified unit fraction decomposition for 4 / 2^4 (k = 4). -/
theorem higher_power_cert_k4_n2 :
    (4 : ℚ) / 16 = 1 / 12 + 1 / 12 + 1 / 12 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 3^4 (k = 4). -/
theorem higher_power_cert_k4_n3 :
    (4 : ℚ) / 81 = 1 / 36 + 1 / 81 + 1 / 108 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 4^4 (k = 4). -/
theorem higher_power_cert_k4_n4 :
    (4 : ℚ) / 256 = 1 / 112 + 1 / 280 + 1 / 320 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 5^4 (k = 4). -/
theorem higher_power_cert_k4_n5 :
    (4 : ℚ) / 625 = 1 / 180 + 1 / 2250 + 1 / 2500 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 6^4 (k = 4). -/
theorem higher_power_cert_k4_n6 :
    (4 : ℚ) / 1296 = 1 / 405 + 1 / 3240 + 1 / 3240 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 7^4 (k = 4). -/
theorem higher_power_cert_k4_n7 :
    (4 : ℚ) / 2401 = 1 / 630 + 1 / 21609 + 1 / 30870 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 8^4 (k = 4). -/
theorem higher_power_cert_k4_n8 :
    (4 : ℚ) / 4096 = 1 / 1064 + 1 / 51072 + 1 / 58368 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 9^4 (k = 4). -/
theorem higher_power_cert_k4_n9 :
    (4 : ℚ) / 6561 = 1 / 1674 + 1 / 135594 + 1 / 203391 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 10^4 (k = 4). -/
theorem higher_power_cert_k4_n10 :
    (4 : ℚ) / 10000 = 1 / 2600 + 1 / 130000 + 1 / 130000 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 11^4 (k = 4). -/
theorem higher_power_cert_k4_n11 :
    (4 : ℚ) / 14641 = 1 / 3672 + 1 / 1976535 + 1 / 2715240 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 12^4 (k = 4). -/
theorem higher_power_cert_k4_n12 :
    (4 : ℚ) / 20736 = 1 / 5265 + 1 / 673920 + 1 / 673920 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 13^4 (k = 4). -/
theorem higher_power_cert_k4_n13 :
    (4 : ℚ) / 28561 = 1 / 7163 + 1 / 3255954 + 1 / 7263282 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 14^4 (k = 4). -/
theorem higher_power_cert_k4_n14 :
    (4 : ℚ) / 38416 = 1 / 9675 + 1 / 2581075 + 1 / 2654820 := by
  norm_num

/-- Certified unit fraction decomposition for 4 / 15^4 (k = 4). -/
theorem higher_power_cert_k4_n15 :
    (4 : ℚ) / 50625 = 1 / 12726 + 1 / 4485915 + 1 / 4758750 := by
  norm_num

/- Section 7: Monic Algebraic Factorizations for Exponents 2, 3, 4, 5, 6. -/

/-- Monic decomposition for quadratic denominator n^2. -/
theorem higher_power_monic_decomp_2 : ∀ n x y : ℚ,
    (x - n^2) * (y - n^2) = x * y - n^2 * (x + y) + n^4 := by
  intro n x y; ring

/-- Monic decomposition for cubic denominator n^3. -/
theorem higher_power_monic_decomp_3 : ∀ n x y : ℚ,
    (x - n^3) * (y - n^3) = x * y - n^3 * (x + y) + n^6 := by
  intro n x y; ring

/-- Monic decomposition for quartic denominator n^4. -/
theorem higher_power_monic_decomp_4 : ∀ n x y : ℚ,
    (x - n^4) * (y - n^4) = x * y - n^4 * (x + y) + n^8 := by
  intro n x y; ring

/-- Monic decomposition for quintic denominator n^5. -/
theorem higher_power_monic_decomp_5 : ∀ n x y : ℚ,
    (x - n^5) * (y - n^5) = x * y - n^5 * (x + y) + n^10 := by
  intro n x y; ring

/-- Monic decomposition for sextic denominator n^6. -/
theorem higher_power_monic_decomp_6 : ∀ n x y : ℚ,
    (x - n^6) * (y - n^6) = x * y - n^6 * (x + y) + n^12 := by
  intro n x y; ring
