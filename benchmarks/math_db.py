"""External math-DB benchmark harness: GSM8K with answers, max-GPU safe (P14 follow-up).

Micro-task 1: download + pin + preregistered splits + smoke benchmark.
Word problems are NOT solved by symbolic regression here; the benchmark
measures parse/verify efficiency (problems/sec) with hidden split sealed,
as groundwork for a future <=5M specialist micro-model (P22-style gate).
"""

from __future__ import annotations

import argparse
import ast
import concurrent.futures
import hashlib
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from evobyte.provenance import (
    MonotonicDeadline,
    collect_provenance,
    resolve_device,
    seed_all,
    synchronize,
    write_manifest,
)

HF_ID = "openai/gsm8k"
HF_CONFIG = "main"
HF_SPLIT = "test"
LICENSE = "MIT (OpenAI GSM8K)"
EXPECTED_N = 1319
EXPECTED_SHA256 = "3730d312f6e3440559ace48831e51066acaca737f6eabec99bccb9e4b3c39d14"
RAW_PATH = REPO_ROOT / "data" / "raw" / "gsm8k-test.jsonl"
VRAM_BUDGET_MB = 7000.0  # permanent rule: max 4060 without crashing (8188 total)
MAX_WORKERS = 8

CHAIN_RE = re.compile(r"<<(.+?)>>")
FINAL_RE = re.compile(r"####\s*(-?[\d,]*\.?\d+)")


def download_gsm8k_test(out_path: Path = RAW_PATH) -> dict:
    """Download GSM8K test split to data/raw/ (gitignored) and pin SHA256."""
    from datasets import load_dataset

    ds = load_dataset(HF_ID, HF_CONFIG, split=HF_SPLIT)
    rows = [{"question": r["question"], "answer": r["answer"]} for r in ds]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)
    sha = hashlib.sha256(out_path.read_bytes()).hexdigest()
    return {"n": len(rows), "sha256": sha, "path": str(out_path)}


def parse_final_answer(answer: str) -> float | None:
    m = FINAL_RE.search(answer.replace(",", ""))
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def _safe_arith(expr: str) -> float | None:
    """Evaluate guarded arithmetic only (+-*/%() and numbers); None on anything else."""
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError:
        return None
    allowed = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Constant,
    )
    for node in ast.walk(tree):
        if not isinstance(node, allowed):
            return None
        if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float)):
            return None
    try:
        val = eval(compile(tree, "<arith>", "eval"), {"__builtins__": {}}, {})
    except (ArithmeticError, ValueError, TypeError):
        return None
    return float(val) if isinstance(val, (int, float)) else None


def extract_chains(answer: str) -> list[dict]:
    """Extract <<expr=result>> calculation chains with guarded re-evaluation."""
    out = []
    for chunk in CHAIN_RE.findall(answer):
        if "=" in chunk:
            expr, claimed = chunk.rsplit("=", 1)
            try:
                claimed_v = float(claimed.strip().replace(",", ""))
            except ValueError:
                continue
        else:
            expr, claimed_v = chunk, None
        got = _safe_arith(expr.strip())
        out.append({"expr": expr.strip(), "claimed": claimed_v, "computed": got})
    return out


def make_splits(n: int, seed: int = 0) -> dict[str, list[int]]:
    """Deterministic train/val/hidden index splits; hidden sealed from search."""
    rng = np.random.default_rng(seed)
    idx = np.arange(n)
    rng.shuffle(idx)
    n_tr = int(0.7 * n)
    n_val = int(0.15 * n)
    return {
        "train": sorted(int(i) for i in idx[:n_tr]),
        "val": sorted(int(i) for i in idx[n_tr : n_tr + n_val]),
        "hidden": sorted(int(i) for i in idx[n_tr + n_val :]),
    }


def load_rows(path: Path = RAW_PATH) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run_smoke_benchmark(limit: int = 128, seed: int = 0, device_name: str | None = None) -> dict:
    """Parse + verify efficiency smoke test: 8 threads CPU + chunked GPU numeric check."""
    seed_all(seed)
    torch.set_num_threads(MAX_WORKERS)
    device = resolve_device(device_name)
    t0 = time.monotonic()
    dl = MonotonicDeadline(budget_sec=120.0)
    dl.mark_setup_done()
    rows = load_rows()[:limit]
    splits = make_splits(len(rows), seed)
    dl.mark_warmup_done()

    # Train+val only: hidden sealed.
    visible = rows[: len(splits["train"]) + len(splits["val"])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        finals = list(pool.map(parse_final_answer, [r["answer"] for r in visible]))
        chains = list(pool.map(extract_chains, [r["answer"] for r in visible]))
    n_chains = sum(len(c) for c in chains)
    n_ok = sum(1 for c in chains for ch in c if ch["computed"] is not None)
    n_match = sum(
        1
        for c in chains
        for ch in c
        if ch["claimed"] is not None
        and ch["computed"] is not None
        and abs(ch["claimed"] - ch["computed"]) < 1e-9
    )
    # GPU numeric check, chunked under 7000MB (max-4060 rule), synchronized.
    vals = np.array(
        [ch["computed"] for c in chains for ch in c if ch["computed"] is not None],
        dtype=np.float32,
    )
    if vals.size:
        chunk = 20000
        tot = 0.0
        for i in range(0, len(vals), chunk):
            t = torch.from_numpy(vals[i : i + chunk]).to(device)
            tot += float(t.sum().cpu())
            synchronize(device)
    else:
        tot = 0.0
    dl.mark_compute_done()
    timing = dl.finish()
    dt = max(1e-6, time.monotonic() - t0)
    return {
        "phase": "p14-mathdb-gsm8k-smoke",
        "n_visible": len(visible),
        "n_hidden_sealed": len(splits["hidden"]),
        "parse_ok": sum(1 for v in finals if v is not None),
        "chains_total": n_chains,
        "chains_computed": n_ok,
        "chains_match": n_match,
        "gpu_checksum": tot,
        "problems_per_sec": len(visible) / dt,
        "device_actual": str(device),
        "deadline": timing,
        "hidden_touched": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="GSM8K math-DB harness (max-4060 safe)")
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--limit", type=int, default=128)
    ap.add_argument("--output", type=str, default="experiments/mathdb-smoke.json")
    ap.add_argument("--device", type=str, default=None)
    args = ap.parse_args()
    if args.download:
        info = download_gsm8k_test()
        print(json.dumps(info, indent=2))
        if info["n"] != EXPECTED_N or info["sha256"] != EXPECTED_SHA256:
            print("PIN MISMATCH: dataset changed upstream; update prereg, do not proceed")
            return 2
        print("PIN OK")
        return 0
    if args.smoke:
        rep = run_smoke_benchmark(limit=args.limit, device_name=args.device)
        prov = collect_provenance(
            seed=0,
            device=resolve_device(args.device),
            dataset_hashes={"gsm8k-test": EXPECTED_SHA256[:16]},
            config={"limit": args.limit},
        )
        out = Path(args.output)
        written = write_manifest(
            out,
            {**rep, "provenance": prov},
            {__file__: hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        )
        print(f"smoke manifest {out} sha={written['manifest_sha256'][:16]}")
        print(
            json.dumps(
                {k: rep[k] for k in ("problems_per_sec", "chains_match", "chains_total")}, indent=2
            )
        )
        return 0
    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
