# P16 — Population-parallel GPU interpreter

**Status:** Proposed.
**Prerequisite:** P15.
**Owner:** assigned when moving to Building; see the phase index.

## Objective

Make the population dimension genuinely parallel while retaining the v0
CPU oracle and protected-math semantics. Establish where launch overhead,
memory traffic and opcode divergence limit the RTX 4060 Laptop.

## Scope and ordered work

- Profile the current implementation with P15 timing; preserve its measured
  baseline before changing it. Record CPU dispatch and CUDA kernel activity.
- Remove Python loops over candidates, tensor-to-CPU decoding and repeated
  allocations from population execution. A bounded loop over instruction
  slots is acceptable; population bytecode and input data stay on device.
- Start with vectorized PyTorch and reusable buffers. Evaluate interpreter
  compilation/fusion only when the profile justifies it; Triton/CUDA needs
  measured benefit and conformance evidence. Never compile each candidate.
- Compare arithmetic-only and the full opcode set at 32/256/4096 points and
  increasing batch sizes under measured VRAM limits. Record active program
  lengths and opcode distributions so trivial/NOP-heavy workloads are clear.
- Test population-level parity, malformed operands, NaN/Inf, domain edges,
  constants and mixed-opcode programs against the CPU oracle. Preserve
  opcode version; any semantic change needs an ADR and a new version.

VM execution and its profiling harness only; no evolution rewrite or new
opcode semantics. Optimized code is adopted only for supported workloads.

## Exit gate

The phase-specific CLI below is an acceptance interface to implement during
this phase, not a claim that the current checkout supports it. Common checks
already exist. Run the experiment only after its prerequisite is green.

```bash
git diff --check
python3 -m pytest tests -q
make verify
python3 benchmarks/cvps.py --grid --provenance --device cuda --output experiments/p16-vm.json
```

A reproducible CPU/current-GPU/new-GPU comparison includes synchronized
timings, peak allocated/reserved VRAM, launch counts and conformance results.
The optimized path must improve representative nontrivial throughput with
no correctness regression. A negative experiment is recorded but does not
unlock P17; choose the next isolated optimization based on the profile.

## Risks

Gather/scatter, divergent opcodes, register pressure and protected math
can erase gains. A fast single-op microbenchmark is not a population result.

## Commit & Push (mandatory)

Start from a clean tree on `codex/p16-population-gpu-vm`. Follow the common
commit procedure in [README.md](README.md#commit-and-push-contract), using
this phase's exact reviewed file list and artifact manifest. One completed
micro-task produces one atomic commit; never commit a failed gate.

```bash
git status --short
git diff --check
git diff --cached --check
git commit -m "perf(vm): complete p16 population-gpu-vm"
git push -u origin HEAD
gh pr create --title "perf(vm): complete p16 population-gpu-vm" --body-file /tmp/evobyte-p16-pr.md
git status --short
```
