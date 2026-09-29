# Glossary

- **Candidate:** one 64-byte (v0) program in EvoByte bytecode.
- **CVPS:** Candidates Verified Per Second (primary metric).
- **Cascade verifier:** staged scoring (S0 validity -> S1 32 pts -> S2 256 pts
  -> S3 4096 pts -> L2 strict), cheap rejection first.
- **Level-1 / Level-2:** fast vectorized scorer for all vs. strict rare audit
  (full + held-out + extrapolation + equivalence).
- **Elite archive:** permanent host-side store of best-by-category programs.
- **Hall of Fame:** curated, committed view of top archive entries.
- **MAP-Elites:** quality-diversity grid over (size, behavior, family) bins.
- **Novelty:** behavioral distance bonus preserving structural diversity.
- **Island model:** independent populations with periodic elite migration.
- **OPCODE_VERSION:** bytecode schema version; bumps on any IR change.
- **Splits:** train (seen by evolution), validation (hyperparams), hidden
  (L2 only), extrapolation (out-of-range generalization).
- **Time-to-quality:** wall-clock seconds to reach an error threshold.
- **Autoevolution:** archive + checkpoints + resume carrying progress forward.
- **Q-Forge:** experimental EvoByte laboratory for quantum problems.
- **Symplectic Pauli representation:** `(x_mask, z_mask)` bitmask encoding
  with `I = 00, X = 10, Z = 01, Y = 11` per qubit.
- **QVPS:** Quantum Candidates Verified Per Second.
- **TTS / TTE:** Time To Solution / Time To Exactness (wall-clock).
- **Exact oracle:** small-`N` diagonalization ground truth, scoring-only.
- **Anomaly Vault:** extra-verification store for strange elite candidates.
- **Infinite Monkey Quantum:** cheap-generator benchmark measuring candidates
  to first valid quantum structure.
