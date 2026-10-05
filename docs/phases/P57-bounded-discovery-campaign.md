# P57 — Executar uma campanha matemática e revisar novidade

**Status:** Done.
**Pré-requisito:** P56, com as rotas negativas explícitas do runbook.
**Branch:** `codex/p57-bounded-discovery-campaign`.
**Resultado:** COMPLETE, sem descoberta — 1181 primos 1 mod 24 selados:
932 certificados duais (1 rediscovery âncora k3/1009, 931 candidates com
novidade não sustentada), 249 budget-exhausted (janela limitada, nunca
exhaustive-null); clássicas 0/1181 na classe dura; 13.2B avaliados;
revisão de novidade publicada; cadeia P40–P57 concluída.

## Objetivo e escopo

Executar uma campanha matemática e revisar novidade. Alterações permitidas: benchmarks/open_problems.py, certificados e docs/research/campaign-review.md.
Fora de escopo: outras fases, mudança não registrada de hipótese, dados
históricos reescritos e promoção automática de descoberta.

Leia [o runbook](../FORMAL_SEARCH_PLAN.md) antes de implementar. Ele define
gates comuns, limites, esquema de evidência e rotas negativas. Executar uma
microtarefa por ciclo; não implementar todas as fases neste PR.

## Trabalho ordenado

1. Nominar uma questão limitada de Erdős–Straus após revisar literatura atual. Padrão inicial: primos n≡1 mod 24, 2≤n≤100000, x,y,z positivos ≤10^9, máximo uma hora de busca; congelar a lista e comparar construções clássicas conhecidas. É uma campanha de instâncias, não prova da conjectura.
2. Reusar checadores, limites GPU e rastreamento aceitos. O proponente polinomial só entra se houver experimento específico mostrando adequação à nova representação; caso contrário usar a busca aritmética aceita. Certificar com inteiros arbitrários e testar todos os limites antes de aceitar.
3. Rever cada candidato contra artigos e catálogos, obter reprodução independente e classificar rediscovery, verified-construction, candidate, counterexample, proven-theorem, exhaustive-null ou budget-exhausted conforme o contrato. A prova universal exige enunciado geral correto e certificado formal correspondente; novidade não é decidida apenas pela falta de um item no catálogo.

## Gate de saída

Nominação, custos, certificados, cobertura e revisão de novidade publicados. Resultado vazio é válido como budget-exhausted; exhaustive-null só com cobertura completa do domínio finito. Uma descoberta exige correção + novidade sustentada + reprodução independente + certificado/prova apropriado.

Aplicar os gates comuns e a aceitação desta fase. A chamada abaixo é um
**contrato futuro a implementar**, não um comando já existente:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/science_matrix.py --acceptance-phase P57 --config experiments/p57-config.json --output /tmp/evobyte-p57-acceptance.json
```

Guardar configuração completa, comando real e artefato recuperável. Uma
fase técnica mede sua condição técnica; não fabrica números de velocidade.
Revisão científica, quando exigida acima, antecede a promoção do resultado.

## Risco principal

Uma nova solução de instância pode ser útil e ainda não resolver o problema mundialmente aberto.

## Commit & Push (obrigatório)

Começar de árvore limpa na branch declarada, a partir do predecessor aceito.
Stage apenas caminhos revisados com `git add` explícito. Escrever
`/tmp/evobyte-p57-pr.md` com problema, mudança, comandos reais, resultados,
artefatos e limitações. Todos os gates precisam estar verdes antes deste
bloco. Se esta fase precisar de subentregas, cada uma tem commit próprio e
não marca a fase inteira Done. Não executar merge automático.

```bash
git diff --cached --check
git commit -m "feat(research): implement p57 bounded-discovery-campaign"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p57 bounded-discovery-campaign" --body-file /tmp/evobyte-p57-pr.md
git status --short
```

Usar main somente se o predecessor já estiver integrado; caso contrário,
usar sua branch aceita como base do PR e registrar a dependência. Nunca
push direto à main, force-push ou bypass de hooks.
