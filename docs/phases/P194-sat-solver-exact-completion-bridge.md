# P194 — Ponte de hibridização EvoByte → Solver SAT (SAT Completion Bridge)

**Status:** Done (2026-10-26).
**Programa:** Descoberta Algébrica Estruturada e Síntese Funcional (P191–P200, D043).
**Dependência:** P193 concluída.
**Owner:** agente executor.
**Branch:** `codex/p194-sat-solver-exact-completion-bridge`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P192-symmetry-groups-orbit-reduction.md`](P192-symmetry-groups-orbit-reduction.md),
[`docs/phases/P193-functional-priority-bytecode-engine.md`](P193-functional-priority-bytecode-engine.md).

## Por que esta fase existe

Algoritmos genéticos e métodos estocásticos são notavelmente eficientes em encontrar a estrutura global aproximada de uma solução combinatória (95% a 98% das restrições satisfeitas), mas enfrentam o "problema do último bit": achar os últimos elementos que fecham todas as restrições rígidas requer backtracking exaustivo.

Por outro lado, solvers SAT modernos de ponta (como CaDiCaL, Kissat ou Glucose via `pysat`) são especializados em resolver sistemas booleanos exatos com propagação de restrições por unidades (CDCL). No entanto, solvers SAT puros engasgam quando o espaço total não tem heurística de guiamento.

Esta fase cria a **ponte híbrida**:
1. O EvoByte gera o esqueleto de simetrias e fixa os blocos mais promissores via prioridade funcional.
2. O problema residual é codificado em CNF (Forma Normal Conjuntiva) com cláusulas de cobertura e restrições de cardinalidade de Sinz.
3. O solver SAT resolve o problema residual em tempo limitado (budget de 1 a 5 segundos). Se SAT, um candidato exato é obtido; se UNSAT, o esqueleto recebe penalidade na fitness.

## Pergunta falsificável da fase

> A ponte híbrida EvoByte + SAT (com codificação CNF exata) consegue resolver instâncias residuais de covering design que a busca estocástica pura rejeitou por violações remanescentes, com orçamento de tempo menor que 5 segundos por chamada de SAT?

**Resposta:** Sim. O tempo medido por chamada de SAT foi de $0,464$ ms para $C(7,3,2)$, $0,809$ ms para $C(8,4,3)$, $40,90$ ms para $C(13,6,3)$, $82,08$ ms para $C(14,6,3)$ e $483,13$ ms para $C(15,8,4)$ (todos $< 0,5$ s, ou seja, mais de $10\times$ abaixo do orçamento de 5 segundos). Todas as soluções obtidas foram formal e estritamente verificadas por `verify_covering_design`.

## Escopo

**Arquivos criados/editados:**
- `src/evobyte/sat_bridge.py`: codificador CNF com contadores sequenciais de Sinz, encadeamento de paridade XOR via Tseitin, motor DPLL em Python puro (`PurePythonSolver`) e interfaces para solvers CDCL (`solve_cnf`, `complete_covering_skeleton`, `complete_covering_orbits`, `StabilizerCnfEncoder`).
- `benchmarks/run_sat_bridge_benchmark.py`: harness de medição comparativa entre solvers e alvos estreitos.
- `docs/research/p194-sat-bridge-report.md`: estudo comparativo de tempo e eficácia da ponte de resolução.
- `docs/research/benchmarks/p194_sat_bridge_results.json`: artefato com metadados de hardware, proveniência e hashes SHA-256.
- `tests/test_sat_bridge.py`: testes de codificação CNF, integridade lógica, round-trip e certificação de cobertura.

## Critérios de Saída (Gates)

1. `tests/test_sat_bridge.py` passa 100% verde (13/13 testes aprovados).
2. Demonstração de que a solução reconstruída do SAT é estritamente verificada pelo verificador independente de dependência zero (`verify_covering_design` e `check_stabilizer`).
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add src/evobyte/sat_bridge.py \
        benchmarks/run_sat_bridge_benchmark.py \
        docs/research/p194-sat-bridge-report.md \
        docs/research/benchmarks/p194_sat_bridge_results.json \
        tests/test_sat_bridge.py \
        docs/phases/P194-sat-solver-exact-completion-bridge.md
git commit -m "feat(frontier): implement SAT solver exact completion bridge (P194)"
git push -u origin codex/p194-sat-solver-exact-completion-bridge
gh pr create --base main --head codex/p194-sat-solver-exact-completion-bridge \
  --title "feat(frontier): implement SAT solver exact completion bridge (P194)" \
  --body "Implement SAT solver exact completion bridge, Sinz cardinality counters, PurePythonSolver fallback, and covering/stabilizer completion routines for P194."
```
