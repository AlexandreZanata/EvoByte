# Reproducibility

**Status:** decision (integrity gate).

Every run records:

- random seed(s);
- git commit SHA;
- config file hash + full resolved config;
- GPU model, VRAM, driver, CUDA/torch versions (`make hw-probe` output);
- dataset hash (SHA-256 of bytes actually evaluated);
- `OPCODE_VERSION`;
- population params (N, cascade cutoffs, operator rates, island topology).

An experiment must be reconstructible from `(commit, config, seed,
dataset hash)` under the numerical and timing contract below. Datasets are generated, never hand-edited; generation
scripts and seeds are versioned.

Checkpoints contain everything needed to resume: RNG state, generation,
full population, fitted constants, archive state, best fitness. Resume must reproduce the
non-resumed trajectory for the same seed (tested in P07).

`OPCODE_VERSION` bumps on any bytecode change; the old interpreter is kept
so old archives remain decodable.

## Expanded acceptance contract (P15–P21)

Record full code revision and clean/dirty status (dirty runs are diagnostic,
not final claims), dependencies and baseline versions, CPU/thread settings,
OS, actual device, seed states for NumPy and PyTorch CPU/CUDA, full resolved
configuration/hash, population/distribution and counters at every stage.
Hash every split, generator configuration and actual input/target bytes;
keep hidden content inaccessible to search. Record workload precision,
program length/opcodes, constants and all relevant verifier thresholds.

Store synchronized elapsed time, warmup/compile/setup cost, deadline/overshoot,
failures, early exits, distinct/repeated candidates and thermal/power/VRAM
telemetry when available. Missing measurements are null with a reason.
A manifest records exact commands, raw artifact checksums and a durable
location; a prose table or ignored local output alone is insufficient.

Fixed-step seeded trajectories must reproduce on the pinned software and
hardware stack; fixed-time runs may complete different step counts and must
be compared statistically. Numerical tolerance and expected timing variation
are preregistered. Checkpoints require full population, constants, counters,
all RNG states and archive state needed to resume, not a population sample.

Freeze winners using train/validation before final hidden scoring. Never
feed hidden errors back into evolution or hyperparameter selection. Repeat
hidden tests only for documented verification of the frozen artifact.
P21 publishes a clean-environment reproduction and a predictor that includes
bytecode, constants/linear head, schema, domain and opcode version.
