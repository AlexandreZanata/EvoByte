# P204 — Codificação SAT exata para comutação simplética e distância mínima (Exact SAT QECC & Covering Formulations)

**Status:** Done (2026-10-27).
**Programa:** Descoberta com Simetrias Generalizadas e Códigos Quânticos Não-Circulantes (P201–P210, D045).
**Dependência:** P203 concluída e integrada em `main`.
**Owner:** agente executor.
**Branch:** `codex/p204-exact-sat-distance-and-symplectic-encoder` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P194-sat-solver-exact-completion-bridge.md`](P194-sat-solver-exact-completion-bridge.md),
[`src/evobyte/sat_bridge.py`](../../src/evobyte/sat_bridge.py).

## Por que esta fase existe

A busca combinatória e evolutiva para encontrar palavras de código que satisfaçam restrições estritas de distância quântica ($d \ge 4$) é computacionalmente pesada se realizada apenas por enumeração exaustiva de vetores simpléticos.
Solvers SAT modernos CDCL (como CaDiCaL) são capazes de provar satisfatibilidade ou insatisfatibilidade de fórmulas CNF com centenas de milhares de cláusulas em frações de segundo.
Esta fase implementa codificações CNF exatas para:
1. **Restrições de Cobertura Afim:** Formulação CNF exata para seleção de órbitas afins/diédricas mínimas cobrindo $t$-tuplas em covering designs.
2. **Restrições de Distância Quântica Mínima ($d \ge d_{target}$):** Codificação de cardinalidade booleana (Totalizer / CardEnc) garantindo que nenhum vetor simplético não-trivial no centralizador $C(\mathcal{S}) \setminus \mathcal{S}$ tenha peso de Hamming menor que $d_{target}$.

## Pergunta falsificável da fase

> A formulação CNF com codificadores de cardinalidade resolve ou refuta instâncias de teste de distância $d=3$ e $d=4$ em blocos de até 16 qubits em menos de 5 segundos por instância no CaDiCaL?

**Resposta:** SIM. Todas as instâncias de teste de distância $d=3$ (Steane em $1.32$\,ms, Shor em $1.00$\,ms) e $d=4$ (Bicirculante $[[16, 2, 4]]$ em $6.93$\,ms) foram resolvidas pelo CaDiCaL em tempos ordens de magnitude inferiores a 5 segundos, provando $d \ge 4$ por insatisfatibilidade completa de erros de peso $w < 4$.

## Escopo Realizado

**Arquivos criados/editados:**
- `src/evobyte/sat_distance_encoder.py`: classes `SATDistanceEncoder` e `SATCoveringEncoder` com operadores lógicos exatos e cardinalidade Sinz.
- `docs/research/p204-sat-encoder-report.md`: relatório formal de complexidade de cláusulas e benchmarks de tempo de resolução.
- `tests/test_sat_distance_encoder.py`: testes unitários de prova de distância, refutação honesta e coberturas afins (6/6 verdes).
- `docs/phases/P204-exact-sat-distance-and-symplectic-encoder.md`: atualização de status e evidências.

## Critérios de Saída (Gates)

1. `tests/test_sat_distance_encoder.py` passa 100% verde com verificação de modelos SAT em instâncias conhecidas (Steane, Shor).
2. Tempo de resolução por instância de calibração $< 5$\,s.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add src/evobyte/sat_distance_encoder.py \
  docs/research/p204-sat-encoder-report.md \
  tests/test_sat_distance_encoder.py \
  docs/phases/P204-exact-sat-distance-and-symplectic-encoder.md
git commit -m "feat(frontier): implement exact SAT distance and symplectic encoder (P204)"
git push -u origin codex/p204-exact-sat-distance-and-symplectic-encoder
gh pr create --base main \
  --title "feat(frontier): implement exact SAT distance and symplectic encoder (P204)" \
  --body "Implementa codificador SAT de distância quântica e cobertura afim sob D045."
```
