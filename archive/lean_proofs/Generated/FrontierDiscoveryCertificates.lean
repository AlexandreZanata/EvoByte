import Mathlib.Tactic

/-!
# Frontier Discovery Certificates in Lean 4 (P185)

Mechanically verified proofs of concrete frontier calibration certificates:
- Covering design: Fano plane C(7, 3, 2) covering all 21 pairs in {0..6}.
- Weak Schur partition: Sum-free coloring of 1..8 into 2 classes without distinct monochromatic triples.
- Quantum stabilizer code: Pairwise symplectic commutation of the 6 Steane [[7, 1, 3]] generators.

All theorems state genuine combinatorial properties verified by the Lean 4 kernel via `decide`.
Predicates are `abbrev` rather than `def` so that `Decidable` instances over finite types (`Fin`)
are synthesized directly by typeclass resolution.
-/

namespace EvoByte.Frontier

/-- Uncovered pair predicate on a finite covering design.

`HasUncoveredPair v b k blocks` holds when there exists a pair of distinct elements
`x < y` in `Fin v` that is not covered by any block in `Fin b → Fin k → Fin v`. -/
abbrev HasUncoveredPair (v b k : Nat) (blocks : Fin b → Fin k → Fin v) : Prop :=
  ∃ (x y : Fin v), x.val < y.val ∧
    ∀ (bi : Fin b), ¬ (∃ (p q : Fin k), blocks bi p = x ∧ blocks bi q = y)

/-- Concrete certified blocks for the Fano plane C(7, 3, 2). -/
def fanoBlocks : Fin 7 → Fin 3 → Fin 7
  | ⟨0, _⟩ => fun | ⟨0, _⟩ => ⟨0, by decide⟩ | ⟨1, _⟩ => ⟨1, by decide⟩ | ⟨2, _⟩ => ⟨2, by decide⟩
  | ⟨1, _⟩ => fun | ⟨0, _⟩ => ⟨0, by decide⟩ | ⟨1, _⟩ => ⟨3, by decide⟩ | ⟨2, _⟩ => ⟨4, by decide⟩
  | ⟨2, _⟩ => fun | ⟨0, _⟩ => ⟨0, by decide⟩ | ⟨1, _⟩ => ⟨5, by decide⟩ | ⟨2, _⟩ => ⟨6, by decide⟩
  | ⟨3, _⟩ => fun | ⟨0, _⟩ => ⟨1, by decide⟩ | ⟨1, _⟩ => ⟨3, by decide⟩ | ⟨2, _⟩ => ⟨5, by decide⟩
  | ⟨4, _⟩ => fun | ⟨0, _⟩ => ⟨1, by decide⟩ | ⟨1, _⟩ => ⟨4, by decide⟩ | ⟨2, _⟩ => ⟨6, by decide⟩
  | ⟨5, _⟩ => fun | ⟨0, _⟩ => ⟨2, by decide⟩ | ⟨1, _⟩ => ⟨3, by decide⟩ | ⟨2, _⟩ => ⟨6, by decide⟩
  | ⟨6, _⟩ => fun | ⟨0, _⟩ => ⟨2, by decide⟩ | ⟨1, _⟩ => ⟨4, by decide⟩ | ⟨2, _⟩ => ⟨5, by decide⟩

/-- Decidable certification that Fano plane blocks leave zero uncovered pairs in {0..6}. -/
theorem fano_covering_valid : ¬ HasUncoveredPair 7 7 3 fanoBlocks := by
  decide

/-- Weak Schur partition violation predicate on a partition of 1..n into classes.

`HasWeakSchurViolation n part` holds when there exist distinct `x < y` with `x + y ≤ n`
such that `x`, `y` and `x + y` all share the same partition class. -/
abbrev HasWeakSchurViolation (n : Nat) (part : Fin n → Nat) : Prop :=
  ∃ (x y : Fin n) (hb : x.val + y.val + 2 ≤ n), x.val < y.val ∧
    part ⟨x.val, by omega⟩ = part ⟨y.val, by omega⟩ ∧
    part ⟨x.val, by omega⟩ = part ⟨x.val + y.val + 1, by omega⟩

/-- Concrete certified weak Schur 2-coloring of [1..8]. -/
def weakSchurSample8 : Fin 8 → Nat
  | ⟨0, _⟩ => 1
  | ⟨1, _⟩ => 1
  | ⟨2, _⟩ => 2
  | ⟨3, _⟩ => 1
  | ⟨4, _⟩ => 2
  | ⟨5, _⟩ => 2
  | ⟨6, _⟩ => 2
  | ⟨7, _⟩ => 1

/-- Decidable certification that weakSchurSample8 contains zero weak Schur violations. -/
theorem weak_schur_sample_8_valid : ¬ HasWeakSchurViolation 8 weakSchurSample8 := by
  decide

/-- Quantum stabilizer non-commutation predicate.

`HasNonCommutingPair m n gens` holds when there exist two generators `i < j`
whose binary symplectic inner product over `Fin 2 × Fin 2` is non-zero mod 2. -/
abbrev HasNonCommutingPair (m n : Nat) (gens : Fin m → Fin n → Fin 2 × Fin 2) : Prop :=
  ∃ (i j : Fin m), i.val < j.val ∧
    (∑ (k : Fin n), ((gens i k).1.val * (gens j k).2.val + (gens i k).2.val * (gens j k).1.val)) % 2 ≠ 0

/-- Pauli single-qubit representation: I = (0,0), X = (1,0), Z = (0,1). -/
def pauliI : Fin 2 × Fin 2 := (0, 0)
def pauliX : Fin 2 × Fin 2 := (1, 0)
def pauliZ : Fin 2 × Fin 2 := (0, 1)

/-- Concrete certified Steane [[7, 1, 3]] stabilizer generators. -/
def steaneGens : Fin 6 → Fin 7 → Fin 2 × Fin 2
  | ⟨0, _⟩ => fun | ⟨3, _⟩ | ⟨4, _⟩ | ⟨5, _⟩ | ⟨6, _⟩ => pauliX | _ => pauliI
  | ⟨1, _⟩ => fun | ⟨1, _⟩ | ⟨2, _⟩ | ⟨5, _⟩ | ⟨6, _⟩ => pauliX | _ => pauliI
  | ⟨2, _⟩ => fun | ⟨0, _⟩ | ⟨2, _⟩ | ⟨4, _⟩ | ⟨6, _⟩ => pauliX | _ => pauliI
  | ⟨3, _⟩ => fun | ⟨3, _⟩ | ⟨4, _⟩ | ⟨5, _⟩ | ⟨6, _⟩ => pauliZ | _ => pauliI
  | ⟨4, _⟩ => fun | ⟨1, _⟩ | ⟨2, _⟩ | ⟨5, _⟩ | ⟨6, _⟩ => pauliZ | _ => pauliI
  | ⟨5, _⟩ => fun | ⟨0, _⟩ | ⟨2, _⟩ | ⟨4, _⟩ | ⟨6, _⟩ => pauliZ | _ => pauliI

/-- Decidable certification that all 6 Steane generators commute pairwise under symplectic product. -/
theorem steane_generators_commute : ¬ HasNonCommutingPair 6 7 steaneGens := by
  decide

end EvoByte.Frontier
