# P52 — Construir dados certificados para o micromodelo

**Status:** Done.
**Pré-requisito:** P51, com as rotas negativas explícitas do runbook.
**Branch:** `codex/p52-certified-learning-data`.
**Resultado:** ACCEPTED — 320 positivos com exact_certificate rechecado
(256 train/256 grupos, 64 val/64 grupos, splits disjuntos, final fechado);
6 negativos rejeitados por razão objetiva (sem timeout); professor
determinístico faturado (~7 s, teto 1 h); controles k1/k2 no train.

## Objetivo e escopo

Construir dados certificados para o micromodelo. Alterações permitidas: benchmarks/math_specialist.py, benchmarks/math_corpus.py e testes de corpus.
Fora de escopo: outras fases, mudança não registrada de hipótese, dados
históricos reescritos e promoção automática de descoberta.

Leia [o runbook](../FORMAL_SEARCH_PLAN.md) antes de implementar. Ele define
gates comuns, limites, esquema de evidência e rotas negativas. Executar uma
microtarefa por ciclo; não implementar todas as fases neste PR.

## Trabalho ordenado

1. Produzir pares problema→programa/certificado somente da família de desenvolvimento P47. Reusar corpus existente após P42; acrescentar controles gerados deterministicamente com resposta exata. Fonte/licença e custo do professor entram no manifesto.
2. Deduplicar por problema original, equivalência do alvo e programa normalizado. Negativos têm razão objetiva: inválido, certificado falso ou domínio errado; timeout da busca não demonstra que o problema é falso.
3. Teto inicial de coleta: uma hora real. Mínimo operacional para piloto: 256 positivos distintos de pelo menos 32 grupos train e 64 positivos de pelo menos oito grupos validation; nunca abrir final. Esses números são requisitos de engenharia, não prova de poder estatístico.

## Gate de saída

100% dos positivos rechecados exatamente, splits sem sobreposição e custos registrados. Se o mínimo não for obtido, registrar INCONCLUSIVE e bloquear P53; P54 pode seguir com baselines sem aprendizado.

Aplicar os gates comuns e a aceitação desta fase. A chamada abaixo é um
**contrato futuro a implementar**, não um comando já existente:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/science_matrix.py --acceptance-phase P52 --config experiments/p52-config.json --output /tmp/evobyte-p52-acceptance.json
```

Guardar configuração completa, comando real e artefato recuperável. Uma
fase técnica mede sua condição técnica; não fabrica números de velocidade.
Revisão científica, quando exigida acima, antecede a promoção do resultado.

## Risco principal

Muitas cópias do mesmo programa não constituem diversidade de supervisão.

## Commit & Push (obrigatório)

Começar de árvore limpa na branch declarada, a partir do predecessor aceito.
Stage apenas caminhos revisados com `git add` explícito. Escrever
`/tmp/evobyte-p52-pr.md` com problema, mudança, comandos reais, resultados,
artefatos e limitações. Todos os gates precisam estar verdes antes deste
bloco. Se esta fase precisar de subentregas, cada uma tem commit próprio e
não marca a fase inteira Done. Não executar merge automático.

```bash
git diff --cached --check
git commit -m "feat(research): implement p52 certified-learning-data"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p52 certified-learning-data" --body-file /tmp/evobyte-p52-pr.md
git status --short
```

Usar main somente se o predecessor já estiver integrado; caso contrário,
usar sua branch aceita como base do PR e registrar a dependência. Nunca
push direto à main, force-push ou bypass de hooks.
