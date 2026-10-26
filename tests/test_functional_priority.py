"""Unit tests for Functional Priority Bytecode Engine (P193).

Verifies:
1. Vectorized bytecode evaluation and parity with scalar reference.
2. Fast greedy Cap Set constructor bitmask correctness and certificate validation.
3. Deterministic rediscovery of Cap Set n=3 (|C|=9) and n=4 (|C|=20) in < 10 seconds.
4. Construction throughput exceeding 50,000 complete constructions/second.
5. Integration with Covering Design orbit base blocks.
"""

from __future__ import annotations

import numpy as np
import pytest

from evobyte.bytecode import encode_instr, nop_program
from evobyte.constructive import evaluate_priority
from evobyte.frontier_catalogue import verify_cap_set
from evobyte.functional_priority import (
    CapSetPrioritySearch,
    CoveringOrbitPriorityBuilder,
    FastGreedyCapSetBuilder,
    FunctionalPriorityEvaluator,
    compute_capset_features,
    measure_priority_throughput,
)
from evobyte.narrow_gap_catalogue import verify_covering_design

try:
    import torch

    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False


def test_evaluator_vectorized_parity():
    """Vectorized evaluator matches scalar evaluate_priority across all candidate points."""
    evaluator = FunctionalPriorityEvaluator()
    rng = np.random.default_rng(1234)

    prog = nop_program()
    prog[0] = encode_instr(0x01, dst=2, a=0, b=1)  # r2 = r0 + r1
    prog[1] = encode_instr(0x03, dst=7, a=2, b=2)  # r7 = r2 * r2

    features = rng.uniform(-2.0, 2.0, size=(27, 7)).astype(np.float32)
    ctx = np.zeros(16, dtype=np.float32)

    vec_scores = evaluator.evaluate_vectorized(prog, features, ctx)
    assert vec_scores.shape == (27,)

    for i in range(27):
        scalar_score = evaluate_priority(prog, features[i], ctx)
        assert np.isclose(vec_scores[i], scalar_score, rtol=1e-5, atol=1e-5)


def test_evaluator_malformed_inputs():
    """Evaluator handles malformed programs and empty features gracefully without raising."""
    evaluator = FunctionalPriorityEvaluator()
    scores = evaluator.evaluate_vectorized(np.zeros(5, dtype=np.uint32), np.zeros((10, 4)))
    assert scores.shape == (10,)
    assert (scores == -np.inf).all()


def test_fast_greedy_capset_builder_n3_validity():
    """Cap sets built for n=3 are always valid cap sets (no collinear triples)."""
    builder = FastGreedyCapSetBuilder(n=3)
    rng = np.random.default_rng(42)

    for _ in range(20):
        scores = rng.standard_normal(27)
        pts = builder.build_cap_points(scores)
        is_valid, msg = verify_cap_set(pts, 3)
        assert is_valid, f"Invalid cap set in n=3: {msg}"
        assert len(pts) <= 9


def test_fast_greedy_capset_builder_n4_validity():
    """Cap sets built for n=4 are always valid cap sets (no collinear triples)."""
    builder = FastGreedyCapSetBuilder(n=4)
    rng = np.random.default_rng(999)

    for _ in range(20):
        scores = rng.standard_normal(81)
        pts = builder.build_cap_points(scores)
        is_valid, msg = verify_cap_set(pts, 4)
        assert is_valid, f"Invalid cap set in n=4: {msg}"
        assert len(pts) <= 20


def test_capset_rediscovery_n3():
    """Deterministic rediscovery of n=3 (|C|=9) in less than 10 seconds."""
    searcher = CapSetPrioritySearch(n=3, seed=42)
    result = searcher.search(target_size=9, max_seconds=10.0)

    assert result["discovered"], "Failed to discover cap set of size 9 in n=3"
    assert result["best_size"] == 9
    assert result["elapsed_sec"] < 10.0
    assert result["certified"], f"Cap set not certified: {result['certification_msg']}"
    assert len(result["sha256"]) == 64


def test_capset_rediscovery_n4():
    """Deterministic rediscovery of n=4 (|C|=20) in less than 10 seconds."""
    searcher = CapSetPrioritySearch(n=4, seed=42)
    result = searcher.search(target_size=20, max_seconds=10.0)

    assert result["discovered"], "Failed to discover cap set of size 20 in n=4"
    assert result["best_size"] == 20
    assert result["elapsed_sec"] < 10.0
    assert result["certified"], f"Cap set not certified: {result['certification_msg']}"
    assert len(result["sha256"]) == 64


def test_throughput_gate_n3():
    """Throughput of greedy constructions exceeds 50,000 constructions/second for n=3."""
    res = measure_priority_throughput(n=3, n_iterations=50000, use_torch=False)
    rate = res["constructions_per_sec"]
    assert rate >= 50000.0, f"Throughput gate failed for n=3: {rate:.1f} < 50000 constructions/sec"


def test_throughput_gate_n4():
    """Throughput of greedy constructions exceeds 50,000 constructions/second for n=4."""
    res = measure_priority_throughput(n=4, n_iterations=50000, use_torch=False)
    rate = res["constructions_per_sec"]
    assert rate >= 50000.0, f"Throughput gate failed for n=4: {rate:.1f} < 50000 constructions/sec"


@pytest.mark.skipif(
    not _TORCH_AVAILABLE or not (torch.cuda.is_available() if _TORCH_AVAILABLE else False),
    reason="CUDA required for GPU batched throughput test",
)
def test_gpu_throughput_gate_n3():
    """GPU batched throughput exceeds 50,000 constructions/second."""
    res = measure_priority_throughput(n=3, n_iterations=50000, use_torch=True)
    rate = res["constructions_per_sec"]
    assert rate >= 50000.0, (
        f"GPU throughput gate failed for n=3: {rate:.1f} < 50000 constructions/sec"
    )


def test_covering_orbit_priority_builder():
    """Covering orbit priority builder produces valid covering designs for C(8, 3, 2)."""
    builder = CoveringOrbitPriorityBuilder(v=8, k=3, t=2)
    rng = np.random.default_rng(101)
    scores = rng.standard_normal(len(builder.base_blocks))

    blocks = builder.build_covering(scores, one_based=True)
    assert len(blocks) > 0

    is_valid, msg = verify_covering_design(blocks=blocks, v=8, k=3, t=2)
    assert is_valid, f"Invalid covering design: {msg}"
