# P214 — Codificação SAT exata de distância quântica d ≥ 5 e decodificador BP-OSD

**Status:** Proposed.
**Programa:** Descoberta com Códigos Quânticos Bicíclicos Bivariados e Geometrias Projetivas (P211–P220, D047).
**Dependência:** P213 concluída e integrada em `main`.
**Owner:** agente executor.
**Branch:** `codex/p214-exact-sat-distance-and-bposd-decoder` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P204-exact-sat-distance-and-symplectic-encoder.md`](P204-exact-sat-distance-and-symplectic-encoder.md),
[`src/evobyte/exact_sat_qecc.py`](../../src/evobyte/exact_sat_qecc.py).

## Por que esta fase existe

Verificar se um código quântico $[[n, k, d]]$ possui distância mínima $d \ge 5$ requer provar que não existe operador de Pauli $P \in \mathcal{P}_n$ com peso $1 \le |P| < 5$ que comute com todos os estabilizadores ($P \in \mathcal{Z}(S)$) mas não pertença ao próprio grupo de estabilizadores ($P \notin S$).
Para $n \ge 18$, a contagem combinatória $\sum_{w=1}^{4} \binom{n}{w} 3^w$ excede centenas de milhares de configurações.
Esta fase implementa:
1. **Codificador SAT Exato para Distância $d \ge 5$:** Formulação booleana CNF com restrições de cardinalidade Totalizer / Sorting Networks, resolvendo satisfatibilidade via solver CDCL moderno (CaDiCaL / PySAT).
2. **Decodificador BP-OSD (Belief Propagation com Ordered Statistics Decoding):** Implementação de decodificador quântico para obter cotas superiores rápidas de distância e taxas de erro sob ruído despolarizante.

## Pergunta falsificável da fase

> A codificação SAT e o decodificador BP-OSD determinam de forma exata e certificável a distância quântica $d$ para códigos com $n \le 20$ qubits em tempo inferior a 30 segundos por instância, concordando 100% com a enumeração exata em instâncias de referência?

## Escopo

**Arquivos a criar/editar:**
- `src/evobyte/sat_distance_solver.py`: formulação CNF de distância quântica mínima $d \ge 5$ com redes de cardinalidade e interface PySAT.
- `src/evobyte/bposd_decoder.py`: decodificador Belief Propagation + Ordered Statistics Decoding.
- `docs/research/p214-sat-bposd-report.md`: tempos de resolução SAT, benchmarks de decodificação e análise de corretude.
- `tests/test_sat_distance_solver.py` e `tests/test_bposd_decoder.py`: testes unitários de acurácia e consistência.
- `docs/phases/P214-exact-sat-distance-and-bposd-decoder.md`: atualização de status e evidências.

## Critérios de Saída (Gates)

1. `tests/test_sat_distance_solver.py` e `tests/test_bposd_decoder.py` passam 100% verdes.
2. Concordância de 100% com distâncias quânticas conhecidas (Steane $[[7, 1, 3]]$, Shor $[[9, 1, 3]]$, Gottesman $[[8, 3, 3]]$).
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add src/evobyte/sat_distance_solver.py \
  src/evobyte/bposd_decoder.py \
  docs/research/p214-sat-bposd-report.md \
  tests/test_sat_distance_solver.py \
  tests/test_bposd_decoder.py \
  docs/phases/P214-exact-sat-distance-and-bposd-decoder.md
git commit -m "feat(sat): implement exact SAT distance solver d>=5 and BP-OSD decoder (P214)"
git push -u origin codex/p214-exact-sat-distance-and-bposd-decoder
gh pr create --base main \
  --title "feat(sat): implement exact SAT distance solver d>=5 and BP-OSD decoder (P214)" \
  --body "Implementa solver SAT exato para d>=5 e BP-OSD sob D047."
```
