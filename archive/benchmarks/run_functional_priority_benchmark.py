"""Benchmark for Functional Priority Bytecode Engine (P193).

Measures:
1. Construction throughput (complete constructions / second) on CPU and GPU.
2. Convergence latency for Cap Set calibration rediscovery: n=3 (|C|=9) and n=4 (|C|=20).
3. Covering design orbit priority synthesis rate.

Mandatory: Evidence over claims (Rule 3). All numbers are measured using time.perf_counter().
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import time

from evobyte.functional_priority import (
    CapSetPrioritySearch,
    CoveringOrbitPriorityBuilder,
    measure_priority_throughput,
)

try:
    import torch

    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False


def run_benchmark(n_iterations: int = 50000, output_path: str | None = None) -> dict:
    results: dict = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "hardware": {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "torch_available": _TORCH_AVAILABLE,
            "cuda_available": torch.cuda.is_available() if _TORCH_AVAILABLE else False,
            "gpu_name": torch.cuda.get_device_name(0)
            if _TORCH_AVAILABLE and torch.cuda.is_available()
            else None,
        },
        "throughput": {},
        "rediscovery": {},
        "covering_orbits": {},
    }

    # 1. Throughput measurements
    print("=" * 60)
    print("1. MEASURING THROUGHPUT (Complete Constructions / Sec)")
    print("=" * 60)

    t_n3_cpu = measure_priority_throughput(n=3, n_iterations=n_iterations, use_torch=False)
    results["throughput"]["n3_cpu"] = t_n3_cpu
    print(f"Cap Set n=3 CPU bitmask: {t_n3_cpu['constructions_per_sec']:,.1f} constr/s")

    t_n4_cpu = measure_priority_throughput(n=4, n_iterations=n_iterations, use_torch=False)
    results["throughput"]["n4_cpu"] = t_n4_cpu
    print(f"Cap Set n=4 CPU bitmask: {t_n4_cpu['constructions_per_sec']:,.1f} constr/s")

    if _TORCH_AVAILABLE and torch.cuda.is_available():
        t_n3_gpu = measure_priority_throughput(n=3, n_iterations=n_iterations, use_torch=True)
        results["throughput"]["n3_gpu"] = t_n3_gpu
        print(f"Cap Set n=3 GPU Tensor:  {t_n3_gpu['constructions_per_sec']:,.1f} constr/s")

        t_n4_gpu = measure_priority_throughput(n=4, n_iterations=n_iterations, use_torch=True)
        results["throughput"]["n4_gpu"] = t_n4_gpu
        print(f"Cap Set n=4 GPU Tensor:  {t_n4_gpu['constructions_per_sec']:,.1f} constr/s")

    # 2. Rediscovery calibration
    print("\n" + "=" * 60)
    print("2. REDISCOVERY CALIBRATION (Cap Set n=3 and n=4)")
    print("=" * 60)

    searcher_n3 = CapSetPrioritySearch(n=3, seed=42)
    res_n3 = searcher_n3.search(target_size=9, max_seconds=10.0)
    results["rediscovery"]["n3"] = {
        "target_size": res_n3["target_size"],
        "best_size": res_n3["best_size"],
        "discovered": res_n3["discovered"],
        "evaluations": res_n3["evaluations"],
        "elapsed_sec": res_n3["elapsed_sec"],
        "certified": res_n3["certified"],
        "sha256": res_n3["sha256"],
    }
    print(
        f"n=3: Discovered size {res_n3['best_size']} in {res_n3['elapsed_sec']:.4f}s "
        f"({res_n3['evaluations']} evals, certified: {res_n3['certified']})"
    )

    searcher_n4 = CapSetPrioritySearch(n=4, seed=42)
    res_n4 = searcher_n4.search(target_size=20, max_seconds=10.0)
    results["rediscovery"]["n4"] = {
        "target_size": res_n4["target_size"],
        "best_size": res_n4["best_size"],
        "discovered": res_n4["discovered"],
        "evaluations": res_n4["evaluations"],
        "elapsed_sec": res_n4["elapsed_sec"],
        "certified": res_n4["certified"],
        "sha256": res_n4["sha256"],
    }
    print(
        f"n=4: Discovered size {res_n4['best_size']} in {res_n4['elapsed_sec']:.4f}s "
        f"({res_n4['evaluations']} evals, certified: {res_n4['certified']})"
    )

    # 3. Covering Design orbit priority synthesis
    print("\n" + "=" * 60)
    print("3. COVERING ORBIT SYNTHESIS (C(10, 3, 2))")
    print("=" * 60)

    covering_builder = CoveringOrbitPriorityBuilder(v=10, k=3, t=2)
    t0 = time.perf_counter()
    import numpy as np

    rng = np.random.default_rng(42)
    scores = rng.standard_normal(len(covering_builder.base_blocks))
    blocks = covering_builder.build_covering(scores, one_based=True)
    t_cov = time.perf_counter() - t0

    results["covering_orbits"]["C_10_3_2"] = {
        "v": 10,
        "k": 3,
        "t": 2,
        "base_blocks_count": len(covering_builder.base_blocks),
        "selected_blocks_count": len(blocks),
        "elapsed_sec": t_cov,
    }
    print(
        f"C(10, 3, 2): selected {len(blocks)} blocks from {len(covering_builder.base_blocks)} "
        f"orbit base blocks in {t_cov * 1000:.3f}ms"
    )

    # Gate verification
    throughput_n3_ok = results["throughput"]["n3_cpu"]["constructions_per_sec"] >= 50000.0
    throughput_n4_ok = results["throughput"]["n4_cpu"]["constructions_per_sec"] >= 50000.0
    rediscovery_n3_ok = res_n3["discovered"] and res_n3["elapsed_sec"] < 10.0
    rediscovery_n4_ok = res_n4["discovered"] and res_n4["elapsed_sec"] < 10.0

    all_gates_pass = (
        throughput_n3_ok and throughput_n4_ok and rediscovery_n3_ok and rediscovery_n4_ok
    )
    results["all_gates_pass"] = all_gates_pass

    print("\n" + "=" * 60)
    print(f"ALL P193 GATES PASS: {all_gates_pass}")
    print("=" * 60)

    if output_path:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"Results written to: {out_file}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run P193 Functional Priority Benchmark")
    parser.add_argument("--iterations", type=int, default=50000, help="Number of iterations")
    parser.add_argument("--output", type=str, default=None, help="Output JSON path")
    args = parser.parse_args()

    run_benchmark(n_iterations=args.iterations, output_path=args.output)
