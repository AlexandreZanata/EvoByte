"""Smoke: determinism + imports (P00 gate)."""

import numpy as np


def test_numpy_deterministic_seed():
    a = np.random.default_rng(123).integers(0, 100, size=10)
    b = np.random.default_rng(123).integers(0, 100, size=10)
    np.testing.assert_array_equal(a, b)


def test_package_imports():
    import evobyte

    assert evobyte.OPCODE_VERSION == 0
