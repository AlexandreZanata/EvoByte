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
from typing import Any

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


def verify_manifest_integrity(path: str | Path) -> dict:
    """Reverify a checksummed manifest: seal hash plus every raw artifact hash.

    Raw paths are resolved against the repo root when relative. Returns a
    finding dict; ``ok`` is True only when the seal and all raw hashes match.
    """
    result: dict = {"manifest": str(path), "ok": False, "errors": [], "raw": []}
    try:
        with open(path, encoding="utf-8") as f:
            stored = json.load(f)
    except (OSError, ValueError) as exc:
        result["errors"].append(f"unreadable_manifest: {exc}")
        return result
    recorded = stored.get("manifest_sha256")
    if not recorded:
        result["errors"].append("missing_manifest_sha256")
        return result
    recomputed = hashlib.sha256(
        json.dumps(
            {k: v for k, v in stored.items() if k != "manifest_sha256"},
            sort_keys=True,
            default=str,
        ).encode()
    ).hexdigest()
    seal_ok = recomputed == recorded
    result["seal_ok"] = seal_ok
    if not seal_ok:
        result["errors"].append("manifest_seal_mismatch")
    for entry in stored.get("raw_artifacts", []):
        ref = entry.get("path", "")
        want = entry.get("sha256", "")
        cand = Path(ref)
        if not cand.is_absolute():
            cand = _REPO_ROOT / ref
        item: dict = {"path": ref, "ok": False, "size": 0}
        if not cand.exists():
            item["error"] = "missing_raw_file"
        else:
            try:
                got = hash_file(cand)
            except OSError as exc:
                item["error"] = f"unreadable_raw_file: {exc}"
            else:
                item["size"] = cand.stat().st_size
                item["sha256"] = got
                if got == want:
                    item["ok"] = True
                else:
                    item["error"] = "raw_hash_mismatch"
        if not item["ok"] and "error" in item:
            result["errors"].append(f"{ref}: {item['error']}")
        result["raw"].append(item)
    result["ok"] = seal_ok and all(r["ok"] for r in result["raw"])
    return result


def _refuse_nonempty(path: Path, label: str) -> None:
    """Refuse to overwrite a non-empty historical destination (P41 immutability)."""
    if path.exists() and path.stat().st_size > 0:
        raise FileExistsError(
            f"Refusing to overwrite non-empty {label} {path}; "
            "use a fresh exclusive run directory instead of replacing sealed evidence."
        )


def write_manifest_exclusive(path: str | Path, manifest: dict, raw_blobs: dict[str, bytes]) -> dict:
    """Seal-first writer: config and raw artifacts land before the manifest.

    Refuses every non-empty destination (manifest or raw); records durable
    references with size and SHA-256 in ``raw_inventory``. Never repairs an
    old hash by replacing its evidence.
    """
    out_p = Path(path)
    _refuse_nonempty(out_p, "manifest")
    for ref in raw_blobs:
        _refuse_nonempty(Path(ref), "raw artifact")
    inventory = []
    hashes = {}
    for ref, blob in raw_blobs.items():
        raw_p = Path(ref)
        raw_p.parent.mkdir(parents=True, exist_ok=True)
        with open(raw_p, "wb") as f:
            f.write(blob)
        digest = hashlib.sha256(bytes(blob)).hexdigest()
        inventory.append({"path": ref, "size_bytes": len(blob), "sha256": digest})
        hashes[ref] = digest
    sealed = dict(manifest)
    sealed["raw_inventory"] = inventory
    return write_manifest(out_p, sealed, hashes)


def parse_budget_duration(budget_str: str) -> float:
    """Parse budget string like '10s', '1m', '10m', '1h', '30' into float seconds."""
    s = str(budget_str).strip().lower()
    if s.endswith("s"):
        return float(s[:-1])
    if s.endswith("m"):
        return float(s[:-1]) * 60.0
    if s.endswith("h"):
        return float(s[:-1]) * 3600.0
    return float(s)


def query_gpu_telemetry(device: torch.device | None = None) -> dict[str, Any]:
    """Query live GPU telemetry (temperature, clocks, power, utilization, VRAM)."""
    telemetry: dict[str, Any] = {
        "temperature_c": None,
        "graphics_clock_mhz": None,
        "power_draw_w": None,
        "power_limit_w": None,
        "gpu_utilization_pct": None,
        "vram_used_mb": None,
        "vram_total_mb": None,
        "telemetry_available": False,
    }
    if not torch.cuda.is_available():
        return telemetry

    dev = device if device is not None else torch.device("cuda:0")
    if dev.type != "cuda":
        return telemetry

    try:
        res = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=temperature.gpu,clocks.current.graphics,power.draw,power.limit,utilization.gpu,memory.used,memory.total",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            parts = [p.strip() for p in res.stdout.strip().split(",")]
            if len(parts) >= 7:
                telemetry["temperature_c"] = float(parts[0]) if parts[0] != "[N/A]" else None
                telemetry["graphics_clock_mhz"] = float(parts[1]) if parts[1] != "[N/A]" else None
                telemetry["power_draw_w"] = float(parts[2]) if parts[2] != "[N/A]" else None
                telemetry["power_limit_w"] = float(parts[3]) if parts[3] != "[N/A]" else None
                telemetry["gpu_utilization_pct"] = float(parts[4]) if parts[4] != "[N/A]" else None
                telemetry["vram_used_mb"] = float(parts[5]) if parts[5] != "[N/A]" else None
                telemetry["vram_total_mb"] = float(parts[6]) if parts[6] != "[N/A]" else None
                telemetry["telemetry_available"] = True
    except (OSError, subprocess.SubprocessError, ValueError):
        pass

    try:
        telemetry["torch_vram_allocated_mb"] = float(
            torch.cuda.memory_allocated(dev) / (1024 * 1024)
        )
        telemetry["torch_vram_reserved_mb"] = float(torch.cuda.memory_reserved(dev) / (1024 * 1024))
        telemetry["torch_max_vram_allocated_mb"] = float(
            torch.cuda.max_memory_allocated(dev) / (1024 * 1024)
        )
    except (RuntimeError, AssertionError, TypeError, AttributeError):
        pass

    return telemetry
