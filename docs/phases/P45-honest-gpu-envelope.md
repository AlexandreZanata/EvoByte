# P45 — Medir o ciclo inteiro dentro de limites seguros

**Status:** Proposed.
**Pré-requisito:** P44, com as rotas negativas explícitas do runbook.
**Branch:** `codex/p45-honest-gpu-envelope`.

## Objetivo e escopo

Medir o ciclo inteiro dentro de limites seguros. Alterações permitidas: benchmarks/gpu_limits.py, benchmarks/math_specialist.py e testes de limites.
Fora de escopo: outras fases, mudança não registrada de hipótese, dados
históricos reescritos e promoção automática de descoberta.

Leia [o runbook](../FORMAL_SEARCH_PLAN.md) antes de implementar. Ele define
gates comuns, limites, esquema de evidência e rotas negativas. Executar uma
microtarefa por ciclo; não implementar todas as fases neste PR.

## Trabalho ordenado

1. Separar smoke e measurement. Measurement recusa scale_factor diferente de 1; imprimir orçamento solicitado e tempo observado. Medir GENERATE→FILTER→VERIFY→SELECT→EVOLVE, incluindo sincronização e custo de certificados/tracing.
2. Iniciar com um stream e lote 256. Dobrar lote apenas após estabilidade e medição. Reservar max(1 GiB, 20% da VRAM total), considerando memória de outros processos. Pool CPU inicia com dois workers; evitar multiplicar threads internos.
3. Comparar tracing ligado/desligado e, somente depois da base estável, um versus dois streams. Testar 60 s e 600 s reais; uma confirmação de 3600 s é necessária antes de afirmar estabilidade por uma hora. Recuar lote ao detectar pressão antes de OOM; OOM invalida a medição e não autoriza reduzir o gate.

## Gate de saída

Relatório com tempos reais, picos de memória, lotes, transferências, checkpoints e contadores reconciliados. Nenhum crash/OOM nas durações declaradas. Publicar taxas de geração, válidos, verificações exatas e soluções distintas separadamente, mesmo abaixo de um milhão/s.

Aplicar os gates comuns e a aceitação desta fase. A chamada abaixo é um
**contrato futuro a implementar**, não um comando já existente:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/science_matrix.py --acceptance-phase P45 --config experiments/p45-config.json --output /tmp/evobyte-p45-acceptance.json
```

Guardar configuração completa, comando real e artefato recuperável. Uma
fase técnica mede sua condição técnica; não fabrica números de velocidade.
Revisão científica, quando exigida acima, antecede a promoção do resultado.

## Risco principal

Nenhum ajuste garante ausência absoluta de crash. Não maximizar uso de VRAM sacrificando reserva.

## Commit & Push (obrigatório)

Começar de árvore limpa na branch declarada, a partir do predecessor aceito.
Stage apenas caminhos revisados com `git add` explícito. Escrever
`/tmp/evobyte-p45-pr.md` com problema, mudança, comandos reais, resultados,
artefatos e limitações. Todos os gates precisam estar verdes antes deste
bloco. Se esta fase precisar de subentregas, cada uma tem commit próprio e
não marca a fase inteira Done. Não executar merge automático.

```bash
git diff --cached --check
git commit -m "feat(research): implement p45 honest-gpu-envelope"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p45 honest-gpu-envelope" --body-file /tmp/evobyte-p45-pr.md
git status --short
```

Usar main somente se o predecessor já estiver integrado; caso contrário,
usar sua branch aceita como base do PR e registrar a dependência. Nunca
push direto à main, force-push ou bypass de hooks.
