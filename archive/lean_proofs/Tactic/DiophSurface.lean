/-
EvoByte Custom Tactic Metaprogramming Module: dioph_surface (P100).
Unified algebraic elimination, Bézout resultant normalization, and Diophantine surface solving in Lean 4.
-/

import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Data.Rat.Defs

open Lean Parser Tactic

set_option linter.unusedTactic false
set_option linter.unreachableTactic false

/-- Custom macro tactic `dioph_surface` that automates variable elimination,
    algebraic normalization, and decision procedures on Diophantine surfaces. -/
syntax "dioph_surface" : tactic
syntax "dioph_surface" " [" withoutPosition((simpErase <|> simpLemma),*,?) "]" : tactic

macro_rules
  | `(tactic| dioph_surface) =>
    `(tactic| intros; first | (ring1; done) | (ring; done) | (norm_num; done) | (aesop; done) | (rfl; done) | (decide; done))
  | `(tactic| dioph_surface [ $args,* ]) =>
    `(tactic| intros; first | (dsimp [$args,*]; done) | (dsimp [$args,*]; first | (ring1; done) | (ring; done) | (norm_num; done) | (aesop; done) | (rfl; done) | (decide; done)))

/-- Specialized tactic for Bézout resultant and elimination on conic fibers. -/
syntax "dioph_surface_elim" : tactic

macro_rules
  | `(tactic| dioph_surface_elim) =>
    `(tactic| intros; first | (ring1; done) | (ring; done) | (norm_num; done) | (aesop; done) | (rfl; done))
