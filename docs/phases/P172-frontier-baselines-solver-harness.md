# P172 — Baselines competitivos honestos e harness de solver para a fronteira

**Status:** Proposed.
**Programa:** Descoberta na Fronteira (P171–P190, D042). Trilhas A, B e fundação comum.
**Dependência:** P171 concluída (`docs/research/targets/frontier_targets_v2.json` commitado; se ausente, PARE).
**Owner:** agente executor; revisor de sistemas nos gates de medição.
**Branch:** `codex/p172-frontier-baselines-solver-harness` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [regras do programa P171–P190](README.md#programa-de-descoberta-na-fronteira-p171p190-d042), [`docs/phases/P171-frontier-target-catalogue-v2.md`](P171-frontier-target-catalogue-v2.md).

## Por que esta fase existe

A Trilha A ataca recordes abertos (covering designs do LJCR, Schur fraco/forte) e a Trilha B
testa a hipótese H2 (evolução em bytecode vs. FunSearch em cap sets). Nenhuma das duas pode
começar sem **baselines honestos, totalmente implementados e calibrados**: Simulated
Annealing, Hill-Climbing com simetria imposta, busca aleatória e um resolvedor exato para
instâncias de calibração. Sem eles, qualquer "avanço" medido depois é incomparável.

## Pergunta falsificável da fase

> Os baselines implementados reproduzem os ótimos de calibração conhecidos — C(7,3,2)=7
> (plano de Fano) e WS(2)=8 (partição fraca de `[1..8]`) — em menos de 3 segundos cada,
> com verificação independente, sem hardcodar a resposta?

Se algum baseline não reproduzir, ele é declarado inadequado e descartado ou corrigido —
nunca mascarado.

## Fatos de partida (todos re-verificados pelo executor; nada é copiado de memória)

Estes fatos foram medidos ou lidos pelo planejador em 2026-10-22. O executor **deve**
re-medi-los e registrar divergências; nenhum valor abaixo entra em código sem passar por
um verificador.

| Fato | Fonte / medição do planejador | Observação |
|---|---|---|
| `PySAT` **não** está instalado neste ambiente (`import pysat` falha) | `python3 -c "import pysat"`, 2026-10-22 | Por isso não há dependência PySAT: o solver exato é DPLL puro em Python + gancho opcional para binário externo (`kissat`/`cadical` no `PATH`) |
| Fano `[(1,2,3),(1,4,5),(1,6,7),(2,4,6),(2,5,7),(3,4,7),(3,5,6)]` cobre `(7,3,2)`; cada remoção de 1 bloco quebra | P171 Passo 5 (construção explícita) | Fixture de calibração do verificador |
| AG(2,3): 12 retas de F₃² cobrem `(9,3,2)`; S(3,4,8): 14 planos de F₂³ cobrem `(8,4,3)` | P171 Passo 5 | Fixtures de calibração |
| `[1,1,2,1,2,2,2,1]` (classes {1,2,4,8},{3,5,6,7}) é válida para Schur **fraco** e inválida para Schur forte | P171 teste 4 | Fixture WS(2) |
| SA guloso+vizinhança de troca encontra C(7,3,2) válido em **0,003 s** (semente 3); SA encontra partição fraca de `[1..8]` em **0,00016 s** (semente 11) | Medido pelo planejador, 2026-10-22 | Margem de ~1000× sobre o orçamento de 3 s; o executor re-mede |
| `{0,1}³` (8 pontos) não contém três distintos com `a+b+c ≡ 0 (mod 3)` | Prova direta: se `a≠b ∈ {0,1}³`, então `c = -(a+b)` tem coordenada 2 onde `a,b` diferem | Fixture de cap set para testes instantâneos |
| `scipy`/`numpy` instalados; `sympy`, `torch` instalados | Ambiente do repo | Apenas essas libs + stdlib podem ser usadas |

## Escopo

**Arquivos que você pode criar:**
- `src/evobyte/frontier_baselines.py` (SA, Hill-Climbing com simetria, Random, DPLL puro, gancho para binário externo)
- `benchmarks/frontier_baseline_calibration.py` (calibração < 3 s com JSON de saída)
- `tests/test_frontier_baselines.py` (só lógica, sem buscas; suíte < 3 s)
- `experiments/p172-calibration.json` (resultado medido da calibração)
- `docs/research/p172-baselines-report.md`

**Arquivos que você pode editar:**
- `pyproject.toml`: registrar o marcador `slow` (`markers = ["slow: ..."]` em `[tool.pytest.ini_options]`)
- `docs/phases/P172-frontier-baselines-solver-harness.md`: só a linha de Status e o bloco final de execução.

**Proibido:**
- adicionar dependências ao `pyproject.toml` (fora o marcador de teste);
- usar `PySAT`, `z3` ou qualquer solver não instalado; o gancho externo só chama binário presente no `PATH` e reporta `available: false` caso contrário;
- hardcodar soluções de calibração no espaço inicial de busca (a população inicial é aleatória ou gulosa genérica);
- testes que rodem buscas, annealing ou DPLL pesado (tudo > 0,2 s por teste é proibido; o que demorar vai para o script de benchmark).

## Trabalho ordenado

### Passo 1 — Branch e pré-condição P171

```bash
git status --short                        # precisa estar vazio
git switch main && git pull --ff-only
git switch -c codex/p172-frontier-baselines-solver-harness
test -f docs/research/targets/frontier_targets_v2.json || { echo "P171 NAO CONCLUIDA"; exit 1; }
mkdir -p experiments
```

Se o catálogo v2 não existir, **PARE**: a P171 não foi concluída e nenhum alvo pode ser referenciado.

### Passo 2 — `src/evobyte/frontier_baselines.py`

Implemente exatamente esta interface (corpo a critério do executor, desde que passe nos testes do Passo 4):

```python
"""Honest competitive baselines for frontier combinatorial search (P172)."""

from __future__ import annotations
import math, shutil, subprocess, time
from dataclasses import dataclass, field
from typing import Any, Callable
import numpy as np

@dataclass(frozen=True)
class BaselineResult:
    method: str                 # "RandomSearch" | "SimulatedAnnealing" | "HillClimbing"
    target_id: str
    best_candidate: Any
    best_score: float           # maior = melhor
    is_solution: bool
    evaluations: int            # chamadas REAIS ao avaliador, nunca contador artificial
    elapsed_sec: float          # time.perf_counter()
    seed: int

def canonical_form(candidate: tuple, symmetries: list[tuple]) -> tuple:
    """Menor tupla na órbita do candidato sob o grupo de permutações dado."""

def run_random_search(target_id, sampler_fn, eval_fn, max_seconds, seed=0) -> BaselineResult: ...
def run_simulated_annealing(target_id, init_fn, neighbor_fn, eval_fn, max_seconds,
                            t_init=1.0, t_min=1e-4, cooling_rate=0.9995,
                            symmetries=None, seed=0) -> BaselineResult: ...
def run_hill_climbing(target_id, init_fn, neighbors_fn, eval_fn, max_seconds,
                      max_restarts=50, symmetries=None, seed=0) -> BaselineResult: ...
def solve_tiny_sat_dpll(clauses: list[frozenset[int]], n_vars: int, max_decisions: int
                        ) -> tuple[bool | None, dict | None, dict]:
    """DPLL puro (unit propagation + literal puro + ordem fixa). Retorna
    (True, modelo, stats) | (False, None, stats) | (None, None, stats=orçamento esgotado).
    None significa 'não sei', nunca um palpite."""
def external_sat_solver_status() -> tuple[bool, str | None]:
    """Detecta `kissat`/`cadical` no PATH. Nunca executa solving aqui."""
```

Regras de implementação (mecânicas, verificadas pelos testes):
- `symmetries` é lista de permutações de índices; `canonical_form` retorna o mínimo
  lexicográfico da órbita; com `symmetries` ativo, o baseline mantém um conjunto de formas
  canônicas já avaliadas e **pula** reavaliação (conta como `skipped_symmetry`, não como `evaluations`).
- Hill-Climbing é *steepest ascent* determinístico (desempate pelo menor índice) + reinícios
  aleatórios até o orçamento; determinístico dada a semente.
- Nenhuma função levanta exceção para entrada malformada de candidato: retorna veredito negativo.

### Passo 3 — `benchmarks/frontier_baseline_calibration.py`

Script com `--output experiments/p172-calibration.json` que executa, nesta ordem, com orçamento
total duro de 3 s (se estourar, aborta com erro):

1. **Portões do verificador** (usa `src/evobyte/frontier_catalogue.py` da P171; instantâneos):
   Fano aceito + 7 remoções rejeitadas; AG(2,3) + S(3,4,8) aceitos + 1 remoção rejeitada cada;
   fixture WS(2) aceita pelo verificador fraco e rejeitada pelo forte (`target_catalogue`).
2. **WS(2) por busca**: SA a partir de partição aleatória, semente 171, orçamento 2 s.
   Esperado: hit (medido 0,00016 s pelo planejador).
3. **C(7,3,2) por construção gulosa + SA com trocas e reinícios**, semente 171, orçamento 2 s.
   Esperado: 7 blocos, 0 pares descobertos (medido 0,003 s pelo planejador).
4. Grava JSON com `{"hits": {...}, "elapsed_sec": ..., "seeds": ..., "verifier_gates": "all_pass"}`.

Se qualquer portão do verificador falhar: **PARE** (bug no verificador ou na fixture — não ajuste para "passar").
Se alguma busca não atingir no orçamento: registre `hit: false` com o melhor valor e **PARE**
(baseline inadequado — reporte, não estenda o orçamento em silêncio).

### Passo 4 — `tests/test_frontier_baselines.py` (rápido por construção)

Todos os testes **< 0,2 s cada; suíte < 3 s no total**. Nomes exatos:

1. `test_sa_acceptance_and_cooling`: SA num objetivo estático de 3 estados com semente fixa;
   verifica que melhoria é sempre aceita, que a temperatura decai geometricamente e que o
   resultado tem os 8 campos de `BaselineResult` com `evaluations > 0`.
2. `test_hillclimbing_reaches_local_optimum`: paisagem estática com ótimo local conhecido;
   verifica convergência determinística (duas execuções, mesma semente, mesmo resultado).
3. `test_symmetry_canonical_filter`: duas colorações na mesma órbita têm a mesma forma
   canônica; o SA com simetria não reavalia a segunda (`skipped_symmetry > 0`, `evaluations`
   não a conta).
4. `test_dpll_tiny_sat_unsat`: CNF `{(1,2),(-1,2),(1,-2)}` é SAT; CNF `{(1),(-1)}` é UNSAT;
   orçamento estourado retorna `None` (não palpite).
5. `test_external_solver_hook_reports_status`: retorna `(bool, nome|None)` sem executar
   solving; se nenhum binário existe, `(False, None)`.
6. `test_baselines_reject_malformed`: candidato com cor fora do intervalo / bloco de tamanho
   errado gera veredito negativo, nunca exceção.
7. `test_provenance_determinism`: mesma semente, alvo resolvido deterministicamente →
   mesmo `evaluations` e mesmo `best_score` em duas execuções.

Marque com `@pytest.mark.slow` qualquer teste que, contra expectativa, ultrapasse 2 s
(não deve haver nenhum nesta fase).

### Passo 5 — Relatório `docs/research/p172-baselines-report.md`

Metodologia, interface dos baselines, resultados da calibração medida, por que não há
PySAT (não instalado; DPLL puro + gancho opcional), e limitações (DPLL puro só vale para
instâncias de calibração; campanhas reais usam o binário externo quando presente).

## Regras de parada (PARE, não commite, reporte)

- Qualquer portão do verificador falhar.
- Qualquer busca de calibração não atingir no orçamento congelado.
- Qualquer teste individual demorar > 0,2 s ou a suíte > 3 s (mova o pesado para `benchmarks/`).
- `frontier_targets_v2.json` ausente (P171 não concluída).
- Falha no pytest ou no `make verify`.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_frontier_baselines.py -q -m "not slow"   # FAST LOOP, ~1s
python3 benchmarks/frontier_baseline_calibration.py --output experiments/p172-calibration.json
python3 -m pytest tests/test_frontier_baselines.py -q                 # FINAL GATE, < 3s
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add src/evobyte/frontier_baselines.py benchmarks/frontier_baseline_calibration.py \
  tests/test_frontier_baselines.py experiments/p172-calibration.json \
  docs/research/p172-baselines-report.md pyproject.toml \
  docs/phases/P172-frontier-baselines-solver-harness.md
git diff --cached --check
git commit -m "feat(research): implement p172 frontier baselines and solver harness"
git push -u origin HEAD
gh pr create --base main \
  --title "feat(research): p172 frontier baselines" \
  --body-file /tmp/evobyte-p172-pr.md
git status --short
```

O corpo do PR (`/tmp/evobyte-p172-pr.md`) traz: problema, comportamento resultante, comandos de
validação exatos, números medidos (calibração < 3 s, hits por baseline), limitações (sem PySAT;
DPLL puro só para calibração) e o link do relatório.
