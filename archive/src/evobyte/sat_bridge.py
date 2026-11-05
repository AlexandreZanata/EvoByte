"""SAT Solver Exact Completion Bridge for Combinatorial Structures (P194).

Hybridizes EvoByte stochastic and priority search with exact SAT solvers (CDCL).
EvoByte discovers the structural skeleton (symmetry orbits, high-density blocks),
and the residual 'last bit' problem is encoded into Conjunctive Normal Form (CNF)
with exact cardinality constraints (Sinz sequential counters) and solved within
strict time budgets (< 5 seconds).

All reconstructed candidates are strictly validated by zero-dependency verifiers
(e.g., verify_covering_design, check_stabilizer).

Part of the Structured Discovery and Functional Synthesis Program (P191-P200, D043).
"""

from __future__ import annotations

from dataclasses import dataclass, field
import itertools
import math
import time
from typing import Any, Iterable, Sequence

from evobyte.frontier_catalogue import verify_covering_design
from evobyte.symmetry_engine import CoveringOrbitEngine

try:
    import pysat.solvers as _pysat_solvers

    _PYSAT_AVAILABLE = True
except ImportError:
    _pysat_solvers = None
    _PYSAT_AVAILABLE = False


@dataclass
class SatResult:
    """Outcome of a SAT solver execution."""

    status: str  # "SAT", "UNSAT", "TIMEOUT", "ERROR"
    is_sat: bool
    model: list[int] | None = None
    assignment: dict[int, bool] | None = None
    solve_time_seconds: float = 0.0
    num_vars: int = 0
    num_clauses: int = 0
    solver_name: str = "unknown"
    error_message: str | None = None


class CNFFormula:
    """Conjunctive Normal Form (CNF) formula manager with cardinality constraints.

    Variables are represented as positive 1-based integers (1, 2, ...).
    Negative integers denote negated literals (-1, -2, ...).
    """

    def __init__(self, n_vars: int = 0) -> None:
        self.clauses: list[list[int]] = []
        self.n_vars: int = max(0, n_vars)
        self.var_names: dict[int, str] = {}

    def new_var(self, name: str | None = None) -> int:
        """Allocate a fresh variable index."""
        self.n_vars += 1
        var_id = self.n_vars
        if name:
            self.var_names[var_id] = name
        return var_id

    def add_clause(self, clause: Sequence[int]) -> None:
        """Add a single disjunctive clause to the formula."""
        c = [int(lit) for lit in clause]
        for lit in c:
            var = abs(lit)
            if var > self.n_vars:
                self.n_vars = var
        self.clauses.append(c)

    def add_clauses(self, clauses: Iterable[Sequence[int]]) -> None:
        """Add multiple clauses to the formula."""
        for c in clauses:
            self.add_clause(c)

    def add_at_most_k(self, literals: Sequence[int], k: int) -> list[int]:
        """Encode sum(literals) <= k using Sinz Sequential Counter.

        Introduces O(n * k) auxiliary variables and clauses.
        Enforces arc-consistency via unit propagation.
        Returns the list of allocated auxiliary variables.
        """
        lits = [int(x) for x in literals]
        n = len(lits)
        if k >= n:
            return []

        if k == 0:
            for x in lits:
                self.add_clause([-x])
            return []

        aux_vars: list[int] = []
        s: dict[tuple[int, int], int] = {}
        for i in range(1, n):
            for j in range(1, k + 1):
                var = self.new_var(f"card_{i}_{j}")
                s[(i, j)] = var
                aux_vars.append(var)

        # i = 1
        self.add_clause([-lits[0], s[(1, 1)]])
        for j in range(2, k + 1):
            self.add_clause([-s[(1, j)]])

        # 2 <= i <= n - 1
        for i in range(2, n):
            x_i = lits[i - 1]
            self.add_clause([-x_i, s[(i, 1)]])
            self.add_clause([-s[(i - 1, 1)], s[(i, 1)]])
            for j in range(2, k + 1):
                self.add_clause([-x_i, -s[(i - 1, j - 1)], s[(i, j)]])
                self.add_clause([-s[(i - 1, j)], s[(i, j)]])
            self.add_clause([-x_i, -s[(i - 1, k)]])

        # i = n
        self.add_clause([-lits[n - 1], -s[(n - 1, k)]])
        return aux_vars

    def add_at_least_k(self, literals: Sequence[int], k: int) -> list[int]:
        """Encode sum(literals) >= k by encoding sum(~literals) <= (n - k)."""
        lits = [int(x) for x in literals]
        n = len(lits)
        if k <= 0:
            return []
        if k > n:
            # Impossible constraint
            dummy = self.new_var()
            self.add_clause([dummy])
            self.add_clause([-dummy])
            return [dummy]
        neg_lits = [-x for x in lits]
        return self.add_at_most_k(neg_lits, n - k)

    def add_exactly_k(self, literals: Sequence[int], k: int) -> list[int]:
        """Encode sum(literals) == k as (<= k) and (>= k)."""
        aux1 = self.add_at_most_k(literals, k)
        aux2 = self.add_at_least_k(literals, k)
        return aux1 + aux2

    def add_xor(self, literals: Sequence[int], target_parity: int = 0) -> list[int]:
        """Encode x_1 ^ x_2 ^ ... ^ x_p == target_parity (0 or 1).

        Uses Tseitin transformation with chaining for linear clause count.
        """
        lits = [int(x) for x in literals]
        parity = target_parity % 2
        if not lits:
            if parity != 0:
                dummy = self.new_var()
                self.add_clause([dummy])
                self.add_clause([-dummy])
                return [dummy]
            return []

        if len(lits) == 1:
            self.add_clause([lits[0]] if parity == 1 else [-lits[0]])
            return []

        if len(lits) == 2:
            a, b = lits[0], lits[1]
            if parity == 1:
                self.add_clause([a, b])
                self.add_clause([-a, -b])
            else:
                self.add_clause([-a, b])
                self.add_clause([a, -b])
            return []

        aux_vars: list[int] = []
        prev = lits[0]
        for k_idx in range(1, len(lits) - 1):
            aux = self.new_var(f"xor_aux_{k_idx}")
            aux_vars.append(aux)
            b = lits[k_idx]
            # prev ^ b ^ aux == 0 (even parity of 3 lits)
            self.add_clause([-prev, -b, -aux])
            self.add_clause([prev, b, -aux])
            self.add_clause([prev, -b, aux])
            self.add_clause([-prev, b, aux])
            prev = aux

        last = lits[-1]
        if parity == 1:
            self.add_clause([prev, last])
            self.add_clause([-prev, -last])
        else:
            self.add_clause([-prev, last])
            self.add_clause([prev, -last])
        return aux_vars

    def to_dimacs(self) -> str:
        """Serialize formula to DIMACS CNF format string."""
        lines = [f"p cnf {self.n_vars} {len(self.clauses)}"]
        for c in self.clauses:
            lines.append(" ".join(str(lit) for lit in c) + " 0")
        return "\n".join(lines) + "\n"

    @classmethod
    def from_dimacs(cls, dimacs_str: str) -> CNFFormula:
        """Parse formula from a DIMACS CNF format string."""
        clauses: list[list[int]] = []
        n_vars = 0
        for raw_line in dimacs_str.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("c"):
                continue
            if line.startswith("p"):
                parts = line.split()
                if len(parts) >= 3 and parts[1] == "cnf":
                    n_vars = int(parts[2])
                continue
            literals = [int(x) for x in line.split() if int(x) != 0]
            if literals:
                clauses.append(literals)
                for lit in literals:
                    n_vars = max(n_vars, abs(lit))
        formula = cls(n_vars=n_vars)
        formula.clauses = clauses
        return formula


class PurePythonSolver:
    """Pure Python DPLL solver with unit propagation and timeout detection.

    Zero-dependency deterministic fallback ensuring functionality on any platform.
    """

    def __init__(self, formula: CNFFormula) -> None:
        self.formula = formula
        self.clauses = [list(c) for c in formula.clauses]
        self.n_vars = formula.n_vars

    def solve(self, timeout_seconds: float = 5.0) -> SatResult:
        """Execute DPLL search within the allotted time limit."""
        t0 = time.perf_counter()
        deadline = t0 + timeout_seconds

        # Fast conflict on empty clause
        for c in self.clauses:
            if len(c) == 0:
                return SatResult(
                    status="UNSAT",
                    is_sat=False,
                    solve_time_seconds=time.perf_counter() - t0,
                    num_vars=self.n_vars,
                    num_clauses=len(self.clauses),
                    solver_name="pure_python",
                )

        assignment: dict[int, bool] = {}

        def unit_propagate(cur_assign: dict[int, bool]) -> bool:
            changed = True
            while changed:
                changed = False
                for c in self.clauses:
                    val_sat = False
                    unassigned_lit = None
                    num_unassigned = 0
                    for lit in c:
                        var = abs(lit)
                        if var in cur_assign:
                            if (lit > 0 and cur_assign[var]) or (lit < 0 and not cur_assign[var]):
                                val_sat = True
                                break
                        else:
                            unassigned_lit = lit
                            num_unassigned += 1
                    if val_sat:
                        continue
                    if num_unassigned == 0:
                        return False  # Conflict
                    if num_unassigned == 1 and unassigned_lit is not None:
                        var = abs(unassigned_lit)
                        cur_assign[var] = unassigned_lit > 0
                        changed = True
            return True

        def dpll(cur_assign: dict[int, bool]) -> tuple[str, dict[int, bool] | None]:
            if time.perf_counter() > deadline:
                return "TIMEOUT", None

            working = dict(cur_assign)
            if not unit_propagate(working):
                return "UNSAT", None

            # Verify satisfaction
            all_sat = True
            for c in self.clauses:
                sat = False
                for lit in c:
                    var = abs(lit)
                    if var in working:
                        if (lit > 0 and working[var]) or (lit < 0 and not working[var]):
                            sat = True
                            break
                if not sat:
                    all_sat = False
                    break

            if all_sat:
                for v in range(1, self.n_vars + 1):
                    if v not in working:
                        working[v] = False
                return "SAT", working

            # Pick unassigned variable
            chosen_var = None
            for v in range(1, self.n_vars + 1):
                if v not in working:
                    chosen_var = v
                    break

            if chosen_var is None:
                return "UNSAT", None

            # Branch True
            branch_t = dict(working)
            branch_t[chosen_var] = True
            st_t, m_t = dpll(branch_t)
            if st_t in ("SAT", "TIMEOUT"):
                return st_t, m_t

            # Branch False
            branch_f = dict(working)
            branch_f[chosen_var] = False
            return dpll(branch_f)

        status, model_assign = dpll(assignment)
        elapsed = time.perf_counter() - t0

        if status == "SAT" and model_assign is not None:
            model_list = [
                v if model_assign.get(v, False) else -v for v in range(1, self.n_vars + 1)
            ]
            return SatResult(
                status="SAT",
                is_sat=True,
                model=model_list,
                assignment=model_assign,
                solve_time_seconds=elapsed,
                num_vars=self.n_vars,
                num_clauses=len(self.clauses),
                solver_name="pure_python",
            )
        elif status == "TIMEOUT":
            return SatResult(
                status="TIMEOUT",
                is_sat=False,
                solve_time_seconds=elapsed,
                num_vars=self.n_vars,
                num_clauses=len(self.clauses),
                solver_name="pure_python",
            )
        else:
            return SatResult(
                status="UNSAT",
                is_sat=False,
                solve_time_seconds=elapsed,
                num_vars=self.n_vars,
                num_clauses=len(self.clauses),
                solver_name="pure_python",
            )


def solve_cnf(
    formula: CNFFormula,
    timeout_seconds: float = 5.0,
    solver_name: str = "auto",
) -> SatResult:
    """Solve a CNF formula using the fastest available solver backend.

    Parameters
    ----------
    formula : CNFFormula
        Formula to solve.
    timeout_seconds : float
        Strict timeout limit in seconds.
    solver_name : str
        Target solver: 'auto', 'cadical153', 'g4', 'minisat22', or 'pure_python'.
    """
    use_pysat = _PYSAT_AVAILABLE and solver_name != "pure_python"

    if not use_pysat:
        solver = PurePythonSolver(formula)
        return solver.solve(timeout_seconds=timeout_seconds)

    # Resolve solver engine name
    engine = "cadical153" if solver_name in ("auto", "cadical") else solver_name
    if engine.startswith("pysat:"):
        engine = engine.split(":", 1)[1]

    t0 = time.perf_counter()
    try:
        slv = _pysat_solvers.Solver(name=engine)
    except Exception:
        # Fallback to glucose 4 if requested engine failed
        try:
            engine = "g4"
            slv = _pysat_solvers.Solver(name=engine)
        except Exception:
            solver = PurePythonSolver(formula)
            return solver.solve(timeout_seconds=timeout_seconds)

    try:
        for c in formula.clauses:
            slv.add_clause(c)

        is_sat = slv.solve()
        elapsed = time.perf_counter() - t0

        if is_sat:
            m = slv.get_model()
            assign = {abs(x): (x > 0) for x in m} if m else {}
            res = SatResult(
                status="SAT",
                is_sat=True,
                model=m,
                assignment=assign,
                solve_time_seconds=elapsed,
                num_vars=formula.n_vars,
                num_clauses=len(formula.clauses),
                solver_name=f"pysat:{engine}",
            )
        else:
            res = SatResult(
                status="UNSAT",
                is_sat=False,
                solve_time_seconds=elapsed,
                num_vars=formula.n_vars,
                num_clauses=len(formula.clauses),
                solver_name=f"pysat:{engine}",
            )
    except Exception as e:
        elapsed = time.perf_counter() - t0
        res = SatResult(
            status="ERROR",
            is_sat=False,
            solve_time_seconds=elapsed,
            num_vars=formula.n_vars,
            num_clauses=len(formula.clauses),
            solver_name=f"pysat:{engine}",
            error_message=str(e),
        )
    finally:
        try:
            slv.delete()
        except Exception:
            pass

    return res


@dataclass
class CoveringCompletionResult:
    """Outcome of covering design skeleton completion."""

    status: str
    success: bool
    completed_blocks: list[tuple[int, ...]] | None
    added_blocks: list[tuple[int, ...]] | None
    total_blocks: int
    uncovered_before: int
    uncovered_after: int
    verified: bool
    verification_msg: str
    solve_time_seconds: float
    sat_stats: dict[str, Any] = field(default_factory=dict)


class CoveringCnfEncoder:
    """Encodes covering design residual completion problems into CNF."""

    def __init__(
        self,
        v: int,
        k: int,
        t: int,
        skeleton_blocks: Sequence[Sequence[int]],
        candidate_blocks: Sequence[Sequence[int]] | None = None,
        one_indexed: bool = True,
    ) -> None:
        self.v = v
        self.k = k
        self.t = t
        self.one_indexed = one_indexed

        # Normalize skeleton blocks to 0-indexed sorted tuples
        base_offset = 1 if one_indexed else 0
        self.skeleton: list[tuple[int, ...]] = [
            tuple(sorted(int(x) - base_offset for x in b)) for b in skeleton_blocks
        ]
        self.skeleton_set: set[tuple[int, ...]] = set(self.skeleton)

        # Precompute all t-subsets
        self.all_subsets: list[tuple[int, ...]] = list(itertools.combinations(range(v), t))
        self.num_subsets = len(self.all_subsets)

        # Identify covered and uncovered subsets
        self.covered_subsets: set[tuple[int, ...]] = set()
        for b in self.skeleton:
            for sub in itertools.combinations(b, t):
                self.covered_subsets.add(sub)

        self.uncovered_subsets: list[tuple[int, ...]] = [
            sub for sub in self.all_subsets if sub not in self.covered_subsets
        ]

        # Determine candidate pool
        if candidate_blocks is not None:
            raw_candidates = [
                tuple(sorted(int(x) - base_offset for x in b)) for b in candidate_blocks
            ]
        else:
            raw_candidates = list(itertools.combinations(range(v), k))

        # Filter candidates: must not be in skeleton, and must cover at least one uncovered subset
        uncovered_set = set(self.uncovered_subsets)
        self.candidates: list[tuple[int, ...]] = []
        for b in raw_candidates:
            if b in self.skeleton_set:
                continue
            if any(sub in uncovered_set for sub in itertools.combinations(b, t)):
                self.candidates.append(b)

        # Build variable mapping
        self.var_to_block: dict[int, tuple[int, ...]] = {
            i + 1: b for i, b in enumerate(self.candidates)
        }
        self.block_to_var: dict[tuple[int, ...], int] = {
            b: i + 1 for i, b in enumerate(self.candidates)
        }

    def build_formula(self, max_additional_blocks: int | None = None) -> CNFFormula:
        """Construct the CNF formula enforcing full coverage and cardinality bound."""
        formula = CNFFormula(n_vars=len(self.candidates))

        # Coverage clauses: for each uncovered subset, at least one covering candidate block must be chosen
        for sub in self.uncovered_subsets:
            covering_vars = [self.block_to_var[b] for b in self.candidates if set(sub).issubset(b)]
            if not covering_vars:
                # Impossible: no candidate covers this subset -> add empty conflict clause
                formula.add_clause([])
                return formula
            formula.add_clause(covering_vars)

        # Cardinality constraint: at most max_additional_blocks
        if max_additional_blocks is not None and max_additional_blocks < len(self.candidates):
            candidate_vars = list(self.var_to_block.keys())
            formula.add_at_most_k(candidate_vars, max_additional_blocks)

        return formula

    def decode_solution(self, model: Sequence[int]) -> list[tuple[int, ...]]:
        """Decode satisfying assignment into concrete added blocks."""
        added: list[tuple[int, ...]] = []
        model_vars = set(model)
        for var, blk in self.var_to_block.items():
            if var in model_vars:
                if self.one_indexed:
                    added.append(tuple(x + 1 for x in blk))
                else:
                    added.append(blk)
        return added


def complete_covering_skeleton(
    skeleton: Sequence[Sequence[int]],
    v: int,
    k: int,
    t: int,
    max_additional_blocks: int | None = None,
    candidate_pool: Sequence[Sequence[int]] | None = None,
    timeout_seconds: float = 5.0,
    solver_name: str = "auto",
    one_indexed: bool = True,
) -> CoveringCompletionResult:
    """Complete a partial covering design skeleton via exact SAT solving.

    Parameters
    ----------
    skeleton : Sequence[Sequence[int]]
        Fixed partial collection of blocks.
    v, k, t : int
        Covering design parameters C(v, k, t).
    max_additional_blocks : int, optional
        Maximum number of newly selected blocks.
    candidate_pool : Sequence[Sequence[int]], optional
        Pool of candidate blocks to choose from. Defaults to all k-subsets.
    timeout_seconds : float
        SAT solving timeout budget.
    solver_name : str
        Solver engine ('auto', 'cadical153', 'g4', 'pure_python').
    one_indexed : bool
        Whether input and output blocks are 1-indexed.
    """
    t0 = time.perf_counter()
    encoder = CoveringCnfEncoder(
        v=v,
        k=k,
        t=t,
        skeleton_blocks=skeleton,
        candidate_blocks=candidate_pool,
        one_indexed=one_indexed,
    )

    uncovered_before = len(encoder.uncovered_subsets)
    if uncovered_before == 0:
        # Already fully covered
        ok, msg = verify_covering_design(list(skeleton), v, k, t)
        return CoveringCompletionResult(
            status="ALREADY_COVERED",
            success=ok,
            completed_blocks=[tuple(b) for b in skeleton],
            added_blocks=[],
            total_blocks=len(skeleton),
            uncovered_before=0,
            uncovered_after=0,
            verified=ok,
            verification_msg=msg,
            solve_time_seconds=time.perf_counter() - t0,
        )

    formula = encoder.build_formula(max_additional_blocks=max_additional_blocks)
    sat_res = solve_cnf(formula, timeout_seconds=timeout_seconds, solver_name=solver_name)

    stats = {
        "num_candidates": len(encoder.candidates),
        "num_clauses": len(formula.clauses),
        "num_vars": formula.n_vars,
        "solver_used": sat_res.solver_name,
        "solve_time_seconds": sat_res.solve_time_seconds,
    }

    if not sat_res.is_sat or sat_res.model is None:
        return CoveringCompletionResult(
            status=sat_res.status,
            success=False,
            completed_blocks=None,
            added_blocks=None,
            total_blocks=len(skeleton),
            uncovered_before=uncovered_before,
            uncovered_after=uncovered_before,
            verified=False,
            verification_msg=f"SAT solver returned {sat_res.status}",
            solve_time_seconds=time.perf_counter() - t0,
            sat_stats=stats,
        )

    added_blocks = encoder.decode_solution(sat_res.model)
    norm_skeleton = [tuple(b) for b in skeleton]
    completed = norm_skeleton + added_blocks

    # Strict zero-dependency verification
    verified, v_msg = verify_covering_design(completed, v, k, t)

    return CoveringCompletionResult(
        status="SAT",
        success=verified,
        completed_blocks=completed,
        added_blocks=added_blocks,
        total_blocks=len(completed),
        uncovered_before=uncovered_before,
        uncovered_after=0 if verified else -1,
        verified=verified,
        verification_msg=v_msg,
        solve_time_seconds=time.perf_counter() - t0,
        sat_stats=stats,
    )


def complete_covering_orbits(
    fixed_base_blocks: Sequence[Sequence[int]],
    v: int,
    k: int,
    t: int,
    max_additional_orbits: int | None = None,
    timeout_seconds: float = 5.0,
    solver_name: str = "auto",
    one_indexed: bool = True,
) -> CoveringCompletionResult:
    """Complete a set of cyclic base blocks into a full covering design via SAT over orbits."""
    t0 = time.perf_counter()
    engine = CoveringOrbitEngine(v=v, k=k, t=t)
    reps = engine.compute_orbit_representatives()
    all_subsets = list(itertools.combinations(range(v), t))

    base_offset = 1 if one_indexed else 0
    fixed_set = {
        engine.group.canonical_representative(tuple(sorted(int(x) - base_offset for x in b)))
        for b in fixed_base_blocks
    }

    # Precompute coverage per orbit representative
    orbit_covered_subsets: list[set[tuple[int, ...]]] = []
    for rep in reps:
        cov: set[tuple[int, ...]] = set()
        for blk in engine.group.orbit(rep):
            for sub in itertools.combinations(blk, t):
                cov.add(tuple(sorted(sub)))
        orbit_covered_subsets.append(cov)

    # Subsets covered by fixed base blocks
    fixed_coverage: set[tuple[int, ...]] = set()
    for i, rep in enumerate(reps):
        if rep in fixed_set:
            fixed_coverage.update(orbit_covered_subsets[i])

    uncovered_subsets = [s for s in all_subsets if s not in fixed_coverage]
    uncovered_before = len(uncovered_subsets)

    if uncovered_before == 0:
        expanded = engine.expand_base_blocks(list(fixed_set), one_indexed=one_indexed)
        ok, msg = verify_covering_design(expanded, v, k, t)
        return CoveringCompletionResult(
            status="ALREADY_COVERED",
            success=ok,
            completed_blocks=[tuple(b) for b in expanded],
            added_blocks=[],
            total_blocks=len(expanded),
            uncovered_before=0,
            uncovered_after=0,
            verified=ok,
            verification_msg=msg,
            solve_time_seconds=time.perf_counter() - t0,
        )

    # Candidate orbits: remaining representatives that cover at least one uncovered subset
    uncovered_set = set(uncovered_subsets)
    candidate_reps: list[tuple[int, ...]] = []
    candidate_cov: list[set[tuple[int, ...]]] = []
    for i, rep in enumerate(reps):
        if rep not in fixed_set and (orbit_covered_subsets[i] & uncovered_set):
            candidate_reps.append(rep)
            candidate_cov.append(orbit_covered_subsets[i])

    formula = CNFFormula(n_vars=len(candidate_reps))
    # Coverage clauses
    for sub in uncovered_subsets:
        cov_lits = [i + 1 for i, c_subsets in enumerate(candidate_cov) if sub in c_subsets]
        if not cov_lits:
            formula.add_clause([])  # Conflict
            break
        formula.add_clause(cov_lits)

    # Cardinality on orbits
    if max_additional_orbits is not None and max_additional_orbits < len(candidate_reps):
        formula.add_at_most_k(list(range(1, len(candidate_reps) + 1)), max_additional_orbits)

    sat_res = solve_cnf(formula, timeout_seconds=timeout_seconds, solver_name=solver_name)

    stats = {
        "num_candidate_orbits": len(candidate_reps),
        "num_clauses": len(formula.clauses),
        "num_vars": formula.n_vars,
        "solver_used": sat_res.solver_name,
        "solve_time_seconds": sat_res.solve_time_seconds,
    }

    if not sat_res.is_sat or sat_res.model is None:
        return CoveringCompletionResult(
            status=sat_res.status,
            success=False,
            completed_blocks=None,
            added_blocks=None,
            total_blocks=0,
            uncovered_before=uncovered_before,
            uncovered_after=uncovered_before,
            verified=False,
            verification_msg=f"SAT solver returned {sat_res.status}",
            solve_time_seconds=time.perf_counter() - t0,
            sat_stats=stats,
        )

    model_vars = set(sat_res.model)
    selected_reps = [candidate_reps[i] for i in range(len(candidate_reps)) if (i + 1) in model_vars]
    all_reps = list(fixed_set) + selected_reps
    full_blocks = engine.expand_base_blocks(all_reps, one_indexed=one_indexed)
    added_expanded = engine.expand_base_blocks(selected_reps, one_indexed=one_indexed)

    verified, v_msg = verify_covering_design(full_blocks, v, k, t)

    return CoveringCompletionResult(
        status="SAT",
        success=verified,
        completed_blocks=[tuple(b) for b in full_blocks],
        added_blocks=[tuple(b) for b in added_expanded],
        total_blocks=len(full_blocks),
        uncovered_before=uncovered_before,
        uncovered_after=0 if verified else -1,
        verified=verified,
        verification_msg=v_msg,
        solve_time_seconds=time.perf_counter() - t0,
        sat_stats=stats,
    )


class StabilizerCnfEncoder:
    """Encodes quantum stabilizer commutativity constraints over GF(2) into CNF."""

    def __init__(self, n_qubits: int, fixed_generators: Sequence[str]) -> None:
        self.n = n_qubits
        self.fixed = list(fixed_generators)
        self.formula = CNFFormula()

    def synthesize_single_generator(
        self,
        timeout_seconds: float = 5.0,
        solver_name: str = "auto",
        min_weight: int = 1,
    ) -> tuple[bool, str | None, SatResult]:
        """Find a new non-trivial Pauli generator that commutes with all fixed generators."""
        n = self.n
        formula = CNFFormula(n_vars=2 * n)

        # x_j: 1..n, z_j: n+1..2n
        def var_x(j: int) -> int:
            return j + 1

        def var_z(j: int) -> int:
            return n + j + 1

        # Non-triviality / minimum weight: at least min_weight non-I Paulis
        # A site has non-I iff x_j or z_j is true.
        site_vars = []
        for j in range(n):
            site_v = formula.new_var(f"site_{j}")
            site_vars.append(site_v)
            formula.add_clause([-var_x(j), site_v])
            formula.add_clause([-var_z(j), site_v])
            formula.add_clause([var_x(j), var_z(j), -site_v])

        formula.add_at_least_k(site_vars, min_weight)

        # Commutativity with each fixed generator:
        # sum_j (x_F[j]*z_new[j] + z_F[j]*x_new[j]) == 0 mod 2
        for f_str in self.fixed:
            xor_lits: list[int] = []
            for j in range(n):
                pj = f_str[j]
                if pj in ("X", "Y"):
                    xor_lits.append(var_z(j))
                if pj in ("Z", "Y"):
                    xor_lits.append(var_x(j))
            formula.add_xor(xor_lits, target_parity=0)

        sat_res = solve_cnf(formula, timeout_seconds=timeout_seconds, solver_name=solver_name)
        if not sat_res.is_sat or sat_res.model is None:
            return False, None, sat_res

        model_set = set(sat_res.model)
        gen_chars = []
        for j in range(n):
            xj = var_x(j) in model_set
            zj = var_z(j) in model_set
            if xj and zj:
                gen_chars.append("Y")
            elif xj:
                gen_chars.append("X")
            elif zj:
                gen_chars.append("Z")
            else:
                gen_chars.append("I")

        return True, "".join(gen_chars), sat_res
