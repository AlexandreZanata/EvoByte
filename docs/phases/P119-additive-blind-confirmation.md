# P119 — Confirmação cega em larga escala com controle estatístico FWER (Bonferroni-Holm)

**Status:** In review.
**Dependência:** P118 concluída; branch a partir de `codex/p118-sum-free-schnirelmann-density`.
**Owner:** agente executor; revisor estatístico/matemático nos gates indicados.
**Pré-requisito:** P118 concluída com teoremas de densidade provados; partição cega selada de 100 instâncias combinatórias intocada.
**Branch:** `codex/p119-additive-blind-confirmation`.

## Hipótese, objetivo e escopo

Validar a metodologia combinatória formal do EvoByte em partição cega selada de 100 instâncias de combinatória aditiva (conjuntos de Sidon, bases aditivas, energia e somas livres), avaliando o proponente estruturado contra samplers aleatórios e crivos combinatórios ingênuos com controle rigoroso de erro familiar (FWER via Bonferroni-Holm em nível nominal $\alpha = 0{,}01$). A hipótese só é sustentada com 100% de certificados válidos, zero vazamentos de dados e superioridade estatisticamente significante ($p_{\text{adj}} < 0{,}01$).

Alterações permitidas: `src/evobyte/additive.py`, `src/evobyte/statistical.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p119-config.json`, `experiments/p119-run.sh`, `experiments/p119-blind-split.json`.
Fora do escopo: vazamento de instâncias seladas para o crivo de desenvolvimento; flexibilização de nível de significância estatística.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-combinatória-aditiva-conjuntos-de-sidon-e-teoria-de-densidade-em-lean-4-p113p120).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Gerar e selar criptograficamente a partição cega de 100 instâncias em `experiments/p119-blind-split.json`.
2. Implementar motor de avaliação pareada e confirmação cega em `src/evobyte/statistical.py`.
3. Adicionar interface de auditoria P119 em `benchmarks/science_matrix.py` (`run_p119_additive_blind_confirmation_audit`) com validação de FWER e integridade.

## Gate de saída

Execução da confirmação cega com 100/100 certificados aprovados, FWER controlado em $\alpha = 0{,}01$ e árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P119 --config experiments/p119-config.json --output /tmp/evobyte-p119-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p119 additive blind confirmation"
git push -u origin HEAD
gh pr create --base codex/p118-sum-free-schnirelmann-density --title "feat(formal): implement p119 additive blind confirmation" --body-file /tmp/evobyte-p119-pr.md
```
