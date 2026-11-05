"""Hardware probe: record provenance for every performance claim. Skips GPU gracefully."""

from __future__ import annotations

import contextlib
import json
import platform
import subprocess
from collections.abc import Generator
from typing import Any


def get_vram_telemetry(device_idx: int = 0) -> dict[str, Any]:
    """Retrieve real-time VRAM allocation and reserved memory telemetry."""
    telemetry: dict[str, Any] = {
        "cuda_available": False,
        "device_name": "none",
        "allocated_mb": 0.0,
        "reserved_mb": 0.0,
        "max_allocated_mb": 0.0,
        "max_reserved_mb": 0.0,
        "free_mb": 0.0,
        "total_mb": 0.0,
    }
    try:
        import torch

        if torch.cuda.is_available() and device_idx < torch.cuda.device_count():
            telemetry["cuda_available"] = True
            telemetry["device_name"] = torch.cuda.get_device_name(device_idx)
            telemetry["allocated_mb"] = round(
                torch.cuda.memory_allocated(device_idx) / (1024 * 1024), 2
            )
            telemetry["reserved_mb"] = round(
                torch.cuda.memory_reserved(device_idx) / (1024 * 1024), 2
            )
            telemetry["max_allocated_mb"] = round(
                torch.cuda.max_memory_allocated(device_idx) / (1024 * 1024), 2
            )
            telemetry["max_reserved_mb"] = round(
                torch.cuda.max_memory_reserved(device_idx) / (1024 * 1024), 2
            )
            try:
                free_b, tot_b = torch.cuda.mem_get_info(device_idx)
                telemetry["free_mb"] = round(free_b / (1024 * 1024), 2)
                telemetry["total_mb"] = round(tot_b / (1024 * 1024), 2)
            except (RuntimeError, OSError):
                pass
    except (ImportError, RuntimeError, OSError):
        pass
    return telemetry


@contextlib.contextmanager
def measure_vram_peak(device_idx: int = 0) -> Generator[dict[str, Any], None, None]:
    """Context manager tracking peak VRAM consumption during an active benchmark block."""
    result: dict[str, Any] = {
        "start_allocated_mb": 0.0,
        "peak_allocated_mb": 0.0,
        "delta_allocated_mb": 0.0,
        "peak_reserved_mb": 0.0,
    }
    try:
        import torch

        if torch.cuda.is_available() and device_idx < torch.cuda.device_count():
            torch.cuda.reset_peak_memory_stats(device_idx)
            start_alloc = torch.cuda.memory_allocated(device_idx) / (1024 * 1024)
            result["start_allocated_mb"] = round(start_alloc, 2)
            yield result
            peak_alloc = torch.cuda.max_memory_allocated(device_idx) / (1024 * 1024)
            peak_res = torch.cuda.max_memory_reserved(device_idx) / (1024 * 1024)
            result["peak_allocated_mb"] = round(peak_alloc, 2)
            result["delta_allocated_mb"] = round(max(0.0, peak_alloc - start_alloc), 2)
            result["peak_reserved_mb"] = round(peak_res, 2)
            return
    except (ImportError, RuntimeError, OSError):
        pass
    yield result


def probe() -> dict[str, Any]:
    """Inspect full hardware and runtime environment with provenance verification."""
    info: dict[str, Any] = {
        "cpu": platform.processor() or platform.machine(),
        "os": f"{platform.system()} {platform.release()}",
        "python": platform.python_version(),
    }
    try:
        import numpy

        info["numpy"] = numpy.__version__
    except ImportError:
        info["numpy"] = "missing"
    try:
        import torch  # type: ignore

        info["torch"] = getattr(torch, "__version__", "unknown")
        cuda_ver = getattr(getattr(torch, "version", None), "cuda", None)
        if cuda_ver is not None:
            info["cuda_version"] = cuda_ver
        is_avail = False
        with contextlib.suppress(RuntimeError, OSError):
            is_avail = bool(torch.cuda.is_available())
        info["cuda_available"] = is_avail
        if is_avail:
            for i in range(torch.cuda.device_count()):
                p = torch.cuda.get_device_properties(i)
                info[f"gpu{i}"] = {
                    "name": p.name,
                    "total_memory_MB": p.total_memory // (1024 * 1024),
                    "compute_capability": f"{p.major}.{p.minor}",
                    "multi_processor_count": getattr(p, "multi_processor_count", None),
                }
            info["vram_telemetry"] = get_vram_telemetry(0)
        else:
            info["gpu"] = "none (CPU-only machine)"
    except ImportError:
        info["torch"] = "missing"
    with contextlib.suppress(FileNotFoundError, subprocess.SubprocessError):
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if out.returncode == 0 and out.stdout.strip():
            info["nvidia_smi"] = out.stdout.strip()
    return info


def check_hardware_integrity(
    expected_gpu_substr: str | None = None,
    min_vram_mb: int | None = None,
) -> tuple[bool, list[str]]:
    """Verify hardware integrity and driver readiness for P153 benchmark harness."""
    findings: list[str] = []
    p = probe()

    if p.get("torch") == "missing":
        findings.append("MISSING_TORCH: PyTorch is not installed in the benchmark environment")

    if expected_gpu_substr:
        cuda_ok = p.get("cuda_available", False)
        if not cuda_ok:
            findings.append(
                f"CUDA_UNAVAILABLE: expected GPU with '{expected_gpu_substr}' but CUDA is unavailable"
            )
        else:
            gpu_found = False
            for k, v in p.items():
                if k.startswith("gpu") and isinstance(v, dict):
                    name = v.get("name", "")
                    if expected_gpu_substr.lower() in name.lower():
                        gpu_found = True
                        if min_vram_mb and v.get("total_memory_MB", 0) < min_vram_mb:
                            findings.append(
                                f"INSUFFICIENT_VRAM: {name} has {v.get('total_memory_MB')}MB < min {min_vram_mb}MB"
                            )
            if not gpu_found:
                findings.append(
                    f"GPU_MISMATCH: expected substring '{expected_gpu_substr}' not found in probed GPUs"
                )

    return len(findings) == 0, findings


if __name__ == "__main__":
    print(json.dumps(probe(), indent=2))
