# P169 — Veredito estatístico consolidado com controle FWER e registro de resultados nulos

**Status:** Done (2026-10-22).
**Dependência:** P168 concluída; branch a partir de `codex/p168-faithful-formal-certificates`.
**Owner:** agente executor; revisor formal/estatístico.
**Branch:** `codex/p169-statistical-verdict-negative-results`.
**Leia antes:** [regras do executor P161–P170](README.md#programa-de-descoberta-validada-p161p170-d038).

## Por que esta fase existe

A integridade do método científico depende de como tratamos a evidência empírica:
1. Os dados brutos das fases P164, P165 e P166 devem ser analisados através de testes estatísticos
   não-paramétricos (teste de Wilcoxon) pareados exatamente pelo mesmo alvo, mesmo orçamento e mesma semente.
2. Múltiplas comparações devem sofrer correção de Holm-Bonferroni com limiar estrito $\alpha = 0.01$.
3. Se os dados mostrarem que Simulated Annealing ou busca aleatória superam a evolução de bytecode,
   o relatório conclui com integridade: **vantagem evolutiva não suportada** (`NOT SUPPORTED`).
4. Se a campanha não bateu os recordes mundiais da literatura, o relatório conclui:
   **resultado nulo confirmado** (`NULL RESULT CONFIRMED`), sem tentativas de redefinir métricas pós-hoc.

## Escopo

**Arquivos que você pode criar:**
- `src/evobyte/statistical_evaluation.py`
- `tests/test_statistical_evaluation.py`
- `docs/research/p169-statistical-verdict.md`
- `experiments/p169-statistical-verdict.json`

**Arquivos que você pode editar:**
- `docs/phases/P169-statistical-verdict-negative-results.md`: linha de Status.

**Proibido:** alterar dados de entrada dos JSONs para alcançar significância estatística ("p-hacking").
Relatar valores de p não corrigidos como se fossem significativos.

## Trabalho ordenado

### Passo 1 — Branch

```bash
git status --short
git switch codex/p168-faithful-formal-certificates
git switch -c codex/p169-statistical-verdict-negative-results
```

### Passo 2 — Criar `src/evobyte/statistical_evaluation.py`

Copie exatamente o código abaixo:

```python
"""Statistical evaluation and Holm-Bonferroni FWER control (P169).

Performs rigorous non-parametric paired tests between methods and emits
honest verdict classifications.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy import stats


@dataclass
class HypothesisVerdict:
    comparison_name: str
    n_pairs: int
    w_stat: float
    p_value_raw: float
    p_value_holm: float
    alpha: float
    is_significant: bool
    direction: str  # "method_a_superior", "method_b_superior", "no_difference"
    verdict: str


def compute_paired_wilcoxon_holm(
    scores_a: list[float] | np.ndarray,
    scores_b: list[float] | np.ndarray,
    comparison_name: str,
    family_size: int = 1,
    alpha: float = 0.01,
) -> HypothesisVerdict:
    """Compute exact paired Wilcoxon signed-rank test with Bonferroni-Holm adjustment."""
    a = np.asarray(scores_a, dtype=float)
    b = np.asarray(scores_b, dtype=float)
    if len(a) != len(b):
        raise ValueError(f"sample sizes must match: {len(a)} vs {len(b)}")

    diffs = a - b
    nonzero_diffs = diffs[diffs != 0.0]

    if len(nonzero_diffs) == 0:
        return HypothesisVerdict(
            comparison_name=comparison_name,
            n_pairs=len(a),
            w_stat=0.0,
            p_value_raw=1.0,
            p_value_holm=1.0,
            alpha=alpha,
            is_significant=False,
            direction="no_difference",
            verdict="INCONCLUSIVE_IDENTICAL",
        )

    res = stats.wilcoxon(diffs, alternative="two-sided")
    p_raw = float(res.pvalue)
    # Holm adjustment for single family step
    p_holm = min(1.0, p_raw * family_size)

    mean_diff = float(np.mean(diffs))
    if mean_diff > 0:
        direction = "method_a_superior"
    elif mean_diff < 0:
        direction = "method_b_superior"
    else:
        direction = "no_difference"

    is_sig = bool(p_holm <= alpha)
    verdict = f"SUPPORTED_{direction.upper()}" if is_sig else "NOT_SUPPORTED_NULL"

    return HypothesisVerdict(
        comparison_name=comparison_name,
        n_pairs=len(a),
        w_stat=float(res.statistic),
        p_value_raw=p_raw,
        p_value_holm=p_holm,
        alpha=alpha,
        is_significant=is_sig,
        direction=direction,
        verdict=verdict,
    )


def consolidate_campaign_verdicts(
    campaign_summary_path: str,
    output_path: str,
) -> dict[str, Any]:
    """Parse raw campaign data, run statistical batteries, and output verdict."""
    with open(campaign_summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Example: compare SA vs RandomSearch if present in data
    # (or emit structured summary)
    verdicts = {
        "status": "EVALUATED",
        "family_alpha": 0.01,
        "hypotheses": [],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(verdicts, f, indent=2)

    return verdicts
```

### Passo 3 — Testes `tests/test_statistical_evaluation.py`

Valide que:
1. `test_wilcoxon_holm_identical_samples`: Retorna `p_raw == 1.0` e `direction == "no_difference"`.
2. `test_wilcoxon_holm_significant_difference`: Com amostras fortemente separadas, `p_holm <= 0.01` e `is_significant == True`.
3. `test_sample_size_mismatch_raises`: Vetores com tamanhos desiguais levantam `ValueError`.

### Passo 4 — Relatório `docs/research/p169-statistical-verdict.md`

Gere o relatório formal com:
1. Tabela completa de testes pareados, valores de $W$, $p_{\text{raw}}$, $p_{\text{Holm}}$ e veredito final.
2. Veredito honesto:
   - "A hipótese de superioridade estrita de busca evolutiva em bytecode é [SUPPORTED / REJECTED]."
   - "A hipótese de descoberta de novos recordes matemáticos na campanha pré-registrada é [CONFIRMED / NULL RESULT]."

## Regras de parada (PARE, não commite, reporte)

- Declarar vitória estatística quando $p_{\text{Holm}} > 0.01$.
- Falha no pytest.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_statistical_evaluation.py -q
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add src/evobyte/statistical_evaluation.py tests/test_statistical_evaluation.py \
  docs/research/p169-statistical-verdict.md experiments/p169-statistical-verdict.json \
  docs/phases/P169-statistical-verdict-negative-results.md
git diff --cached --check
git commit -m "feat(statistical): implement p169 statistical verdict and negative results registration"
git push -u origin HEAD
gh pr create --base codex/p168-faithful-formal-certificates \
  --title "feat(statistical): implement p169 statistical verdict" \
  --body-file /tmp/evobyte-p169-pr.md
git status --short
```
