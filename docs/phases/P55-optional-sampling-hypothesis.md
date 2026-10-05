# P55 — Testar uma hipótese de aleatoriedade, opcional

**Status:** Done.
**Pré-requisito:** P54, com as rotas negativas explícitas do runbook.
**Branch:** `codex/p55-optional-sampling-hypothesis`.
**Resultado:** DEFERRED explícito — sem orçamento aprovado para P55 em
nenhum manifesto (runbook cobre P52/P53/P54/P57) e sem mecanismo único
pré-registrado; gate mecânico em `qrand_ab.p55_budget_gate`, custo zero,
P37 NULL como histórico (sem rerun), sem linguagem de vantagem/hardware
quântico. P56 segue com o sampler clássico.

## Objetivo e escopo

Testar uma hipótese de aleatoriedade, opcional. Alterações permitidas: benchmarks/qrand_ab.py e sampler existente, sem alterar o verificador.
Fora de escopo: outras fases, mudança não registrada de hipótese, dados
históricos reescritos e promoção automática de descoberta.

Leia [o runbook](../FORMAL_SEARCH_PLAN.md) antes de implementar. Ele define
gates comuns, limites, esquema de evidência e rotas negativas. Executar uma
microtarefa por ciclo; não implementar todas as fases neste PR.

## Trabalho ordenado

1. Executar apenas se restar orçamento aprovado no manifesto; caso contrário registrar DEFERRED e seguir P56 com o sampler clássico. Não bloquear pesquisa útil pela ausência de uma ideia quântica.
2. Comparar uma única transformação clássica de distribuição inspirada em amplitudes com uma distribuição clássica equivalente, mantendo gramática, filtros, tarefas, seeds e custo iguais. Reusar P37 como resultado histórico, não como prova geral de equivalência.
3. Pré-fixar métrica de sucesso certificado, análise pareada e correção se houver múltiplas comparações. Não misturar ganhos de outra gramática com efeito do sampler; zero sucessos nos dois lados resulta em INCONCLUSIVE.

## Gate de saída

KEEP/DROP/INCONCLUSIVE com procedimento registrado e custos reais, ou DEFERRED explícito. Exigir integridade mesmo para resultado nulo. Não usar termos vantagem quântica ou hardware quântico para operações clássicas.

Aplicar os gates comuns e a aceitação desta fase. A chamada abaixo é um
**contrato futuro a implementar**, não um comando já existente:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/science_matrix.py --acceptance-phase P55 --config experiments/p55-config.json --output /tmp/evobyte-p55-acceptance.json
```

Guardar configuração completa, comando real e artefato recuperável. Uma
fase técnica mede sua condição técnica; não fabrica números de velocidade.
Revisão científica, quando exigida acima, antecede a promoção do resultado.

## Risco principal

Uma parametrização com seno/cosseno não torna o algoritmo um computador quântico.

## Commit & Push (obrigatório)

Começar de árvore limpa na branch declarada, a partir do predecessor aceito.
Stage apenas caminhos revisados com `git add` explícito. Escrever
`/tmp/evobyte-p55-pr.md` com problema, mudança, comandos reais, resultados,
artefatos e limitações. Todos os gates precisam estar verdes antes deste
bloco. Se esta fase precisar de subentregas, cada uma tem commit próprio e
não marca a fase inteira Done. Não executar merge automático.

```bash
git diff --cached --check
git commit -m "feat(research): implement p55 optional-sampling-hypothesis"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p55 optional-sampling-hypothesis" --body-file /tmp/evobyte-p55-pr.md
git status --short
```

Usar main somente se o predecessor já estiver integrado; caso contrário,
usar sua branch aceita como base do PR e registrar a dependência. Nunca
push direto à main, force-push ou bypass de hooks.
