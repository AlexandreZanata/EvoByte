Dear Dr. Dan Gordon,

I am writing to share verified structural obstruction results (NULL_BOUND) for the La Jolla Covering Repository.

Targets:
1. C(13, 5, 3) under AGL(1, 13) [Current Record: 34]
2. C(15, 10, 4) under D_15 [Current Record: 14]

Our systematic investigation of non-cyclic automorphism groups proves that certain symmetry classes cannot achieve the known records:
- For C(13, 5, 3) under AGL(1, 13), all orbit lengths on 5-subsets are in {39, 78, 156}. Since min orbit length 39 > 34, no AGL(1, 13)-invariant covering can match 34 blocks.
- For C(15, 10, 4) under D_15, all non-trivial orbit lengths are in {15, 30}. Since min non-trivial length 15 > 14, no D_15-invariant covering can match 14 blocks.

Enclosed:
1. `certificate_C_13_5_3.json`: canonical v3.0.0 JSON certificate for C(13, 5, 3) obstruction.
2. `certificate_C_15_10_4.json`: canonical v3.0.0 JSON certificate for C(15, 10, 4) obstruction.
3. `verify_generalized_certificate.py`: pure standard-library Python verifier (< 1 ms).
4. `reproduce.sh`: 1-click reproduction script.
5. Formal Lean 4 kernel certification: proven by decide without custom axioms.

Archived open-source repository:
https://github.com/AlexandreZanata/EvoByte

Thank you for your continuous curation of the LJCR.

Sincerely,
Alexandre Zanata
EvoByte Project
https://github.com/AlexandreZanata/EvoByte
