"""P164 guard tests: honest combinatorial baselines under paired wall-clock budgets."""

from __future__ import annotations

import numpy as np

from evobyte.combinatorial_baselines import (
    run_random_search,
    run_simulated_annealing,
    run_tabu_search,
)
from evobyte.target_catalogue import verify_vanderwaerden_coloring

TOY_BITS = 6


def _toy_score(candidate: np.ndarray) -> tuple[float, bool]:
    """Toy objective: minimize the number of set bits. Optimum is the all-zero vector."""
    ones = int(np.sum(candidate))
    return -float(ones), ones == 0


def _toy_init(rng: np.random.Generator) -> np.ndarray:
    return rng.integers(0, 2, size=TOY_BITS)


def _toy_neighbor(current: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    neighbor = current.copy()
    pos = int(rng.integers(0, len(neighbor)))
    neighbor[pos] = 1 - neighbor[pos]
    return neighbor


def test_random_search_respects_timeout():
    """With an objective that is never solved, the search must run to the deadline."""

    def unsolvable_score(candidate: np.ndarray) -> tuple[float, bool]:
        return float(np.sum(candidate)), False

    result = run_random_search(
        target_id="toy",
        sampler_fn=_toy_init,
        eval_fn=unsolvable_score,
        max_seconds=0.05,
        seed=7,
    )
    assert result.evaluations > 0
    assert result.elapsed_sec >= 0.05
    assert result.elapsed_sec < 0.05 * 3.0
    assert result.method == "RandomSearch"


def test_simulated_annealing_optimizes_simple_target():
    result = run_simulated_annealing(
        target_id="toy",
        init_fn=_toy_init,
        neighbor_fn=_toy_neighbor,
        eval_fn=_toy_score,
        max_seconds=1.0,
        seed=42,
    )
    assert result.evaluations > 0
    assert result.is_solution is True
    assert result.best_score == 0.0
    assert int(np.sum(result.best_candidate)) == 0


def test_tabu_search_avoids_immediate_reversal():
    """The tabu list must block an immediate reversal of the previous move.

    Scores are arranged so that the reversal is strictly better than the only
    admissible alternative, but still below the global best (no aspiration).
    """

    state0 = np.array([0])
    state1 = np.array([1])
    state2 = np.array([2])
    state3 = np.array([3])
    scores = {0: 0.9, 1: 1.0, 2: 0.5, 3: 0.7}
    visited_currents: list[int] = []
    iteration = {"n": 0}

    def init_fn(rng: np.random.Generator) -> np.ndarray:
        return state0.copy()

    def eval_fn(candidate: np.ndarray) -> tuple[float, bool]:
        return scores[int(candidate[0])], False

    def neighbors_fn(
        current: np.ndarray, rng: np.random.Generator, k: int
    ) -> list[tuple[np.ndarray, str]]:
        visited_currents.append(int(current[0]))
        iteration["n"] += 1
        if iteration["n"] == 1:
            return [(state1.copy(), "A"), (state2.copy(), "B")]
        return [(state0.copy(), "A"), (state3.copy(), "C")]

    result = run_tabu_search(
        target_id="toy",
        init_fn=init_fn,
        neighbors_fn=neighbors_fn,
        eval_fn=eval_fn,
        max_seconds=0.05,
        tabu_tenure=5,
        sample_neighbors=2,
        seed=3,
    )

    assert result.evaluations > 0
    # First step takes "A" (score 1.0) and puts it on the tabu list. On the next
    # step the reversal "A" (score 0.9) would win on score alone (0.9 > 0.7), but
    # it is tabu and does not beat the global best (1.0), so "C" must be chosen.
    assert visited_currents[0] == 0
    assert visited_currents[1] == 1
    assert visited_currents[2] == 3
    assert result.best_score == 1.0


def test_provenance_determinism():
    first = run_simulated_annealing(
        target_id="toy",
        init_fn=_toy_init,
        neighbor_fn=_toy_neighbor,
        eval_fn=_toy_score,
        max_seconds=1.0,
        seed=11,
    )
    second = run_simulated_annealing(
        target_id="toy",
        init_fn=_toy_init,
        neighbor_fn=_toy_neighbor,
        eval_fn=_toy_score,
        max_seconds=1.0,
        seed=11,
    )
    assert first.evaluations == second.evaluations
    assert first.best_score == second.best_score
    assert first.is_solution == second.is_solution
    assert first.seed == second.seed
    assert np.array_equal(np.asarray(first.best_candidate), np.asarray(second.best_candidate))


def test_local_counter_agrees_with_independent_oracle():
    """The benchmark's local violation counter must agree with the P163 oracle.

    A bitwise-AND bug in the local counter once reported zero violations for
    colorings that the independent oracle rejects, so the two are cross-checked.
    """
    from combinatorial_benchmark import count_mono_progression_aps

    rng = np.random.default_rng(0)
    for _ in range(50):
        n = int(rng.integers(5, 24))
        coloring = rng.integers(1, 4, size=n)
        local_violations = count_mono_progression_aps(coloring, 3)
        certified, _ = verify_vanderwaerden_coloring(coloring, 3, 3)
        assert (local_violations == 0) is certified
