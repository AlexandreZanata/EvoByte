"""Preregistered covering-designs record campaign (P176).

For each (record target, break size = published_size - 1, algorithm, seed):
search under a dual budget (time OR evaluations). Any candidate with fewer
blocks than published_size is submitted to the P171 independent verifier
immediately; a certificate records DISCOVERY_BEATEN with object + SHA-256.
Incremental JSON checkpoint after every trial; --resume skips completed ones.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
import time
from array import array
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evobyte.frontier_catalogue import verify_covering_design  # noqa: E402

try:
    import numpy as _np

    _HAS_NUMPY = True
except Exception:  # pragma: no cover
    _np = None  # type: ignore
    _HAS_NUMPY = False


# --------------------------------------------------------------------------
# Pure helpers (importable by tests; no search here).
# --------------------------------------------------------------------------


def break_size(published_size: int) -> int:
    """Record-attempt size: exactly published_size - 1 (no goalpost moves)."""
    return int(published_size) - 1


def trial_key(target_id: str, attempt_size: int, algorithm: str, seed: int) -> str:
    return f"{target_id}|B{int(attempt_size)}|{algorithm}|seed{int(seed)}"


def verdict_for_target(published_size: int, certificates: list[dict]) -> str:
    """DISCOVERY_BEATEN iff a certificate has blocks < published_size."""
    for cert in certificates:
        try:
            if int(cert.get("n_blocks", 10**18)) < int(published_size):
                return "DISCOVERY_BEATEN"
        except Exception:
            continue
    return "NULL_RESULT"


def load_checkpoint(path: Path) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return {"completed": {}}


def save_checkpoint(path: Path, state: dict) -> None:
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(json.dumps(state, indent=1), encoding="utf-8")
    tmp.replace(path)


def canonical_blocks_sha(blocks: list[tuple[int, ...]]) -> str:
    canon = "|".join(",".join(str(x) for x in b) for b in sorted(blocks))
    return hashlib.sha256(canon.encode()).hexdigest()


# --------------------------------------------------------------------------
# Covering search state with incremental delta evaluation.
# --------------------------------------------------------------------------


class CoveringState:
    """B blocks over {1..v}; incremental cover-count array over C(v,t) ranks."""

    def __init__(self, v: int, k: int, t: int, n_blocks: int, rng) -> None:
        self.v, self.k, self.t, self.n_blocks = int(v), int(k), int(t), int(n_blocks)
        self.rng = rng
        self.n_sub = math.comb(self.v, self.t)
        self.counts = array("i", [0]) * self.n_sub
        self.covered = 0
        self.blocks: list[tuple[int, ...]] = []
        # binom table for colex ranking (matches P171 verifier).
        self._tab = _np.array(
            [
                [math.comb(nn, rr) if rr <= nn else 0 for rr in range(self.t + 1)]
                for nn in range(self.v + 1)
            ],
            dtype=_np.int64,
        )
        self._rhs = _np.arange(1, self.t + 1, dtype=_np.int64)

    def block_ranks(self, block: tuple[int, ...]) -> list[int]:
        """All C(k,t) subset ranks of a 1-based sorted block (vectorized)."""
        mat = _np.array(
            [c for c in itertools.combinations([x - 1 for x in block], self.t)],
            dtype=_np.int64,
        )
        return self._tab[mat, self._rhs].sum(axis=1).tolist()

    def random_block(self) -> tuple[int, ...]:
        pts = self.rng.choice(self.v, size=self.k, replace=False)
        return tuple(sorted(int(x) + 1 for x in pts))

    def _add_ranks(self, ranks: list[int]) -> None:
        cc = self.counts
        for s in ranks:
            if cc[s] == 0:
                self.covered += 1
            cc[s] += 1

    def _remove_ranks(self, ranks: list[int]) -> None:
        cc = self.counts
        for s in ranks:
            cc[s] -= 1
            if cc[s] == 0:
                self.covered -= 1

    def add_block(self, block: tuple[int, ...]) -> None:
        self._add_ranks(self.block_ranks(block))
        self.blocks.append(block)

    def delta_replace(self, idx: int, new_block: tuple[int, ...]) -> int:
        """Net coverage gain of swapping blocks[idx] -> new_block (no mutation)."""
        old_ranks = self.block_ranks(self.blocks[idx])
        new_ranks = self.block_ranks(new_block)
        cc = self.counts
        gain = 0
        for s in old_ranks:
            if cc[s] == 1:
                gain -= 1
        for s in new_ranks:
            if cc[s] == 0:
                gain += 1
        return gain

    def apply_replace(self, idx: int, new_block: tuple[int, ...]) -> None:
        self._remove_ranks(self.block_ranks(self.blocks[idx]))
        self._add_ranks(self.block_ranks(new_block))
        self.blocks[idx] = new_block

    def uncovered(self) -> int:
        return self.n_sub - self.covered


# --------------------------------------------------------------------------
# Trial runners. 1 eval = 1 delta (move/candidate) evaluation.
# --------------------------------------------------------------------------


def _certify(blocks: list[tuple[int, ...]], v: int, k: int, t: int) -> tuple[bool, str]:
    ok, msg = verify_covering_design([list(b) for b in blocks], v, k, t)
    return bool(ok), str(msg)


def run_sa_trial(
    v: int, k: int, t: int, n_blocks: int, budget_sec: float, max_evals: int, seed: int
) -> dict:
    rng = __import__("numpy").random.default_rng(seed)
    t0 = time.perf_counter()
    st = CoveringState(v, k, t, n_blocks, rng)
    for _ in range(n_blocks):
        st.add_block(st.random_block())
    init_sec = time.perf_counter() - t0
    evals = 0
    verifs = 0
    best_uncovered = st.uncovered()
    best_sha = canonical_blocks_sha(st.blocks)
    cert = None
    temp, cooling = 2.0, 0.9995
    if best_uncovered == 0:
        verifs += 1
        ok, _ = _certify(st.blocks, v, k, t)
        if ok:
            cert = {
                "n_blocks": len(st.blocks),
                "sha256": canonical_blocks_sha(st.blocks),
                "blocks": [list(b) for b in st.blocks],
            }
    while evals < max_evals and (time.perf_counter() - t0) < budget_sec:
        idx = int(rng.integers(0, n_blocks))
        cand = st.random_block()
        gain = st.delta_replace(idx, cand)
        evals += 1
        # gain > 0 reduces uncovered; accept worsening moves by SA rule.
        if gain >= 0 or rng.random() < math.exp(gain / max(temp, 1e-9)):
            st.apply_replace(idx, cand)
            u = st.uncovered()
            if u < best_uncovered:
                best_uncovered = u
                best_sha = canonical_blocks_sha(st.blocks)
                if u == 0:
                    verifs += 1
                    ok, _ = _certify(st.blocks, v, k, t)
                    if ok:
                        cert = {
                            "n_blocks": len(st.blocks),
                            "sha256": canonical_blocks_sha(st.blocks),
                            "blocks": [list(b) for b in st.blocks],
                        }
                        break
        temp = max(temp * cooling, 1e-3)
    return {
        "best_uncovered": best_uncovered,
        "evaluations": evals,
        "verifications": verifs,
        "elapsed_sec": time.perf_counter() - t0,
        "init_sec": init_sec,
        "best_sha256": best_sha,
        "certificate": cert,
    }


def run_hc_trial(
    v: int, k: int, t: int, n_blocks: int, budget_sec: float, max_evals: int, seed: int
) -> dict:
    rng = __import__("numpy").random.default_rng(seed)
    t0 = time.perf_counter()
    st = CoveringState(v, k, t, n_blocks, rng)
    for _ in range(n_blocks):
        st.add_block(st.random_block())
    init_sec = time.perf_counter() - t0
    evals = 0
    verifs = 0
    best_uncovered = st.uncovered()
    best_sha = canonical_blocks_sha(st.blocks)
    cert = None
    if best_uncovered == 0:
        verifs += 1
        ok, _ = _certify(st.blocks, v, k, t)
        if ok:
            cert = {
                "n_blocks": len(st.blocks),
                "sha256": canonical_blocks_sha(st.blocks),
                "blocks": [list(b) for b in st.blocks],
            }
    restarts = 0
    while evals < max_evals and (time.perf_counter() - t0) < budget_sec:
        improved = False
        order = rng.permutation(n_blocks)
        for idx in order:
            if evals >= max_evals or (time.perf_counter() - t0) >= budget_sec:
                break
            cand = st.random_block()
            gain = st.delta_replace(int(idx), cand)
            evals += 1
            if gain > 0:
                st.apply_replace(int(idx), cand)
                improved = True
                u = st.uncovered()
                if u < best_uncovered:
                    best_uncovered = u
                    best_sha = canonical_blocks_sha(st.blocks)
                    if u == 0:
                        verifs += 1
                        ok, _ = _certify(st.blocks, v, k, t)
                        if ok:
                            cert = {
                                "n_blocks": len(st.blocks),
                                "sha256": canonical_blocks_sha(st.blocks),
                                "blocks": [list(b) for b in st.blocks],
                            }
                            return {
                                "best_uncovered": best_uncovered,
                                "evaluations": evals,
                                "verifications": verifs,
                                "elapsed_sec": time.perf_counter() - t0,
                                "init_sec": init_sec,
                                "best_sha256": best_sha,
                                "certificate": cert,
                            }
                break
        if not improved:
            restarts += 1
            # Random restart (keeps best on record).
            st = CoveringState(v, k, t, n_blocks, rng)
            for _ in range(n_blocks):
                st.add_block(st.random_block())
            u = st.uncovered()
            if u < best_uncovered:
                best_uncovered = u
                best_sha = canonical_blocks_sha(st.blocks)
    return {
        "best_uncovered": best_uncovered,
        "evaluations": evals,
        "verifications": verifs,
        "elapsed_sec": time.perf_counter() - t0,
        "init_sec": init_sec,
        "best_sha256": best_sha,
        "certificate": cert,
    }


def run_greedy_trial(
    v: int, k: int, t: int, n_blocks: int, budget_sec: float, max_evals: int, seed: int
) -> dict:
    rng = __import__("numpy").random.default_rng(seed)
    st = CoveringState(v, k, t, n_blocks, rng)
    t0 = time.perf_counter()
    evals = 0
    # Adaptive candidate width: construction costs ~ n_blocks * width * C(k,t).
    per_pick = max(1, math.comb(k, t))
    width = max(2, min(32, 2_000_000 // max(1, n_blocks * per_pick)))
    for _ in range(n_blocks):
        if (time.perf_counter() - t0) >= budget_sec:
            break
        best_gain, best_cand = -1, None
        for _ in range(width):
            if evals >= max_evals or (time.perf_counter() - t0) >= budget_sec:
                break
            cand = st.random_block()
            ranks = st.block_ranks(cand)
            evals += 1
            gain = sum(1 for s in ranks if st.counts[s] == 0)
            if gain > best_gain:
                best_gain, best_cand = gain, (cand, ranks)
        if best_cand is None:
            best_cand = (st.random_block(), None)
            cand, ranks = best_cand[0], st.block_ranks(best_cand[0])
        else:
            cand, ranks = best_cand
        st._add_ranks(ranks)
        st.blocks.append(cand)
    # Local-search polish with the remaining budget.
    verifs = 0
    best_uncovered = st.uncovered()
    best_sha = canonical_blocks_sha(st.blocks)
    cert = None
    if best_uncovered == 0:
        verifs += 1
        ok, _ = _certify(st.blocks, v, k, t)
        if ok:
            cert = {
                "n_blocks": len(st.blocks),
                "sha256": best_sha,
                "blocks": [list(b) for b in st.blocks],
            }
    while evals < max_evals and (time.perf_counter() - t0) < budget_sec and cert is None:
        idx = int(rng.integers(0, n_blocks))
        cand = st.random_block()
        gain = st.delta_replace(idx, cand)
        evals += 1
        if gain > 0:
            st.apply_replace(idx, cand)
            u = st.uncovered()
            if u < best_uncovered:
                best_uncovered = u
                best_sha = canonical_blocks_sha(st.blocks)
                if u == 0:
                    verifs += 1
                    ok, _ = _certify(st.blocks, v, k, t)
                    if ok:
                        cert = {
                            "n_blocks": len(st.blocks),
                            "sha256": best_sha,
                            "blocks": [list(b) for b in st.blocks],
                        }
                        break
    return {
        "best_uncovered": best_uncovered,
        "evaluations": evals,
        "verifications": verifs,
        "elapsed_sec": time.perf_counter() - t0,
        "init_sec": 0.0,
        "best_sha256": best_sha,
        "certificate": cert,
    }


RUNNERS = {
    "SimulatedAnnealing": run_sa_trial,
    "HillClimbing": run_hc_trial,
    "GreedyPlusLocalSearch": run_greedy_trial,
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
    parser.add_argument(
        "--max-new-trials",
        type=int,
        default=None,
        help="Chunked execution: stop after this many NEW trials (checkpoint kept).",
    )
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

    started_at = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
    t_start = time.perf_counter()
    trials: list[dict] = []
    certs_by_target: dict[str, list[dict]] = {}
    new_trials = 0
    chunk_cap = args.max_new_trials
    outer_break = False

    for target_id in manifest["targets"]:
        spec = by_id[target_id]
        v, k, t = (int(spec["params"][x]) for x in ("v", "k", "t"))
        published = int(spec["best_known_value"])
        attempt = break_size(published)
        for algo in manifest["algorithms"]:
            for seed in manifest["seeds"]:
                key = trial_key(target_id, attempt, algo, int(seed))
                if key in completed:
                    rec = completed[key]
                    trials.append(rec)
                    if rec.get("certificate"):
                        certs_by_target.setdefault(target_id, []).append(rec["certificate"])
                    continue
                runner = RUNNERS[algo]
                res = runner(
                    v,
                    k,
                    t,
                    attempt,
                    float(manifest["budget_sec_per_seed"]),
                    int(manifest.get("max_evaluations_per_trial", 10_000_000)),
                    int(seed),
                )
                rec = {
                    "trial_key": key,
                    "target_id": target_id,
                    "attempt_size": attempt,
                    "algorithm": algo,
                    "seed": int(seed),
                    "published_size": published,
                    "result": "BEATEN" if res["certificate"] else "UNBEATEN",
                    **{kk: vv for kk, vv in res.items() if kk != "certificate"},
                }
                if res["certificate"]:
                    rec["certificate"] = res["certificate"]
                    certs_by_target.setdefault(target_id, []).append(res["certificate"])
                completed[key] = rec
                save_checkpoint(ckpt_path, ckpt)
                trials.append(rec)
                new_trials += 1
                print(
                    f"  {key}: uncovered={res['best_uncovered']} evals={res['evaluations']} "
                    f"t={res['elapsed_sec']:.1f}s {rec['result']}",
                    flush=True,
                )
                if chunk_cap is not None and new_trials >= chunk_cap:
                    outer_break = True
                    break
            if outer_break:
                break
        if outer_break:
            break

    per_target = []
    expected_trials = len(manifest["algorithms"]) * len(manifest["seeds"])
    for target_id in manifest["targets"]:
        spec = by_id[target_id]
        published = int(spec["best_known_value"])
        certs = certs_by_target.get(target_id, [])
        t_trials = [r for r in trials if r["target_id"] == target_id]
        if len(t_trials) < expected_trials:
            verdict = "INCOMPLETE"
            best_unc = min((r["best_uncovered"] for r in t_trials), default=None)
        else:
            verdict = verdict_for_target(published, certs)
            best_unc = min(r["best_uncovered"] for r in t_trials)
        entry: dict = {
            "target_id": target_id,
            "params": spec["params"],
            "published_size": published,
            "attempt_size": break_size(published),
            "verdict": verdict,
            "best_uncovered": best_unc,
            "n_trials": len(t_trials),
        }
        if certs:
            entry["certificate"] = certs[0]
        per_target.append(entry)

    finished_at = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
    results = {
        "phase": "P176",
        "started_at": started_at,
        "finished_at": finished_at,
        "manifest_sha256": manifest_sha,
        "manifest_created_at": manifest.get("created_at"),
        "total_sec": time.perf_counter() - t_start,
        "verdict_counts": {
            v: sum(1 for e in per_target if e["verdict"] == v)
            for v in ("DISCOVERY_BEATEN", "NULL_RESULT", "INCOMPLETE")
        },
        "targets": per_target,
        "trials": trials,
    }
    out_p = Path(args.output)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(results, indent=1), encoding="utf-8")
    print(f"verdicts: {results['verdict_counts']} total={results['total_sec']:.1f}s -> {out_p}")


if __name__ == "__main__":
    main()
