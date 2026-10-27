Dear Dr. Markus Grassl,

I am writing to share verified quasi-cyclic non-circulant CSS quantum code constructions for codetables.de.

Targets:
1. [[14, 3, 4]] Stabilizer Code (World Record Tied: d=4)
2. [[16, 5, 4]] Stabilizer Code (World Record Tied: d=4)

In prior searches restricted to pure circulant blocks, distance 4 could not be achieved (d <= 3).
Using quasi-cyclic non-circulant parity blocks with cross-coupling, our automated synthesis engine (EvoByte) successfully constructed:
- An explicit [[14, 3, 4]] CSS code with 11 generators (6 X, 5 Z) on 14 qubits.
- An explicit [[16, 5, 4]] CSS code with 11 generators (6 X, 5 Z) on 16 qubits.

Both codes satisfy:
- Symplectic commutativity: H_X * H_Z^T == 0 (mod 2).
- Exact code distance d = 4 verified by dual enumeration and SAT solver.
- Formal theorem certification in the Lean 4 kernel (zero sorry, standard axioms).

Enclosed files:
1. `certificate_qecc_14_3.json`: canonical v3.0.0 JSON certificate for [[14, 3, 4]].
2. `certificate_qecc_16_5.json`: canonical v3.0.0 JSON certificate for [[16, 5, 4]].
3. `verify_generalized_certificate.py`: pure standard-library Python 3 verifier.
4. `reproduce.sh`: 1-click reproduction script (< 2.0 ms execution).

The complete open-source codebase, verification logs, and Lean 4 proofs are archived at:
https://github.com/AlexandreZanata/EvoByte

Thank you for maintaining codetables.de.

Sincerely,
Alexandre Zanata
EvoByte Project
https://github.com/AlexandreZanata/EvoByte
