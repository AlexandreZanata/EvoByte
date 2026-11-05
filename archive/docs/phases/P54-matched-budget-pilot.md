# P54 — Decidir se o micromodelo compensa

**Status:** Done.
**Pré-requisito:** P53, com as rotas negativas explícitas do runbook.
**Branch:** `codex/p54-matched-budget-pilot`.
**Resultado:** DROP — construção clássica exata certifica 30/30 em ~15 ms
(família trivializada, sem espaço para o modelo); híbrido 29/30 mas 3–7×
mais lento que evolução (IC95 pareado [1.01, 1.87] no log-razão, 25 pares);
triagem íntegra, negativos rejeitados, custos com/sem amortização
publicados. Método aceito mantido; sem ADR (só KEEP exigiria).

**Continuidade atual:** DROP preservado e modelo desligado; D019/P58 admite somente uso histórico restrito, com análise exploratória.

## Objetivo e escopo

Decidir se o micromodelo compensa. Alterações permitidas: benchmarks/math_specialist.py e relatório novo de comparação.
Fora de escopo: outras fases, mudança não registrada de hipótese, dados
históricos reescritos e promoção automática de descoberta.

Leia [o runbook](../FORMAL_SEARCH_PLAN.md) antes de implementar. Ele define
gates comuns, limites, esquema de evidência e rotas negativas. Executar uma
microtarefa por ciclo; não implementar todas as fases neste PR.

## Trabalho ordenado

1. Pré-registrar braços: aleatório estruturado, evolução, método clássico mais forte e híbrido com o modelo P53 quando disponível. Registrar inferência separada da evolução; o híbrido não prova que a rede sozinha é melhor.
2. Pilotar cinco seeds em seis tarefas development a 10 s reais por braço. Só comparar os dois melhores métodos de busca e o clássico a 60 s se a triagem for íntegra. Teto de campanha: três horas incluindo certificação, não reduzir tempos silenciosamente para caber.
3. Publicar sucesso certificado por tarefa, timeouts censurados, diversidade, VRAM e custo total com/sem amortização. KEEP exige intervalo pré-registrado de 95% sustentando redução de pelo menos 20% no tempo até certificado, sem queda de sucesso; poucas soluções ou muitos timeouts dão INCONCLUSIVE. Procedimento pareado e tratamento da censura precisam de revisão estatística antes de medir.

## Gate de saída

Resultado KEEP/DROP/INCONCLUSIVE válido com todos os braços e negativos. KEEP exige ADR de adoção limitada à família; DROP mantém o método aceito. Nenhum limiar é relaxado depois de observar os resultados.

Aplicar os gates comuns e a aceitação desta fase. A chamada abaixo é um
**contrato futuro a implementar**, não um comando já existente:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/science_matrix.py --acceptance-phase P54 --config experiments/p54-config.json --output /tmp/evobyte-p54-acceptance.json
```

Guardar configuração completa, comando real e artefato recuperável. Uma
fase técnica mede sua condição técnica; não fabrica números de velocidade.
Revisão científica, quando exigida acima, antecede a promoção do resultado.

## Uso histórico na continuidade D019

Preservar DROP e dados originais; modelo desligado. Registrar a revisão prévia
ausente, o intervalo t de log-tempos apenas em pares sem censura e a diferença
em relação ao bootstrap de sucesso da nominação. Tratar o intervalo como
exploratório condicionado aos sucessos; seeds não são grupos independentes.
O braço Horner recebe fórmula privada e não sustenta ganho de descoberta justo.
A disposição P58 pode aprovar a não adoção e excluir claims confirmatórios,
sem renomear uma revisão posterior como prévia. P59 corrige informação/custos;
P60 fixa procedimento prospectivo, agrupamento, censura e critérios completos.
KEEP futuro exige novo experimento íntegro e ADR; não reabrir finais antigos.
Aplicar [D019](../FORMAL_SEARCH_PLAN.md#correção-de-atuação-e-continuidade-técnica-d019).

## Risco principal

O gasto em professor e treinamento pode anular uma inferência rápida.

## Commit & Push (obrigatório)

Começar de árvore limpa na branch declarada, a partir do predecessor aceito.
Stage apenas caminhos revisados com `git add` explícito. Escrever
`/tmp/evobyte-p54-pr.md` com problema, mudança, comandos reais, resultados,
artefatos e limitações. Todos os gates precisam estar verdes antes deste
bloco. Se esta fase precisar de subentregas, cada uma tem commit próprio e
não marca a fase inteira Done. Não executar merge automático.

```bash
git diff --cached --check
git commit -m "feat(research): implement p54 matched-budget-pilot"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p54 matched-budget-pilot" --body-file /tmp/evobyte-p54-pr.md
git status --short
```

Usar main somente se o predecessor já estiver integrado; caso contrário,
usar sua branch aceita como base do PR e registrar a dependência. Nunca
push direto à main, force-push ou bypass de hooks.
