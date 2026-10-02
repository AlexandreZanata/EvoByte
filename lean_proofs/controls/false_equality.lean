-- P48 false control: a false identity; the compiler must reject it.
import Mathlib.Tactic.Ring

theorem false_identity : ∀ x : ℚ, x ^ 2 + 1 = x ^ 2 := by
  intro x
  ring
