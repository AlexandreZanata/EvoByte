"""Benchmark for SAT Solver Exact Completion Bridge (P194).

Measures:
1. Solving time and success rate for partial skeleton completion on C(7,3,2) and C(8,4,3).
2. Orbit-level exact completion on narrow-gap targets C(13,6,3), C(14,6,3), and C(15,8,4).
3. Solver backend comparison (CaDiCaL153 vs Glucose 4 vs Pure Python).
4. Quantum stabilizer generator synthesis latency.
5. Strict zero-dependency verification for all completed combinatorial structures.

Evidence over claims (Rule 3). All times measured via time.perf_counter().
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import time
from typing import Any

from evobyte.frontier_catalogue import verify_covering_design
from evobyte.narrow_gap_catalogue import _C_7_3_2_BLOCKS, _C_8_4_3_BLOCKS, _STEANE_GENERATORS
from evobyte.qecc_verifier import check_stabilizer
from evobyte.sat_bridge import (
    StabilizerCnfEncoder,
    complete_covering_orbits,
    complete_covering_skeleton,
)

try:
    import pysat

    _PYSAT_VERSION = pysat.__version__
except ImportError:
    _PYSAT_VERSION = None


def get_git_commit() -> str:
    """Retrieve the current HEAD git commit hash."""
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except Exception:
        return "unknown"


def run_benchmark(output_path: str | None = None) -> dict[str, Any]:
    commit_sha = get_git_commit()
    results: dict[str, Any] = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "commit": commit_sha,
        "hardware": {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "pysat_version": _PYSAT_VERSION,
        },
        "skeleton_completion": {},
        "orbit_completion": {},
        "solver_comparison": {},
        "stabilizer_synthesis": {},
        "summary": {
            "all_under_5_seconds": True,
            "all_verified": True,
        },
    }

    print("=" * 70)
    print("P194 SAT SOLVER EXACT COMPLETION BRIDGE BENCHMARK")
    print(f"Commit: {commit_sha} | Python: {platform.python_version()} | PySAT: {_PYSAT_VERSION}")
    print("=" * 70)

    # 1. Skeleton Completion: C(7, 3, 2) and C(8, 4, 3)
    print("\n1. SKELETON COMPLETION (Stochastic / Partial Skeleton -> SAT Completion)")
    print("-" * 70)

    # C(7, 3, 2)
    skel_c7 = list(_C_7_3_2_BLOCKS[:5])
    t0 = time.perf_counter()
    res_c7 = complete_covering_skeleton(
        skeleton=skel_c7,
        v=7,
        k=3,
        t=2,
        max_additional_blocks=2,
        timeout_seconds=5.0,
        solver_name="cadical153",
    )
    t_c7 = time.perf_counter() - t0

    c7_bytes = json.dumps(res_c7.completed_blocks, sort_keys=True).encode()
    c7_sha = hashlib.sha256(c7_bytes).hexdigest()

    results["skeleton_completion"]["C_7_3_2"] = {
        "target": "C(7,3,2)",
        "skeleton_blocks": len(skel_c7),
        "target_blocks": 7,
        "completed_blocks": res_c7.total_blocks,
        "added_blocks": len(res_c7.added_blocks or []),
        "uncovered_before": res_c7.uncovered_before,
        "uncovered_after": res_c7.uncovered_after,
        "status": res_c7.status,
        "verified": res_c7.verified,
        "solve_time_seconds": res_c7.solve_time_seconds,
        "wall_clock_seconds": t_c7,
        "sha256": c7_sha,
    }
    print(
        f"C(7,3,2): 5 -> {res_c7.total_blocks} blocks in {res_c7.solve_time_seconds * 1000:.3f} ms "
        f"(added: {res_c7.added_blocks}, verified: {res_c7.verified})"
    )

    # C(8, 4, 3)
    skel_c8 = list(_C_8_4_3_BLOCKS[:11])
    t0 = time.perf_counter()
    res_c8 = complete_covering_skeleton(
        skeleton=skel_c8,
        v=8,
        k=4,
        t=3,
        max_additional_blocks=3,
        timeout_seconds=5.0,
        solver_name="cadical153",
    )
    t_c8 = time.perf_counter() - t0

    c8_bytes = json.dumps(res_c8.completed_blocks, sort_keys=True).encode()
    c8_sha = hashlib.sha256(c8_bytes).hexdigest()

    results["skeleton_completion"]["C_8_4_3"] = {
        "target": "C(8,4,3)",
        "skeleton_blocks": len(skel_c8),
        "target_blocks": 14,
        "completed_blocks": res_c8.total_blocks,
        "added_blocks": len(res_c8.added_blocks or []),
        "uncovered_before": res_c8.uncovered_before,
        "uncovered_after": res_c8.uncovered_after,
        "status": res_c8.status,
        "verified": res_c8.verified,
        "solve_time_seconds": res_c8.solve_time_seconds,
        "wall_clock_seconds": t_c8,
        "sha256": c8_sha,
    }
    print(
        f"C(8,4,3): 11 -> {res_c8.total_blocks} blocks in {res_c8.solve_time_seconds * 1000:.3f} ms "
        f"(added: {len(res_c8.added_blocks or [])} blocks, verified: {res_c8.verified})"
    )

    # 2. Orbit-Level Completion for Narrow-Gap Targets
    print("\n2. NARROW-GAP ORBIT COMPLETION (Cyclic Group Automorphisms)")
    print("-" * 70)

    orbit_targets = [
        ("covering_C_13_6_3", 13, 6, 3, 2, "Z_13"),
        ("covering_C_14_6_3", 14, 6, 3, 2, "Z_14"),
        ("covering_C_15_8_4", 15, 8, 4, 2, "Z_15"),
    ]

    for target_id, v, k, t, max_orbits, group_name in orbit_targets:
        t0 = time.perf_counter()
        orb_res = complete_covering_orbits(
            fixed_base_blocks=[],
            v=v,
            k=k,
            t=t,
            max_additional_orbits=max_orbits,
            timeout_seconds=5.0,
            solver_name="cadical153",
        )
        orb_wall = time.perf_counter() - t0

        orb_bytes = json.dumps(orb_res.completed_blocks, sort_keys=True).encode()
        orb_sha = hashlib.sha256(orb_bytes).hexdigest()

        results["orbit_completion"][target_id] = {
            "target_id": target_id,
            "v": v,
            "k": k,
            "t": t,
            "symmetry_group": group_name,
            "base_orbits_selected": max_orbits,
            "total_blocks": orb_res.total_blocks,
            "uncovered_before": orb_res.uncovered_before,
            "uncovered_after": orb_res.uncovered_after,
            "status": orb_res.status,
            "verified": orb_res.verified,
            "solve_time_seconds": orb_res.solve_time_seconds,
            "wall_clock_seconds": orb_wall,
            "sha256": orb_sha,
        }
        print(
            f"{target_id} ({group_name}): {max_orbits} orbits -> {orb_res.total_blocks} blocks "
            f"in {orb_res.solve_time_seconds * 1000:.2f} ms (verified: {orb_res.verified})"
        )

    # 3. Solver Comparison across Backends
    print("\n3. SOLVER BACKEND COMPARISON (CaDiCaL153 vs Glucose 4 vs Pure Python)")
    print("-" * 70)

    solvers_to_test = ["cadical153", "g4", "pure_python"]
    for slv_name in solvers_to_test:
        t0 = time.perf_counter()
        s_res = complete_covering_skeleton(
            skeleton=skel_c7,
            v=7,
            k=3,
            t=2,
            max_additional_blocks=2,
            timeout_seconds=5.0,
            solver_name=slv_name,
        )
        t_el = time.perf_counter() - t0
        results["solver_comparison"][slv_name] = {
            "solver": slv_name,
            "solve_time_seconds": s_res.solve_time_seconds,
            "wall_clock_seconds": t_el,
            "verified": s_res.verified,
            "total_blocks": s_res.total_blocks,
        }
        print(
            f"Solver {slv_name:12s}: {s_res.solve_time_seconds * 1000:7.3f} ms "
            f"(verified: {s_res.verified}, blocks: {s_res.total_blocks})"
        )

    # 4. Stabilizer Generator Commutativity Synthesis
    print("\n4. QUANTUM STABILIZER GENERATOR SYNTHESIS (Steane [[7,1,3]])")
    print("-" * 70)

    fixed_steane = list(_STEANE_GENERATORS[:4])
    stab_encoder = StabilizerCnfEncoder(n_qubits=7, fixed_generators=fixed_steane)
    t0 = time.perf_counter()
    stab_ok, stab_gen, stab_sat = stab_encoder.synthesize_single_generator(
        timeout_seconds=5.0,
        solver_name="cadical153",
        min_weight=3,
    )
    t_stab = time.perf_counter() - t0

    all_gens = fixed_steane + ([stab_gen] if stab_gen else [])
    ok_stab, stab_verif = check_stabilizer(all_gens)

    results["stabilizer_synthesis"]["steane_partial"] = {
        "fixed_generators": len(fixed_steane),
        "synthesized_generator": stab_gen,
        "success": stab_ok,
        "verified_commuting": ok_stab,
        "verification_result": stab_verif,
        "solve_time_seconds": stab_sat.solve_time_seconds,
        "wall_clock_seconds": t_stab,
    }
    print(
        f"Synthesized generator: {stab_gen} in {stab_sat.solve_time_seconds * 1000:.2f} ms "
        f"(commuting: {ok_stab}, rank: {stab_verif.get('rank') if isinstance(stab_verif, dict) else 'fail'})"
    )

    # Verification summary
    all_ok = True
    for sec in ["skeleton_completion", "orbit_completion"]:
        for item in results[sec].values():
            if not item.get("verified", False) or item.get("solve_time_seconds", 999.0) >= 5.0:
                all_ok = False

    results["summary"]["all_under_5_seconds"] = all_ok
    results["summary"]["all_verified"] = all_ok

    print("\n" + "=" * 70)
    print(f"VERDICT: All solutions verified: {all_ok} | All runtimes < 5.0s: {all_ok}")
    print("=" * 70)

    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with out_p.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, sort_keys=True)
        print(f"Saved benchmark results to {out_p}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run SAT solver completion benchmark")
    parser.add_argument(
        "--output",
        type=str,
        default="docs/research/benchmarks/p194_sat_bridge_results.json",
        help="Path to output JSON results",
    )
    args = parser.parse_args()
    run_benchmark(output_path=args.output)
