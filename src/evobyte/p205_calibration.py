"""Blind Historical Calibration Protocol for Affine and Non-Circulant Targets (P205).

Implements blind rediscovery on three literature milestones:
1. Covering Design C(9, 3, 2) = 12: Affine plane AG(2, 3) over F_9.
2. Steane [[7, 1, 3]] CSS Quantum Code: Dual Hamming / Fano plane stabilizer.
3. Shor [[9, 1, 3]] Non-Circulant Stabilizer Code: 9 qubits, 8 generators, d=3.

All targets are discovered blindly from first principles via exact SAT encodings
and verified using independent zero-dependency verifiers without any injected
seeds or hard-coded generator tables.

Part of the Generalized Symmetries & Non-Circulant Quantum Codes Program (P201-P210, D045).
"""

from __future__ import annotations

import hashlib
import itertools
import json
import time
from typing import Any, Sequence

import numpy as np

from evobyte.frontier_catalogue import verify_covering_design
from evobyte.qecc_verifier import check_stabilizer, code_distance
from evobyte.sat_bridge import CNFFormula, solve_cnf


def verify_affine_plane_properties(
    blocks: Sequence[Sequence[int]], v: int = 9, k: int = 3
) -> tuple[bool, str]:
    """Verify combinatorial properties of the affine plane AG(2, 3).

    Checks:
    1. Exactly 12 lines of size 3 on 9 points.
    2. Every point has degree r = 4.
    3. Every pair of points lies on exactly lambda = 1 line.
    4. The 12 lines decompose into 4 parallel classes of 3 mutually disjoint lines.
    """
    if len(blocks) != 12:
        return False, f"Expected 12 blocks, got {len(blocks)}"

    for b in blocks:
        if len(b) != k:
            return False, f"Block {b} has size {len(b)}, expected {k}"
        if len(set(b)) != k:
            return False, f"Block {b} contains duplicate points"
        for p in b:
            if not (1 <= p <= v):
                return False, f"Point {p} out of range [1, {v}]"

    # Degree check: each point in exactly 4 lines
    degrees: dict[int, int] = {p: 0 for p in range(1, v + 1)}
    for b in blocks:
        for p in b:
            degrees[p] += 1
    if not all(d == 4 for d in degrees.values()):
        return False, f"Points do not all have degree 4: {degrees}"

    # Pair check: lambda = 1
    pair_counts: dict[tuple[int, int], int] = {}
    for p1 in range(1, v + 1):
        for p2 in range(p1 + 1, v + 1):
            pair_counts[(p1, p2)] = 0
    for b in blocks:
        for p1, p2 in itertools.combinations(sorted(b), 2):
            pair_counts[(p1, p2)] += 1
    if not all(cnt == 1 for cnt in pair_counts.values()):
        return False, "Not all pairs covered with lambda = 1"

    # Parallel classes check: 4 parallel classes of 3 mutually disjoint lines
    disjoint_adj: dict[int, set[int]] = {i: set() for i in range(12)}
    for i in range(12):
        for j in range(i + 1, 12):
            if len(set(blocks[i]).intersection(set(blocks[j]))) == 0:
                disjoint_adj[i].add(j)
                disjoint_adj[j].add(i)

    for i in range(12):
        if len(disjoint_adj[i]) != 2:
            return False, f"Line {i} is disjoint from {len(disjoint_adj[i])} lines, expected 2"

    return True, "Valid affine plane AG(2, 3) with 4 parallel classes of 3 lines"


def synthesize_affine_covering_c9_3_2(
    seed: int = 42,
    timeout_seconds: float = 30.0,
    solver_name: str = "cadical153",
) -> tuple[bool, list[list[int]], dict[str, Any]]:
    """Synthesize minimal covering design C(9, 3, 2) = 12 blocks blindly via SAT.

    Parameters: v=9, k=3, t=2.
    Targets exact affine plane AG(2, 3) realization with b = 12 blocks.
    """
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)
    v, k, t, b = 9, 3, 2, 12

    all_blocks = list(itertools.combinations(range(v), k))
    pairs = list(itertools.combinations(range(v), t))

    formula = CNFFormula(n_vars=len(all_blocks))
    for pair in pairs:
        clause = [
            idx + 1 for idx, blk in enumerate(all_blocks) if pair[0] in blk and pair[1] in blk
        ]
        formula.add_clause(clause)

    formula.add_at_most_k(list(range(1, len(all_blocks) + 1)), b)

    cls = list(formula.clauses)
    rng.shuffle(cls)
    shuffled_formula = CNFFormula(n_vars=formula.n_vars)
    shuffled_formula.clauses = cls

    sat_res = solve_cnf(shuffled_formula, timeout_seconds=timeout_seconds, solver_name=solver_name)
    elapsed = time.perf_counter() - t0

    stats: dict[str, Any] = {
        "seed": seed,
        "v": v,
        "k": k,
        "t": t,
        "target_blocks": b,
        "status": sat_res.status,
        "solve_time_seconds": sat_res.solve_time_seconds,
        "wall_clock_seconds": elapsed,
        "verified": False,
        "total_blocks": 0,
    }

    if not sat_res.is_sat or sat_res.model is None:
        return False, [], stats

    model_set = set(sat_res.model)
    chosen_blocks_0idx = [
        all_blocks[idx] for idx in range(len(all_blocks)) if (idx + 1) in model_set
    ]
    full_blocks = [[x + 1 for x in blk] for blk in chosen_blocks_0idx]

    verified_cov, v_msg = verify_covering_design(full_blocks, v, k, t)
    verified_affine, a_msg = verify_affine_plane_properties(full_blocks, v, k)
    is_valid = verified_cov and verified_affine and (len(full_blocks) <= b)

    stats["verified"] = is_valid
    stats["verification_msg"] = v_msg
    stats["affine_msg"] = a_msg
    stats["total_blocks"] = len(full_blocks)
    stats["blocks"] = full_blocks
    stats["sha256"] = hashlib.sha256(json.dumps(full_blocks, sort_keys=True).encode()).hexdigest()

    return is_valid, full_blocks, stats


def synthesize_steane_7_1_3(
    seed: int = 42,
    timeout_seconds: float = 30.0,
    solver_name: str = "cadical153",
) -> tuple[bool, list[str], dict[str, Any]]:
    """Synthesize Steane [[7, 1, 3]] CSS quantum code blindly via exact SAT constraints.

    Generates m_X = 3 and m_Z = 3 commuting generators on 7 qubits with distance d >= 3.
    """
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)
    n = 7
    m_x = 3
    m_z = 3

    formula = CNFFormula()
    var_x: dict[tuple[int, int], int] = {}
    var_z: dict[tuple[int, int], int] = {}

    for i in range(m_x):
        for q in range(n):
            var_x[(i, q)] = formula.new_var(f"hx_{i}_{q}")
    for j in range(m_z):
        for q in range(n):
            var_z[(j, q)] = formula.new_var(f"hz_{j}_{q}")

    # Echelon pivots to break row-permutation symmetry and guarantee full row rank
    pivots_x = sorted(list(rng.choice(n, size=m_x, replace=False)))
    for i, p_col in enumerate(pivots_x):
        formula.add_clause([var_x[(i, p_col)]])
        for i2 in range(i + 1, m_x):
            formula.add_clause([-var_x[(i2, p_col)]])

    pivots_z = sorted(list(rng.choice(n, size=m_z, replace=False)))
    for j, p_col in enumerate(pivots_z):
        formula.add_clause([var_z[(j, p_col)]])
        for j2 in range(j + 1, m_z):
            formula.add_clause([-var_z[(j2, p_col)]])

    # Commutation: H_X * H_Z^T == 0 mod 2
    for i in range(m_x):
        for j in range(m_z):
            and_vars: list[int] = []
            for q in range(n):
                w = formula.new_var(f"w_{i}_{j}_{q}")
                xi = var_x[(i, q)]
                zj = var_z[(j, q)]
                formula.add_clause([-xi, -zj, w])
                formula.add_clause([xi, -w])
                formula.add_clause([zj, -w])
                and_vars.append(w)
            formula.add_xor(and_vars, target_parity=0)

    # Weight 1 and 2 X errors must produce non-zero syndrome in H_Z
    for q in range(n):
        formula.add_clause([var_z[(j, q)] for j in range(m_z)])
    for q1 in range(n):
        for q2 in range(q1 + 1, n):
            diff_vars = []
            for j in range(m_z):
                d = formula.new_var(f"diff_z_{j}_{q1}_{q2}")
                diff_vars.append(d)
                formula.add_xor([var_z[(j, q1)], var_z[(j, q2)], d], target_parity=0)
            formula.add_clause(diff_vars)

    # Weight 1 and 2 Z errors must produce non-zero syndrome in H_X
    for q in range(n):
        formula.add_clause([var_x[(i, q)] for i in range(m_x)])
    for q1 in range(n):
        for q2 in range(q1 + 1, n):
            diff_vars = []
            for i in range(m_x):
                d = formula.new_var(f"diff_x_{i}_{q1}_{q2}")
                diff_vars.append(d)
                formula.add_xor([var_x[(i, q1)], var_x[(i, q2)], d], target_parity=0)
            formula.add_clause(diff_vars)

    cls = list(formula.clauses)
    rng.shuffle(cls)
    shuffled_formula = CNFFormula(n_vars=formula.n_vars)
    shuffled_formula.clauses = cls

    sat_res = solve_cnf(shuffled_formula, timeout_seconds=timeout_seconds, solver_name=solver_name)
    elapsed = time.perf_counter() - t0

    stats: dict[str, Any] = {
        "seed": seed,
        "n": n,
        "k": 1,
        "target_d": 3,
        "status": sat_res.status,
        "solve_time_seconds": sat_res.solve_time_seconds,
        "wall_clock_seconds": elapsed,
        "verified": False,
        "code_distance": 0,
    }

    if not sat_res.is_sat or sat_res.model is None:
        return False, [], stats

    model_set = set(sat_res.model)
    gens: list[str] = []
    for i in range(m_x):
        chars = ["X" if var_x[(i, q)] in model_set else "I" for q in range(n)]
        gens.append("".join(chars))
    for j in range(m_z):
        chars = ["Z" if var_z[(j, q)] in model_set else "I" for q in range(n)]
        gens.append("".join(chars))

    ok_stab, stab_info = check_stabilizer(gens)
    ok_dist, dist_info = code_distance(gens)

    actual_d = dist_info.get("d", 0) if isinstance(dist_info, dict) else 0
    is_valid = ok_stab and ok_dist and (actual_d >= 3)

    stats["verified"] = is_valid
    stats["code_distance"] = actual_d
    stats["stabilizer_info"] = stab_info
    stats["distance_info"] = dist_info
    stats["generators"] = gens
    stats["sha256"] = hashlib.sha256(json.dumps(gens, sort_keys=True).encode()).hexdigest()

    return is_valid, gens, stats


def synthesize_shor_9_1_3(
    seed: int = 42,
    timeout_seconds: float = 30.0,
    solver_name: str = "cadical153",
) -> tuple[bool, list[str], dict[str, Any]]:
    """Synthesize Shor-class [[9, 1, 3]] non-circulant quantum stabilizer code blindly via SAT.

    Generates m = 8 commuting Pauli generators on 9 qubits with distance d >= 3.
    """
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)
    n = 9
    m = 8

    formula = CNFFormula()
    var_x: dict[tuple[int, int], int] = {}
    var_z: dict[tuple[int, int], int] = {}

    for i in range(m):
        for q in range(n):
            var_x[(i, q)] = formula.new_var(f"x_{i}_{q}")
            var_z[(i, q)] = formula.new_var(f"z_{i}_{q}")

    # Echelon pivots to guarantee rank m and break generator permutation symmetry
    pivot_cols = sorted(list(rng.choice(n, size=m, replace=False)))
    for i, p_col in enumerate(pivot_cols):
        formula.add_clause([var_x[(i, p_col)]])
        for j in range(i + 1, m):
            formula.add_clause([-var_x[(j, p_col)]])

    # Mutual symplectic commutativity between all pairs i < j:
    for i in range(m):
        for j in range(i + 1, m):
            xor_terms: list[int] = []
            for q in range(n):
                w = formula.new_var(f"w_{i}_{j}_{q}")
                u = formula.new_var(f"u_{i}_{j}_{q}")
                xi = var_x[(i, q)]
                zj = var_z[(j, q)]
                zi = var_z[(i, q)]
                xj = var_x[(j, q)]

                formula.add_clause([-xi, -zj, w])
                formula.add_clause([xi, -w])
                formula.add_clause([zj, -w])

                formula.add_clause([-zi, -xj, u])
                formula.add_clause([zi, -u])
                formula.add_clause([xj, -u])

                xor_terms.extend([w, u])
            formula.add_xor(xor_terms, target_parity=0)

    # Distance d >= 3: Every non-identity error of weight 1 and 2 must be detected
    errors: list[list[tuple[int, str]]] = []
    # Weight-1 errors
    for q in range(n):
        for p in ("X", "Z", "Y"):
            errors.append([(q, p)])
    # Weight-2 errors
    for q1 in range(n):
        for q2 in range(q1 + 1, n):
            for p1 in ("X", "Z", "Y"):
                for p2 in ("X", "Z", "Y"):
                    errors.append([(q1, p1), (q2, p2)])

    for err_idx, err in enumerate(errors):
        det_vars: list[int] = []
        for i in range(m):
            lits_for_err: list[int] = []
            for q, p in err:
                if p in ("X", "Y"):
                    lits_for_err.append(var_z[(i, q)])
                if p in ("Z", "Y"):
                    lits_for_err.append(var_x[(i, q)])
            det_var = formula.new_var(f"det_{i}_{err_idx}")
            det_vars.append(det_var)
            formula.add_xor(lits_for_err + [det_var], target_parity=0)
        formula.add_clause(det_vars)

    cls = list(formula.clauses)
    rng.shuffle(cls)
    shuffled_formula = CNFFormula(n_vars=formula.n_vars)
    shuffled_formula.clauses = cls

    sat_res = solve_cnf(shuffled_formula, timeout_seconds=timeout_seconds, solver_name=solver_name)
    elapsed = time.perf_counter() - t0

    stats: dict[str, Any] = {
        "seed": seed,
        "n": n,
        "k": 1,
        "target_d": 3,
        "num_vars": formula.n_vars,
        "num_clauses": len(formula.clauses),
        "status": sat_res.status,
        "solve_time_seconds": sat_res.solve_time_seconds,
        "wall_clock_seconds": elapsed,
        "verified": False,
        "code_distance": 0,
    }

    if not sat_res.is_sat or sat_res.model is None:
        return False, [], stats

    model_set = set(sat_res.model)
    gens = []
    for i in range(m):
        chars = []
        for q in range(n):
            x = var_x[(i, q)] in model_set
            z = var_z[(i, q)] in model_set
            if x and z:
                chars.append("Y")
            elif x:
                chars.append("X")
            elif z:
                chars.append("Z")
            else:
                chars.append("I")
        gens.append("".join(chars))

    # Independent oracle verification
    ok_stab, stab_info = check_stabilizer(gens)
    ok_dist, dist_info = code_distance(gens)

    actual_d = dist_info.get("d", 0) if isinstance(dist_info, dict) else 0
    is_valid = ok_stab and ok_dist and (actual_d >= 3)

    stats["verified"] = is_valid
    stats["code_distance"] = actual_d
    stats["stabilizer_info"] = stab_info
    stats["distance_info"] = dist_info
    stats["generators"] = gens
    stats["sha256"] = hashlib.sha256(json.dumps(gens, sort_keys=True).encode()).hexdigest()

    return is_valid, gens, stats


def run_p205_calibration_protocol(
    seeds: Sequence[int] = (42, 43, 44, 45, 46),
    timeout_per_trial: float = 30.0,
    solver_name: str = "cadical153",
) -> dict[str, Any]:
    """Execute the preregistered 5-seed blind calibration protocol across all 3 targets."""
    t_start = time.perf_counter()

    results: dict[str, Any] = {
        "protocol": "P205 Blind Calibration on Affine and Non-Circulant Targets",
        "seeds": list(seeds),
        "timeout_per_trial": timeout_per_trial,
        "solver_used": solver_name,
        "targets": {
            "covering_c9_3_2": {
                "name": "Affine Covering Design C(9, 3, 2) = 12 (AG(2, 3))",
                "trials_total": len(seeds),
                "successes": 0,
                "trials": [],
            },
            "steane_7_1_3": {
                "name": "Steane [[7, 1, 3]] CSS Quantum Code",
                "trials_total": len(seeds),
                "successes": 0,
                "trials": [],
            },
            "shor_9_1_3": {
                "name": "Shor-class [[9, 1, 3]] Non-Circulant Quantum Stabilizer Code",
                "trials_total": len(seeds),
                "successes": 0,
                "trials": [],
            },
        },
    }

    # Target 1: Affine Covering C(9, 3, 2) = 12
    for s in seeds:
        ok, blocks, stats = synthesize_affine_covering_c9_3_2(
            seed=s,
            timeout_seconds=timeout_per_trial,
            solver_name=solver_name,
        )
        if ok:
            results["targets"]["covering_c9_3_2"]["successes"] += 1
        results["targets"]["covering_c9_3_2"]["trials"].append(stats)

    # Target 2: Steane [[7, 1, 3]]
    for s in seeds:
        ok, gens, stats = synthesize_steane_7_1_3(
            seed=s,
            timeout_seconds=timeout_per_trial,
            solver_name=solver_name,
        )
        if ok:
            results["targets"]["steane_7_1_3"]["successes"] += 1
        results["targets"]["steane_7_1_3"]["trials"].append(stats)

    # Target 3: Shor [[9, 1, 3]]
    for s in seeds:
        ok, gens, stats = synthesize_shor_9_1_3(
            seed=s,
            timeout_seconds=timeout_per_trial,
            solver_name=solver_name,
        )
        if ok:
            results["targets"]["shor_9_1_3"]["successes"] += 1
        results["targets"]["shor_9_1_3"]["trials"].append(stats)

    total_time = time.perf_counter() - t_start
    results["total_wall_clock_seconds"] = total_time

    all_reproduced = (
        results["targets"]["covering_c9_3_2"]["successes"] == len(seeds)
        and results["targets"]["steane_7_1_3"]["successes"] == len(seeds)
        and results["targets"]["shor_9_1_3"]["successes"] == len(seeds)
    )

    results["verdict"] = "CALIBRATION_REPRODUCED" if all_reproduced else "CALIBRATION_FAILED"
    return results
