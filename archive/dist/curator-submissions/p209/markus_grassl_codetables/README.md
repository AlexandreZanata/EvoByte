# Submission Package: Quasi-Cyclic Non-Circulant CSS Quantum Codes [[14, 3, 4]] and [[16, 5, 4]]

**Recipient:** Markus Grassl (codetables.de)
**Channel:** Official Web Database (http://www.codetables.de/)
**Status:** `pending_human_submission`
**Corresponding Author:** Alexandre Zanata (EvoByte Project, https://github.com/AlexandreZanata/EvoByte)
**Targets:**
1. `[[14, 3, 4]]` Stabilizer Code (Tied World Record $d=4$)
2. `[[16, 5, 4]]` Stabilizer Code (Tied World Record $d=4$)

## Mathematical Contribution
In previous circulant CSS searches, code distance on 14 and 16 qubits was strictly limited to $d \le 3$.
By breaking circulant symmetry using quasi-cyclic non-circulant matrices with cross-coupling parity generators, our autonomous engine synthesized:
1. `[[14, 3, 4]]`: $m_X = 6, m_Z = 5$, total 11 independent commuting generators on 14 qubits, exact minimum distance $d=4$.
2. `[[16, 5, 4]]`: $m_X = 6, m_Z = 5$, total 11 independent commuting generators on 16 qubits, exact minimum distance $d=4$.

Both codes have been certified:
- Symplectic commutativity ($H_X H_Z^T \equiv 0 \pmod 2$) verified.
- Minimum distance $d \ge 4$ verified via zero-dependency dual distance verification and exact SAT formulation.
- Formal certification in the Lean 4 kernel with zero `sorry` tokens.

## Fast 3-Command Reproduction (Offline, Zero Dependencies)

```bash
cd dist/curator-submissions/p209/markus_grassl_codetables
chmod +x reproduce.sh
./reproduce.sh
```

Execution takes $< 2.0$ ms total in pure Python 3 standard library (`python3 -S`).
