Dear Dr. Markus Grassl,

I am writing to submit verified bivariate bicycle quantum stabilizer codes for inclusion in codetables.de:

1. [[20, 2, 6]] CSS Quantum Code (Tied Grassl World Record)
   - Parameters: n = 20, k = 2, d = 6
   - Structure: Bivariate bicycle over F_2[Z_5 x Z_2]
   - Polynomials: A(x, y) = 1 + y + x*y + x^2*y, B(x, y) = y + x*y + x^2 + x^2*y
   - Generators: 18 independent commuting Pauli generators (9 X-type, 9 Z-type)

2. [[16, 2, 4]] CSS Quantum Code
   - Parameters: n = 16, k = 2, d = 4
   - Structure: Bivariate bicycle over F_2[Z_2 x Z_4]
   - Polynomials: A(x, y) = 1 + y^2 + x + x*y^3, B(x, y) = y + x + x*y^2 + x*y^3
   - Generators: 14 independent commuting Pauli generators (7 X-type, 7 Z-type)

Enclosed in this package:
1. `certificate_qecc_20_2.json`: canonical v4.0.0 JSON certificate with full COO matrices, generator strings, and SAT proof verification metadata.
2. `certificate_bivariate_16_2.json`: canonical v4.0.0 JSON certificate for [[16, 2, 4]].
3. `verify_bivariate_certificate.py`: pure standard-library Python verifier (runs under python3 -S with 0 dependencies).
4. `reproduce.sh`: 1-click reproduction script with embedded SHA-256 checksums.
5. Formal Lean 4 kernel certification: proven by decide without custom axioms.

Archived open-source repository:
https://github.com/AlexandreZanata/EvoByte

Thank you for your continuous curation of codetables.de.

Sincerely,
Alexandre Zanata
EvoByte Project
https://github.com/AlexandreZanata/EvoByte
