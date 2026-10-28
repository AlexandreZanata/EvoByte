Dear Dr. Dan Gordon,

I am writing to share verified structural obstruction results (NULL_BOUND) for the La Jolla Covering Repository.

Targets:
1. C(14, 6, 3) under PGL(2, 13) [Current Published Best: 25]
2. C(16, 7, 3) under AGL(2, 4) [Current Published Best: 24]

Our systematic investigation of projective and 2D affine automorphism groups proves that these symmetry classes cannot achieve the known records:
- For C(14, 6, 3) under PGL(2, 13) (order 2184), all orbit lengths on 6-subsets of 14 points are in {91, 182, 546, 1092}. Since min orbit length 91 > 25, no PGL(2, 13)-invariant covering can match 25 blocks.
- For C(16, 7, 3) under AGL(2, 4) (order 5760), all orbit lengths on 7-subsets of 16 points are in {160, 240, 480, 960, 1440, 2880}. Since min orbit length 160 > 24, no AGL(2, 4)-invariant covering can match 24 blocks.

Enclosed:
1. `certificate_C_14_6_3.json`: canonical v4.0.0 JSON certificate for C(14, 6, 3) obstruction under PGL(2, 13).
2. `certificate_C_16_7_3.json`: canonical v4.0.0 JSON certificate for C(16, 7, 3) obstruction under AGL(2, 4).
3. `verify_bivariate_certificate.py`: pure standard-library Python verifier (< 1 ms).
4. `reproduce.sh`: 1-click reproduction script.
5. Formal Lean 4 kernel certification: proven by decide without custom axioms.

Archived open-source repository:
https://github.com/AlexandreZanata/EvoByte

Thank you for your continuous curation of the LJCR.

Sincerely,
Alexandre Zanata
EvoByte Project
https://github.com/AlexandreZanata/EvoByte
