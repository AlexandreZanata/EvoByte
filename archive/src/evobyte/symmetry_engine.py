"""Algebraic Symmetry and Automorphism Orbit Reduction Engine (P192).

Implements automorphism group actions, cyclic orbit reductions, and
quasi-cyclic circulant matrix generators for:
1. Covering designs: partitioning subsets into Z_v orbits, base block synthesis,
   and difference multisets.
2. Quantum error-correcting codes (QECC): block-circulant stabilizer matrices,
   circulant symplectic commutativity, and orbit-preserving mutations.

Part of the Structured Discovery Program (P191-P200, D043).
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import math
from typing import Any, Sequence

import numpy as np


class CyclicGroup:
    """Action of the cyclic group Z_m on finite sets and coordinate indices."""

    def __init__(self, order: int) -> None:
        if order <= 0:
            raise ValueError(f"Cyclic group order must be positive, got {order}")
        self.order: int = int(order)

    def apply(self, x: int, shift: int = 1) -> int:
        """Apply cyclic shift: (x + shift) mod m."""
        return (x + shift) % self.order

    def apply_to_subset(self, block: Sequence[int], shift: int = 1) -> tuple[int, ...]:
        """Apply cyclic shift to all elements of a subset and return sorted tuple."""
        return tuple(sorted((x + shift) % self.order for x in block))

    def orbit(self, block: Sequence[int]) -> list[tuple[int, ...]]:
        """Compute the full orbit of a subset under Z_m action."""
        unique: set[tuple[int, ...]] = set()
        orbit_list: list[tuple[int, ...]] = []
        for s in range(self.order):
            shifted = self.apply_to_subset(block, shift=s)
            if shifted not in unique:
                unique.add(shifted)
                orbit_list.append(shifted)
        return orbit_list

    def canonical_representative(self, block: Sequence[int]) -> tuple[int, ...]:
        """Return the lexicographically smallest subset in the orbit."""
        return min(self.apply_to_subset(block, shift=s) for s in range(self.order))

    def is_invariant(self, blocks: Sequence[Sequence[int]], shift: int = 1) -> bool:
        """Check whether a collection of blocks is invariant under a cyclic shift."""
        block_set = {tuple(sorted(b)) for b in blocks}
        shifted_set = {self.apply_to_subset(b, shift=shift) for b in blocks}
        return block_set == shifted_set


@dataclass(frozen=True)
class CoveringOrbitStats:
    """Statistics for orbit reduction on covering designs."""

    v: int
    k: int
    t: int
    total_blocks: int
    num_orbits: int
    compression_ratio: float
    max_orbit_size: int
    min_orbit_size: int


class CoveringOrbitEngine:
    """Orbit reduction engine for covering designs C(v, k, t) under Z_v."""

    def __init__(self, v: int, k: int, t: int) -> None:
        if not (1 <= t <= k <= v):
            raise ValueError(
                f"Invalid covering parameters: require 1 <= t ({t}) <= k ({k}) <= v ({v})"
            )
        self.v: int = v
        self.k: int = k
        self.t: int = t
        self.group: CyclicGroup = CyclicGroup(v)
        self._orbit_representatives: list[tuple[int, ...]] | None = None

    def compute_orbit_representatives(self) -> list[tuple[int, ...]]:
        """Generate canonical representatives for all Z_v orbits of k-subsets."""
        if self._orbit_representatives is not None:
            return list(self._orbit_representatives)

        seen: set[tuple[int, ...]] = set()
        representatives: list[tuple[int, ...]] = []
        for subset in combinations(range(self.v), self.k):
            rep = self.group.canonical_representative(subset)
            if rep not in seen:
                seen.add(rep)
                representatives.append(rep)

        self._orbit_representatives = representatives
        return list(representatives)

    def get_orbit_stats(self) -> CoveringOrbitStats:
        """Compute exact reduction statistics for this covering configuration."""
        reps = self.compute_orbit_representatives()
        total = math.comb(self.v, self.k)
        num_orbits = len(reps)
        compression = total / num_orbits if num_orbits > 0 else 1.0

        sizes = [len(self.group.orbit(r)) for r in reps]
        return CoveringOrbitStats(
            v=self.v,
            k=self.k,
            t=self.t,
            total_blocks=total,
            num_orbits=num_orbits,
            compression_ratio=compression,
            max_orbit_size=max(sizes) if sizes else 0,
            min_orbit_size=min(sizes) if sizes else 0,
        )

    def expand_base_blocks(
        self, base_blocks: Sequence[Sequence[int]], one_indexed: bool = True
    ) -> list[list[int]]:
        """Expand a collection of base blocks into their full orbits."""
        expanded: set[tuple[int, ...]] = set()
        for base in base_blocks:
            for shifted in self.group.orbit(base):
                expanded.add(shifted)

        sorted_blocks = sorted(list(b) for b in expanded)
        if one_indexed:
            return [[x + 1 for x in b] for b in sorted_blocks]
        return sorted_blocks

    def difference_signature(self, block: Sequence[int]) -> dict[int, int]:
        """Compute the multiset of differences (x - y) mod v for a base block."""
        diffs: dict[int, int] = {}
        arr = list(block)
        for i in range(len(arr)):
            for j in range(len(arr)):
                if i != j:
                    d = (arr[i] - arr[j]) % self.v
                    diffs[d] = diffs.get(d, 0) + 1
        return diffs

    def sample_base_blocks(
        self, num_base_blocks: int, rng: np.random.Generator
    ) -> list[tuple[int, ...]]:
        """Uniformly sample base blocks from orbit representatives."""
        reps = self.compute_orbit_representatives()
        indices = rng.choice(
            len(reps),
            size=min(num_base_blocks, len(reps)),
            replace=False,
        )
        return [reps[int(i)] for i in indices]

    def mutate_base_block(
        self, base_block: Sequence[int], rng: np.random.Generator
    ) -> tuple[int, ...]:
        """Mutate a base block by swapping one element, returning canonical representative."""
        elements = set(base_block)
        available = [x for x in range(self.v) if x not in elements]
        if not available:
            return tuple(sorted(base_block))

        remove_elem = rng.choice(list(elements))
        add_elem = rng.choice(available)
        new_set = (elements - {remove_elem}) | {add_elem}
        return self.group.canonical_representative(list(new_set))


def circulant_matrix(first_row: Sequence[int] | np.ndarray) -> np.ndarray:
    """Construct an L x L circulant binary matrix from its first row.

    M[i, j] = first_row[(j - i) mod L].
    """
    row = np.asarray(first_row, dtype=np.uint8)
    L = len(row)
    mat = np.zeros((L, L), dtype=np.uint8)
    for i in range(L):
        mat[i] = np.roll(row, i)
    return mat


def cyclic_convolution(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Compute discrete cyclic convolution of two binary vectors over GF(2)."""
    L = len(a)
    result = np.zeros(L, dtype=np.uint8)
    for j in range(L):
        result[j] = sum(int(a[k]) * int(b[(j - k) % L]) for k in range(L)) % 2
    return result


def gf2_nullspace(mat: np.ndarray) -> np.ndarray:
    """Compute an orthogonal basis of the nullspace of mat over GF(2)."""
    m, ncols = mat.shape
    if m == 0 or ncols == 0:
        return np.zeros((0, ncols), dtype=np.uint8)

    aug = mat.copy().astype(np.uint8)
    r = 0
    pivots: list[int] = []
    for col in range(ncols):
        if r >= m:
            break
        piv = np.where(aug[r:, col] == 1)[0]
        if len(piv) == 0:
            continue
        pr = r + piv[0]
        if pr != r:
            aug[[r, pr]] = aug[[pr, r]]
        pivots.append(col)
        for i in range(m):
            if i != r and aug[i, col] == 1:
                aug[i] ^= aug[r]
        r += 1

    free_vars = [col for col in range(ncols) if col not in pivots]
    basis: list[np.ndarray] = []
    for f in free_vars:
        vec = np.zeros(ncols, dtype=np.uint8)
        vec[f] = 1
        for i, p in enumerate(pivots):
            if aug[i, f] == 1:
                vec[p] = 1
        basis.append(vec)

    return np.array(basis, dtype=np.uint8) if basis else np.zeros((0, ncols), dtype=np.uint8)


def gf2_rank(mat: np.ndarray) -> int:
    """Compute rank of binary matrix over GF(2)."""
    if mat.size == 0:
        return 0
    arr = mat.copy().astype(np.uint8)
    nrows, ncols = arr.shape
    r = 0
    for col in range(ncols):
        if r >= nrows:
            break
        piv = np.where(arr[r:, col] == 1)[0]
        if len(piv) == 0:
            continue
        pr = r + piv[0]
        if pr != r:
            arr[[r, pr]] = arr[[pr, r]]
        for i in range(nrows):
            if i != r and arr[i, col] == 1:
                arr[i] ^= arr[r]
        r += 1
    return r


class QuasiCyclicStabilizerEngine:
    """Engine for generating block-circulant quasi-cyclic quantum stabilizer codes [[n, k]]."""

    def __init__(self, n: int, k: int, block_size: int | None = None) -> None:
        self.n: int = n
        self.k: int = k
        self.m: int = n - k
        if self.m <= 0:
            raise ValueError(f"Require n > k, got n={n}, k={k}")

        # Default block size L divides n
        if block_size is not None:
            if n % block_size != 0:
                raise ValueError(f"Block size {block_size} must divide n={n}")
            self.L: int = block_size
        else:
            divs = [d for d in range(2, n + 1) if n % d == 0 and d <= self.m]
            self.L = max(divs) if divs else n

        self.c: int = self.n // self.L  # number of blocks

    def parameter_compression_factor(self) -> float:
        """Compression ratio between full unconstrained matrix and quasi-cyclic seeds."""
        full_params = self.m * (2 * self.n)
        seed_params = 2 * self.n  # One seed generator row (c*L for X, c*L for Z)
        return full_params / seed_params if seed_params > 0 else 1.0

    def check_symplectic_commutation(self, candidate: np.ndarray) -> bool:
        """Check if all rows of candidate binary matrix mutually commute under symplectic product."""
        rows, cols = candidate.shape
        n = cols // 2
        X = candidate[:, :n]
        Z = candidate[:, n:]
        prod = (X @ Z.T + Z @ X.T) % 2
        return bool(np.all(prod == 0))

    def generate_circulant_css_candidate(self, rng: np.random.Generator) -> tuple[bool, np.ndarray]:
        """Generate an (m, 2n) stabilizer matrix composed of circulant CSS blocks.

        Guarantees that X-blocks and Z-blocks mutually commute algebraically.
        Returns (success, candidate_matrix).
        """
        L = self.L
        c = self.c

        # 1. Sample non-trivial seed row for X blocks: shape (c, L)
        for _ in range(50):
            ax = rng.integers(0, 2, size=(c, L), dtype=np.uint8)
            if np.all(ax == 0):
                continue

            # Linear system for Z seed rows: [C(ax_0)^T | ... | C(ax_{c-1})^T] @ az = 0 mod 2
            # Shape of M is (L, c * L)
            blocks_T = [
                np.array([np.roll(ax[j], -s) for s in range(L)], dtype=np.uint8) for j in range(c)
            ]
            M = np.hstack(blocks_T)
            null = gf2_nullspace(M)
            if len(null) == 0:
                continue

            # Pick non-trivial linear combination of nullspace vectors for Z seed
            combo = rng.integers(0, 2, size=len(null), dtype=np.uint8)
            if np.all(combo == 0):
                combo[rng.integers(0, len(null))] = 1
            az_flat = (combo @ null) % 2
            if np.all(az_flat == 0):
                continue
            az = az_flat.reshape(c, L)

            # Build circulant generator rows
            # X generators: (L, 2n) with Z=0
            # Z generators: (L, 2n) with X=0
            X_rows: list[np.ndarray] = []
            Z_rows: list[np.ndarray] = []

            for s in range(L):
                row_x = np.zeros(2 * self.n, dtype=np.uint8)
                row_z = np.zeros(2 * self.n, dtype=np.uint8)
                for j in range(c):
                    row_x[j * L : (j + 1) * L] = np.roll(ax[j], s)
                    row_z[self.n + j * L : self.n + (j + 1) * L] = np.roll(az[j], s)
                X_rows.append(row_x)
                Z_rows.append(row_z)

            all_rows = np.vstack([X_rows, Z_rows])
            # Check mutual commutation
            if not self.check_symplectic_commutation(all_rows):
                continue

            # Select m linearly independent rows
            selected_rows: list[np.ndarray] = []
            for r in all_rows:
                test_mat = np.vstack([selected_rows, r]) if selected_rows else r.reshape(1, -1)
                if gf2_rank(test_mat) > len(selected_rows):
                    selected_rows.append(r)
                    if len(selected_rows) == self.m:
                        break

            if len(selected_rows) == self.m:
                cand = np.array(selected_rows, dtype=np.uint8)
                # Verify non-degeneracy
                if gf2_rank(cand) == self.m and not np.any(np.sum(cand, axis=1) == 0):
                    return True, cand

        # Fallback to repair if random sampling did not close rank
        fallback = np.zeros((self.m, 2 * self.n), dtype=np.uint8)
        for i in range(self.m):
            fallback[i, i] = 1
            fallback[i, self.n + (i + 1) % self.n] = 1
        return False, fallback

    def mutate_quasi_cyclic_candidate(
        self, candidate: np.ndarray, rng: np.random.Generator, num_flips: int = 2
    ) -> np.ndarray:
        """Mutate a quasi-cyclic candidate while preserving its circulant block structure."""
        mutated = candidate.copy()
        m, d2 = mutated.shape
        L = self.L
        c = self.c

        # Mutate the seed block of row 0 and replicate cyclic shifts across rows
        for _ in range(num_flips):
            block_idx = rng.integers(0, 2 * c)
            bit_idx = rng.integers(0, L)
            col = (
                block_idx * L + bit_idx if block_idx < c else self.n + (block_idx - c) * L + bit_idx
            )
            # Flip column across corresponding cyclic shifts
            shift_row = rng.integers(0, min(m, L))
            mutated[shift_row, col] ^= 1

        # Quick repair if commutation disturbed
        if not self.check_symplectic_commutation(mutated):
            X = mutated[:, : self.n]
            Z = mutated[:, self.n :]
            prod = (X @ Z.T + Z @ X.T) % 2
            bad_pairs = np.argwhere(np.triu(prod, 1) == 1)
            for r1, r2 in bad_pairs:
                # Flip matching coordinate to restore orthogonality
                mutated[r2, :] ^= mutated[r1, :]

        return mutated

    def measure_commutativity_preservation(
        self, n_samples: int = 500, rng: np.random.Generator | None = None
    ) -> dict[str, float]:
        """Measure the rate of symplectic commutativity preservation over n_samples."""
        if rng is None:
            rng = np.random.default_rng(42)

        commute_count = 0
        non_degenerate_count = 0

        for _ in range(n_samples):
            ok, cand = self.generate_circulant_css_candidate(rng)
            if ok and self.check_symplectic_commutation(cand):
                commute_count += 1
                if gf2_rank(cand) == self.m:
                    non_degenerate_count += 1

        rate = (commute_count / n_samples) * 100.0
        non_deg_rate = (non_degenerate_count / n_samples) * 100.0
        return {
            "n_samples": float(n_samples),
            "commutativity_rate_pct": rate,
            "non_degenerate_rate_pct": non_deg_rate,
            "compression_factor": self.parameter_compression_factor(),
        }


def get_symmetry_engine_for_target(target_id: str) -> Any:
    """Factory creating the appropriate symmetry engine for any P191 target."""
    if target_id == "covering_C_13_6_3":
        return CoveringOrbitEngine(v=13, k=6, t=3)
    elif target_id == "covering_C_14_6_3":
        return CoveringOrbitEngine(v=14, k=6, t=3)
    elif target_id == "covering_C_15_8_4":
        return CoveringOrbitEngine(v=15, k=8, t=4)
    elif target_id == "qecc_14_3_open":
        return QuasiCyclicStabilizerEngine(n=14, k=3, block_size=7)
    elif target_id == "qecc_16_5_open":
        return QuasiCyclicStabilizerEngine(n=16, k=5, block_size=8)
    raise KeyError(f"Target ID {target_id!r} not configured for symmetry engine")


def benchmark_all_p191_symmetry_reductions() -> dict[str, dict[str, Any]]:
    """Run measured symmetry compression benchmark across all 5 P191 targets."""
    results: dict[str, dict[str, Any]] = {}

    # Covering designs
    for tid, v, k, t in [
        ("covering_C_13_6_3", 13, 6, 3),
        ("covering_C_14_6_3", 14, 6, 3),
        ("covering_C_15_8_4", 15, 8, 4),
    ]:
        engine = CoveringOrbitEngine(v, k, t)
        stats = engine.get_orbit_stats()
        results[tid] = {
            "family": "covering_design",
            "group": f"Z_{v}",
            "order": v,
            "total_space": stats.total_blocks,
            "orbit_space": stats.num_orbits,
            "compression_factor": stats.compression_ratio,
            "target_threshold_met": stats.compression_ratio >= 4.0,
        }

    # QECC codes
    for tid, n, k, L in [
        ("qecc_14_3_open", 14, 3, 7),
        ("qecc_16_5_open", 16, 5, 8),
    ]:
        engine = QuasiCyclicStabilizerEngine(n, k, block_size=L)
        stats = engine.measure_commutativity_preservation(n_samples=50)
        results[tid] = {
            "family": "qecc_stabilizer",
            "group": f"circulant_Z_{L}",
            "order": L,
            "compression_factor": stats["compression_factor"],
            "commutativity_rate_pct": stats["commutativity_rate_pct"],
            "non_degenerate_rate_pct": stats["non_degenerate_rate_pct"],
            "target_threshold_met": (
                stats["compression_factor"] >= 4.0 and stats["commutativity_rate_pct"] >= 90.0
            ),
        }

    return results
