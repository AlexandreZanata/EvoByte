/-
EvoByte Custom Tactic Metaprogramming Module: evobyte_solve and evobyte_diophantine (P89).
Unifies algebraic ring rewriting, arithmetic simplification, and automated tactic dispatch.
-/

import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Data.Rat.Defs

set_option linter.unusedTactic false
set_option linter.unreachableTactic false

/-- Custom macro tactic `evobyte_solve` that cascades algebraic and arithmetic solvers
    (`ring1`, `omega`, `linarith`, `aesop`, `norm_num`, `ring`) to close Diophantine goals. -/
syntax "evobyte_solve" : tactic

macro_rules
  | `(tactic| evobyte_solve) => `(tactic| first | ring1 | omega | linarith | aesop | norm_num | ring)

/-- Custom macro tactic `evobyte_diophantine` that introduces all hypotheses
    and dispatches to `evobyte_solve`. -/
syntax "evobyte_diophantine" : tactic

macro_rules
  | `(tactic| evobyte_diophantine) => `(tactic| intros; first | ring1 | omega | linarith | aesop | norm_num | ring)
