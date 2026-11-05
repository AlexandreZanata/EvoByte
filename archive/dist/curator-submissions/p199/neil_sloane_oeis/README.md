# Submission Package: OEIS Sequence A066010 / SQS(10)

**Recipient:** Neil Sloane & OEIS Editorial Board  
**Channel:** OEIS (https://oeis.org/A066010)  
**Status:** `pending_human_submission`  
**Corresponding Author:** Alexandre Zanata (EvoByte Project, https://github.com/AlexandreZanata/EvoByte)  
**Target:** Steiner Quadruple System $\text{SQS}(10)$, $C(10, 4, 3) = 30$  

## Mathematical Background
Mills (1979) established that the minimum covering number for triples of 10 points with 4-blocks is exactly 30, realizing an SQS(10).
Our structured SAT solver blindly synthesized the exact 30-block design using 3 cyclic base blocks in $Z_{10}$:
- `(1, 2, 3, 7)`
- `(1, 2, 4, 5)`
- `(1, 3, 5, 8)`

Mechanically verified in pure Python standard library and certified in the Lean 4 kernel with zero axioms.
