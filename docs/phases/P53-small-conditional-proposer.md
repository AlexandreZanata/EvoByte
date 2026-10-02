# P53 — Treinar um único proponente pequeno

**Status:** Done.
**Pré-requisito:** P52, com as rotas negativas explícitas do runbook.
**Branch:** `codex/p53-small-conditional-proposer`.
**Resultado:** ACCEPTED — um SequentialHistoryProposer (28184 params,
condicional a features+histórico+máscara), 20 épocas em ~2 s, checkpoint
pela val (época 19, 0.128); export e reload independente com 32/32 válidos
e piso de 12.5%; treino e amostragem bit-reproduzíveis. Sem KEEP: P54
decide utilidade.

## Objetivo e escopo

Treinar um único proponente pequeno. Alterações permitidas: src/evobyte/generator.py, benchmarks/math_specialist.py e testes existentes de generator.
Fora de escopo: outras fases, mudança não registrada de hipótese, dados
históricos reescritos e promoção automática de descoberta.

Leia [o runbook](../FORMAL_SEARCH_PLAN.md) antes de implementar. Ele define
gates comuns, limites, esquema de evidência e rotas negativas. Executar uma
microtarefa por ciclo; não implementar todas as fases neste PR.

## Trabalho ordenado

1. Usar a arquitetura sequencial existente, com objetivo codificado em números, instruções previamente amostradas e máscaras de validade. Uma rede que recebe apenas a posição não é condicional ao histórico.
2. Limitar a um modelo de até 1 milhão de parâmetros, batch inicial 32, no máximo 20 épocas ou 30 min reais; escolher checkpoint por validation. Manter pelo menos 10% de propostas do aleatório estruturado. Não procurar dezenas de arquiteturas.
3. Guardar pesos, schema, normalização, configuração, curvas, seeds e custo total da coleta/treino. Implementar proposta standalone sem iniciar evolução; com VRAM insuficiente reduzir batch antes de ampliar qualquer limite.

## Gate de saída

Treinamento e export reais reproduzíveis; carregamento independente gera candidatos válidos. Nenhum KEEP aqui: P54 decide utilidade. Insuficiência de dados ou treino inválido bloqueia promoção e preserva o baseline.

Aplicar os gates comuns e a aceitação desta fase. A chamada abaixo é um
**contrato futuro a implementar**, não um comando já existente:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/science_matrix.py --acceptance-phase P53 --config experiments/p53-config.json --output /tmp/evobyte-p53-acceptance.json
```

Guardar configuração completa, comando real e artefato recuperável. Uma
fase técnica mede sua condição técnica; não fabrica números de velocidade.
Revisão científica, quando exigida acima, antecede a promoção do resultado.

## Risco principal

Não afirmar que exportar um buscador sem pesos significa treinar um micromodelo.

## Commit & Push (obrigatório)

Começar de árvore limpa na branch declarada, a partir do predecessor aceito.
Stage apenas caminhos revisados com `git add` explícito. Escrever
`/tmp/evobyte-p53-pr.md` com problema, mudança, comandos reais, resultados,
artefatos e limitações. Todos os gates precisam estar verdes antes deste
bloco. Se esta fase precisar de subentregas, cada uma tem commit próprio e
não marca a fase inteira Done. Não executar merge automático.

```bash
git diff --cached --check
git commit -m "feat(research): implement p53 small-conditional-proposer"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p53 small-conditional-proposer" --body-file /tmp/evobyte-p53-pr.md
git status --short
```

Usar main somente se o predecessor já estiver integrado; caso contrário,
usar sua branch aceita como base do PR e registrar a dependência. Nunca
push direto à main, force-push ou bypass de hooks.
