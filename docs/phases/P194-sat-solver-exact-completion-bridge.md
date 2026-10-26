# P194 — Ponte de hibridização EvoByte → Solver SAT (SAT Completion Bridge)

**Status:** Proposed.
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
2. O problema residual é codificado em CNF (Forma Normal Conjuntiva) com cláusulas de cobertura e não-colisão.
3. O solver SAT resolve o problema residual em tempo limitado (budget de 1 a 10 segundos). Se SAT, um candidato exato é obtido; se UNSAT, o esqueleto recebe penalidade na fitness.

## Pergunta falsificável da fase

> A ponte híbrida EvoByte + SAT (com codificação CNF exata) consegue resolver instâncias residuais de covering design que a busca estocástica pura rejeitou por violações remanescentes, com orçamento de tempo menor que 5 segundos por chamada de SAT?

## Escopo

**Arquivos a criar/editar:**
- `src/evobyte/sat_bridge.py`: codificador CNF para problemas de recobrimento e estabilizadores, interface com solver SAT.
- `docs/research/p194-sat-bridge-report.md`: estudo comparativo de tempo e eficácia da ponte de resolução.
- `tests/test_sat_bridge.py`: testes de codificação CNF, integridade lógica e round-trip de soluções.

## Critérios de Saída (Gates)

1. `tests/test_sat_bridge.py` passa 100% verde.
2. Demonstração de que a solução reconstruída do SAT é estritamente verificada pelo verificador independente de dependência zero.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.
