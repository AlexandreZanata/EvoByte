# P56 — Confirmar o método congelado em teste novo

**Status:** Proposed.
**Pré-requisito:** P55, com as rotas negativas explícitas do runbook.
**Branch:** `codex/p56-fresh-frozen-confirmation`.

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
