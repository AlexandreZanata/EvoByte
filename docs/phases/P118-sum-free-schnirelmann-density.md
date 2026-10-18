# P118 — Alvo aberto Erdős sobre conjuntos livres de soma e densidade de Schnirelmann

**Status:** In review.
**Dependência:** P117 concluída; branch a partir de `codex/p117-erdos-turan-additive-bases`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P117 concluída com teoremas de bases aditivas no Lean 4.
**Branch:** `codex/p118-sum-free-schnirelmann-density`.

## Hipótese, objetivo e escopo

Investigar e provar formalmente no Lean 4 (`lean_proofs/Generated/SumFreeTheorems.lean`) lemas sobre a densidade máxima de conjuntos livres de soma em subconjuntos finitos $\{1, \dots, N\}$ (provando a cota clássica $\lceil N/3 \rceil$ e invariantes sob dilatações) e relacionar a densidade de Schnirelmann $\sigma(A)$ com o crescimento de somas iteradas $A + A$ (teoremas de Schnirelmann e Mann $\sigma(A+B) \ge \min(1, \sigma(A) + \sigma(B))$), integrando crivo de busca de famílias extremas livres de soma.

Alterações permitidas: `lean_proofs/`, `src/evobyte/additive.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p118-config.json`, `experiments/p118-run.sh`.
Fora do escopo: uso de axiomas não padrão; alegações de resoluções de conjecturas universais sem certificados formais completos.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-combinatória-aditiva-conjuntos-de-sidon-e-teoria-de-densidade-em-lean-4-p113p120).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar motor de verificação e síntese de conjuntos livres de soma e cálculo de densidade de Schnirelmann em `src/evobyte/additive.py`.
2. Provar teoremas de conjuntos livres de soma e desigualdades de densidade em `lean_proofs/Generated/SumFreeTheorems.lean` no kernel do Lean 4.
3. Adicionar interface de auditoria P118 em `benchmarks/science_matrix.py` (`run_p118_sum_free_density_audit`) com validação de compilação sem `sorry`.

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P118 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P118 --config experiments/p118-config.json --output /tmp/evobyte-p118-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p118 sum free schnirelmann density"
git push -u origin HEAD
gh pr create --base codex/p117-erdos-turan-additive-bases --title "feat(formal): implement p118 sum free schnirelmann density" --body-file /tmp/evobyte-p118-pr.md
```
