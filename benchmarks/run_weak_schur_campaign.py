"""Preregistered weak-Schur symmetric campaign (P177).

For each (target, attempt size = best_known_value + 1, algorithm, seed, mode):
search under a dual budget (time OR evaluations). Any valid partition of the
attempt size is submitted to the P171 independent verifier immediately;
a certificate records DISCOVERY_BEATEN with object + SHA-256. Incremental JSON
checkpoint after every trial; --resume skips completed ones.

Symmetric mode (cyclic_shift_period_p) restricts proposals to p-periodic
colorings (color[i] = pat[(i-1) mod p]); free mode does not restrict. This is
a declared search bias, not a theorem -- and for fixed p it is refuted at
these m (any p-periodic coloring of {1..m}, m >= 3p, contains p,2p,3p in one
color class). The report states this explicitly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evobyte.frontier_catalogue import verify_weak_schur_partition  # noqa: E402


# --------------------------------------------------------------------------
# Pure helpers (importable by tests; no search here).
# --------------------------------------------------------------------------

def break_size(best_known_value: int) -> int:
    """Record-attempt size: exactly best_known_value + 1 (no goalpost moves)."""
    return int(best_known_value) + 1


def trial_key(target_id: str, attempt_size: int, algorithm: str, seed: int, mode: str) -> str:
    return f"{target_id}|m{int(attempt_size)}|{algorithm}|seed{int(seed)}|{mode}"


def verdict_for_target(best_known_value: int, certificates: list[dict]) -> str:
    """DISCOVERY_BEATEN iff a certificate covers more than best_known_value."""
    for cert in certificates:
        try:
            if int(cert.get("size", -1)) > int(best_known_value):
                return "DISCOVERY_BEATEN"
        except Exception:
            continue
    return "NULL_RESULT"


def is_p_periodic(coloring: list[int], p: int) -> bool:
    """Check color[i] == color[i mod p] (0-based) for the whole coloring."""
    return all(c == coloring[i % p] for i, c in enumerate(coloring))


def random_coloring(m: int, k: int, rng) -> list[int]:
    return [int(x) + 1 for x in rng.integers(0, k, size=m)]


def random_symmetric_coloring(m: int, k: int, p: int, rng) -> list[int]:
    """Uniform p-periodic coloring: free pattern of length p, tiled to m."""
    pat = [int(x) + 1 for x in rng.integers(0, k, size=p)]
    return [pat[i % p] for i in range(m)]


def canonical_partition_sha(coloring: list[int]) -> str:
    return hashlib.sha256(",".join(str(c) for c in coloring).encode()).hexdigest()


def load_checkpoint(path: Path) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return {"completed": {}}


def save_checkpoint(path: Path, state: dict) -> None:
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(json.dumps(state, indent=1), encoding="utf-8")
    tmp.replace(path)


# --------------------------------------------------------------------------
# Search state with incremental violation deltas: 1 eval = 1 delta.
# --------------------------------------------------------------------------

class WeakSchurState:
    """Coloring of {1..m} into k classes; incremental weak-violation count.

    A violation is a distinct pair x < y with x + y = z <= m, all same color
    (x + x = 2x allowed: weak rule). `viol` counts such triples.
    """

    def __init__(self, coloring: list[int], k: int) -> None:
        self.color = list(coloring)
        self.k = int(k)
        self.m = len(coloring)
        self.viol = self._full_count()

    def _full_count(self) -> int:
        color = self.color
        m = self.m
        n = 0
        # For each y as middle element: x in 1..y-1 with same color and z=x+y same color.
        for y in range(2, m + 1):
            cy = color[y - 1]
            # x as the smaller addend
            for x in range(1, y):
                if color[x - 1] != cy:
                    continue
                z = x + y
                if z <= m and color[z - 1] == cy:
                    n += 1
        return n

    def delta_recolor(self, pos0: int, new_c: int) -> int:
        """Net violation change of setting color[pos0] = new_c (no mutation)."""
        color = self.color
        m = self.m
        v = pos0 + 1
        old_c = color[pos0]
        if old_c == new_c:
            return 0
        destroyed = 0
        # triples where v plays a role, currently all old_c
        for x in range(1, v):
            if color[x - 1] != old_c:
                continue
            z = x + v
            if z <= m and color[z - 1] == old_c:  # (x, v, z), x < v
                destroyed += 1
            if 2 * x == v:  # (x, x, v) not counted (needs x < y); skip
                pass
        for y in range(v + 1, m + 1):
            if color[y - 1] != old_c:
                continue
            z = v + y
            if z <= m and color[z - 1] == old_c:  # (v, y, z), v < y
                destroyed += 1
        for x in range(1, v // 2 + 1):
            y2 = v - x
            if y2 > x and color[y2 - 1] == old_c and color[x - 1] == old_c:  # (x, y2, v)
                destroyed += 1
        created = 0
        for x in range(1, v):
            if color[x - 1] != new_c:
                continue
            z = x + v
            if z <= m and color[z - 1] == new_c:
                created += 1
        for y in range(v + 1, m + 1):
            if color[y - 1] != new_c:
                continue
            z = v + y
            if z <= m and color[z - 1] == new_c:
                created += 1
        for x in range(1, v // 2 + 1):
            y2 = v - x
            if y2 > x and color[y2 - 1] == new_c and color[x - 1] == new_c:
                created += 1
        return created - destroyed

    def apply_recolor(self, pos0: int, new_c: int, delta: int) -> None:
        self.color[pos0] = new_c
        self.viol += delta


def _certify(coloring: list[int], k: int) -> tuple[bool, str]:
    return verify_weak_schur_partition(list(coloring), int(k))


def _symmetric_positions(m: int, p: int, j: int) -> list[int]:
    return list(range(j, m, p))


def run_sa_trial(m: int, k: int, mode: str, period: int, budget_sec: float,
                 max_evals: int, seed: int) -> dict:
    import numpy as np

    rng = np.random.default_rng(seed)
    t0 = time.perf_counter()
    if mode == "symmetric":
        pat = [int(x) + 1 for x in rng.integers(0, k, size=period)]
        coloring = [pat[i % period] for i in range(m)]
    else:
        pat = []
        coloring = [int(x) + 1 for x in rng.integers(0, k, size=m)]
    st = WeakSchurState(coloring, k)
    init_sec = time.perf_counter() - t0
    evals = 0
    verifs = 0
    best_viol = st.viol
    best_sha = canonical_partition_sha(st.color)
    cert = None
    temp, cooling = 2.0, 0.9995
    if best_viol == 0:
        verifs += 1
        ok, _ = _certify(st.color, k)
        if ok:
            cert = {"size": m, "sha256": best_sha, "partition": list(st.color)}
    while evals < max_evals and (time.perf_counter() - t0) < budget_sec and cert is None:
        if mode == "symmetric":
            j = int(rng.integers(0, period))
            new_c = int(rng.integers(1, k + 1))
            if new_c == pat[j]:
                continue
            # Sequential single-position deltas for affected slots.
            saved: list[tuple[int, int]] = []
            total = 0
            for pos0 in _symmetric_positions(m, period, j):
                d = st.delta_recolor(pos0, new_c)
                evals += 1
                total += d
                saved.append((pos0, st.color[pos0]))
                st.apply_recolor(pos0, new_c, d)
                if evals >= max_evals or (time.perf_counter() - t0) >= budget_sec:
                    break
            if total <= 0 or rng.random() < float(__import__("math").exp(-total / max(temp, 1e-9))):
                pass  # keep
            else:
                for pos0, old_c in reversed(saved):
                    d = st.delta_recolor(pos0, old_c)
                    st.apply_recolor(pos0, old_c, d)
                pat[j] = pat[j]  # unchanged
                temp = max(temp * cooling, 1e-3)
                continue
            pat[j] = new_c
        else:
            pos0 = int(rng.integers(0, m))
            new_c = int(rng.integers(1, k + 1))
            if new_c == st.color[pos0]:
                continue
            d = st.delta_recolor(pos0, new_c)
            evals += 1
            if d <= 0 or rng.random() < float(__import__("math").exp(-d / max(temp, 1e-9))):
                st.apply_recolor(pos0, new_c, d)
        if st.viol < best_viol:
            best_viol = st.viol
            best_sha = canonical_partition_sha(st.color)
            if best_viol == 0:
                verifs += 1
                ok, _ = _certify(st.color, k)
                if ok:
                    cert = {"size": m, "sha256": best_sha, "partition": list(st.color)}
                    break
        temp = max(temp * cooling, 1e-3)
    return {"best_violations": best_viol, "evaluations": evals,
            "verifications": verifs, "elapsed_sec": time.perf_counter() - t0,
            "init_sec": init_sec, "best_sha256": best_sha, "certificate": cert}


def run_hc_trial(m: int, k: int, mode: str, period: int, budget_sec: float,
                 max_evals: int, seed: int) -> dict:
    import numpy as np

    rng = np.random.default_rng(seed)
    t0 = time.perf_counter()
    if mode == "symmetric":
        pat = [int(x) + 1 for x in rng.integers(0, k, size=period)]
        coloring = [pat[i % period] for i in range(m)]
    else:
        coloring = [int(x) + 1 for x in rng.integers(0, k, size=m)]
    st = WeakSchurState(coloring, k)
    init_sec = time.perf_counter() - t0
    evals = 0
    verifs = 0
    best_viol = st.viol
    best_sha = canonical_partition_sha(st.color)
    best_color = list(st.color)
    cert = None
    if best_viol == 0:
        verifs += 1
        ok, _ = _certify(st.color, k)
        if ok:
            cert = {"size": m, "sha256": best_sha, "partition": list(st.color)}
    while evals < max_evals and (time.perf_counter() - t0) < budget_sec and cert is None:
        improved = False
        if mode == "symmetric":
            order = list(rng.permutation(period))
        else:
            order = list(rng.permutation(m))
        for pick in order:
            if evals >= max_evals or (time.perf_counter() - t0) >= budget_sec:
                break
            if mode == "symmetric":
                new_c = int(rng.integers(1, k + 1))
                if new_c == pat[int(pick)]:
                    continue
                # Incremental whole-pattern move: apply, keep iff improving.
                saved = [(pos0, st.color[pos0]) for pos0 in _symmetric_positions(m, period, int(pick))]
                viol_before = st.viol
                for pos0, _old in saved:
                    d = st.delta_recolor(pos0, new_c)
                    evals += 1
                    st.apply_recolor(pos0, new_c, d)
                    if evals >= max_evals or (time.perf_counter() - t0) >= budget_sec:
                        break
                if st.viol < viol_before:
                    pat[int(pick)] = new_c
                    improved = True
                    break
                for pos0, old_c in reversed(saved):
                    d = st.delta_recolor(pos0, old_c)
                    st.apply_recolor(pos0, old_c, d)
            else:
                new_c = int(rng.integers(1, k + 1))
                if new_c == st.color[int(pick)]:
                    continue
                d = st.delta_recolor(int(pick), new_c)
                evals += 1
                if d < 0:
                    st.apply_recolor(int(pick), new_c, d)
                    improved = True
                    break
        if st.viol < best_viol:
            best_viol = st.viol
            best_sha = canonical_partition_sha(st.color)
            best_color = list(st.color)
            if best_viol == 0:
                verifs += 1
                ok, _ = _certify(st.color, k)
                if ok:
                    cert = {"size": m, "sha256": best_sha, "partition": list(st.color)}
                    break
        if not improved:
            # Random restart (keeps best on record).
            if mode == "symmetric":
                pat = [int(x) + 1 for x in rng.integers(0, k, size=period)]
                st = WeakSchurState([pat[i % period] for i in range(m)], k)
            else:
                st = WeakSchurState([int(x) + 1 for x in rng.integers(0, k, size=m)], k)
            if st.viol < best_viol:
                best_viol = st.viol
                best_sha = canonical_partition_sha(st.color)
                best_color = list(st.color)
    return {"best_violations": best_viol, "evaluations": evals,
            "verifications": verifs, "elapsed_sec": time.perf_counter() - t0,
            "init_sec": init_sec, "best_sha256": best_sha,
            "best_partition_prefix": best_color[:32], "certificate": cert}


RUNNERS = {
    "SimulatedAnnealing": run_sa_trial,
    "HillClimbing": run_hc_trial,
}


# --------------------------------------------------------------------------
# Campaign driver.
# --------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    parser.add_argument("--max-new-trials", type=int, default=None)
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    catalogue = json.loads(Path(manifest["targets_source"]).read_text(encoding="utf-8"))
    by_id = {t["target_id"]: t for t in catalogue["targets"]}

    manifest_sha = hashlib.sha256(Path(args.manifest).read_bytes()).hexdigest()
    ckpt_path = Path(args.checkpoint)
    ckpt = load_checkpoint(ckpt_path) if args.resume else {"completed": {}}
    if ckpt.get("manifest_sha256") not in (None, manifest_sha):
        print("checkpoint manifest mismatch; starting fresh")
        ckpt = {"completed": {}}
    ckpt["manifest_sha256"] = manifest_sha
    completed: dict = ckpt.setdefault("completed", {})

    modes = ["free"] + [f"symmetric_p{p}" for p in manifest["symmetry"]["periods"]]
    started_at = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
    t_start = time.perf_counter()
    trials: list[dict] = []
    certs_by_target: dict[str, list[dict]] = {}
    new_trials = 0
    outer_break = False

    for target_id in manifest["targets"]:
        spec = by_id[target_id]
        k = int(spec["params"]["k"])
        best = int(spec["best_known_value"])
        attempt = break_size(best)
        for algo in manifest["algorithms"]:
            for seed in manifest["seeds"]:
                for mode in modes:
                    period = int(mode.split("_p")[1]) if mode.startswith("symmetric_p") else 0
                    key = trial_key(target_id, attempt, algo, int(seed), mode)
                    if key in completed:
                        rec = completed[key]
                        trials.append(rec)
                        if rec.get("certificate"):
                            certs_by_target.setdefault(target_id, []).append(rec["certificate"])
                        continue
                    runner = RUNNERS[algo]
                    res = runner(attempt, k, "symmetric" if mode.startswith("symmetric") else "free",
                                 period, float(manifest["budget_sec_per_seed"]),
                                 int(manifest.get("max_evaluations_per_trial", 1_000_000)), int(seed))
                    rec = {"trial_key": key, "target_id": target_id, "attempt_size": attempt,
                           "k": k, "algorithm": algo, "seed": int(seed), "mode": mode,
                           "best_known_value": best,
                           "result": "BEATEN" if res["certificate"] else "UNBEATEN",
                           **{kk: vv for kk, vv in res.items()
                              if kk not in ("certificate", "best_partition_prefix")}}
                    if res["certificate"]:
                        rec["certificate"] = res["certificate"]  # includes full partition
                    completed[key] = rec
                    save_checkpoint(ckpt_path, ckpt)
                    trials.append(rec)
                    new_trials += 1
                    print(f"  {key}: viol={res['best_violations']} evals={res['evaluations']} "
                          f"t={res['elapsed_sec']:.1f}s {rec['result']}", flush=True)
                    if args.max_new_trials is not None and new_trials >= args.max_new_trials:
                        outer_break = True
                        break
                if outer_break:
                    break
            if outer_break:
                break
        if outer_break:
            break

    expected = len(manifest["algorithms"]) * len(manifest["seeds"]) * len(modes)
    per_target = []
    for target_id in manifest["targets"]:
        spec = by_id[target_id]
        best = int(spec["best_known_value"])
        certs = certs_by_target.get(target_id, [])
        t_trials = [r for r in trials if r["target_id"] == target_id]
        if len(t_trials) < expected:
            verdict = "INCOMPLETE"
        else:
            verdict = verdict_for_target(best, certs)
        entry: dict = {"target_id": target_id, "k": int(spec["params"]["k"]),
                       "best_known_value": best,
                       "attempt_size": break_size(best), "verdict": verdict,
                       "n_trials": len(t_trials)}
        if certs:
            entry["certificate"] = certs[0]
        else:
            evo = min((r["best_violations"] for r in t_trials), default=None)
            entry["best_violations"] = evo
            by_mode: dict[str, int | None] = {}
            for mo in modes:
                vals = [r["best_violations"] for r in t_trials if r["mode"] == mo]
                by_mode[mo] = min(vals) if vals else None
            entry["best_violations_by_mode"] = by_mode
        per_target.append(entry)

    finished_at = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
    results = {"phase": "P177", "started_at": started_at, "finished_at": finished_at,
               "manifest_sha256": manifest_sha,
               "manifest_created_at": manifest.get("created_at"),
               "verdict_counts": {v: sum(1 for e in per_target if e["verdict"] == v)
                                  for v in ("DISCOVERY_BEATEN", "NULL_RESULT", "INCOMPLETE")},
               "targets": per_target, "trials": trials,
               "total_sec": time.perf_counter() - t_start}
    out_p = Path(args.output)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(results, indent=1), encoding="utf-8")
    print(f"verdicts: {results['verdict_counts']} total={results['total_sec']:.1f}s -> {out_p}")


if __name__ == "__main__":
    main()
