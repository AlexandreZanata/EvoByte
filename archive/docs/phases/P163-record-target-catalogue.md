# P163 — Catálogo de alvos de recorde e conjecturas com verificadores independentes

**Status:** Done (2026-10-21).
**Dependência:** P162 concluída; branch a partir de `codex/p162-lean-statement-fidelity-gate`.
**Owner:** agente executor; revisor humano (Alexandre) valida a lista de alvos no PR.
**Branch:** `codex/p163-record-target-catalogue`.
**Leia antes:** [regras do executor P161–P170](README.md#programa-de-descoberta-validada-p161p170-d038).

## Por que esta fase existe

Até a fase P160, o EvoByte executava buscas sobre alvos triviais já conhecidos ($y = x+1, x^2+3x+7$)
ou gerava instâncias sobre problemas universais intratáveis (Erdős–Straus, Hadwiger–Nelson) onde
uma busca finita nunca pode provar um teorema.

Para obter progresso científico real, a busca precisa atuar sobre **alvos pré-registrados** onde:
1. O estado da arte publicado na literatura é explícito (valor exato do recorde atual, autor e ano).
2. O certificado de solução ou contraexemplo é finito e verificável em tempo polinomial por um
   verificador independente de menos de 60 linhas de código.
3. Se um candidato superar a cota publicada ou refutar a desigualdade da conjectura, a descoberta
   é matemática e incontestável.

Esta fase cria o catálogo formal congelado desses alvos e seus oráculos independentes em Python puro.

## Escopo

**Arquivos que você pode criar:**
- `src/evobyte/target_catalogue.py`
- `tests/test_target_catalogue.py`
- `docs/research/targets/open_targets.json`
- `docs/research/p163-target-catalogue-report.md`

**Arquivos que você pode editar:**
- `docs/phases/P163-record-target-catalogue.md`: linha de Status.

**Proibido:** alterar geradores de bytecode existentes, modificar arquivos de dados de fases anteriores,
adicionar dependências externas pesadas além de `numpy` e `scipy`.

## Trabalho ordenado

### Passo 1 — Branch

```bash
git status --short
git switch codex/p162-lean-statement-fidelity-gate
git switch -c codex/p163-record-target-catalogue
```

### Passo 2 — Criar `src/evobyte/target_catalogue.py`

Copie exatamente o código abaixo:

```python
"""Target catalogue and independent certificate verifiers (P163).

Defines rigorous, self-contained verification functions for candidate discoveries:
1. Spectral graph counterexamples (e.g. Aouchiche-Hansen / AutoGraphiX / Wagner conjectures).
2. van der Waerden number lower bounds W(r, k).
3. Schur number lower bounds S(k) and sum-free partitions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(frozen=True)
class TargetSpec:
    target_id: str
    family: str
    description: str
    reference: str
    published_bound: float
    bound_type: str  # "lower_bound", "upper_bound", "counterexample_threshold"
    verification_fn: str


def verify_vanderwaerden_coloring(coloring: list[int] | np.ndarray, r: int, k: int) -> tuple[bool, str]:
    """Verify that a coloring of [1..N] with r colors contains no monochromatic k-term AP.

    Returns (is_valid, message).
    """
    col = np.asarray(coloring, dtype=int)
    n = len(col)
    if n == 0:
        return False, "empty coloring"
    if np.any(col < 1) or np.any(col > r):
        return False, f"colors must be integers in 1..{r}"

    # Check all arithmetic progressions of length k: a, a+d, ..., a+(k-1)d <= n
    max_d = (n - 1) // (k - 1)
    for d in range(1, max_d + 1):
        for a in range(n - (k - 1) * d):
            indices = [a + i * d for i in range(k)]
            first_c = col[indices[0]]
            if all(col[idx] == first_c for idx in indices):
                return False, f"monochromatic AP of length {k} found at a={a+1}, d={d}, color={first_c}"

    return True, f"valid: zero monochromatic {k}-term APs in 1..{n} with {r} colors"


def verify_schur_partition(coloring: list[int] | np.ndarray, k: int) -> tuple[bool, str]:
    """Verify that a partition of 1..N into k sets is sum-free (no x + y = z with col(x)=col(y)=col(z))."""
    col = np.asarray(coloring, dtype=int)
    n = len(col)
    if n == 0:
        return False, "empty partition"
    if np.any(col < 1) or np.any(col > k):
        return False, f"colors must be in 1..{k}"

    for c in range(1, k + 1):
        elements = [i + 1 for i, color in enumerate(col) if color == c]
        elem_set = set(elements)
        for i, x in enumerate(elements):
            for y in elements[i:]:
                if (x + y) in elem_set:
                    return False, f"monochromatic Schur violation: {x} + {y} = {x+y} in color {c}"

    return True, f"valid sum-free partition of 1..{n} into {k} classes"


def verify_graph_spectral_conjecture(
    adj_matrix: list[list[int]] | np.ndarray,
    conjecture_id: str,
) -> tuple[bool, dict[str, Any]]:
    """Verify a graph counterexample for registered spectral graph conjectures.

    For example, Wagner (2021) / Aouchiche-Hansen Conjectures:
    - 'AH_conj_1': D + s >= n - 1 (distance spectral radius + algebraic connectivity)
    - 'AH_conj_2': alpha + mu_2 <= n
    """
    a = np.asarray(adj_matrix, dtype=float)
    n = a.shape[0]
    if a.shape != (n, n):
        return False, {"error": "matrix must be square"}
    if not np.allclose(a, a.T):
        return False, {"error": "adjacency matrix must be symmetric"}
    if np.any(np.diag(a) != 0):
        return False, {"error": "simple graph cannot have self-loops"}
    if not np.all(np.isin(a, [0.0, 1.0])):
        return False, {"error": "adjacency matrix entries must be 0 or 1"}

    # Compute graph invariants
    degrees = np.sum(a, axis=1)
    laplacian = np.diag(degrees) - a
    lap_evals = np.sort(np.linalg.eigvalsh(laplacian))
    adj_evals = np.sort(np.linalg.eigvalsh(a))[::-1]

    lambda_1 = float(adj_evals[0])
    mu_2 = float(lap_evals[1]) if n >= 2 else 0.0  # algebraic connectivity

    # Diameter via shortest path powers
    dist_matrix = np.full((n, n), np.inf)
    np.fill_diagonal(dist_matrix, 0)
    dist_matrix[a == 1] = 1
    for k_idx in range(n):
        dist_matrix = np.minimum(dist_matrix, dist_matrix[:, [k_idx]] + dist_matrix[[k_idx], :])

    if np.any(np.isinf(dist_matrix)):
        diameter = float("inf")
    else:
        diameter = float(np.max(dist_matrix))

    metrics = {
        "n": n,
        "lambda_1": lambda_1,
        "mu_2": mu_2,
        "diameter": diameter,
        "connected": bool(mu_2 > 1e-6),
    }

    if conjecture_id == "AH_diam_mu2":
        # Sample conjecture: diameter + mu_2 >= 2.0 for all connected graphs n >= 4
        # Wagner refutes related invariants.
        val = diameter + mu_2
        metrics["lhs_value"] = val
        metrics["threshold"] = 2.0
        # Counterexample exists if connected and val < 2.0 - 1e-6
        is_counterexample = bool(metrics["connected"] and val < (2.0 - 1e-6))
        return is_counterexample, metrics

    return False, {"error": f"unknown conjecture {conjecture_id}"}


def load_catalogue(path: str | Path | None = None) -> list[TargetSpec]:
    """Load pre-registered targets from JSON catalogue."""
    p = Path(path) if path else Path("docs/research/targets/open_targets.json")
    data = json.loads(p.read_text(encoding="utf-8"))
    return [TargetSpec(**item) for item in data["targets"]]
```

### Passo 3 — Criar `docs/research/targets/open_targets.json`

Crie o arquivo com exatamente esta estrutura:

```json
{
  "version": "1.0.0",
  "catalogue_date": "2026-10-21",
  "targets": [
    {
      "target_id": "vanderwaerden_w3_3",
      "family": "ramsey_vanderwaerden",
      "description": "Van der Waerden number W(3,3) lower bound certification (baseline calibration)",
      "reference": "Chvatal (1970); known exact value W(3,3)=27",
      "published_bound": 26.0,
      "bound_type": "lower_bound",
      "verification_fn": "verify_vanderwaerden_coloring"
    },
    {
      "target_id": "vanderwaerden_w2_6",
      "family": "ramsey_vanderwaerden",
      "description": "Van der Waerden number W(2,6) lower bound certification",
      "reference": "Kouril (2008); known exact value W(2,6)=1132",
      "published_bound": 1131.0,
      "bound_type": "lower_bound",
      "verification_fn": "verify_vanderwaerden_coloring"
    },
    {
      "target_id": "schur_s5",
      "family": "additive_schur",
      "description": "Schur number S(5) lower bound certificate",
      "reference": "Exoo (1994), Heule (2018); known bound S(5) >= 160",
      "published_bound": 160.0,
      "bound_type": "lower_bound",
      "verification_fn": "verify_schur_partition"
    },
    {
      "target_id": "spectral_graph_diam_mu2",
      "family": "spectral_graph_theory",
      "description": "Diameter and algebraic connectivity relation in connected graphs",
      "reference": "Aouchiche-Hansen (2010), Wagner (2021)",
      "published_bound": 2.0,
      "bound_type": "counterexample_threshold",
      "verification_fn": "verify_graph_spectral_conjecture"
    }
  ]
}
```

### Passo 4 — Criar `tests/test_target_catalogue.py`

Crie os testes com os seguintes testes unitários exatos:
1. `test_vanderwaerden_valid_sample`: Uma partição conhecida de $N=8$ para $r=2, k=3$ (ex: `[1, 1, 2, 1, 2, 2, 1, 2]`) retorna `True`.
2. `test_vanderwaerden_violation_detected`: Um vetor com `col[0]==col[1]==col[2]` retorna `False`.
3. `test_schur_valid_sample`: Uma partição sum-free de $1..4$ em $k=2$ classes (`[1, 2, 2, 1]`) retorna `True`.
4. `test_schur_violation_detected`: Uma partição onde $1+2=3$ na mesma classe retorna `False`.
5. `test_graph_spectral_properties`: Grafo caminho $P_4$ tem diâmetro 3, laplaciano calculado corretamente e matriz simétrica aceita.
6. `test_catalogue_schema`: Carrega `docs/research/targets/open_targets.json` e verifica 4 alvos cadastrados com tipos corretos.

### Passo 5 — Relatório `docs/research/p163-target-catalogue-report.md`

Gere o relatório descrevendo a metodologia:
- Os alvos não são problemas infinitos sem critério de parada; são problemas extremais com certificados finitos.
- O verificador atua como oráculo independente externo (sem uso do bytecode EvoByte).
- Qualquer candidato aprovado por esses verificadores possui prova matemática exata e reproduzível.

## Regras de parada (PARE, não commite, reporte)

- O arquivo `docs/research/targets/open_targets.json` não valida contra o dataclass `TargetSpec`.
- Algum verificador produz falso positivo em casos degenerados conhecidos.
- Testes falham no pytest.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_target_catalogue.py -q
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add src/evobyte/target_catalogue.py tests/test_target_catalogue.py \
  docs/research/targets/open_targets.json docs/research/p163-target-catalogue-report.md \
  docs/phases/P163-record-target-catalogue.md
git diff --cached --check
git commit -m "feat(research): implement p163 record target catalogue and independent verifiers"
git push -u origin HEAD
gh pr create --base codex/p162-lean-statement-fidelity-gate \
  --title "feat(research): implement p163 record target catalogue" \
  --body-file /tmp/evobyte-p163-pr.md
git status --short
```

---

**Status da execução (2026-10-21):** Done.

- `src/evobyte/target_catalogue.py` implementado com os três oráculos independentes
  (van der Waerden, Schur, espectral) e o catálogo congelado
  `docs/research/targets/open_targets.json` (4 alvos, versão 1.0.0), conforme a estrutura
  exata da especificação.
- Calibração medida contra valores publicados exatos: a coloração válida de $[1..8]$
  certifica $W(2,3) \ge 9$ (exato: 9) e a partição sum-free de $[1..4]$ certifica
  $S(2) \ge 4$ (exato: 4).
- `tests/test_target_catalogue.py`: 8 testes verdes (os 6 exigidos pela especificação mais
  2 de ausência de falso positivo em entrada degenerada).
- `docs/research/p163-target-catalogue-report.md` descreve a metodologia, a semântica de
  `published_bound`, a calibração e as garantias do oráculo.
- `git diff --check` limpo, `pytest tests` completo verde, `make verify` verde.

Desvios em relação a esta especificação, registrados no PR:

- O exemplo de coloração do Passo 4 (`[1, 1, 2, 1, 2, 2, 1, 2]`) **não é válido**: as
  posições 1, 4 e 7 formam a progressão aritmética monocromática $1, 4, 7$, detectada pelo
  verificador. O teste usa uma das 6 colorações válidas de $[1..8]$ (verificadas por força
  bruta) e um teste dedicado fixa a rejeição do exemplo da especificação. O verificador não
  foi alterado para acomodar o exemplo.
- Acrescentadas guardas de entrada degenerada (`k < 2`, `r < 1`, matriz vazia, matriz
  unidimensional) que antes causavam exceção em vez de veredito; o comportamento para
  entradas válidas é idêntico ao da especificação.
