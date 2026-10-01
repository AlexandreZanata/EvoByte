# GPU access runbook (reference hardware: RTX 4060 Laptop, 8 GB VRAM)

**Status:** generic agent instructions. No machine-specific data lives in
this file on purpose — exact driver versions, paths, and measured numbers
belong to each machine's local copy (see `.local/GPU_THIS_MACHINE.md`,
git-ignored, never pushed). Read this before any GPU benchmark or GPU-gated
phase (P05+). Follow the steps in order, copy-paste the commands.

## What "access" means here

The reference machine carries a discrete NVIDIA GPU (RTX 4060 Laptop class,
8 GB VRAM) alongside an integrated GPU. All EvoByte GPU work goes through
PyTorch CUDA tensors (`vm_torch.py`, `benchmarks/cvps.py`). This runbook
proves, step by step, that an agent on a fresh checkout can reach the card.

## Step-by-step access (in order, stop at first red step)

### Step 0 — driver alive?

```bash
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
```

Expected: one NVIDIA GPU line with ~8 GB total. If you see `Unknown Error`
or `No devices were found`, the discrete GPU is probably runtime-suspended
(power saving on notebooks) — this is transient. Wake it and retry:

```bash
sleep 2; nvidia-smi
```

`nvidia-smi` itself wakes the card. Do NOT reboot, reinstall drivers, or
change graphics modes on a red Step 0 — retry twice, record your machine's
details in `.local/GPU_THIS_MACHINE.md`, then escalate to the user.

### Step 1 — graphics mode sane? (hybrid notebooks only)

Check your distro's GPU switcher and confirm the discrete GPU is enabled
(e.g. `system76-power graphics` on Pop!_OS should print `nvidia` or
`hybrid`; Ubuntu uses `prime-select query`). If the mode is
integrated-only, the card is disabled by policy: **stop and ask the user** —
switching modes requires logout and is never done autonomously.

### Step 2 — device nodes and kernel modules present?

```bash
ls /dev/nvidia* && lsmod | grep -E "^nvidia "
```

Expected: `/dev/nvidia0`, `/dev/nvidiactl`, `/dev/nvidia-uvm`, plus loaded
`nvidia`, `nvidia_modeset`, `nvidia_drm`, `nvidia_uvm` modules. Missing nodes
with a green Step 0 means a driver/user-space mismatch — escalate, do not
`modprobe` blindly more than once (`sudo modprobe nvidia nvidia_uvm` is the
single safe retry).

### Step 3 — PyTorch sees CUDA?

```bash
python3 -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

Expected: a `+cuXXX` torch build, `True`, and the RTX 4060 device name. If
`False`: the environment likely has a CPU-only torch or you are using the
wrong interpreter — use the repo's virtualenv/pyenv python (the one that
installed `.[dev]`), never the system python. Reinstall only the pinned
torch line, then re-run this step.

### Step 4 — repo GPU path green?

```bash
python3 -m pytest tests/test_vm_torch.py -q
python3 benchmarks/cvps.py --provenance --device cuda
```

Both must pass, and the provenance header must name the GPU, the commit,
the seed, and the dataset hash. Paste that header into any PR claiming a
GPU number, and record the measured numbers in your local
`.local/GPU_THIS_MACHINE.md` — never invent them.

## Troubleshooting matrix

| Symptom | Likely cause | Action |
|---|---|---|
| `nvidia-smi`: `Unknown Error`, then works on retry | dGPU was runtime-suspended | normal on notebooks; retry, no fix needed |
| `nvidia-smi`: persistent `No devices were found` | graphics mode or driver | check Step 1; escalate, do not reinstall |
| `torch.cuda.is_available()` is `False` | CPU torch or env mismatch | verify a `+cuXXX` build under the repo python |
| `CUDA out of memory` in a benchmark | budget exceeded | shrink the P x B grid (P06 policy: chunk + stay within the VRAM budget) |
| Another PID holds VRAM (`nvidia-smi` shows processes) | shared machine | note it in the run record; do NOT kill other users' processes |

## Rules for agents

- GPU numbers without the `--provenance` header are rumors, not measurements.
- Machine-specific facts (paths, versions, temperatures, PIDs, measured
  throughput) go in `.local/GPU_THIS_MACHINE.md` — git-ignored, never
  committed, never pushed.
- Never switch graphics modes, never reboot, never reinstall the driver
  without explicit user confirmation.
- A red Step 0–2 after two retries means: stop the phase, report the step
  output, keep working on CPU-only tasks.
- CPU remains the correctness oracle (`tests/test_vm.py`); GPU must match it
  before any throughput claim (P05 conformance rule, always in force).
