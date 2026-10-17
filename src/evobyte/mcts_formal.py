"""Monte Carlo Tree Search (MCTS) over Lean 4 tactic spaces guided by kernel feedback (P108).

Spec: docs/phases/P108-tactic-tree-formal-mcts.md
Systematic formal exploration of Lean 4 tactic trees with direct binary reward from
the Lean 4 compiler (lake env lean --stdin), guided by neural proposer priors and
pruning obstructions. Zero sorry, zero heuristic shortcuts.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from evobyte.models import CANONICAL_LEAN_TACTICS, StructuredConditionalProposer


@dataclass
class FormalMCTSConfig:
    """Configuration hyperparameters for formal Lean 4 tactic tree MCTS."""

    max_iterations: int = 30
    max_depth: int = 3
    c_puct: float = 1.414
    timeout_sec: float = 20.0
    allowed_tactics: list[str] = field(
        default_factory=lambda: [
            "omega",
            "ring",
            "norm_num",
            "linarith",
            "nlinarith",
            "aesop",
            "positivity",
            "decide",
            "intro h; omega",
            "intros; ring",
            "intro h; linarith",
        ]
    )


class MCTSNode:
    """A node in the Lean 4 tactic search tree."""

    def __init__(
        self,
        tactic_chain: tuple[str, ...],
        parent: MCTSNode | None = None,
        action: str | None = None,
        prior: float = 1.0,
    ) -> None:
        self.tactic_chain = tactic_chain
        self.parent = parent
        self.action = action
        self.prior = prior
        self.children: dict[str, MCTSNode] = {}
        self.visit_count: int = 0
        self.total_value: float = 0.0
        self.is_terminal: bool = False
        self.is_proved: bool = False
        self.depth: int = len(tactic_chain)

    @property
    def q_value(self) -> float:
        """Mean action value (Q)."""
        if self.visit_count == 0:
            return 0.0
        return self.total_value / self.visit_count

    def puct_score(self, c_puct: float, parent_visits: int) -> float:
        """Compute Polynomial Upper Confidence Trees (PUCT) score."""
        exploration = c_puct * self.prior * (math.sqrt(max(1, parent_visits)) / (1 + self.visit_count))
        return self.q_value + exploration

    def select_child(self, c_puct: float) -> tuple[str, MCTSNode]:
        """Select best child action maximizing PUCT score."""
        best_score = -float("inf")
        best_pair = ("", self)
        for action, child in self.children.items():
            score = child.puct_score(c_puct, self.visit_count)
            if score > best_score:
                best_score = score
                best_pair = (action, child)
        return best_pair


@dataclass
class MCTSResult:
    """Outcome of an MCTS formal proof search session."""

    is_proved: bool
    proof_script: str | None
    best_tactic_chain: list[str]
    iterations_executed: int
    nodes_expanded: int
    max_depth_reached: int
    elapsed_sec: float
    verified_by_lean: bool
    has_sorry: bool = False


class FormalMCTSSearcher:
    """MCTS engine for Lean 4 theorem proving with direct binary compiler feedback."""

    def __init__(
        self,
        config: FormalMCTSConfig | None = None,
        proposer: StructuredConditionalProposer | None = None,
        oracle: Callable[[str, list[str]], dict[str, Any]] | None = None,
    ) -> None:
        self.config = config or FormalMCTSConfig()
        self.proposer = proposer
        self.oracle = oracle

    def _get_priors(self, actions: list[str], a: int = 4, n: int = 101) -> dict[str, float]:
        """Obtain prior probabilities for actions using neural proposer if available."""
        if self.proposer is not None:
            try:
                tac_dist = dict(self.proposer.predict_tactics(a, n))
                priors: dict[str, float] = {}
                total = 0.0
                for act in actions:
                    # Match base tactic from composite string if needed
                    base = act.split(";")[-1].strip().split()[0] if ";" in act else act.split()[0]
                    p = tac_dist.get(base, 0.05)
                    priors[act] = p
                    total += p
                if total > 0:
                    return {k: v / total for k, v in priors.items()}
            except Exception:
                pass

        # Uniform fallback
        u = 1.0 / max(1, len(actions))
        return {act: u for act in actions}

    def search(
        self,
        theorem_decl: str,
        imports: list[str] | None = None,
        a: int = 4,
        n: int = 101,
        project_dir: str | Path = "lean_proofs",
    ) -> MCTSResult:
        """Search for a valid Lean 4 tactic sequence that proves theorem_decl without sorry."""
        from evobyte.formal_bridge import evaluate_lean4_tactic_candidate

        oracle_fn = self.oracle or (
            lambda thm, tacs: evaluate_lean4_tactic_candidate(
                thm, tacs, imports=imports, project_dir=project_dir
            )
        )

        t0 = time.perf_counter()
        root = MCTSNode(tactic_chain=())
        actions = list(self.config.allowed_tactics)
        priors = self._get_priors(actions, a=a, n=n)

        # Expand root
        for act in actions:
            child = MCTSNode(
                tactic_chain=(act,),
                parent=root,
                action=act,
                prior=priors.get(act, 1.0 / len(actions)),
            )
            root.children[act] = child

        nodes_expanded = len(actions) + 1
        max_depth_reached = 1
        is_proved = False
        proved_script: str | None = None
        best_chain: list[str] = []
        verified_by_lean = False

        for iteration in range(1, self.config.max_iterations + 1):
            if time.perf_counter() - t0 > self.config.timeout_sec:
                break

            # 1. Selection
            node = root
            while node.children and not node.is_terminal:
                _, node = node.select_child(self.config.c_puct)

            current_chain = list(node.tactic_chain)
            if node.depth > max_depth_reached:
                max_depth_reached = node.depth

            # 2. Evaluation with Lean 4 Kernel
            eval_result = oracle_fn(theorem_decl, current_chain)
            if eval_result.get("success", False) and not eval_result.get("has_sorry", True):
                # PROVED!
                node.is_proved = True
                node.is_terminal = True
                is_proved = True
                verified_by_lean = True
                best_chain = current_chain
                proved_script = "by\n  " + "\n  ".join(current_chain)
                reward = 1.0

                # Backpropagate and exit early
                curr: MCTSNode | None = node
                while curr is not None:
                    curr.visit_count += 1
                    curr.total_value += reward
                    curr = curr.parent
                break
            else:
                reward = 0.0

            # 3. Expansion if not at max_depth and not terminal
            if node.depth < self.config.max_depth and not node.is_terminal:
                child_priors = self._get_priors(actions, a=a, n=n)
                for act in actions:
                    if act not in node.children:
                        new_chain = tuple(list(node.tactic_chain) + [act])
                        child = MCTSNode(
                            tactic_chain=new_chain,
                            parent=node,
                            action=act,
                            prior=child_priors.get(act, 1.0 / len(actions)),
                        )
                        node.children[act] = child
                        nodes_expanded += 1
            else:
                node.is_terminal = True

            # 4. Backpropagation
            curr = node
            while curr is not None:
                curr.visit_count += 1
                curr.total_value += reward
                curr = curr.parent

        elapsed = time.perf_counter() - t0

        if not is_proved:
            # Pick most visited leaf
            best_child = max(root.children.values(), key=lambda c: c.visit_count, default=None)
            if best_child is not None:
                best_chain = list(best_child.tactic_chain)

        return MCTSResult(
            is_proved=is_proved,
            proof_script=proved_script,
            best_tactic_chain=best_chain,
            iterations_executed=iteration,
            nodes_expanded=nodes_expanded,
            max_depth_reached=max_depth_reached,
            elapsed_sec=elapsed,
            verified_by_lean=verified_by_lean,
            has_sorry=False,
        )


def get_default_formal_mcts_benchmark_goals() -> list[dict[str, Any]]:
    """Curated formal benchmark goals covering algebraic, arithmetic, and bound lemmas."""
    return [
        {
            "id": "goal_ring_square",
            "name": "Binomial expansion identity",
            "decl": "theorem mcts_ring_square (x y : Nat) : (x + y)^2 = x^2 + 2*x*y + y^2",
            "expected_tactic": "ring",
        },
        {
            "id": "goal_nat_ineq_bound",
            "name": "Linear bound inequality",
            "decl": "theorem mcts_nat_bound (n : Nat) (h : n >= 4) : 4 * n > n + 3",
            "expected_tactic": "omega",
        },
        {
            "id": "goal_arith_eval",
            "name": "Exact integer arithmetic identity",
            "decl": "theorem mcts_arith_eval : 4 * 2 * 4 * 20 = 5 * (4 * 20 + 2 * 20 + 2 * 4)",
            "expected_tactic": "norm_num",
        },
        {
            "id": "goal_linarith_trans",
            "name": "Linear strict ordering transitivity",
            "decl": "theorem mcts_linear_order (a b c : Nat) (h1 : a + 1 <= b) (h2 : b + 2 <= c) : a + 3 <= c",
            "expected_tactic": "omega",
        },
        {
            "id": "goal_algebraic_cube_factor",
            "name": "Cubic difference formula",
            "decl": "theorem mcts_cube_factor (a b : Nat) : (a + b) * (a^2 - a*b + b^2) = a^3 + b^3",
            "expected_tactic": "ring",
        },
        {
            "id": "goal_mod_parity_even",
            "name": "Even square parity division",
            "decl": "theorem mcts_even_div (k : Nat) : 2 * (k * 2) = 4 * k",
            "expected_tactic": "omega",
        },
        {
            "id": "goal_norm_num_frac",
            "name": "Concrete unit fraction equivalence",
            "decl": "theorem mcts_unit_frac : 4 * 3 * 4 = 12 + 12 + 24",
            "expected_tactic": "norm_num",
        },
        {
            "id": "goal_strict_mono",
            "name": "Strict monotonicity bound",
            "decl": "theorem mcts_strict_mono (x : Nat) (h : x > 0) : x + x >= 2",
            "expected_tactic": "omega",
        },
    ]


def run_formal_mcts_benchmark(
    searcher: FormalMCTSSearcher,
    goals: list[dict[str, Any]] | None = None,
    project_dir: str | Path = "lean_proofs",
) -> dict[str, Any]:
    """Run formal MCTS benchmark across curated mathematical proof goals."""
    test_goals = goals or get_default_formal_mcts_benchmark_goals()
    t0 = time.perf_counter()

    results: list[dict[str, Any]] = []
    proved_count = 0
    total_iterations = 0
    total_nodes = 0
    max_depth_all = 0

    for g in test_goals:
        res = searcher.search(
            theorem_decl=g["decl"],
            project_dir=project_dir,
        )
        if res.is_proved:
            proved_count += 1

        total_iterations += res.iterations_executed
        total_nodes += res.nodes_expanded
        if res.max_depth_reached > max_depth_all:
            max_depth_all = res.max_depth_reached

        results.append({
            "id": g["id"],
            "name": g["name"],
            "decl": g["decl"],
            "is_proved": res.is_proved,
            "proof_script": res.proof_script,
            "best_tactic_chain": res.best_tactic_chain,
            "iterations": res.iterations_executed,
            "nodes_expanded": res.nodes_expanded,
            "elapsed_sec": res.elapsed_sec,
            "verified_by_lean": res.verified_by_lean,
        })

    elapsed = time.perf_counter() - t0
    N = len(test_goals)
    closure_rate = float(proved_count / max(1, N))

    return {
        "total_goals": N,
        "proved_goals": proved_count,
        "closure_rate": round(closure_rate, 4),
        "avg_iterations": round(total_iterations / max(1, N), 2),
        "avg_nodes_expanded": round(total_nodes / max(1, N), 2),
        "max_depth": max_depth_all,
        "elapsed_sec": round(elapsed, 4),
        "all_proved": (proved_count == N),
        "zero_sorry": True,
        "results": results,
    }
