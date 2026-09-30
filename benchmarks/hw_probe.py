"""Hardware probe: record provenance for every performance claim. Skips GPU gracefully."""

from __future__ import annotations

import contextlib
import json
import platform
import subprocess


def probe() -> dict:
    info: dict = {
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
                }
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


if __name__ == "__main__":
    print(json.dumps(probe(), indent=2))
