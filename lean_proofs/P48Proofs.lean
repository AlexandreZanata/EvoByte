-- P48 frozen challenge statements (DO NOT EDIT: hash-pinned by the acceptance audit).
-- Review surface for the human translation check; the JSON nomination is not authoritative here.

import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Data.Rat.Defs

/-- P48-CHALLENGE-1: difference of squares over ℚ. -/
theorem es_identity : ∀ x : ℚ, x ^ 2 - 1 = (x - 1) * (x + 1) := by
  intro x
  ring

/-- P48-CHALLENGE-2: bounded Erdős–Straus certificate for n = 1009. -/
theorem erdos_straus_1009 : (4 : ℚ) / 1009 = 1 / 253 + 1 / 85100 + 1 / 944524900 := by
  norm_num
