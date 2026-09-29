"""Q-Forge smoke: conserved-operator baseline + oracle demo (Q04 scope)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from evobyte.quantum.hamiltonians import (
    commutator_norm,
    exact,
    hamiltonian_hash,
    heisenberg,
    ising,
    total_sz,
)
from evobyte.quantum.pauli import decode_human, Pauli
from evobyte.quantum.search import random_conserved_search


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--experiment", default="conserved", choices=["conserved"])
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--qubits", type=int, default=4)
    ap.add_argument("--budget", type=int, default=20000)
    args = ap.parse_args()

    n = args.qubits
    h = heisenberg(n)
    owe = exact(h, n)
    print(f"oracle: heisenberg-{n} E_exact={owe['E_exact']:.6f} hash={hamiltonian_hash(h)}")
    sz_norm = commutator_norm(h, total_sz(n), n)
    print(f"oracle: total-Sz commutator norm={sz_norm:.2e} (expected ~0)")
    assert sz_norm < 1e-9

    h2 = ising(n)
    print(f"oracle: ising-{n} E_exact={exact(h2, n)['E_exact']:.6f} hash={hamiltonian_hash(h2)}")

    for seed in range(args.seeds):
        out = random_conserved_search(h, n, budget=args.budget, n_terms=1, seed=seed)
        terms = ", ".join(decode_human(Pauli(t.x_mask, t.z_mask, 0, n)) for t in out["candidate"])
        print(
            f"seed={seed} best_norm={out['commutator_error']:.3e} "
            f"candidate=[{terms}] qps={out['qps']:.0f} budget={out['budget']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
