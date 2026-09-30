"""Measurement-integrity helpers: seeding, strict devices, deadlines, counters, provenance (P15)."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import torch

_REPO_ROOT = Path(__file__).resolve().parents[2]


def seed_all(seed: int) -> None:
    """Seed NumPy and all PyTorch CPU/CUDA RNGs deterministically."""
    np.random.seed(seed % (2**32))
    torch.manual_seed(seed % (2**32))
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed % (2**32))


def resolve_device(requested: str | None) -> torch.device:
    """Resolve a compute device strictly: CUDA requests fail if CUDA is unavailable."""
    if requested is None:
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dev = torch.device(requested)
    if dev.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA device requested but torch.cuda.is_available() is False; "
            "refusing to silently report CPU as GPU (P15 integrity gate)."
        )
    return dev


def synchronize(device: torch.device) -> None:
    """Block until all GPU work on device completes (no-op on CPU)."""
    if device.type == "cuda" and torch.cuda.is_available():
        torch.cuda.synchronize()


def get_git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
            cwd=_REPO_ROOT,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return "unknown"


def get_git_status() -> str:
    try:
        out = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
            cwd=_REPO_ROOT,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return "unknown"


def hash_bytes(*blobs: bytes) -> str:
    h = hashlib.sha256()
    for b in blobs:
        h.update(np.ascontiguousarray(np.frombuffer(b, dtype=np.uint8)).tobytes())
    return h.hexdigest()


def hash_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class MonotonicDeadline:
    """Monotonic wall-clock deadline for one method/target/seed/budget cell."""

    budget_sec: float
    t_start: float = field(default_factory=time.monotonic)
    t_setup_end: float | None = None
    t_warmup_end: float | None = None
    t_compute_end: float | None = None
    t_end: float | None = None

    def mark_setup_done(self) -> None:
        self.t_setup_end = time.monotonic()

    def mark_warmup_done(self) -> None:
        self.t_warmup_end = time.monotonic()

    def mark_compute_done(self) -> None:
        self.t_compute_end = time.monotonic()

    def expired(self) -> bool:
        return (time.monotonic() - self.t_start) >= self.budget_sec

    def remaining(self) -> float:
        return max(0.0, self.budget_sec - (time.monotonic() - self.t_start))

    def finish(self) -> dict:
        self.t_end = time.monotonic()
        elapsed = self.t_end - self.t_start
        overshoot = max(0.0, elapsed - self.budget_sec)
        setup = (self.t_setup_end - self.t_start) if self.t_setup_end else 0.0
        warmup = 0.0
        if self.t_warmup_end and self.t_setup_end:
            warmup = self.t_warmup_end - self.t_setup_end
        elif self.t_warmup_end:
            warmup = self.t_warmup_end - self.t_start
        compute = 0.0
        c0 = self.t_warmup_end or self.t_setup_end or self.t_start
        c1 = self.t_compute_end or self.t_end
        if c1 and c0:
            compute = c1 - c0
        verification = 0.0
        if self.t_compute_end and self.t_end:
            verification = self.t_end - self.t_compute_end
        return {
            "budget_sec": self.budget_sec,
            "elapsed_sec": elapsed,
            "overshoot_sec": overshoot,
            "setup_sec": setup,
            "warmup_sec": warmup,
            "compute_sec": compute,
            "verification_sec": verification,
        }


class CandidateCounter:
    """Bounded-memory distinct/repeat candidate counting (P15).

    Method: exact hash set of program bytes up to `max_tracked` entries.
    Beyond the cap, new hashes are counted as repeats with `truncated=True`
    so memory stays bounded while totals remain exact. Distinct counts are
    exact while `truncated` is False, otherwise they are a lower bound.
    """

    def __init__(self, max_tracked: int = 200_000) -> None:
        self.max_tracked = max_tracked
        self._seen: set[bytes] = set()
        self.total = 0
        self.repeats = 0
        self.truncated = False

    def add(self, program: np.ndarray) -> bool:
        key = np.ascontiguousarray(program, dtype=np.uint32).tobytes()
        self.total += 1
        if key in self._seen:
            self.repeats += 1
            return False
        if len(self._seen) >= self.max_tracked:
            self.truncated = True
            self.repeats += 1
            return False
        self._seen.add(key)
        return True

    def add_many(self, programs: np.ndarray) -> None:
        for p in programs:
            self.add(p)

    @property
    def distinct(self) -> int:
        return len(self._seen)

    def summary(self) -> dict:
        return {
            "method": "exact-hash-set-bounded",
            "max_tracked": self.max_tracked,
            "total": self.total,
            "distinct": self.distinct,
            "repeats": self.repeats,
            "truncated": self.truncated,
        }


def collect_provenance(
    *,
    seed: int,
    device: torch.device,
    dataset_hashes: dict | None = None,
    config: dict | None = None,
) -> dict:
    """Build the REPRODUCIBILITY.md provenance record for one run."""
    try:
        import numpy as _np

        numpy_ver = _np.__version__
    except ImportError:
        numpy_ver = "missing"
    hw: dict = {
        "cpu": platform.processor() or platform.machine(),
        "os": f"{platform.system()} {platform.release()}",
        "python": platform.python_version(),
        "numpy": numpy_ver,
        "torch": getattr(torch, "__version__", "unknown"),
        "cuda_version": getattr(getattr(torch, "version", None), "cuda", None),
        "cuda_available": bool(torch.cuda.is_available()),
        "threads_torch": torch.get_num_threads(),
        "threads_omp": os.environ.get("OMP_NUM_THREADS"),
    }
    if torch.cuda.is_available():
        try:
            hw["gpu"] = torch.cuda.get_device_name(0)
            hw["gpu_mem_MB"] = torch.cuda.get_device_properties(0).total_memory // (1024 * 1024)
        except (RuntimeError, ValueError, OSError) as exc:  # pragma: no cover - hardware dependent
            hw["gpu_error"] = str(exc)
    try:
        nvidia = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if nvidia.returncode == 0 and nvidia.stdout.strip():
            hw["nvidia_smi"] = nvidia.stdout.strip()
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    record = {
        "commit": get_git_commit(),
        "git_status": get_git_status(),
        "clean_tree": get_git_status() == "",
        "seed_numpy": seed,
        "seed_torch_cpu": seed % (2**32),
        "seed_torch_cuda": seed % (2**32),
        "device_requested": str(device),
        "device_actual": str(device),
        "hardware": hw,
        "dataset_hashes": dataset_hashes or {},
        "config": config or {},
    }
    if config is not None:
        blob = json.dumps(config, sort_keys=True, default=str).encode()
        record["config_hash"] = hashlib.sha256(blob).hexdigest()[:16]
    try:
        from evobyte import OPCODE_VERSION

        record["opcode_version"] = OPCODE_VERSION
    except (ImportError, AttributeError):
        record["opcode_version"] = None
    record["python_argv"] = sys.argv[:]
    return record


def write_manifest(path: str | Path, manifest: dict, raw_artifacts: dict[str, str]) -> dict:
    """Write a checksummed artifact manifest; raw artifacts referenced by path+sha256."""
    checksummed = dict(manifest)
    checksummed["raw_artifacts"] = [
        {"path": k, "sha256": v} for k, v in sorted(raw_artifacts.items())
    ]
    blob = json.dumps(checksummed, sort_keys=True, default=str).encode()
    checksummed["manifest_sha256"] = hashlib.sha256(blob).hexdigest()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(checksummed, f, indent=2, sort_keys=True, default=str)
    return checksummed
