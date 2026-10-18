# P126 — Alvo aberto de Erdős-Gyárfás sobre ciclos de potências de 2 e número cromático

**Status:** Proposed.
**Dependência:** P125 concluída; branch a partir de `codex/p125-roth-salem-spencer-ap-free`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P125 concluída com teoremas de conjuntos livres de 3-AP provados em Lean 4.
**Branch:** `codex/p126-erdos-gyarfas-cycles-chromatic`.

## Hipótese, objetivo e escopo

Investigar e formalizar invariantes ligados à conjectura de Erdős–Gyárfás (todo grafo com grau mínimo $\delta(G) \ge 3$ possui ciclo de comprimento potência de 2, $2^k \ge 4$), juntamente com o limitante de Dirac–Pósa para existência de ciclos longos ($\ell \ge \delta(G) + 1$), cotas cromáticas ($\chi(G) \ge n / \alpha(G)$ e $\chi(G) \le \Delta(G) + 1$) e certificados construtivos de ciclos de comprimento $2^k$ em famílias cúbicas e circulantes, gerando `lean_proofs/Generated/ErdosGyarfasChromaticTheorems.lean`.

Alterações permitidas: `lean_proofs/`, `src/evobyte/graph_ramsey.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p126-config.json`, `experiments/p126-run.sh`.
Fora do escopo: reivindicação de prova universal irrestrita da conjectura aberta de Erdős–Gyárfás; uso de `sorry`.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoria-extremal-de-grafos-números-de-ramsey-e-progressões-aritméticas-em-lean-4-p121p128).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar detecção exata de ciclos de comprimento $2^k$, verificação da propriedade de Erdős–Gyárfás em grafos com $\delta(G) \ge 3$ e cotas cromáticas $\lceil n/\alpha(G) \rceil \le \chi(G) \le \Delta(G)+1$ em `src/evobyte/graph_ramsey.py`.
2. Exportar mais de 60 teoremas formais em `lean_proofs/Generated/ErdosGyarfasChromaticTheorems.lean` com zero `sorry`.
3. Adicionar interface de auditoria P126 em `benchmarks/science_matrix.py` (`run_p126_erdos_gyarfas_chromatic_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P126 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P126 --config experiments/p126-config.json --output /tmp/evobyte-p126-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p126 erdos gyarfas cycles chromatic"
git push -u origin HEAD
gh pr create --base codex/p125-roth-salem-spencer-ap-free --title "feat(formal): implement p126 erdos gyarfas cycles chromatic" --body-file /tmp/evobyte-p126-pr.md
```
