# Experiments

Per-experiment configs and logs. Large artifacts (`runs/`, `checkpoints/`,
datasets) are git-ignored — only configs, scripts, and summary tables are
committed.

Convention per experiment `experiments/<phase>_<slug>/`:

- `config.yaml` — full resolved config (seeds, budget, N, cutoffs, rates).
- `run.sh` — exact reproduction command.
- `RESULTS.md` — table with commit SHA + dataset hash + hardware.
- `fame.jsonl` — promoted elites only (small).

Hidden-test data never lives here in plaintext before L2 promotion.
