# P161 — Retratação de alegações refutadas e guarda de integralidade

**Status:** Done (2026-10-21).
**Dependência:** plano D038 mesclado; branch a partir de `codex/plan-p161-p170-validated-discovery`.
**Owner:** agente executor; revisor humano (Alexandre) aprova o texto de retratação no PR.
**Branch:** `codex/p161-claim-retraction-integrality-guard`.
**Leia antes:** [regras do executor P161–P170](README.md#programa-de-descoberta-validada-p161p170-d038).

## Por que esta fase existe

A auditoria D038 mediu três problemas nos artefatos já commitados:

1. **P150**: 49 das 58 identidades de Schinzel classificadas como `novel-extension` não produzem
   `x, y, z` inteiros positivos para nenhum `k` em `0..49`. Elas só valem em ℚ, e em ℚ qualquer
   fração se decompõe. As 9 restantes cobrem classes de rotina. Nenhuma é novidade.
2. **P158**: o veredito "H1 SUPPORTED" contradiz `experiments/p155-baselines/summary_baselines.json`:
   - o Classical‑SR tem 100% de sucesso contra 80% do EvoByte, e MSE menor;
   - o PySR teve `completed_runs = 0`;
   - os orçamentos foram 0,4 s e 0,8 s, não 10 s–1 h.
3. **P160**: o abstract de `docs/paper/main.tex` afirma "10 s a 1 h", "contra PySR" e "residente
   em VRAM". Nada disso foi medido.

Esta fase **não apaga histórico**. Ela adiciona avisos de retratação, corrige o manuscrito e cria
testes que impedem a mesma alegação de voltar.

## Escopo

**Arquivos que você pode criar:**
- `src/evobyte/claim_audit.py`
- `tests/test_claim_audit.py`
- `docs/research/p161-claim-retraction.md`

**Arquivos que você pode editar (só os trechos indicados):**
- `docs/research/p150-novelty-audit-report.md`: inserir aviso no topo.
- `docs/research/p158-h1-verdict-report.md`: inserir aviso no topo.
- `docs/research/p144-discrepancy-covering-dossier.md` e `docs/research/p152-constructive-algebraic-dossier.md`: inserir aviso no topo.
- `docs/HYPOTHESIS.md`: acrescentar nota de status ao final.
- `docs/paper/main.tex`: abstract e frases factualmente falsas.
- `docs/paper/main.pdf`: só recompilar.
- `docs/DECISIONS.md`: acrescentar uma linha D039 ao final da tabela.
- `docs/phases/P161-claim-retraction-integrality-guard.md`: linha de Status no final.

**Proibido:** apagar ou reescrever números históricos, mexer em `lean_proofs/`, mudar testes
existentes, rodar campanhas novas.

## Trabalho ordenado

### Passo 1 — Árvore limpa e branch

```bash
git status --short            # deve imprimir nada
git switch codex/plan-p161-p170-validated-discovery
git switch -c codex/p161-claim-retraction-integrality-guard
```

### Passo 2 — Criar `src/evobyte/claim_audit.py`

Crie o arquivo com exatamente esta API. Pode copiar o código abaixo.

```python
"""Claim audit helpers (P161): integrality of unit-fraction identities.

The Erdos-Straus / Sierpinski / Schinzel problems require POSITIVE INTEGERS
x, y, z with a/n = 1/x + 1/y + 1/z. An identity that only holds in Q[k] is not
a solution. This module re-evaluates generated Lean identities exactly.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from fractions import Fraction
from math import gcd
from pathlib import Path

_IDENTITY_RE = re.compile(
    r"theorem schinzel_identity_a(\d+)_m(\d+)_r(\d+) \(k : ℚ\) :\s*"
    r"let n : ℚ := (.+?)\n\s*let X : ℚ := (.+?)\n\s*let Y : ℚ := (.+?)\n"
    r"\s*let Z : ℚ := (.+?)\n"
)
_SAFE_EXPR_RE = re.compile(r"^[0-9k+\-*/^() ]+$")


@dataclass(frozen=True)
class UnitFractionIdentity:
    a: int
    m: int
    r: int
    n_expr: str
    x_expr: str
    y_expr: str
    z_expr: str


def parse_schinzel_identities(text: str) -> list[UnitFractionIdentity]:
    """Parse every `schinzel_identity_a*_m*_r*` theorem in a Lean source text."""
    out = []
    for a, m, r, n_e, x_e, y_e, z_e in _IDENTITY_RE.findall(text):
        out.append(UnitFractionIdentity(int(a), int(m), int(r), n_e.strip(),
                                        x_e.strip(), y_e.strip(), z_e.strip()))
    return out


def evaluate_expr(expr: str, k: int) -> Fraction:
    """Exactly evaluate a polynomial/rational expression in k (whitelisted chars only)."""
    if not _SAFE_EXPR_RE.match(expr):
        raise ValueError(f"unsafe or unsupported expression: {expr!r}")
    py = re.sub(r"(\d+)", r"Fraction(\1)", expr).replace("^", "**")
    value = eval(py, {"__builtins__": {}, "Fraction": Fraction}, {"k": Fraction(k)})
    return Fraction(value)


def integral_k_count(identity: UnitFractionIdentity, k_values: range) -> int:
    """Count k for which (x, y, z) are positive integers; raise if the identity is false."""
    count = 0
    for k in k_values:
        n = evaluate_expr(identity.n_expr, k)
        x = evaluate_expr(identity.x_expr, k)
        y = evaluate_expr(identity.y_expr, k)
        z = evaluate_expr(identity.z_expr, k)
        if identity.a * x * y * z != n * (x * y + y * z + z * x):
            raise ValueError(f"rational identity fails for {identity} at k={k}")
        if all(v.denominator == 1 and v > 0 for v in (x, y, z)):
            count += 1
    return count


def is_quadratic_residue(r: int, m: int) -> bool:
    """True when gcd(r, m) = 1 and r is a square modulo m."""
    return gcd(r, m) == 1 and any((t * t - r) % m == 0 for t in range(m))


def audit_schinzel_text(text: str, k_max: int = 50) -> dict:
    """Summarize integrality of every parsed identity for k in range(k_max)."""
    ids = parse_schinzel_identities(text)
    rows = []
    for ident in ids:
        good = integral_k_count(ident, range(k_max))
        rows.append({"a": ident.a, "m": ident.m, "r": ident.r,
                     "quadratic_residue": is_quadratic_residue(ident.r, ident.m),
                     "integral_k": good})
    return {
        "k_max": k_max,
        "identities": len(rows),
        "quadratic_residue_classes": sum(r["quadratic_residue"] for r in rows),
        "integral_for_all_k": sum(r["integral_k"] == k_max for r in rows),
        "integral_for_no_k": sum(r["integral_k"] == 0 for r in rows),
        "rows": rows,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python3 -m evobyte.claim_audit <lean_file>", file=sys.stderr)
        return 2
    summary = audit_schinzel_text(Path(argv[1]).read_text(encoding="utf-8"))
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

Rode e **confira os números**:

```bash
PYTHONPATH=src python3 -m evobyte.claim_audit lean_proofs/Generated/SchinzelHighModuliTheorems.lean
```

Saída esperada: `identities: 58`, `quadratic_residue_classes: 58`, `integral_for_all_k: 9`,
`integral_for_no_k: 49`. **Se algum número for diferente, PARE** e reporte no PR, sem commit.

### Passo 3 — Criar `tests/test_claim_audit.py`

Os testes abaixo são obrigatórios. Use os nomes exatos.

1. `test_valid_identity_is_integral`: use esta fixture, terminada com `\n`:
   ```text
   theorem schinzel_identity_a4_m3_r2 (k : ℚ) :
       let n : ℚ := 3*k + 2
       let X : ℚ := 3*k + 2
       let Y : ℚ := k + 1
       let Z : ℚ := (3*k + 2)*(k + 1)
   ```
   O identificador vem de `4/n = 1/n + 3/(n+1) + 3/(n(n+1))`. Afirme que
   `integral_k_count(ident, range(50)) == 50`.
2. `test_rational_only_identity_is_rejected`: copie literalmente do arquivo Lean o bloco
   `schinzel_identity_a5_m840_r1`, só as 5 linhas do enunciado. Afirme `integral_k_count(...) == 0`.
3. `test_unsafe_expression_raises`: `evaluate_expr("__import__('os')", 1)` levanta `ValueError`.
4. `test_false_identity_raises`: uma fixture com `Z` trocado por `k + 7` levanta `ValueError`.
5. `test_p150_schinzel_regression`: audita `lean_proofs/Generated/SchinzelHighModuliTheorems.lean`
   e afirma 58 / 9 / 49 como no Passo 2.
6. `test_manuscript_abstract_matches_baseline_data`:
   - carregue `experiments/p155-baselines/summary_baselines.json`;
   - extraia o texto entre `\begin{abstract}` e `\end{abstract}` de `docs/paper/main.tex`;
   - se `comparison["PySR-Adapter"]["completed_runs"] == 0`, a palavra `PySR` só pode aparecer
     junto de `not executed`;
   - se `max(budgets_sec) < 10`, o abstract não pode conter `1\,h` nem `10\,s`.
7. `test_retraction_banners_present`: os 4 relatórios do escopo começam (primeiros 400 caracteres)
   com a string `RETRATADO (P161)` ou `REVISADO (P161)`.

### Passo 4 — Avisos nos relatórios antigos

Insira **no topo**, sem remover nada abaixo:

- Em `p150-novelty-audit-report.md`:
  ```markdown
  > **RETRATADO (P161, D039).** A classificação `novel-extension` está retirada. 49 das 58
  > identidades de Schinzel não dão solução inteira (só valem em ℚ). As 9 inteiras cobrem classes
  > de rotina, e os certificados Sidon são instâncias de construções conhecidas. Nenhuma novidade
  > é alegada. Ver [p161-claim-retraction.md](p161-claim-retraction.md).
  ```
- Em `p158-h1-verdict-report.md`:
  ```markdown
  > **RETRATADO (P161, D039).** O veredito global passa a ser **NOT SUPPORTED**. Pelos dados do
  > P155, o Classical-SR supera o EvoByte (sucesso 100% vs 80%, MSE oculto menor). O PySR não foi
  > executado. Os orçamentos foram 0,4 s/0,8 s, não 10 s–1 h. Ver
  > [p161-claim-retraction.md](p161-claim-retraction.md).
  ```
- Nos dossiês P144 e P152:
  ```markdown
  > **REVISADO (P161, D039).** "PROVED" significa apenas que o arquivo compila sem `sorry`. Não
  > implica que o enunciado seja o teorema nomeado (por exemplo, `degrey_chromatic_lower_bound`
  > prova `5 = 5`). A fidelidade é medida em P162.
  ```

### Passo 5 — `docs/research/p161-claim-retraction.md`

Estrutura obrigatória:

1. Tabela "Alegação | Fonte | Evidência medida | Novo status", com uma linha por item da seção
   "Por que esta fase existe".
2. A saída JSON do Passo 2, colada como bloco de código.
3. Os números do P155, copiados do JSON (não digite de memória).
4. Os comandos de reprodução.
5. Frase final: "Nenhuma descoberta matemática inédita foi obtida até P161."

### Passo 6 — Corrigir o manuscrito

Substitua o abstract de `docs/paper/main.tex` por este texto. Se algum número não bater com os
JSONs, **PARE**.

```latex
\begin{abstract}
Symbolic regression searches for closed-form expressions that fit observations. We present
\textbf{EvoByte}, a program-synthesis engine built on a fixed 64-byte linear bytecode virtual
machine and a four-stage verification cascade (S0--S3) designed for GPU execution without string
or AST parsing on the hot path.

We evaluate the falsifiable Hypothesis H1 on two Level-A targets ($x+1$ and $x^2+3x+7$) with
wall-clock budgets of 0.4\,s and 0.8\,s on an NVIDIA GeForce RTX 4060 Laptop GPU against random
search, a classic genetic-programming baseline and a classical symbolic-regression baseline; the
PySR adapter was not executed (missing dependency) and is reported as not run. The cascade yields
a measured 15.51$\times$ throughput speedup over the project's naive full-dataset evaluation, and
early termination a further 3.00$\times$. Evolutionary search beats random search (Wilcoxon
$W = 55.0$, Holm-adjusted $p = 2.49 \times 10^{-3}$), but the classical symbolic-regression
baseline reaches 100\% success versus 80\% for EvoByte, with lower hidden error and higher
throughput. H1's honest-baseline criterion is therefore \emph{not supported}. We report this
negative result together with all raw artifacts and reproduction commands.
\end{abstract}
```

Depois rode `grep -n "PySR\|1\\\\,h\|resident\|superior\|novel" docs/paper/main.tex`. Para cada
linha fora do abstract que afirme algo contrário aos JSONs, reescreva a frase para o fato medido.
Liste cada mudança no PR. Recompile o PDF:

```bash
(cd docs/paper && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex)
```

Se o `pdflatex` falhar, **PARE**. Não commite PDF desatualizado.

### Passo 7 — HYPOTHESIS.md e DECISIONS.md

- Ao final de `docs/HYPOTHESIS.md` acrescente:
  `> **Status note (D039, P161):** H1 is NOT SUPPORTED by the P155–P158 data (classical SR dominates; PySR not run; budgets 0.4–0.8 s). The P158 verdict is retracted.`
- Ao final da tabela de `docs/DECISIONS.md` acrescente a linha D039: data, "Retratação P150/P158/P160",
  contexto = auditoria D038, consequências = os 4 avisos + testes de guarda.

## Regras de parada (PARE, não commite, reporte)

- Os números do Passo 2 diferem de 58/9/49.
- Algum teste existente quebrou.
- O abstract novo contradiz um número de JSON.
- O `pdflatex` falha.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests -q
python3 -m pytest tests/test_claim_audit.py -q        # 7 testes passam
make verify
PYTHONPATH=src python3 -m evobyte.claim_audit lean_proofs/Generated/SchinzelHighModuliTheorems.lean
git status --short                                    # só os arquivos do escopo
```

## Commit & Push (obrigatório)

```bash
git add src/evobyte/claim_audit.py tests/test_claim_audit.py docs/research/p161-claim-retraction.md \
  docs/research/p150-novelty-audit-report.md docs/research/p158-h1-verdict-report.md \
  docs/research/p144-discrepancy-covering-dossier.md docs/research/p152-constructive-algebraic-dossier.md \
  docs/HYPOTHESIS.md docs/paper/main.tex docs/paper/main.pdf docs/DECISIONS.md \
  docs/phases/P161-claim-retraction-integrality-guard.md
git diff --cached --check
git commit -m "fix(research): retract p150 p158 p160 claims with integrality guard"
git push -u origin HEAD
gh pr create --base codex/plan-p161-p170-validated-discovery \
  --title "fix(research): retract p150 p158 p160 claims with integrality guard" \
  --body-file /tmp/evobyte-p161-pr.md
git status --short
```

---

**Status da execução (2026-10-21):** Done.

- Auditoria de integralidade executada: 58 identidades, 9 integrais em todo `k in 0..49`,
  49 sem solução inteira — os números esperados do Passo 2.
- Quatro avisos de retratação inseridos (P150, P158, P144, P152), sem apagar conteúdo
  histórico.
- Manuscrito P160 corrigido (`docs/paper/main.tex`) e `docs/paper/main.pdf` recompilado.
- 7 testes de guarda verdes em `tests/test_claim_audit.py`.
- Desvios em relação a esta especificação, registrados no PR: a decisão foi registrada como
  `D040` (o ID `D039` já estava ocupado pela linha "Plano P153–P160" em `docs/DECISIONS.md`);
  o teste 6 confere o abstract contra uma cópia commitada do resumo do P155, porque
  `experiments/p155-baselines/` é ignorado pelo git e não existe em CI (quando o artefato bruto
  está presente, os dois têm que concordar); e a tabela `docs/paper/table_h1_verdict.tex`
  preserva o veredito pré-retratação do P158 como registro histórico, com aviso de retratação
  no corpo do manuscrito — a consolidação da tabela fica para P169/P170.
