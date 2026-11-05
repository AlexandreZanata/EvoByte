-- P48 false control: proves a different statement than challenged.
-- The boundary must reject it by statement-hash mismatch.
import Mathlib.Tactic.Ring

theorem other_identity : ∀ x : ℚ, x ^ 2 + 2 * x + 1 = (x + 1) ^ 2 := by
  intro x
  ring
