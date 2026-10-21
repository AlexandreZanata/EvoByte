# P165 — Protocolo de redescoberta cega de recordes conhecidos da literatura

**Status:** Proposed.
**Dependência:** P164 concluída; branch a partir de `codex/p164-honest-combinatorial-baselines`.
**Owner:** agente executor; revisor formal/estatístico nos gates de significância.
**Branch:** `codex/p165-blind-rediscovery-protocol`.
**Leia antes:** [regras do executor P161–P170](README.md#programa-de-descoberta-validada-p161p170-d038).

## Por que esta fase existe

Antes de lançar uma busca cara por recordes inéditos mundiais, o método precisa provar sua
competência reproduzindo **soluções ótimas conhecidas em instâncias de calibração** sem ter acesso
à resposta no espaço de busca ("cega"):
1. Se o sistema não consegue reencontrar $W(3,3) \ge 26$ ou $S(3) \ge 13$ em poucos segundos,
   ele não tem capacidade algorítmica de buscar $W(2,6)$ ou $S(5)$.
2. A comparação deve ser feita contra os baselines implementados em P164 sob o mesmo orçamento de
   tempo de relógio de parede.
3. Se um baseline (como Simulated Annealing) vencer o EvoByte em tempo até a redescoberta, isso
   deve ser explicitamente registrado.

Esta fase estabelece o harness de calibração e mede a taxa de redescoberta em 4 alvos conhecidos.

## Escopo

**Arquivos que você pode criar:**
- `src/evobyte/rediscovery.py`
- `tests/test_rediscovery.py`
- `benchmarks/run_rediscovery_campaign.py`
- `experiments/p165-rediscovery-results.json`
- `docs/research/p165-blind-rediscovery-report.md`

**Arquivos que você pode editar:**
- `docs/phases/P165-blind-rediscovery-protocol.md`: linha de Status.

**Proibido:** hardcodar candidatos conhecidos no espaço inicial de busca. A população inicial
deve ser puramente aleatória ou estruturada conforme as regras do gerador.

## Trabalho ordenado

### Passo 1 — Branch

```bash
git status --short
git switch codex/p164-honest-combinatorial-baselines
git switch -c codex/p165-blind-rediscovery-protocol
```

### Passo 2 — Criar `src/evobyte/rediscovery.py`

Copie exatamente o código abaixo:

```python
"""Blind rediscovery protocol for literature benchmark targets (P165).

Calibrates search algorithms on known combinatorial milestones:
- vdw_3_3_26: van der Waerden coloring of length 26 with 3 colors (optimum known).
- vdw_2_4_34: van der Waerden coloring of length 34 with 2 colors.
- schur_3_13: sum-free partition of 1..13 into 3 classes.
- spectral_counter_sample: small connected graph refuting naive spectral heuristics.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable

import numpy as np

from evobyte.combinatorial_baselines import (
    BaselineResult,
    run_random_search,
    run_simulated_annealing,
    run_tabu_search,
)
from evobyte.target_catalogue import (
    verify_schur_partition,
    verify_vanderwaerden_coloring,
)


@dataclass
class RediscoveryTrial:
    instance_id: str
    method: str
    seed: int
    success: bool
    time_to_hit_sec: float | None
    total_evals: int
    elapsed_sec: float


def make_vdw_evaluator(n: int, r: int, k: int) -> tuple[
    Callable[[np.random.Generator], np.ndarray],
    Callable[[np.ndarray, np.random.Generator], np.ndarray],
    Callable[[np.ndarray, np.random.Generator, int], list[tuple[np.ndarray, str]]],
    Callable[[np.ndarray], tuple[float, bool]],
]:
    """Return (init_fn, neighbor_fn, neighbors_fn, eval_fn) for VdW coloring."""
    def init_fn(rng: np.random.Generator) -> np.ndarray:
        return rng.integers(1, r + 1, size=n)

    def neighbor_fn(cand: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        out = cand.copy()
        idx = rng.integers(0, n)
        cur = out[idx]
        choices = [c for c in range(1, r + 1) if c != cur]
        out[idx] = rng.choice(choices)
        return out

    def neighbors_fn(cand: np.ndarray, rng: np.random.Generator, k_sample: int) -> list[tuple[np.ndarray, str]]:
        res = []
        for _ in range(k_sample):
            idx = rng.integers(0, n)
            cur = cand[idx]
            choices = [c for c in range(1, r + 1) if c != cur]
            new_c = int(rng.choice(choices))
            out = cand.copy()
            out[idx] = new_c
            res.append((out, f"{idx}:{new_c}"))
        return res

    def eval_fn(cand: np.ndarray) -> tuple[float, bool]:
        # Count violations (fewer violations = higher score)
        valid, _ = verify_vanderwaerden_coloring(cand, r=r, k=k)
        if valid:
            return 0.0, True

        violations = 0
        max_d = (n - 1) // (k - 1)
        for d in range(1, max_d + 1):
            for a in range(n - (k - 1) * d):
                idxs = [a + i * d for i in range(k)]
                if all(cand[i] == cand[idxs[0]] for i in idxs):
                    violations += 1
        return -float(violations), False

    return init_fn, neighbor_fn, neighbors_fn, eval_fn


def run_single_calibration_trial(
    instance_id: str,
    method: str,
    max_seconds: float,
    seed: int,
) -> RediscoveryTrial:
    """Execute one calibration trial with exact wall-clock budget."""
    if instance_id == "vdw_3_3_26":
        init_fn, neighbor_fn, neighbors_fn, eval_fn = make_vdw_evaluator(n=26, r=3, k=3)
    elif instance_id == "vdw_2_4_34":
        init_fn, neighbor_fn, neighbors_fn, eval_fn = make_vdw_evaluator(n=34, r=2, k=4)
    else:
        raise ValueError(f"unsupported calibration instance {instance_id}")

    if method == "RandomSearch":
        res = run_random_search(instance_id, init_fn, eval_fn, max_seconds, seed)
    elif method == "SimulatedAnnealing":
        res = run_simulated_annealing(instance_id, init_fn, neighbor_fn, eval_fn, max_seconds, seed=seed)
    elif method == "TabuSearch":
        res = run_tabu_search(instance_id, init_fn, neighbors_fn, eval_fn, max_seconds, seed=seed)
    else:
        raise ValueError(f"unknown method {method}")

    return RediscoveryTrial(
        instance_id=instance_id,
        method=method,
        seed=seed,
        success=res.is_solution,
        time_to_hit_sec=res.elapsed_sec if res.is_solution else None,
        total_evals=res.evaluations,
        elapsed_sec=res.elapsed_sec,
    )
```

### Passo 3 — Criar `tests/test_rediscovery.py`

Crie os testes unitários com asserções exatas:
1. `test_make_vdw_evaluator_validates_known_optimum`: Uma solução conhecida de $W(3,3)=27$ (ou seja vetor de comprimento 26) avaliada por `eval_fn` retorna `score == 0.0` e `solved == True`.
2. `test_single_calibration_trial_random`: Executa `run_single_calibration_trial("vdw_3_3_26", "RandomSearch", 0.1, 42)` e confere que retorna `RediscoveryTrial` bem formado.
3. `test_single_calibration_trial_sa`: Executa com SA por 0.1s e verifica que o número de avaliações é positivo.

### Passo 4 — Executar campanha de calibração

Implemente `benchmarks/run_rediscovery_campaign.py` e execute:

```bash
python3 benchmarks/run_rediscovery_campaign.py --instances vdw_3_3_26 --seconds 1.0 --seeds 5 --output experiments/p165-rediscovery-results.json
```

Confira que o arquivo JSON foi gerado com resumo estatístico por método.

### Passo 5 — Relatório `docs/research/p165-blind-rediscovery-report.md`

Tabela de resultados contendo:
- Método | Instância | Taxa de Sucesso (seeds) | Evals/seg | Tempo médio até o hit.
- Declaração explícita de qual método obteve a melhor performance de redescoberta.

## Regras de parada (PARE, não commite, reporte)

- Nenhum método atingir redescoberta em `vdw_3_3_26` em menos de 10s (indica bug no gerador de vizinhança ou avaliador).
- Falha no pytest.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_rediscovery.py -q
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add src/evobyte/rediscovery.py tests/test_rediscovery.py \
  benchmarks/run_rediscovery_campaign.py experiments/p165-rediscovery-results.json \
  docs/research/p165-blind-rediscovery-report.md docs/phases/P165-blind-rediscovery-protocol.md
git diff --cached --check
git commit -m "feat(benchmark): implement p165 blind rediscovery protocol"
git push -u origin HEAD
gh pr create --base codex/p164-honest-combinatorial-baselines \
  --title "feat(benchmark): implement p165 blind rediscovery protocol" \
  --body-file /tmp/evobyte-p165-pr.md
git status --short
```
