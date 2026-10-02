# P40 — Reconciliar a base e auditar as evidências

**Status:** Proposed.
**Pré-requisito:** auditoria pendente de P33–P39 e base aceita, conforme o runbook.
**Branch:** `codex/p40-evidence-reconciliation`.

## Objetivo e escopo

Reconciliar a base e auditar as evidências. Alterações permitidas: benchmarks/science_matrix.py, src/evobyte/provenance.py e testes de integridade.
Fora de escopo: outras fases, mudança não registrada de hipótese, dados
históricos reescritos e promoção automática de descoberta.

Leia [o runbook](../FORMAL_SEARCH_PLAN.md) antes de implementar. Ele define
gates comuns, limites, esquema de evidência e rotas negativas. Executar uma
microtarefa por ciclo; não implementar todas as fases neste PR.

## Trabalho ordenado

1. Identificar o ancestral comum da branch P39 e da main atual; listar correções aceitas que ainda faltam na branch. Não executar merges de PRs neste ciclo. Se faltar correção obrigatória, registrar BLOCKED até uma microtarefa própria integrar a base.
2. Adicionar uma auditoria executável que confira revisão, configuração resolvida, hashes brutos, duração efetiva, verificador realmente chamado e evidência de continuação do checkpoint. A interface comum de aceitação começa aqui, expondo somente a capacidade de auditoria; PNN é metadado, não promessa de handlers futuros.
3. Preservar P33–P39. Emitir accepted/provisional/rejected por alegação: escala reduzida é diagnóstico; MSE não é prova; carregar checkpoint não é resume; geração aleatória não mede toda a evolução.

## Gate de saída

O relatório identifica a base real e todas as alegações sem suporte. Fixtures com hash alterado, revisão suja e duração divergente são rejeitadas. Um relatório de auditoria pode ser válido com alegações rejeitadas, mas P41 exige a integração das correções obrigatórias documentada e gates verdes.

Aplicar os gates comuns e a aceitação desta fase. A chamada abaixo é um
**contrato futuro a implementar**, não um comando já existente:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/science_matrix.py --acceptance-phase P40 --config experiments/p40-config.json --output /tmp/evobyte-p40-acceptance.json
```

Guardar configuração completa, comando real e artefato recuperável. Uma
fase técnica mede sua condição técnica; não fabrica números de velocidade.
Revisão científica, quando exigida acima, antecede a promoção do resultado.

## Risco principal

Não reinterpretar a auditoria como confirmação das fases antigas.

## Commit & Push (obrigatório)

Começar de árvore limpa na branch declarada, a partir do predecessor aceito.
Stage apenas caminhos revisados com `git add` explícito. Escrever
`/tmp/evobyte-p40-pr.md` com problema, mudança, comandos reais, resultados,
artefatos e limitações. Todos os gates precisam estar verdes antes deste
bloco. Se esta fase precisar de subentregas, cada uma tem commit próprio e
não marca a fase inteira Done. Não executar merge automático.

```bash
git diff --cached --check
git commit -m "feat(research): implement p40 evidence-reconciliation"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p40 evidence-reconciliation" --body-file /tmp/evobyte-p40-pr.md
git status --short
```

Usar main somente se o predecessor já estiver integrado; caso contrário,
usar sua branch aceita como base do PR e registrar a dependência. Nunca
push direto à main, force-push ou bypass de hooks.
