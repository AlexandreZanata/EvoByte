import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Data.Rat.Defs

-- P48 false control: extra axiom smuggles the answer; the boundary must reject it.
axiom myOracle : ∀ x : ℚ, x ^ 2 - 1 = (x - 1) * (x + 1)

theorem assumed_identity : ∀ x : ℚ, x ^ 2 - 1 = (x - 1) * (x + 1) :=
  myOracle
