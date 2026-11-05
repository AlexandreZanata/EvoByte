# Dashboard and Hall of Fame

**Status:** decision (minimal first).

## Live view (post-MVP, cheap)

Terminal/file dashboard updated per generation:

```text
generation, candidates_total, candidates_per_sec, verified_per_sec (CVPS),
best_fitness, best_expression, avg_complexity, diversity,
gpu_util, vram_used/total
```

No web service before P13. Logs are append-only JSONL; rendering is a
separate offline script.

## Hall of Fame (persistent, curated)

File-backed (`hall_of_fame/fame.jsonl` — small, committed; generated
copies stay local). One entry per promotion:

```text
rank, fitness, expression, generation, discovered_after_N_candidates,
train/val/hidden/extrapolation errors, complexity, parents, hash
```

Example:

```text
#1 fitness=0.00031 expr=((x*x)+(3*x)+7) gen=1832 after=1.83B
#2 ...
```

Memorizers (poor hidden/extrapolation) are ineligible even with good train
fitness (gated by `is_memorizer` and `write_hall_of_fame_entry` in `evobyte.archive`).
Every entry links its reproduction command (commit + config + seed).
