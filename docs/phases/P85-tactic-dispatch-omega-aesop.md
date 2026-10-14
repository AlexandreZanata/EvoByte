# P85 — Compilação de provas com automação de táticas (omega/aesop)

**Status:** Done.
**Dependência:** P84 Done; branch a partir de `codex/p84-multiparameter-quadratic-identities`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P84 concluída com identidades quadráticas validadas.
**Branch:** `codex/p85-tactic-dispatch-omega-aesop`.

## Hipótese, objetivo e escopo

Automatizar o despacho de táticas de prova no Lean 4 (`omega`, `aesop`, `linarith`, `ring`, `norm_num`) pelo pipeline do EvoByte, gerando scripts de prova que resolvem lemas com hipóteses de desigualdade inteira e inequações diofantinas sem intervenção humana.

Alterações permitidas: `src/evobyte/formal_bridge.py`, `lean_proofs/`, `tests/test_formal_bridge.py`, `benchmarks/science_matrix.py`, `experiments/`.
Fora do escopo: dependência de serviços externos de IA ou APIs remotas; enfraquecimento do kernel Lean 4.

## Trabalho ordenado

1. Implementar despacho hierárquico de táticas em `src/evobyte/formal_bridge.py` (`try_prove_lemma_with_tactics`).
2. Gerar scripts de prova robustos que utilizam `omega` para metas aritméticas inteiras, `linarith` para limites de desigualdade e `aesop` para busca lógica estrutural.
3. Testar a taxa de sucesso da automação sobre um banco de 30 lemas diofantinos em `tests/test_formal_bridge.py`.

## Gate de saída

Automação de táticas Lean 4 funcionando com zero falhas e taxa de aceitação de 100% no kernel:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P85 --config experiments/p85-config.json --output /tmp/evobyte-p85-acceptance.json
```

## Evidência de aceitação e auditoria formal

Auditoria executada em árvore limpa com veredicto **ACCEPTED** registrado em `/tmp/evobyte-p85-acceptance.json`:

- **Veredicto:** `ACCEPTED`
- **Total de teoremas compilados:** 30 (taxa de sucesso de automação de 100%: 30/30).
- **Distribuição de táticas vencedoras:**
  - `omega`: 18 lemas de aritmética de Presburger sobre denominadores naturais.
  - `linarith`: 6 lemas de limites de inequações racionais sobre $\mathbb{Q}$.
  - `aesop`: 4 lemas de estrutura lógica proposicional eWitness.
  - `ring`: 1 lema de equivalência polinomial algébrica.
  - `norm_num`: 1 lema de normalização numérica exata.
- **Has sorry:** `false` (0 tokens `sorry`).
- **Módulo Lean 4:** `lean_proofs/Generated/AutomatedTheorems.lean`.
- **SHA-256 do módulo:** `6bf1697eee5f2e321e8f7380594125f0f7595ca4c8832d7b1d081a55d2cff264`.
- **Revisão:** `8c93f8f10d776aea5ccdc7d6a45ae908f75fda72`.
- **Árvore limpa:** `dirty: ""` confirmado.

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p85 tactic dispatch omega aesop"
git push -u origin HEAD
gh pr create --base codex/p84-multiparameter-quadratic-identities --title "feat(formal): implement p85 tactic dispatch omega aesop" --body-file /tmp/evobyte-p85-pr.md
```
