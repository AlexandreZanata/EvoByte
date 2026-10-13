# P78 — Generalização para famílias de Sierpiński e Schinzel

**Status:** Proposed.
**Dependência:** P77 Proposed; branch a partir de `codex/p77-bytecode-lean-proof-bridge`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P77 aceita com ponte bytecode-Lean funcional.
**Branch:** `codex/p78-sierpinski-schinzel-generalization`.

## Hipótese, objetivo e escopo

O motor de síntese algébrica e verificação formal generaliza para frações egípcias com numeradores arbitrários $a \in \{5, 6, 7\}$ (conjecturas de Sierpiński $5/n$ e Schinzel $a/n$), mantendo a mesma disciplina de custo e provas formais.

Alterações permitidas: `benchmarks/open_problems.py`, `src/evobyte/algebraic.py`, `tests/test_algebraic.py`.
Fora do escopo: alteração de regras de integridade ou afrouxamento de limites de coordenadas.

## Trabalho ordenado

1. Parametrizar o motor de busca algébrica para numeradores $a \ge 4$.
2. Avaliar cobertura modular e identidades polinomiais para a conjectura de Sierpiński ($5/n$).
3. Comparar tempo de síntese e taxa de cobertura entre numeradores 4 e 5 sob o mesmo teto de computação.

## Gate de saída

Identidades válidas encontradas e provadas em Lean para Sierpiński ($5/n$), sem vazamento de splits ou falhas de checagem:

```bash
git diff --check
git status --short
python3 -m pytest tests/test_algebraic.py -q
python3 benchmarks/science_matrix.py --acceptance-phase P78
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p78 sierpinski schinzel generalization"
git push -u origin HEAD
gh pr create --base codex/p77-bytecode-lean-proof-bridge --title "feat(formal): implement p78 sierpinski schinzel generalization" --body-file /tmp/evobyte-p78-pr.md
```
