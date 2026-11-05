/-
EvoByte Formal Proof Catalog: Bytecode Decompilations and Algebraic Equivalence Theorems.
-/

import Mathlib.Tactic.Ring
import Mathlib.Data.Rat.Defs

def bytecode_linear_3x_plus_2 (x : ℚ) : ℚ :=
  let r0 : ℚ := x
  let r1 : ℚ := (0 : ℚ)
  let r2 := r1 + (3 : ℚ)
  let r2 := r2 * r0
  let r7 := r2 + (2 : ℚ)
  r7

/-- Formal algebraic equivalence: bytecode program `bytecode_linear_3x_plus_2` computes `(3 : ℚ) * x + 2`. -/
theorem bytecode_spec_linear : ∀ x : ℚ, bytecode_linear_3x_plus_2 x = (3 : ℚ) * x + 2 := by
  intro x
  dsimp [bytecode_linear_3x_plus_2]
  ring

def bytecode_quadratic_2x2_plus_3 (x : ℚ) : ℚ :=
  let r0 : ℚ := x
  let r1 : ℚ := (0 : ℚ)
  let r2 := r1 + (2 : ℚ)
  let r2 := r2 * r0
  let r2 := r2 * r0
  let r7 := r2 + (3 : ℚ)
  r7

/-- Formal algebraic equivalence: bytecode program `bytecode_quadratic_2x2_plus_3` computes `(2 : ℚ) * x ^ 2 + 3`. -/
theorem bytecode_spec_quadratic : ∀ x : ℚ, bytecode_quadratic_2x2_plus_3 x = (2 : ℚ) * x ^ 2 + 3 := by
  intro x
  dsimp [bytecode_quadratic_2x2_plus_3]
  ring

def bytecode_diff_squares (x : ℚ) : ℚ :=
  let r0 : ℚ := x
  let r1 : ℚ := (0 : ℚ)
  let r2 := r1 + (1 : ℚ)
  let r2 := r2 * r0
  let r2 := r2 * r0
  let r7 := r2 + (-1 : ℚ)
  r7

/-- Formal algebraic equivalence: bytecode program `bytecode_diff_squares` computes `x ^ 2 - 1`. -/
theorem bytecode_spec_diff_squares : ∀ x : ℚ, bytecode_diff_squares x = x ^ 2 - 1 := by
  intro x
  dsimp [bytecode_diff_squares]
  ring

def bytecode_linear_3x_minus_1 (x : ℚ) : ℚ :=
  let r0 : ℚ := x
  let r1 : ℚ := (0 : ℚ)
  let r2 := r1 + (3 : ℚ)
  let r2 := r2 * r0
  let r7 := r2 + (-1 : ℚ)
  r7

/-- Formal algebraic equivalence: bytecode program `bytecode_linear_3x_minus_1` computes `(3 : ℚ) * x - 1`. -/
theorem bytecode_spec_linear_sub : ∀ x : ℚ, bytecode_linear_3x_minus_1 x = (3 : ℚ) * x - 1 := by
  intro x
  dsimp [bytecode_linear_3x_minus_1]
  ring
