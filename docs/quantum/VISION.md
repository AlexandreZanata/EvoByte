# Q-Forge vision

**Status:** principle (experimental track).

## Target problem class

Q-Forge pursues only problems of the form **"finding is hard, verifying is
cheap"**:

- **A. Lowest-energy state.** Given Hamiltonian `H`, generate candidates `ψ`
  and score `E(ψ) = <ψ|H|ψ> / <ψ|ψ>`. With exact diagonalization available,
  `E_exact` is the oracle and fitness is `|E_candidate - E_exact|`. EvoByte
  must approximate or rediscover the ground state by evolution — never
  receiving it as input.
- **B. Conserved quantities.** Given `H`, generate operators `O` and score
  `||HO - OH||`. A norm near zero marks a conserved-quantity candidate. This
  experiment is prized because verification is extremely objective. Fitness is
  `commutator_error + complexity_penalty - novelty_reward`: we want *simple*
  operators that commute with the Hamiltonian.

## Scientific questions (not "can AI solve quantum physics?")

1. In quantum problems with compact representation and efficient
   verification, how far can massively parallel stochastic search with
   evolution and memory discover correct structures without explicit symbolic
   reasoning?
2. Is there a regime where generating billions of simple candidates is
   computationally superior to generating few highly intelligent ones?
3. Can we find compact structures that traditional optimizers miss under the
   same wall-clock budget?

## Final principle

The generator may be wrong billions of times — that is not a problem. The
fundamental requirement is **fast verification + trustworthy verification**.
The architecture deliberately exploits the asymmetry: discovering a structure
is very hard, verifying whether it works is cheap. Q-Forge turns VRAM and
parallelism into a hypothesis factory:

```text
BITS -> CANDIDATES -> PHYSICS -> VERIFY -> KILL 99.999%
-> PRESERVE SURVIVORS -> MUTATE -> REPEAT
```

Do not stop the machine from "hallucinating". Make hallucination cheap, and
truth rigorous enough to be strict yet fast enough to select the survivors.
