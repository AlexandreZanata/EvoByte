# P50 — Estabelecer buscas e baselines verificáveis

**Status:** Proposed.
**Pré-requisito:** P49, com as rotas negativas explícitas do runbook.
**Branch:** `codex/p50-structured-search-controls`.

## Objetivo e escopo

Estabelecer buscas e baselines verificáveis. Alterações permitidas: benchmarks/math_specialist.py, src/evobyte/grammar.py e testes de busca.
Fora de escopo: outras fases, mudança não registrada de hipótese, dados
históricos reescritos e promoção automática de descoberta.

Leia [o runbook](../FORMAL_SEARCH_PLAN.md) antes de implementar. Ele define
gates comuns, limites, esquema de evidência e rotas negativas. Executar uma
microtarefa por ciclo; não implementar todas as fases neste PR.

## Trabalho ordenado

1. Comparar aleatório estruturado, evolução existente e um baseline clássico adequado. Para polinômios, incluir construção simbólica/interpolação exata quando aplicável; para instâncias aritméticas, incluir construção conhecida/enumerador determinístico.
2. Validar em controles conhecidos e falsos. CPU serve como referência; GPU faz geração/filtros em lote e finalistas recebem certificação exata. Não usar exemplos falsos para provar que uma busca limitada é completa.
3. Orçamento inicial: cinco seeds e 10 s reais por tarefa. Contar duplicatas, inválidos, certificados e tempo de verificação. Caso o método clássico resolva imediatamente, registrar esse resultado sem escondê-lo.

## Gate de saída

Pelo menos controles conhecidos são reencontrados e falsos não promovidos. Todos os braços têm o mesmo critério matemático e custos registrados. Nenhum ganho é inferido apenas do gerador isolado.

Aplicar os gates comuns e a aceitação desta fase. A chamada abaixo é um
**contrato futuro a implementar**, não um comando já existente:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/science_matrix.py --acceptance-phase P50 --config experiments/p50-config.json --output /tmp/evobyte-p50-acceptance.json
```

Guardar configuração completa, comando real e artefato recuperável. Uma
fase técnica mede sua condição técnica; não fabrica números de velocidade.
Revisão científica, quando exigida acima, antecede a promoção do resultado.

## Risco principal

Problemas com solução direta simples podem não justificar um modelo aprendido.

## Commit & Push (obrigatório)

Começar de árvore limpa na branch declarada, a partir do predecessor aceito.
Stage apenas caminhos revisados com `git add` explícito. Escrever
`/tmp/evobyte-p50-pr.md` com problema, mudança, comandos reais, resultados,
artefatos e limitações. Todos os gates precisam estar verdes antes deste
bloco. Se esta fase precisar de subentregas, cada uma tem commit próprio e
não marca a fase inteira Done. Não executar merge automático.

```bash
git diff --cached --check
git commit -m "feat(research): implement p50 structured-search-controls"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p50 structured-search-controls" --body-file /tmp/evobyte-p50-pr.md
git status --short
```

Usar main somente se o predecessor já estiver integrado; caso contrário,
usar sua branch aceita como base do PR e registrar a dependência. Nunca
push direto à main, force-push ou bypass de hooks.
