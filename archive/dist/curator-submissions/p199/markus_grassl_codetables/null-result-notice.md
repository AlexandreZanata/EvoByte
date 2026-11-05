# Notice of Negative Bound: Circulant CSS Structure for [[14, 3, 4]] and [[16, 5, 4]]

**Repository:** codetables.de (Markus Grassl)  
**Investigated Open Targets:**
1. `[[14, 3, d]]`: Known best $d=3$. Open question: Can $d=4$ be achieved?
2. `[[16, 5, d]]`: Known best $d=3$. Open question: Can $d=4$ be achieved?

## Findings
Across comprehensive random sampling and structured search using pure circulant CSS codes over cyclic blocks of orders 7 and 8, the maximum code distance strictly satisfies $d \le 3$.
- **Theorem / Empirical Bound:** No pure circulant CSS stabilizer code achieves $d \ge 4$ on 14 or 16 qubits with $k=3$ or $k=5$.
- **Conclusion:** Any code achieving $d=4$ must break circulant block symmetry and utilize non-circulant matrices.
