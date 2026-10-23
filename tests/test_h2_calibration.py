"""H2 preregistered calibration components and micro-constructions (P174)."""

from __future__ import annotations

import ast
import itertools
import json
import time
from pathlib import Path
from typing import Any

import numpy as np


def test_capset_verifier_calibration() -> None:
    from evobyte.frontier_catalogue import verify_cap_set

    cube = [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
    ok, _ = verify_cap_set(cube, 3)
    assert ok is True
    ok_line, _ = verify_cap_set([(0, 0), (1, 1), (2, 2)], 2)
    assert ok_line is False
    ok_dup, _ = verify_cap_set([(0, 0, 0), (0, 0, 0)], 3)
    assert ok_dup is False
    ok_oob, _ = verify_cap_set([(0, 0, 3)], 3)
    assert ok_oob is False


def test_greedy_builds_cube_from_static_priority() -> None:
    from evobyte.constructive import greedy_construct

    pts27 = list(itertools.product((0, 1, 2), repeat=3))

    def static_priority(pt: tuple[int, int, int], ctx: dict[str, Any]) -> float:
        return -float(pt[0] ** 2 + pt[1] ** 2 + pt[2] ** 2)

    def is_feasible(cand: tuple[int, int, int], built: list[tuple[int, int, int]], ctx: dict[str, Any]) -> bool:
        for i in range(len(built)):
            for j in range(i + 1, len(built)):
                p1, p2 = built[i], built[j]
                if (
                    (p1[0] + p2[0] + cand[0]) % 3 == 0
                    and (p1[1] + p2[1] + cand[1]) % 3 == 0
                    and (p1[2] + p2[2] + cand[2]) % 3 == 0
                ):
                    return False
        return True

    def is_complete(built: list[tuple[int, int, int]], ctx: dict[str, Any]) -> bool:
        return len(built) == 8

    t0 = time.perf_counter()
    built, steps, evals = greedy_construct(
        pts27, priority_fn=static_priority, is_feasible_fn=is_feasible, is_complete_fn=is_complete
    )
    elapsed = time.perf_counter() - t0
    assert elapsed < 0.1
    assert set(built) == set(itertools.product((0, 1), repeat=3))
    assert steps == 8 and evals > 0


def test_evolution_loop_counts_evaluations() -> None:
    from evobyte.priority_evolution import evolve_priorities

    calls = {"n": 0}

    def toy_objective(prog: np.ndarray) -> float:
        calls["n"] += 1
        return float(int(prog[0]) & 0xFF) + float(int(prog[1]) & 0xFF)

    best1, score1, evals1, _ = evolve_priorities(
        toy_objective, budget_evals=40, pop_size=8, seed=123, max_seconds=5.0
    )
    assert evals1 == calls["n"]
    assert evals1 <= 40 and evals1 > 0

    calls["n"] = 0
    best2, score2, evals2, _ = evolve_priorities(
        toy_objective, budget_evals=40, pop_size=8, seed=123, max_seconds=5.0
    )
    assert evals2 == calls["n"] == evals1
    assert score2 == score1
    assert list(np.asarray(best2).tolist()) == list(np.asarray(best1).tolist())


def test_manifest_schema() -> None:
    manifest_p = Path(__file__).resolve().parents[1] / "experiments" / "p174-h2-manifest.json"
    manifest = json.loads(manifest_p.read_text(encoding="utf-8"))
    for field in (
        "phase",
        "target_id",
        "reproduction_size",
        "reproduction_source",
        "algorithms",
        "budget_sec_per_seed",
        "max_evaluations_per_seed",
        "seeds",
        "funsearch_evaluations",
        "funsearch_source",
        "verdict_rule",
    ):
        assert field in manifest, f"missing manifest field: {field}"
    assert manifest["phase"] == "P174"
    assert manifest["target_id"] == "cap_set_8"
    assert manifest["reproduction_size"] == 512
    assert set(manifest["algorithms"]) == {"BytecodeEvolution", "RandomSearch", "SimulatedAnnealing"}
    fe = manifest["funsearch_evaluations"]
    assert (isinstance(fe, int) and fe > 0) or fe == "not_obtained"
    vr = manifest["verdict_rule"]
    assert set(vr) == {"H2_SUPPORTED", "H2_REPRODUCED", "H2_NOT_SUPPORTED", "H2_INCONCLUSIVE"}


def test_manifest_has_no_example_placeholder() -> None:
    manifest_p = Path(__file__).resolve().parents[1] / "experiments" / "p174-h2-manifest.json"
    raw = manifest_p.read_text(encoding="utf-8")
    assert "123456789" not in raw


def test_no_llm_no_network_in_loop() -> None:
    banned = {"openai", "anthropic", "transformers", "requests", "urllib", "socket", "torch.hub"}
    repo = Path(__file__).resolve().parents[1]
    targets = [repo / "src" / "evobyte" / "priority_evolution.py"]
    bench = repo / "benchmarks" / "h2_capset_evolution.py"
    if bench.exists():
        targets.append(bench)
    assert targets[0].exists()
    for path in targets:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported.add(node.module.split(".")[0])
        assert not (banned & imported), f"{path.name} imports banned: {banned & imported}"
