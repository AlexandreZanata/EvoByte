# P51 — Rastrear a busca sem guardar um universo infinito

**Status:** Proposed.
**Pré-requisito:** P50, com as rotas negativas explícitas do runbook.
**Branch:** `codex/p51-bounded-replay-map`.

## Objetivo e escopo

Rastrear a busca sem guardar um universo infinito. Alterações permitidas: benchmarks/evo_trace.py, src/evobyte/archive.py e tests/test_evo_trace.py.
Fora de escopo: outras fases, mudança não registrada de hipótese, dados
históricos reescritos e promoção automática de descoberta.

Leia [o runbook](../FORMAL_SEARCH_PLAN.md) antes de implementar. Ele define
gates comuns, limites, esquema de evidência e rotas negativas. Executar uma
microtarefa por ciclo; não implementar todas as fases neste PR.

## Trabalho ordenado

1. Reusar o rastreador existente: contadores por geração, seed/configuração, checkpoints, IDs dos elites/finalistas e todos os certificados. Encontrar a implementação real por rg antes de criar qualquer módulo.
2. Definir mapa limitado por execução: até 100 mil nós amostrados, fila de I/O até 64 MiB e interrupção limpa antes de 1 GiB de disco bruto por execução. Para reconstruir gerações não armazenadas, guardar estado RNG e checkpoint compatível; se não houver replay, declarar cobertura parcial.
3. Validar links pai/filho, hashes e contadores. Gravar a taxa de amostragem e medir tracing ligado/desligado; não alegar que o mapa contém todos os candidatos quando só conserva amostras.

## Gate de saída

Replay reconstrói os segmentos declarados; nenhum certificado é perdido; buffers não crescem sem limite. Publicar custo e cobertura do mapa, inclusive eventuais perdas amostradas.

Aplicar os gates comuns e a aceitação desta fase. A chamada abaixo é um
**contrato futuro a implementar**, não um comando já existente:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/science_matrix.py --acceptance-phase P51 --config experiments/p51-config.json --output /tmp/evobyte-p51-acceptance.json
```

Guardar configuração completa, comando real e artefato recuperável. Uma
fase técnica mede sua condição técnica; não fabrica números de velocidade.
Revisão científica, quando exigida acima, antecede a promoção do resultado.

## Risco principal

Logging por candidato na CPU pode custar mais que a própria geração.

## Commit & Push (obrigatório)

Começar de árvore limpa na branch declarada, a partir do predecessor aceito.
Stage apenas caminhos revisados com `git add` explícito. Escrever
`/tmp/evobyte-p51-pr.md` com problema, mudança, comandos reais, resultados,
artefatos e limitações. Todos os gates precisam estar verdes antes deste
bloco. Se esta fase precisar de subentregas, cada uma tem commit próprio e
não marca a fase inteira Done. Não executar merge automático.

```bash
git diff --cached --check
git commit -m "feat(research): implement p51 bounded-replay-map"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p51 bounded-replay-map" --body-file /tmp/evobyte-p51-pr.md
git status --short
```

Usar main somente se o predecessor já estiver integrado; caso contrário,
usar sua branch aceita como base do PR e registrar a dependência. Nunca
push direto à main, force-push ou bypass de hooks.
