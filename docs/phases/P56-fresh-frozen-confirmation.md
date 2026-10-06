# P56 — Confirmar o método congelado em teste novo

**Status:** Done.
**Pré-requisito:** P55, com as rotas negativas explícitas do runbook.
**Branch:** `codex/p56-fresh-frozen-confirmation`.
**Resultado:** CONFIRMED (provisional, sem rótulo de descoberta) — 360
ensaios em 6 tarefas seladas novas: clássico 120/120 (~ms), evolução e
aleatório 40/120 (só 2 tarefas fáceis); derrota publicada com intervalos
de Wilson por tarefa; reverificação limpa ok (6 certificados, 2 controles,
6 negativos, P43 resume, 4 selos); acesso registrado persistentemente.

**Continuidade atual:** Resultado histórico provisório e final consumido; D019/P58 restringe seu uso e P71 exige confirmação nova.

## Objetivo e escopo

Confirmar o método congelado em teste novo. Alterações permitidas: configuração previamente congelada, dados externos e relatório de reprodução. Usar interfaces já aceitas de benchmarks/full_matrix.py; nenhuma edição de algoritmo nesta fase.
Fora de escopo: outras fases, mudança não registrada de hipótese, dados
históricos reescritos e promoção automática de descoberta.

Leia [o runbook](../FORMAL_SEARCH_PLAN.md) antes de implementar. Ele define
gates comuns, limites, esquema de evidência e rotas negativas. Executar uma
microtarefa por ciclo; não implementar todas as fases neste PR.

## Trabalho ordenado

1. Fixar revisão limpa, dependências, pesos quando houver, schema, seeds, limites, verificadores e métodos selecionados somente em development. Anexar pré-registro; nenhuma alteração após abrir o teste. Se faltar funcionalidade de confirmação/log persistente, implementar e testar em microtarefa anterior e congelar uma nova revisão antes da abertura.
2. Rodar 20 seeds em seis tarefas final novas a 10 s reais, método selecionado versus clássico e aleatório estruturado. Contabilizar todos os custos; registrar intervalos por tarefa e limitações da amostra. Registrar acesso em estado persistente fora da memória do processo.
3. Reexecutar controles e certificados em ambiente limpo; conferir continuação P43 e restauração dos artefatos. Outra pessoa/revisor repete a verificação quando disponível; auto-repetição tem rótulo próprio. Mudança após final exige novo teste futuro.

## Gate de saída

Pacote recuperável e resultados finais completos, inclusive nulos. Perda ou empate são resultados válidos. Resultado provisório sem revisão independente não recebe o rótulo de descoberta; falha de integridade bloqueia P57.

Aplicar os gates comuns e a aceitação desta fase. A chamada abaixo é um
**contrato futuro a implementar**, não um comando já existente:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/science_matrix.py --acceptance-phase P56 --config experiments/p56-config.json --output /tmp/evobyte-p56-acceptance.json
```

Guardar configuração completa, comando real e artefato recuperável. Uma
fase técnica mede sua condição técnica; não fabrica números de velocidade.
Revisão científica, quando exigida acima, antecede a promoção do resultado.

## Uso histórico na continuidade D019

Preservar o relatório, incluindo `dirty`, `provisional-confirmation` e o log
consumido. Recheck/restauração em processo limpo não transforma a busca antiga
em campanha executada de revisão limpa; delegação não cria autoria independente.
P58 pode aceitar arquivo provisório com uso restrito a referência/development;
nunca como confirmação independente, teste fresco ou descoberta. Para promover
um método, P71 cria final novo após congelamento e exige outro operador real.
Não refazer o final P56 para ajustar método/hipótese nem apagar seu acesso.
Aplicar [D019](../FORMAL_SEARCH_PLAN.md#correção-de-atuação-e-continuidade-técnica-d019).

## Risco principal

Não reutilizar o final P38 nem reabrir o novo final para afinar hiperparâmetros.

## Commit & Push (obrigatório)

Começar de árvore limpa na branch declarada, a partir do predecessor aceito.
Stage apenas caminhos revisados com `git add` explícito. Escrever
`/tmp/evobyte-p56-pr.md` com problema, mudança, comandos reais, resultados,
artefatos e limitações. Todos os gates precisam estar verdes antes deste
bloco. Se esta fase precisar de subentregas, cada uma tem commit próprio e
não marca a fase inteira Done. Não executar merge automático.

```bash
git diff --cached --check
git commit -m "feat(research): implement p56 fresh-frozen-confirmation"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p56 fresh-frozen-confirmation" --body-file /tmp/evobyte-p56-pr.md
git status --short
```

Usar main somente se o predecessor já estiver integrado; caso contrário,
usar sua branch aceita como base do PR e registrar a dependência. Nunca
push direto à main, force-push ou bypass de hooks.
