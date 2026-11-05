# P164 — Baselines combinatórios honestos pareados (Simulated Annealing, Tabu, Random)

**Status:** Done (2026-10-21).
**Dependência:** P163 concluída; branch a partir de `codex/p163-record-target-catalogue`.
**Owner:** agente executor; revisor de sistemas nos gates de medição.
**Branch:** `codex/p164-honest-combinatorial-baselines`.
**Leia antes:** [regras do executor P161–P170](README.md#programa-de-descoberta-validada-p161p170-d038).

## Por que esta fase existe

A auditoria D038 revelou que na fase P155 o baseline alegado PySR teve zero execuções completas
(`completed_runs = 0`) e os orçamentos foram de frações de segundo (0.4 s / 0.8 s).
Para que uma alegação de superioridade ou eficácia algorítmica seja cientificamente válida,
o método de busca (seja evolução em GPU ou bytecode) deve ser comparado contra **baselines honestos
e totalmente implementados**, sob **orçamento pareado de tempo de relógio de parede (wall-clock)**:
1. **Random Search**: linha de base estocástica pura sem memória.
2. **Simulated Annealing (SA)**: meta-heurística clássica com programação geométrica de temperatura.
3. **Tabu Search**: busca local com lista tabu de proibição de movimentos recentes para escapar de ótimos locais.

Esta fase implementa os baselines padrão em Python/NumPy, sem dependências externas faltantes,
com interface estrita que registra tempo de execução, número de estados avaliados e melhor candidato.

## Escopo

**Arquivos que você pode criar:**
- `src/evobyte/combinatorial_baselines.py`
- `tests/test_combinatorial_baselines.py`
- `benchmarks/combinatorial_benchmark.py`
- `experiments/p164-baseline-smoke.json`
- `docs/research/p164-baselines-report.md`

**Arquivos que você pode editar:**
- `docs/phases/P164-honest-combinatorial-baselines.md`: linha de Status.

**Proibido:** simular execuções, usar mocks ou retornar contadores artificiais. Se um baseline
superar o método principal, o resultado deve ser reportado sem censura.

## Trabalho ordenado

### Passo 1 — Branch

```bash
git status --short
git switch codex/p163-record-target-catalogue
git switch -c codex/p164-honest-combinatorial-baselines
```

### Passo 2 — Criar `src/evobyte/combinatorial_baselines.py`

Copie exatamente o código abaixo:

```python
"""Honest combinatorial baselines for extremal search (P164).

Provides pure, fully-implemented baselines for discrete optimization:
- RandomSearch
- SimulatedAnnealing
- TabuSearch

All algorithms operate under strict wall-clock time budgets and return identical
result dictionaries with full provenance.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any, Callable

import numpy as np


@dataclass
class BaselineResult:
    method: str
    target_id: str
    best_candidate: Any
    best_score: float
    is_solution: bool
    evaluations: int
    elapsed_sec: float
    seed: int


def run_random_search(
    target_id: str,
    sampler_fn: Callable[[np.random.Generator], Any],
    eval_fn: Callable[[Any], tuple[float, bool]],
    max_seconds: float,
    seed: int = 0,
) -> BaselineResult:
    """Evaluate randomly generated candidates until wall-clock deadline."""
    rng = np.random.default_rng(seed)
    start_time = time.perf_counter()
    evals = 0
    best_score = float("-inf")
    best_cand = None
    is_solved = False

    while (time.perf_counter() - start_time) < max_seconds:
        cand = sampler_fn(rng)
        evals += 1
        score, solved = eval_fn(cand)
        if score > best_score:
            best_score = score
            best_cand = cand
            if solved:
                is_solved = True
                break

    elapsed = time.perf_counter() - start_time
    return BaselineResult(
        method="RandomSearch",
        target_id=target_id,
        best_candidate=best_cand,
        best_score=best_score,
        is_solution=is_solved,
        evaluations=evals,
        elapsed_sec=elapsed,
        seed=seed,
    )


def run_simulated_annealing(
    target_id: str,
    init_fn: Callable[[np.random.Generator], Any],
    neighbor_fn: Callable[[Any, np.random.Generator], Any],
    eval_fn: Callable[[Any], tuple[float, bool]],
    max_seconds: float,
    t_init: float = 1.0,
    t_min: float = 1e-4,
    cooling_rate: float = 0.9995,
    seed: int = 0,
) -> BaselineResult:
    """Run Simulated Annealing with geometric temperature decay."""
    rng = np.random.default_rng(seed)
    start_time = time.perf_counter()
    evals = 0

    current_cand = init_fn(rng)
    current_score, is_solved = eval_fn(current_cand)
    evals += 1

    best_cand = current_cand
    best_score = current_score
    temp = t_init

    while (time.perf_counter() - start_time) < max_seconds and not is_solved:
        neighbor = neighbor_fn(current_cand, rng)
        n_score, n_solved = eval_fn(neighbor)
        evals += 1

        delta = n_score - current_score
        if delta > 0 or (temp > 1e-12 and rng.random() < math.exp(delta / max(temp, 1e-12))):
            current_cand = neighbor
            current_score = n_score
            if current_score > best_score:
                best_score = current_score
                best_cand = current_cand
                if n_solved:
                    is_solved = True
                    break

        temp = max(temp * cooling_rate, t_min)

    elapsed = time.perf_counter() - start_time
    return BaselineResult(
        method="SimulatedAnnealing",
        target_id=target_id,
        best_candidate=best_cand,
        best_score=best_score,
        is_solution=is_solved,
        evaluations=evals,
        elapsed_sec=elapsed,
        seed=seed,
    )


def run_tabu_search(
    target_id: str,
    init_fn: Callable[[np.random.Generator], Any],
    neighbors_fn: Callable[[Any, np.random.Generator, int], list[tuple[Any, str]]],
    eval_fn: Callable[[Any], tuple[float, bool]],
    max_seconds: float,
    tabu_tenure: int = 20,
    sample_neighbors: int = 15,
    seed: int = 0,
) -> BaselineResult:
    """Run Tabu Search with short-term memory list."""
    rng = np.random.default_rng(seed)
    start_time = time.perf_counter()
    evals = 0

    current_cand = init_fn(rng)
    current_score, is_solved = eval_fn(current_cand)
    evals += 1

    best_cand = current_cand
    best_score = current_score
    tabu_list: list[str] = []

    while (time.perf_counter() - start_time) < max_seconds and not is_solved:
        neighbors = neighbors_fn(current_cand, rng, sample_neighbors)
        if not neighbors:
            break

        best_cand_step = None
        best_score_step = float("-inf")
        best_move_step = None

        for cand, move_repr in neighbors:
            score, solved = eval_fn(cand)
            evals += 1
            # Aspiration criterion: accept move if it beats global best even if tabu
            if (move_repr not in tabu_list) or (score > best_score):
                if score > best_score_step:
                    best_score_step = score
                    best_cand_step = cand
                    best_move_step = move_repr
                    if solved:
                        is_solved = True
                        break

        if best_cand_step is not None:
            current_cand = best_cand_step
            current_score = best_score_step
            if best_move_step:
                tabu_list.append(best_move_step)
                if len(tabu_list) > tabu_tenure:
                    tabu_list.pop(0)

            if current_score > best_score:
                best_score = current_score
                best_cand = current_cand

    elapsed = time.perf_counter() - start_time
    return BaselineResult(
        method="TabuSearch",
        target_id=target_id,
        best_candidate=best_cand,
        best_score=best_score,
        is_solution=is_solved,
        evaluations=evals,
        elapsed_sec=elapsed,
        seed=seed,
    )
```

### Passo 3 — Criar `tests/test_combinatorial_baselines.py`

Crie os testes com cobertura total:
1. `test_random_search_respects_timeout`: Executa com `max_seconds=0.05` e garante que o tempo decorrido fica dentro da tolerância de deadline e `evaluations > 0`.
2. `test_simulated_annealing_optimizes_simple_target`: Em uma função de brinquedo simples (ex: número de uns em vetor booleano), o SA encontra o ótimo global.
3. `test_tabu_search_avoids_immediate_reversal`: Verifica que o tabu_list proíbe reversão imediata de movimentos recentes.
4. `test_provenance_determinism`: Duas execuções com a mesma semente geram exatamente o mesmo número de avaliações e mesmo score.

### Passo 4 — Implementar `benchmarks/combinatorial_benchmark.py`

Crie o benchmark que aceita `--target-id`, `--seconds` e `--seeds`, executa os três baselines e grava o resultado JSON.

```bash
python3 benchmarks/combinatorial_benchmark.py --target-id vanderwaerden_w3_3 --seconds 0.5 --seeds 42,101 --output experiments/p164-baseline-smoke.json
```

Confira que `experiments/p164-baseline-smoke.json` contém dados reais para todos os 3 métodos (nenhum método com 0 execuções).

### Passo 5 — Relatório `docs/research/p164-baselines-report.md`

Documente:
- O protocolo de medição com `time.perf_counter()`.
- O compromisso de auditoria: todos os baselines executam código de verdade.

## Regras de parada (PARE, não commite, reporte)

- Qualquer método reportar `evaluations = 0`.
- O tempo decorrido exceder em mais de 200% o tempo estipulado (falha de checagem de timeout).
- Falha no pytest.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_combinatorial_baselines.py -q
python3 benchmarks/combinatorial_benchmark.py --target-id vanderwaerden_w3_3 --seconds 0.5 --seeds 42 --output /tmp/p164-smoke.json
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add src/evobyte/combinatorial_baselines.py tests/test_combinatorial_baselines.py \
  benchmarks/combinatorial_benchmark.py experiments/p164-baseline-smoke.json \
  docs/research/p164-baselines-report.md docs/phases/P164-honest-combinatorial-baselines.md
git diff --cached --check
git commit -m "feat(benchmark): implement p164 honest combinatorial baselines"
git push -u origin HEAD
gh pr create --base codex/p163-record-target-catalogue \
  --title "feat(benchmark): implement p164 honest combinatorial baselines" \
  --body-file /tmp/evobyte-p164-pr.md
git status --short
```

---

**Status da execução (2026-10-21):** Done.

- `src/evobyte/combinatorial_baselines.py` implementado com o código da especificação
  (Random Search, Simulated Annealing e Tabu Search), sob orçamento estrito de relógio de
  parede com `time.perf_counter()` e contagem real de avaliações.
- `benchmarks/combinatorial_benchmark.py` criado com `--target-id`, `--seconds`, `--seeds`
  e `--output`; executa os três baselines no alvo do catálogo da P163 e certifica o melhor
  candidato com o oráculo independente `verify_vanderwaerden_coloring`.
- `experiments/p164-baseline-smoke.json` gerado com execução real: 6 execuções
  (2 sementes × 3 métodos), todas com `evaluations > 0` e `elapsed_sec <= 0,500 s`.
  Resultado medido: Random Search 6 e 7 violações; Simulated Annealing 1 e 2 violações;
  Tabu Search 1 e 1 violações; **nenhuma solução e nenhum certificado pelo oráculo** —
  nenhum recorde foi quebrado, reportado sem censura.
- `tests/test_combinatorial_baselines.py`: 5 testes verdes (os 4 exigidos pela
  especificação mais o cruzamento do contador local contra o oráculo independente da P163).
- `docs/research/p164-baselines-report.md` documenta o protocolo de medição, o compromisso
  de auditoria, os resultados medidos e as limitações.
- `git diff --check` limpo, `pytest tests` completo verde, `make verify` verde.

Desvios em relação a esta especificação, registrados no PR:

- Nenhum desvio de escopo de código: o módulo dos baselines é o da especificação, sem
  alteração. O que mudou foi o *benchmark*, que precisou implementar o espaço de busca
  concreto do alvo do catálogo (`N = published_bound + 1`, minimização de progressões
  aritméticas monocromáticas) e a certificação pelo oráculo da P163, pois a especificação
  só fixava a interface de linha de comando.
- Bug real encontrado e corrigido durante a execução: o contador local de progressões
  aritméticas do benchmark usava `&` bitwise entre inteiros e máscara booleana (as cores 2
  e 3 viravam 0), zerando contagens e produzindo um falso "0 violações" na primeira
  execução. O oráculo independente da P163 detectou a discrepância; a correção está travada
  pelo teste `test_local_counter_agrees_with_independent_oracle`. O artefato versionado
  contém o resultado corrigido.
