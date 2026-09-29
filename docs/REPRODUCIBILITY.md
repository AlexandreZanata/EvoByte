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

An experiment must be exactly repeatable from `(commit, config, seed,
dataset hash)`. Datasets are generated, never hand-edited; generation
scripts and seeds are versioned.

Checkpoints contain everything needed to resume: RNG state, generation,
population sample, archive pointer, best fitness. Resume must reproduce the
non-resumed trajectory for the same seed (tested in P07).

`OPCODE_VERSION` bumps on any bytecode change; the old interpreter is kept
so old archives remain decodable.
