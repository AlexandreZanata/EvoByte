# P46 — Catalogar 100 problemas com fontes

**Status:** Proposed.
**Pré-requisito:** P45, com as rotas negativas explícitas do runbook.
**Branch:** `codex/p46-open-problem-catalogue`.

## Objetivo e escopo

Catalogar 100 problemas com fontes. Alterações permitidas: docs/research/open-problems.json e um validador de metadados em benchmarks/science_matrix.py.
Fora de escopo: outras fases, mudança não registrada de hipótese, dados
históricos reescritos e promoção automática de descoberta.

Leia [o runbook](../FORMAL_SEARCH_PLAN.md) antes de implementar. Ele define
gates comuns, limites, esquema de evidência e rotas negativas. Executar uma
microtarefa por ciclo; não implementar todas as fases neste PR.

## Trabalho ordenado

1. Criar catálogo de 100 enunciados distintos, sem executá-los. Cada registro tem ID, título, enunciado, área, fonte primária, data da consulta, estado atual, tipo de certificado, verificabilidade e referências de resultados parciais.
2. Consultar publicações dos autores e catálogos mantidos como pistas; confirmar estado aberto e formulação nas fontes. Não preencher números, URLs ou status pela memória do agente. Respeitar licença; guardar metadados/paráfrase e referência, não copiar bases inteiras.
3. Separar open-confirmed, status-unconfirmed, solved e unsuitable. Somente open-confirmed conta para a meta de 100. Deduplicar reformulações equivalentes. Se não alcançar 100 com evidência, publicar contagem parcial e não marcar Done.

## Gate de saída

100 problemas distintos com fontes verificáveis e estado aberto conferido; esquema valida sem campos ausentes. Revisão matemática humana aprova a curadoria antes de P47. O catálogo não precisa ter 100 formalizações Lean.

Aplicar os gates comuns e a aceitação desta fase. A chamada abaixo é um
**contrato futuro a implementar**, não um comando já existente:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/science_matrix.py --acceptance-phase P46 --config experiments/p46-config.json --output /tmp/evobyte-p46-acceptance.json
```

Guardar configuração completa, comando real e artefato recuperável. Uma
fase técnica mede sua condição técnica; não fabrica números de velocidade.
Revisão científica, quando exigida acima, antecede a promoção do resultado.

## Risco principal

Uma variante nova do mesmo enunciado não aumenta a contagem; uma página dizendo open pode estar desatualizada.

## Commit & Push (obrigatório)

Começar de árvore limpa na branch declarada, a partir do predecessor aceito.
Stage apenas caminhos revisados com `git add` explícito. Escrever
`/tmp/evobyte-p46-pr.md` com problema, mudança, comandos reais, resultados,
artefatos e limitações. Todos os gates precisam estar verdes antes deste
bloco. Se esta fase precisar de subentregas, cada uma tem commit próprio e
não marca a fase inteira Done. Não executar merge automático.

```bash
git diff --cached --check
git commit -m "feat(research): implement p46 open-problem-catalogue"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p46 open-problem-catalogue" --body-file /tmp/evobyte-p46-pr.md
git status --short
```

Usar main somente se o predecessor já estiver integrado; caso contrário,
usar sua branch aceita como base do PR e registrar a dependência. Nunca
push direto à main, force-push ou bypass de hooks.
