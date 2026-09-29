# P05 — GPU interpreter + CVPS benchmark

**Status:** Proposed.
**Goal:** first trusted **CVPS** number with conformance proof.

## Objective

Port execution to PyTorch tensor ops (data + population resident in VRAM),
prove bitwise/1e-6 equivalence with the P02 oracle on the conformance corpus,
then measure CVPS across (N programs x batch) grid on the reference GPU.

## Scope

In: `src/evobyte/vm_torch.py` (or torch path in `vm.py`), conformance test
CPU-vs-GPU, `benchmarks/cvps.py` harness with provenance header.
Out: custom Triton/CUDA kernels (only if PyTorch bottlenecks — then a new
task with Nsight/cProfile evidence).

## Tasks

1. `feat(vm): add PyTorch batched interpreter (VRAM-resident)`.
2. `test(vm): assert CPU-vs-GPU conformance on oracle corpus`.
3. `feat(bench): add CVPS harness with hardware+seed+hash provenance`.

## Exit gate

```bash
git diff --check
python3 -m pytest tests/test_vm_torch.py -q
python3 benchmarks/cvps.py --grid --provenance
```

Artifact: CVPS table + conformance log (commit + GPU + driver in PR body).
No kernel work without a measured bottleneck.

## Risks

- Sync-per-candidate or copy-per-step — profile; keep tensors resident.

## Commit & Push (mandatory for this phase)

```bash
git status --short
git add src/evobyte/vm_torch.py tests/test_vm_torch.py benchmarks/cvps.py docs/STACK.md docs/METRICS.md docs/phases/P05-gpu-interpreter.md
git commit -m "feat(vm): add GPU interpreter and CVPS harness"
git push -u origin phase-05-gpu-interpreter
gh pr create --title "feat(vm): add GPU interpreter and CVPS harness" --body "P05 exit gate green. Closes #<issue>."
```
