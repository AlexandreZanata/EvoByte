"""Exact SAT Distance and Symplectic Encoder (P204).

Implements exact Conjunctive Normal Form (CNF) formulations for:
1. Minimum quantum distance verification and refutation ($d \\ge d_{target}$) for CSS
   stabilizer codes via boolean cardinality encodings (Sinz counters) and GF(2) parity clauses.
2. Generalized automorphism covering design optimization: selecting minimal base orbits
   under Affine AGL(1, q) and Dihedral D_m groups to cover all target t-subsets.
3. Fast CDCL solver integration (CaDiCaL / PySAT) with strict timeout budgets (< 5 seconds).

Part of the Generalized Symmetries & Non-Circulant Quantum Codes Program (P201-P210, D045).
"""

from __future__ import annotations

from dataclasses import dataclass
import itertools
import time
from typing import Any, Sequence

import numpy as np

from evobyte.generalized_symmetry import GeneralizedCoveringOrbitEngine, GroupAction
from evobyte.quasi_cyclic_qecc import (
    QuasiCyclicStabilizer,
    gf2_basis_and_indices,
    in_gf2_span,
    verify_symplectic_orthogonality,
)
from evobyte.sat_bridge import CNFFormula, solve_cnf


def nullspace_gf2(mat: np.ndarray, n_cols: int | None = None) -> np.ndarray:
    """Compute an exact GF(2) nullspace (kernel) basis using Gaussian elimination."""
    if len(mat) == 0:
        return (
            np.eye(n_cols, dtype=np.uint8)
            if n_cols is not None
            else np.empty((0, 0), dtype=np.uint8)
        )
    m, n = mat.shape
    A = mat.copy()
    pivots: list[int] = []
    r = 0
    for c in range(n):
        pivot_row = None
        for i in range(r, m):
            if A[i, c] == 1:
                pivot_row = i
                break
        if pivot_row is not None:
            A[[r, pivot_row]] = A[[pivot_row, r]]
            for i in range(m):
                if i != r and A[i, c] == 1:
                    A[i] ^= A[r]
            pivots.append(c)
            r += 1
    free_vars = [c for c in range(n) if c not in pivots]
    null_basis: list[np.ndarray] = []
    for f in free_vars:
        vec = np.zeros(n, dtype=np.uint8)
        vec[f] = 1
        for i, p in enumerate(pivots):
            if A[i, f] == 1:
                vec[p] = 1
        null_basis.append(vec)
    if not null_basis:
        return np.empty((0, n), dtype=np.uint8)
    return np.array(null_basis, dtype=np.uint8)


def extract_css_logicals(
    HX: np.ndarray, HZ: np.ndarray
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Extract independent basis vectors for logical X and logical Z operators.

    Logical X operators lie in ker(HZ) \\ rowspan(HX).
    Logical Z operators lie in ker(HX) \\ rowspan(HZ).
    """
    n = HX.shape[1]

    # Logical Z operators
    ker_HX = nullspace_gf2(HX, n)
    basis_z, _ = gf2_basis_and_indices(HZ)
    logicals_z: list[np.ndarray] = []
    for vec in ker_HX:
        v_int = int(sum(int(b) << i for i, b in enumerate(vec)))
        if not in_gf2_span(v_int, basis_z):
            logicals_z.append(vec)
            basis_z.append(v_int)

    # Logical X operators
    ker_HZ = nullspace_gf2(HZ, n)
    basis_x, _ = gf2_basis_and_indices(HX)
    logicals_x: list[np.ndarray] = []
    for vec in ker_HZ:
        v_int = int(sum(int(b) << i for i, b in enumerate(vec)))
        if not in_gf2_span(v_int, basis_x):
            logicals_x.append(vec)
            basis_x.append(v_int)

    return logicals_x, logicals_z


@dataclass(frozen=True)
class SATDistanceResult:
    """Outcome of SAT-based quantum code distance verification."""

    code_n: int
    code_k: int
    target_distance: int
    distance_verified: bool
    proven_distance_lower_bound: int
    exact_distance: int | None
    minimal_logical: str | None
    solve_time_seconds: float
    num_clauses: int
    solver_name: str


class SATDistanceEncoder:
    """Exact SAT encoder for quantum stabilizer code distance bounds."""

    @staticmethod
    def encode_logical_operator(
        H_checks: np.ndarray,
        anti_commute_target: np.ndarray,
        weight: int,
    ) -> tuple[CNFFormula, list[int]]:
        """Encode whether an undetectable error of prescribed weight exists.

        For X errors:
        H_checks is HZ (must commute with all Z stabilizers).
        anti_commute_target is a logical Z operator (must anti-commute, proving x outside span(HX)).
        """
        n = H_checks.shape[1]
        formula = CNFFormula()
        vars_vec = [formula.new_var(f"v_{i}") for i in range(n)]

        # 1. Parity checks: H_checks @ v == 0 (mod 2)
        for row in H_checks:
            lits = [vars_vec[i] for i, b in enumerate(row) if b]
            formula.add_xor(lits, target_parity=0)

        # 2. Non-triviality check: v @ anti_commute_target == 1 (mod 2)
        lits_anti = [vars_vec[i] for i, b in enumerate(anti_commute_target) if b]
        formula.add_xor(lits_anti, target_parity=1)

        # 3. Cardinality constraint: Hamming weight <= weight
        formula.add_at_most_k(vars_vec, weight)

        return formula, vars_vec

    @classmethod
    def verify_distance_bound(
        cls,
        code: QuasiCyclicStabilizer | tuple[np.ndarray, np.ndarray],
        target_distance: int,
        timeout_seconds: float = 5.0,
        solver_name: str = "auto",
    ) -> SATDistanceResult:
        """Verify whether code distance satisfies d >= target_distance.

        Tests whether any non-trivial logical operator of weight w < target_distance
        exists. If all queries are UNSAT, d >= target_distance is proven.
        """
        if isinstance(code, QuasiCyclicStabilizer):
            HX, HZ = code.HX, code.HZ
            n = code.n
            k = code.k
        else:
            HX, HZ = code
            n = HX.shape[1]
            rx = len(gf2_basis_and_indices(HX)[0])
            rz = len(gf2_basis_and_indices(HZ)[0])
            k = n - rx - rz

        if k <= 0:
            return SATDistanceResult(
                code_n=n,
                code_k=k,
                target_distance=target_distance,
                distance_verified=False,
                proven_distance_lower_bound=0,
                exact_distance=0,
                minimal_logical=None,
                solve_time_seconds=0.0,
                num_clauses=0,
                solver_name=solver_name,
            )

        if not verify_symplectic_orthogonality(HX, HZ):
            raise ValueError("Check matrices do not commute symplectically!")

        t0 = time.perf_counter()
        logicals_x, logicals_z = extract_css_logicals(HX, HZ)

        total_clauses = 0
        used_solver = solver_name

        # Check weights w = 1 .. target_distance - 1
        for w in range(1, target_distance):
            # Test X logicals
            for lz in logicals_z:
                formula, _ = cls.encode_logical_operator(HZ, lz, weight=w)
                total_clauses += len(formula.clauses)
                res = solve_cnf(formula, timeout_seconds=timeout_seconds, solver_name=solver_name)
                used_solver = res.solver_name
                if res.is_sat:
                    elapsed = time.perf_counter() - t0
                    return SATDistanceResult(
                        code_n=n,
                        code_k=k,
                        target_distance=target_distance,
                        distance_verified=False,
                        proven_distance_lower_bound=w,
                        exact_distance=w,
                        minimal_logical=f"X-error (wt={w})",
                        solve_time_seconds=elapsed,
                        num_clauses=total_clauses,
                        solver_name=used_solver,
                    )

            # Test Z logicals
            for lx in logicals_x:
                formula, _ = cls.encode_logical_operator(HX, lx, weight=w)
                total_clauses += len(formula.clauses)
                res = solve_cnf(formula, timeout_seconds=timeout_seconds, solver_name=solver_name)
                used_solver = res.solver_name
                if res.is_sat:
                    elapsed = time.perf_counter() - t0
                    return SATDistanceResult(
                        code_n=n,
                        code_k=k,
                        target_distance=target_distance,
                        distance_verified=False,
                        proven_distance_lower_bound=w,
                        exact_distance=w,
                        minimal_logical=f"Z-error (wt={w})",
                        solve_time_seconds=elapsed,
                        num_clauses=total_clauses,
                        solver_name=used_solver,
                    )

        elapsed = time.perf_counter() - t0
        return SATDistanceResult(
            code_n=n,
            code_k=k,
            target_distance=target_distance,
            distance_verified=True,
            proven_distance_lower_bound=target_distance,
            exact_distance=None,
            minimal_logical=None,
            solve_time_seconds=elapsed,
            num_clauses=total_clauses,
            solver_name=used_solver,
        )

    @classmethod
    def find_exact_distance(
        cls,
        code: QuasiCyclicStabilizer | tuple[np.ndarray, np.ndarray],
        max_search: int = 5,
        timeout_seconds: float = 5.0,
        solver_name: str = "auto",
    ) -> SATDistanceResult:
        """Find the exact distance by incremental SAT queries."""
        if isinstance(code, QuasiCyclicStabilizer):
            HX, HZ = code.HX, code.HZ
            n = code.n
            k = code.k
        else:
            HX, HZ = code
            n = HX.shape[1]
            rx = len(gf2_basis_and_indices(HX)[0])
            rz = len(gf2_basis_and_indices(HZ)[0])
            k = n - rx - rz

        t0 = time.perf_counter()
        logicals_x, logicals_z = extract_css_logicals(HX, HZ)

        total_clauses = 0
        used_solver = solver_name

        for w in range(1, max_search + 1):
            # Test X logicals
            for lz in logicals_z:
                formula, vars_vec = cls.encode_logical_operator(HZ, lz, weight=w)
                total_clauses += len(formula.clauses)
                res = solve_cnf(formula, timeout_seconds=timeout_seconds, solver_name=solver_name)
                used_solver = res.solver_name
                if res.is_sat and res.assignment:
                    model_vec = "".join(
                        "X" if res.assignment.get(v, False) else "I" for v in vars_vec
                    )
                    elapsed = time.perf_counter() - t0
                    return SATDistanceResult(
                        code_n=n,
                        code_k=k,
                        target_distance=w,
                        distance_verified=True,
                        proven_distance_lower_bound=w,
                        exact_distance=w,
                        minimal_logical=model_vec,
                        solve_time_seconds=elapsed,
                        num_clauses=total_clauses,
                        solver_name=used_solver,
                    )

            # Test Z logicals
            for lx in logicals_x:
                formula, vars_vec = cls.encode_logical_operator(HX, lx, weight=w)
                total_clauses += len(formula.clauses)
                res = solve_cnf(formula, timeout_seconds=timeout_seconds, solver_name=solver_name)
                used_solver = res.solver_name
                if res.is_sat and res.assignment:
                    model_vec = "".join(
                        "Z" if res.assignment.get(v, False) else "I" for v in vars_vec
                    )
                    elapsed = time.perf_counter() - t0
                    return SATDistanceResult(
                        code_n=n,
                        code_k=k,
                        target_distance=w,
                        distance_verified=True,
                        proven_distance_lower_bound=w,
                        exact_distance=w,
                        minimal_logical=model_vec,
                        solve_time_seconds=elapsed,
                        num_clauses=total_clauses,
                        solver_name=used_solver,
                    )

        elapsed = time.perf_counter() - t0
        return SATDistanceResult(
            code_n=n,
            code_k=k,
            target_distance=max_search,
            distance_verified=False,
            proven_distance_lower_bound=max_search + 1,
            exact_distance=None,
            minimal_logical=None,
            solve_time_seconds=elapsed,
            num_clauses=total_clauses,
            solver_name=used_solver,
        )


@dataclass(frozen=True)
class SATCoveringResult:
    """Outcome of SAT-based generalized orbit covering design search."""

    v: int
    k: int
    t: int
    group_name: str
    is_sat: bool
    num_base_blocks: int
    total_blocks: int
    base_blocks: list[tuple[int, ...]]
    solve_time_seconds: float
    num_clauses: int
    solver_name: str


class SATCoveringEncoder:
    """Exact SAT encoder for covering designs under generalized automorphism groups."""

    @classmethod
    def encode_and_solve(
        cls,
        v: int,
        k: int,
        t: int,
        group: GroupAction,
        max_base_blocks: int,
        timeout_seconds: float = 5.0,
        solver_name: str = "auto",
    ) -> SATCoveringResult:
        """Encode and solve for minimal base blocks under group action."""
        t0 = time.perf_counter()
        engine = GeneralizedCoveringOrbitEngine(v, k, t, group)
        reps = engine.compute_orbit_representatives()
        t_subsets = list(itertools.combinations(range(v), t))
        orbit_blocks = [group.orbit(r) for r in reps]

        # For each t-subset, list of orbit representative indices that cover it
        covers: list[list[int]] = [[] for _ in t_subsets]
        for rep_idx, blocks in enumerate(orbit_blocks):
            for b in blocks:
                b_set = set(b)
                for t_idx, t_sub in enumerate(t_subsets):
                    if set(t_sub).issubset(b_set):
                        covers[t_idx].append(rep_idx)

        # Deduplicate
        covers = [sorted(list(set(c))) for c in covers]

        formula = CNFFormula()
        y_vars = [formula.new_var(f"orbit_{i}") for i in range(len(reps))]

        # Coverage constraints: each t-subset must be covered by at least 1 chosen orbit
        for covering_orbits in covers:
            clause = [y_vars[i] for i in covering_orbits]
            formula.add_clause(clause)

        # Cardinality constraint: at most max_base_blocks
        formula.add_at_most_k(y_vars, max_base_blocks)

        res = solve_cnf(formula, timeout_seconds=timeout_seconds, solver_name=solver_name)
        elapsed = time.perf_counter() - t0

        chosen_reps: list[tuple[int, ...]] = []
        total_blocks = 0
        if res.is_sat and res.assignment:
            chosen_indices = [i for i, y in enumerate(y_vars) if res.assignment.get(y, False)]
            chosen_reps = [reps[i] for i in chosen_indices]
            total_blocks = sum(len(orbit_blocks[i]) for i in chosen_indices)

        return SATCoveringResult(
            v=v,
            k=k,
            t=t,
            group_name=type(group).__name__,
            is_sat=res.is_sat,
            num_base_blocks=len(chosen_reps),
            total_blocks=total_blocks,
            base_blocks=chosen_reps,
            solve_time_seconds=elapsed,
            num_clauses=len(formula.clauses),
            solver_name=res.solver_name,
        )
