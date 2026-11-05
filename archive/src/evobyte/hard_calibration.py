"""Hard Historical Records Calibration Protocol (P195).

Implements blind calibration on two historically challenging combinatorial milestones:
1. Hard QECC: Blind rediscovery of Gottesman [[8, 3, 3]] stabilizer code.
2. Hard Covering Design: Exact rediscovery of optimal C(10, 4, 3) = 30 blocks (Mills 1979 / SQS(10)).

Both targets are approached strictly 'blind' without any injection of published
solution matrices or blocks.

Part of the Structured Discovery and Functional Synthesis Program (P191-P200, D043).
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
from evobyte.symmetry_engine import CoveringOrbitEngine


def synthesize_stabilizer_8_3_3(
    seed: int = 42,
    timeout_seconds: float = 300.0,
    solver_name: str = "auto",
) -> tuple[bool, list[str], dict[str, Any]]:
    """Synthesize Gottesman [[8, 3, 3]] stabilizer code blindly via exact SAT constraints.

    Generates m = n - k = 5 commuting Pauli generators on 8 qubits with distance d >= 3.
    Enforces detection of all 276 Pauli errors of weight 1 and 2.
    """
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)
    n = 8
    m = 5  # 5 generators for [[8, 3, 3]]

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
    # sum_q (x_{i, q} * z_{j, q} + z_{i, q} * x_{j, q}) == 0 mod 2
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

    # Distance d >= 3: Every error of weight 1 and 2 must fail to commute with >= 1 generator
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

    # Shuffle clause trail based on pseudo-random seed
    cls = list(formula.clauses)
    rng.shuffle(cls)
    shuffled_formula = CNFFormula(n_vars=formula.n_vars)
    shuffled_formula.clauses = cls

    sat_res = solve_cnf(shuffled_formula, timeout_seconds=timeout_seconds, solver_name=solver_name)
    elapsed = time.perf_counter() - t0

    stats: dict[str, Any] = {
        "seed": seed,
        "n": n,
        "k": 3,
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

    m_set = set(sat_res.model)
    gens: list[str] = []
    for i in range(m):
        chars: list[str] = []
        for q in range(n):
            x = var_x[(i, q)] in m_set
            z = var_z[(i, q)] in m_set
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


def solve_hard_covering_c10_4_3(
    seed: int = 42,
    timeout_seconds: float = 300.0,
    solver_name: str = "auto",
) -> tuple[bool, list[list[int]], dict[str, Any]]:
    """Solve optimal covering design C(10, 4, 3) = 30 blindly via Z_10 cyclic orbit SAT.

    Parameters: v=10, k=4, t=3. Total triples = comb(10, 3) = 120.
    Optimal bound: b = 30 blocks (Steiner Quadruple System SQS(10) / Mills 1979).
    """
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)
    v, k, t = 10, 4, 3
    engine = CoveringOrbitEngine(v=v, k=k, t=t)
    reps = engine.compute_orbit_representatives()
    all_subsets = list(itertools.combinations(range(v), t))

    orbit_subsets: list[set[tuple[int, ...]]] = []
    for rep in reps:
        cov: set[tuple[int, ...]] = set()
        for blk in engine.group.orbit(rep):
            for sub in itertools.combinations(blk, t):
                cov.add(tuple(sorted(sub)))
        orbit_subsets.append(cov)

    formula = CNFFormula(n_vars=len(reps))
    for sub in all_subsets:
        formula.add_clause([i + 1 for i, cov in enumerate(orbit_subsets) if sub in cov])

    # Exactly 3 base blocks -> 30 expanded blocks
    formula.add_at_most_k(list(range(1, len(reps) + 1)), 3)

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
        "target_blocks": 30,
        "num_orbits": len(reps),
        "status": sat_res.status,
        "solve_time_seconds": sat_res.solve_time_seconds,
        "wall_clock_seconds": elapsed,
        "verified": False,
        "total_blocks": 0,
    }

    if not sat_res.is_sat or sat_res.model is None:
        return False, [], stats

    model_set = set(sat_res.model)
    chosen_reps = [reps[i] for i in range(len(reps)) if (i + 1) in model_set]
    full_blocks = engine.expand_base_blocks(chosen_reps, one_indexed=True)

    verified, v_msg = verify_covering_design(full_blocks, v, k, t)
    is_valid = verified and (len(full_blocks) <= 30)

    stats["verified"] = is_valid
    stats["verification_msg"] = v_msg
    stats["total_blocks"] = len(full_blocks)
    stats["base_orbits"] = [list(r) for r in chosen_reps]
    stats["sha256"] = hashlib.sha256(json.dumps(full_blocks, sort_keys=True).encode()).hexdigest()

    return is_valid, full_blocks, stats


def run_hard_calibration_protocol(
    seeds: Sequence[int] | None = None,
    timeout_per_trial: float = 300.0,
    solver_name: str = "auto",
) -> dict[str, Any]:
    """Execute the preregistered 5-seed hard calibration protocol across both targets."""
    if seeds is None:
        seeds = [42, 43, 44, 45, 46]

    results: dict[str, Any] = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "seeds": list(seeds),
        "timeout_per_trial_sec": timeout_per_trial,
        "solver_used": solver_name,
        "targets": {
            "qecc_8_3_3": {
                "name": "Gottesman [[8, 3, 3]]",
                "trials": [],
                "successes": 0,
                "trials_total": len(seeds),
            },
            "covering_c10_4_3": {
                "name": "C(10, 4, 3) = 30 (SQS(10))",
                "trials": [],
                "successes": 0,
                "trials_total": len(seeds),
            },
        },
        "verdict": "FAIL",
    }

    # 1. QECC [[8, 3, 3]]
    for seed in seeds:
        ok, gens, st = synthesize_stabilizer_8_3_3(
            seed=seed,
            timeout_seconds=timeout_per_trial,
            solver_name=solver_name,
        )
        results["targets"]["qecc_8_3_3"]["trials"].append(st)
        if ok:
            results["targets"]["qecc_8_3_3"]["successes"] += 1

    # 2. Covering Design C(10, 4, 3) = 30
    for seed in seeds:
        ok, blocks, st = solve_hard_covering_c10_4_3(
            seed=seed,
            timeout_seconds=timeout_per_trial,
            solver_name=solver_name,
        )
        results["targets"]["covering_c10_4_3"]["trials"].append(st)
        if ok:
            results["targets"]["covering_c10_4_3"]["successes"] += 1

    succ_qecc = results["targets"]["qecc_8_3_3"]["successes"]
    succ_cov = results["targets"]["covering_c10_4_3"]["successes"]

    # Falsifiable condition: at least 3 of 5 seeds succeed on both targets
    if succ_qecc >= 3 and succ_cov >= 3:
        results["verdict"] = "CALIBRATION_PASSED"
    else:
        results["verdict"] = "CALIBRATION_FAILED"

    return results
