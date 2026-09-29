# Evolution: selection, diversity, islands, autoevolution

**Status:** decision.

## Generation zero (order matters)

Start dumb, add smarts only with measurement:

- **A — pure random:** uniform bytes + S0 validity filter.
- **B — structured random:** opcode-aware sampling (fewer invalids).
- **C — genetic:** tournament selection + point mutation + crossover.
- **D — quality diversity:** MAP-Elites / novelty on top of C.

A neural generator (P12) is tested only after A–D baselines exist, so we
know whether it adds anything.

## Operators (v0 rates, tuned in P08)

- Point mutation per byte: `p = 0.02`; large (block) mutation: `p = 0.05`.
- Crossover (single-point over 16 slots): `p = 0.3`.
- Random injection: **>= 10% of every generation is pure random**, always.
  100% elite-derived populations are forbidden.
- Elitism: top-K copied verbatim (K = 64 in v0).

## Elite archive (never only "one best")

Keep best by: fitness, size class, structure hash, behavior cluster, math
family, novelty. Concepts used: MAP-Elites grid (size x behavior bins, implemented
in `evobyte.diversity.MapElitesGrid`), novelty search (k-NN behavioral distance on
normalized prediction vectors, implemented in `evobyte.diversity.NoveltyArchive`),
island models.

Each elite row records:

```text
generation, opcode_version, candidate_binary, decoded_expression,
fitness, train_error, validation_error, test_error (L2 only),
complexity, parents, mutation_history, timestamp, sha256, novelty_score
```

Archive lives on host (implemented in `evobyte.archive.EliteArchive` via SQLite),
checkpoints every N generations with atomic swap, resumable with 100% bitwise equivalence.
VRAM holds only the working population.

## Islands

v0: 4 islands with distinct pressures (small-size, high-mutation,
low-mutation, high-novelty, implemented in `evobyte.islands.IslandModel`).
Ring migration of top-4 every M generations (M=5 in P10). Single-population
control retains stronger unified selection pressure on simple targets, while
islands accelerate escape on difficult seeds.

## Controls (explicit, logged)

`random_p, large_mut_p, crossover_p, random_inject_p, elite_k,
novelty_w, migration_interval`. Every experiment logs all of them plus seed,
commit, dataset hash, and opcode version (see REPRODUCIBILITY).
