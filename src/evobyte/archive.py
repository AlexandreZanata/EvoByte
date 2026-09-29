"""Elite archive, checkpointing, and Hall of Fame writer (spec: docs/EVOLUTION.md, P07)."""

from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import sqlite3
import time
from pathlib import Path
from typing import Any

import numpy as np

from evobyte.bytecode import OPCODE_VERSION, decode_human

DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS elites (
    sha256 TEXT PRIMARY KEY,
    generation INTEGER,
    opcode_version INTEGER,
    candidate_binary BLOB,
    decoded_expression TEXT,
    fitness REAL,
    train_error REAL,
    validation_error REAL,
    test_error REAL,
    complexity REAL,
    parents TEXT,
    mutation_history TEXT,
    timestamp REAL,
    novelty_score REAL
);
"""


def compute_program_hash(program: np.ndarray) -> str:
    """Compute 16-hex sha256 of candidate binary bytes."""
    return hashlib.sha256(np.ascontiguousarray(program).tobytes()).hexdigest()[:16]


class EliteArchive:
    """Host-side SQLite-backed archive for persistent elite discovery tracking."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = str(db_path) if db_path is not None else ":memory:"
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        with self.conn:
            self.conn.executescript(DB_SCHEMA)

    def add_elite(
        self,
        program: np.ndarray,
        generation: int,
        fitness: float,
        train_error: float,
        validation_error: float = 0.0,
        test_error: float = 0.0,
        complexity: float = 0.0,
        parents: list[str] | None = None,
        mutation_history: str = "",
        novelty_score: float = 0.0,
        timestamp: float | None = None,
    ) -> bool:
        """Add an elite row to the archive. Returns True if inserted, False if duplicate."""
        prog_bytes = np.ascontiguousarray(program, dtype=np.uint32).tobytes()
        sha = hashlib.sha256(prog_bytes).hexdigest()[:16]
        expr = decode_human(program)
        ts = timestamp if timestamp is not None else time.time()
        parents_json = json.dumps(parents or [])

        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO elites (
                    sha256, generation, opcode_version, candidate_binary,
                    decoded_expression, fitness, train_error, validation_error,
                    test_error, complexity, parents, mutation_history,
                    timestamp, novelty_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    sha,
                    generation,
                    OPCODE_VERSION,
                    prog_bytes,
                    expr,
                    float(fitness),
                    float(train_error),
                    float(validation_error),
                    float(test_error),
                    float(complexity),
                    parents_json,
                    mutation_history,
                    float(ts),
                    float(novelty_score),
                ),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Duplicate sha256
            return False

    def __enter__(self) -> EliteArchive:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def count(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM elites")
        return cur.fetchone()[0]

    def get_by_hash(self, sha256: str) -> dict[str, Any] | None:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM elites WHERE sha256 = ?", (sha256,))
        row = cur.fetchone()
        if row is None:
            return None
        return dict(row)

    def get_elites(self, limit: int | None = 10, order_by: str = "fitness") -> list[dict[str, Any]]:
        cur = self.conn.cursor()
        valid_orders = {
            "fitness": "fitness ASC",
            "novelty": "novelty_score DESC",
            "generation": "generation DESC",
        }
        order_clause = valid_orders.get(order_by, "fitness ASC")
        if limit is not None:
            cur.execute(f"SELECT * FROM elites ORDER BY {order_clause} LIMIT ?", (limit,))
        else:
            cur.execute(f"SELECT * FROM elites ORDER BY {order_clause}")
        return [dict(r) for r in cur.fetchall()]

    def close(self) -> None:
        self.conn.close()


def save_checkpoint(path: str | Path, state: dict[str, Any]) -> None:
    """Save evolution state (generation, RNG state, population, archive) atomically."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    state_to_save = dict(state)
    state_to_save["opcode_version"] = OPCODE_VERSION
    state_to_save["timestamp"] = time.time()

    temp_path = path.with_suffix(".tmp")
    with open(temp_path, "wb") as f:
        pickle.dump(state_to_save, f, protocol=pickle.HIGHEST_PROTOCOL)
    temp_path.replace(path)


def load_checkpoint(path: str | Path) -> dict[str, Any]:
    """Load evolution state, verifying OPCODE_VERSION compatibility."""
    path = Path(path)
    with open(path, "rb") as f:
        state = pickle.load(f)

    loaded_version = state.get("opcode_version", None)
    if loaded_version != OPCODE_VERSION:
        raise ValueError(
            f"Checkpoint opcode version mismatch: expected {OPCODE_VERSION}, got {loaded_version}"
        )
    return state


def is_memorizer(
    train_error: float,
    val_error: float,
    val_gap: float = 0.0,
    extrapolation_error: float | None = None,
) -> bool:
    """Check if candidate exhibits overfitting/memorization signatures."""
    if val_error > 2.0 * train_error + 0.05:
        return True
    if val_gap > 0.05:
        return True
    if extrapolation_error is not None and extrapolation_error > 2.0 * train_error + 0.1:
        return True
    return False


def write_hall_of_fame_entry(fame_path: str | Path, entry: dict[str, Any]) -> bool:
    """Append a promoted discovery to fame.jsonl if eligible (non-memorizer)."""
    train_err = float(entry.get("train_error", 0.0))
    val_err = float(entry.get("validation_error", entry.get("val_error", 0.0)))
    val_gap = float(entry.get("val_gap", max(0.0, val_err - train_err)))
    extrap_err = entry.get("extrapolation_error", None)
    extrap_val = float(extrap_err) if extrap_err is not None else None

    if is_memorizer(train_err, val_err, val_gap, extrap_val):
        return False

    fame_path = Path(fame_path)
    fame_path.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "rank": entry.get("rank", 1),
        "fitness": float(entry.get("fitness", 0.0)),
        "expression": str(entry.get("expression", entry.get("decoded_expression", ""))),
        "generation": int(entry.get("generation", 0)),
        "discovered_after_N_candidates": int(entry.get("discovered_after_N_candidates", 0)),
        "train_error": train_err,
        "validation_error": val_err,
        "val_gap": val_gap,
        "complexity": float(entry.get("complexity", 0.0)),
        "parents": entry.get("parents", []),
        "hash": str(entry.get("hash", entry.get("sha256", ""))),
        "timestamp": float(entry.get("timestamp", time.time())),
    }
    if extrap_val is not None:
        record["extrapolation_error"] = extrap_val
    if "reproduction_cmd" in entry:
        record["reproduction_cmd"] = str(entry["reproduction_cmd"])

    with open(fame_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return True


def run_resume_selftest(
    seed: int = 42, checkpoint_dir: str | Path = "/tmp/evobyte_selftest"
) -> bool:
    """Prove resume equivalence: uninterrupted execution == checkpoint-resumed execution."""
    from evobyte.evolution import crossover_single_point, mutate_point, sample_structured
    from evobyte.verifier import evaluate

    checkpoint_dir = Path(checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    ckpt_file = checkpoint_dir / "ckpt.pkl"

    xs = np.linspace(-5.0, 5.0, 64, dtype=np.float32)
    ys = xs * xs + 3 * xs + 7

    # Run 1: Uninterrupted for 6 generations
    rng_unbroken = np.random.default_rng(seed)
    pop_unbroken = np.stack([sample_structured(rng_unbroken) for _ in range(30)])

    for gen in range(1, 7):
        # Evaluate
        fits = [evaluate(p, xs, ys)["fitness"] for p in pop_unbroken]
        order = np.argsort(fits)
        pop_unbroken = pop_unbroken[order]

        # Mutate and cross
        next_pop = [pop_unbroken[0], pop_unbroken[1]]
        while len(next_pop) < 30:
            p1 = pop_unbroken[rng_unbroken.integers(0, 10)]
            p2 = pop_unbroken[rng_unbroken.integers(0, 10)]
            c1, c2 = crossover_single_point(p1, p2, rng_unbroken)
            next_pop.append(mutate_point(c1, rng_unbroken))
            if len(next_pop) < 30:
                next_pop.append(mutate_point(c2, rng_unbroken))
        pop_unbroken = np.stack(next_pop)

    # Run 2: Run for 3 generations, checkpoint, load, run remaining 3 generations
    rng_split = np.random.default_rng(seed)
    pop_split = np.stack([sample_structured(rng_split) for _ in range(30)])

    for gen in range(1, 4):
        fits = [evaluate(p, xs, ys)["fitness"] for p in pop_split]
        order = np.argsort(fits)
        pop_split = pop_split[order]

        next_pop = [pop_split[0], pop_split[1]]
        while len(next_pop) < 30:
            p1 = pop_split[rng_split.integers(0, 10)]
            p2 = pop_split[rng_split.integers(0, 10)]
            c1, c2 = crossover_single_point(p1, p2, rng_split)
            next_pop.append(mutate_point(c1, rng_split))
            if len(next_pop) < 30:
                next_pop.append(mutate_point(c2, rng_split))
        pop_split = np.stack(next_pop)

    # Checkpoint at gen 3
    state = {
        "generation": 3,
        "rng_state": rng_split.bit_generator.state,
        "population": pop_split.copy(),
    }
    save_checkpoint(ckpt_file, state)

    # Restore from checkpoint
    loaded = load_checkpoint(ckpt_file)
    restored_gen = loaded["generation"]
    pop_resumed = loaded["population"]
    rng_resumed = np.random.default_rng()
    rng_resumed.bit_generator.state = loaded["rng_state"]

    for gen in range(restored_gen + 1, 7):
        fits = [evaluate(p, xs, ys)["fitness"] for p in pop_resumed]
        order = np.argsort(fits)
        pop_resumed = pop_resumed[order]

        next_pop = [pop_resumed[0], pop_resumed[1]]
        while len(next_pop) < 30:
            p1 = pop_resumed[rng_resumed.integers(0, 10)]
            p2 = pop_resumed[rng_resumed.integers(0, 10)]
            c1, c2 = crossover_single_point(p1, p2, rng_resumed)
            next_pop.append(mutate_point(c1, rng_resumed))
            if len(next_pop) < 30:
                next_pop.append(mutate_point(c2, rng_resumed))
        pop_resumed = np.stack(next_pop)

    # Assert 100% bitwise equivalence between uninterrupted and resumed runs
    assert np.array_equal(pop_unbroken, pop_resumed), (
        "Resumed population diverges from uninterrupted run!"
    )
    print(
        f"Resume equivalence test PASSED: seed={seed}, 6 generations, bit-identical final population."
    )
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Archive and Checkpointing Self-Test")
    ap.add_argument(
        "--selftest-resume",
        dest="selftest_resume",
        action="store_true",
        help="Run resume equivalence self-test",
    )
    args = ap.parse_args()

    if args.selftest_resume:
        success = run_resume_selftest()
        return 0 if success else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
