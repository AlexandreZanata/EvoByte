"""Unit and integration tests for P108 Lean 4 tactic tree formal MCTS engine."""

from __future__ import annotations

from evobyte.formal_bridge import (
    evaluate_lean4_tactic_candidate,
    verify_formal_mcts_soundness,
)
from evobyte.mcts_formal import (
    FormalMCTSConfig,
    FormalMCTSSearcher,
    MCTSNode,
    get_default_formal_mcts_benchmark_goals,
    run_formal_mcts_benchmark,
)
from evobyte.models import StructuredConditionalProposer


def test_mcts_node_puct_selection():
    root = MCTSNode(tactic_chain=())
    c1 = MCTSNode(tactic_chain=("omega",), parent=root, action="omega", prior=0.7)
    c2 = MCTSNode(tactic_chain=("ring",), parent=root, action="ring", prior=0.3)
    root.children["omega"] = c1
    root.children["ring"] = c2

    # Initial selection with 0 visits follows prior
    best_act, best_child = root.select_child(c_puct=1.414)
    assert best_act == "omega"
    assert best_child is c1

    # Update visit counts and values
    c1.visit_count = 5
    c1.total_value = 0.0  # Q = 0.0
    c2.visit_count = 1
    c2.total_value = 1.0  # Q = 1.0
    root.visit_count = 6

    # C2 has higher Q value now
    best_act2, _best_child2 = root.select_child(c_puct=1.0)
    assert best_act2 == "ring"


def test_evaluate_lean4_tactic_candidate_success_and_failure():
    # Omega success
    res_omega = evaluate_lean4_tactic_candidate(
        "theorem test_om (a b : Nat) : a + b = b + a",
        ["omega"],
    )
    assert res_omega["success"] is True
    assert res_omega["has_sorry"] is False

    # Ring success on binomial
    res_ring = evaluate_lean4_tactic_candidate(
        "theorem test_rg (x y : Nat) : (x + y)^2 = x^2 + 2*x*y + y^2",
        ["ring"],
    )
    assert res_ring["success"] is True

    # Failed tactic
    res_fail = evaluate_lean4_tactic_candidate(
        "theorem test_fail (x y : Nat) : (x + y)^2 = x^2 + 2*x*y + y^2",
        ["decide"],
    )
    assert res_fail["success"] is False


def test_reject_sorry_tokens():
    res = evaluate_lean4_tactic_candidate(
        "theorem test_s (n : Nat) : n = n",
        ["sorry"],
    )
    assert res["success"] is False
    assert res["has_sorry"] is True

    res2 = evaluate_lean4_tactic_candidate(
        "theorem test_s2 (n : Nat) : sorry = n",
        ["omega"],
    )
    assert res2["success"] is False
    assert res2["has_sorry"] is True


def test_mcts_searcher_binomial():
    searcher = FormalMCTSSearcher(config=FormalMCTSConfig(max_iterations=10, max_depth=2))
    decl = "theorem mcts_unit_square (x y : Nat) : (x + y)^2 = x^2 + 2*x*y + y^2"
    result = searcher.search(decl)

    assert result.is_proved is True
    assert result.verified_by_lean is True
    assert result.has_sorry is False
    assert "ring" in result.best_tactic_chain


def test_mcts_searcher_linear_ineq():
    searcher = FormalMCTSSearcher(config=FormalMCTSConfig(max_iterations=10, max_depth=2))
    decl = "theorem mcts_unit_bound (n : Nat) (h : n >= 4) : 4 * n > n + 3"
    result = searcher.search(decl)

    assert result.is_proved is True
    assert result.verified_by_lean is True
    assert "omega" in result.best_tactic_chain


def test_mcts_guided_by_neural_proposer():
    proposer = StructuredConditionalProposer()
    searcher = FormalMCTSSearcher(
        config=FormalMCTSConfig(max_iterations=10, max_depth=2),
        proposer=proposer,
    )
    decl = "theorem mcts_proposer_eval : 4 * 2 * 4 * 20 = 5 * (4 * 20 + 2 * 20 + 2 * 4)"
    result = searcher.search(decl)

    assert result.is_proved is True
    assert result.verified_by_lean is True
    assert len(result.best_tactic_chain) > 0
    assert any(
        any(t in tac for t in ["norm_num", "decide", "omega", "ring"])
        for tac in result.best_tactic_chain
    )


def test_run_formal_mcts_benchmark():
    searcher = FormalMCTSSearcher(config=FormalMCTSConfig(max_iterations=15, max_depth=2))
    goals = get_default_formal_mcts_benchmark_goals()[:4]
    bench_res = run_formal_mcts_benchmark(searcher, goals=goals)

    assert bench_res["total_goals"] == 4
    assert bench_res["proved_goals"] == 4
    assert bench_res["closure_rate"] == 1.0
    assert bench_res["zero_sorry"] is True

    sound, findings = verify_formal_mcts_soundness(
        {"closure_rate": 1.0, "proved_goals": 4, "zero_sorry": True, "has_sorry": False},
        min_closure_rate=0.75,
        min_proved_goals=4,
    )
    assert sound is True
    assert len(findings) == 0
