# P86 — Generalização multitermo e frações egípcias coprimas

**Status:** Proposed.
**Dependência:** P85 Proposed; branch a partir de `codex/p85-tactic-dispatch-omega-aesop`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P85 concluída com automação de táticas operando.
**Branch:** `codex/p86-multiterm-diophantine-generalization`.

## Hipótese, objetivo e escopo

Generalizar a busca algébrica e os certificados formais para problemas diofantinos com restrições adicionais de coprimalidade $\gcd(x, y, z) = 1$ e decomposições de frações egípcias com 4 termos ($a/n = \sum_{i=1}^4 1/x_i$), compilando teoremas certificados correspondentes em Lean 4.

Alterações permitidas: `src/evobyte/algebraic.py`, `src/evobyte/formal_bridge.py`, `lean_proofs/Generated/`, `benchmarks/science_matrix.py`, `experiments/`.
Fora do escopo: extrapolação assintótica sem prova; alegação de teorema universal não demonstrado.

## Trabalho ordenado

1. Implementar verificação e busca de soluções estritamente coprimas em `src/evobyte/algebraic.py`.
2. Estender o crivo diofantino para decomposições de 4 termos com cotas controladas.
3. Gerar teoremas certificados em Lean 4 demonstrando soluções com restrição de coprimalidade para classes teste.

## Gate de saída

Decomposições multitermo e coprimas verificadas e aceitas via auditoria formal P86:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P86 --config experiments/p86-config.json --output /tmp/evobyte-p86-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p86 multiterm diophantine generalization"
git push -u origin HEAD
gh pr create --base codex/p85-tactic-dispatch-omega-aesop --title "feat(formal): implement p86 multiterm diophantine generalization" --body-file /tmp/evobyte-p86-pr.md
```
