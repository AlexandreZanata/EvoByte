"""Provenance-first timing helpers (CVPS support)."""

from __future__ import annotations

import hashlib
import time


def sha256_of_floats(xs) -> str:
    """Stable dataset hash for run records."""
    import numpy as np

    arr = np.asarray(xs, dtype=np.float32)
    return hashlib.sha256(arr.tobytes()).hexdigest()[:16]


class Stopwatch:
    def __init__(self) -> None:
        self._t0 = time.perf_counter()
        self.count = 0

    def add(self, n: int = 1) -> None:
        self.count += n

    def rate(self) -> float:
        dt = max(time.perf_counter() - self._t0, 1e-9)
        return self.count / dt
