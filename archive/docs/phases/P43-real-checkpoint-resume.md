# P43 — Demonstrar continuação real de checkpoint

**Status:** Done.
**Pré-requisito:** P42, com as rotas negativas explícitas do runbook.
**Branch:** `codex/p43-real-checkpoint-resume`.
**Resultado:** ACCEPTED — 40 gerações + processo encerrado + 60 restauradas
coincidem bit a bit com 100 diretas (população, elites, contadores, RNGs);
truncado/versão/config recusados explicitamente.

## Objetivo e escopo

Demonstrar continuação real de checkpoint. Alterações permitidas: src/evobyte/archive.py, src/evobyte/resident.py, src/evobyte/grammar.py e testes existentes de archive/resident.
Fora de escopo: outras fases, mudança não registrada de hipótese, dados
históricos reescritos e promoção automática de descoberta.

Leia [o runbook](../FORMAL_SEARCH_PLAN.md) antes de implementar. Ele define
gates comuns, limites, esquema de evidência e rotas negativas. Executar uma
microtarefa por ciclo; não implementar todas as fases neste PR.

## Trabalho ordenado

1. Salvar população, fitness, arquivo de elites, constantes, geração, contadores, configuração e estados RNG Python/NumPy/Torch CPU/CUDA usados pelo método.
2. Comparar uma execução de 100 gerações com 40 gerações + processo encerrado + restauração + 60 gerações. Comparar população final, elites, contadores e estados RNG.
3. Recusar versões, configuração e checkpoint truncado incompatíveis. Não comparar apenas duas execuções iniciadas do zero; wall-clock não é o critério de igualdade determinística.

## Gate de saída

A continuação em processo novo coincide com a execução inteira no mesmo ambiente fixado. Checkpoints incompatíveis falham explicitamente.

Aplicar os gates comuns e a aceitação desta fase. A chamada abaixo é um
**contrato futuro a implementar**, não um comando já existente:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/science_matrix.py --acceptance-phase P43 --config experiments/p43-config.json --output /tmp/evobyte-p43-acceptance.json
```

Guardar configuração completa, comando real e artefato recuperável. Uma
fase técnica mede sua condição técnica; não fabrica números de velocidade.
Revisão científica, quando exigida acima, antecede a promoção do resultado.

## Risco principal

Não prometer igualdade binária entre GPUs ou versões diferentes de PyTorch.

## Commit & Push (obrigatório)

Começar de árvore limpa na branch declarada, a partir do predecessor aceito.
Stage apenas caminhos revisados com `git add` explícito. Escrever
`/tmp/evobyte-p43-pr.md` com problema, mudança, comandos reais, resultados,
artefatos e limitações. Todos os gates precisam estar verdes antes deste
bloco. Se esta fase precisar de subentregas, cada uma tem commit próprio e
não marca a fase inteira Done. Não executar merge automático.

```bash
git diff --cached --check
git commit -m "feat(research): implement p43 real-checkpoint-resume"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p43 real-checkpoint-resume" --body-file /tmp/evobyte-p43-pr.md
git status --short
```

Usar main somente se o predecessor já estiver integrado; caso contrário,
usar sua branch aceita como base do PR e registrar a dependência. Nunca
push direto à main, force-push ou bypass de hooks.
