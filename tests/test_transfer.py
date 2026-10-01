"""P22 cross-task transfer helpers (disjoint families, learned prior).

Covers the pure, fast parts of the P22 protocol: family split disjointness
by structure, dataset hashes, opcode-distribution normalization, and sampled
program validity. The full billed experiment runs via the phase exit gate.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))

from p12_generator_ab import (
    P22_PREREG,
    p22_build_opcode_distribution,
    p22_family_function,
    p22_family_splits,
    p22_sample_from_opcode_dist,
)

from evobyte.bytecode import is_valid


def test_p22_families_split_by_structure():
    fams = p22_family_splits()
    assert set(fams) == {"quad", "cubic", "sinlin"}
    structs = {fams[k]["family"] for k in fams}
    assert structs == {"quad", "cubic", "sinlin"}  # disjoint by structure
    # Preregistration matches the implemented split.
    assert set(P22_PREREG["train_families"]) == {"quad"}
    assert set(P22_PREREG["val_families"]) == {"cubic"}
    assert set(P22_PREREG["test_families"]) == {"sinlin"}


def test_p22_family_values_and_hashes():
    fams = p22_family_splits()
    x = np.array([0.0, 1.0, 2.0], dtype=np.float32)
    assert np.allclose(p22_family_function("quad", x), [7.0, 11.0, 17.0])
    assert np.allclose(p22_family_function("cubic", x), [1.0, 0.0, 5.0])
    assert np.allclose(p22_family_function("sinlin", x), np.sin(x) + 2.0 * x + 1.0)
    for spec in fams.values():
        for split in ("train", "hidden", "extrapolation"):
            xs, ys = spec[split]
            assert len(xs) == 64 and len(ys) == 64
            assert np.all(np.isfinite(ys))
        assert len(spec["sha16"]) == 16
    # Train vs held-out hashes differ (distinct datasets).
    assert fams["quad"]["sha16"] != fams["cubic"]["sha16"]
    assert fams["quad"]["sha16"] != fams["sinlin"]["sha16"]


def test_p22_opcode_distribution_is_prior():
    rng = np.random.default_rng(0)
    from evobyte.evolution import sample_structured

    elites = [sample_structured(rng) for _ in range(8)]
    probs = p22_build_opcode_distribution(elites)
    assert probs.shape == (16,)
    assert abs(float(probs.sum()) - 1.0) < 1e-12
    assert bool((probs > 0).all())  # Laplace smoothing: no zero mass


def test_p22_sampled_programs_valid():
    rng = np.random.default_rng(1)
    from evobyte.evolution import sample_structured

    elites = [sample_structured(rng) for _ in range(8)]
    probs = p22_build_opcode_distribution(elites)
    pop = p22_sample_from_opcode_dist(rng, probs, 16)
    assert pop.shape[0] == 16
    assert all(is_valid(p) for p in pop)
