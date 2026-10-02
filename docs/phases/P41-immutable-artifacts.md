# P41 — Impedir sobrescrita de evidências

**Status:** Proposed.
**Pré-requisito:** P40, com as rotas negativas explícitas do runbook.
**Branch:** `codex/p41-immutable-artifacts`.

## Objetivo e escopo

Impedir sobrescrita de evidências. Alterações permitidas: benchmarks/gpu_limits.py, src/evobyte/provenance.py e tests/test_gpu_limits.py.
Fora de escopo: outras fases, mudança não registrada de hipótese, dados
históricos reescritos e promoção automática de descoberta.

Leia [o runbook](../FORMAL_SEARCH_PLAN.md) antes de implementar. Ele define
gates comuns, limites, esquema de evidência e rotas negativas. Executar uma
microtarefa por ciclo; não implementar todas as fases neste PR.

## Trabalho ordenado

1. Exigir diretório exclusivo por execução; um teste recebe tmp_path e nunca escreve em experiments/p34-raw ou outro diretório histórico.
2. Gravar configuração e dados brutos antes de finalizar o manifesto. Recusar destino não vazio; referências duráveis precisam de tamanho e SHA-256. Não corrigir um hash antigo substituindo sua evidência.
3. Executar um smoke em diretório novo e comparar hashes dos artefatos históricos antes/depois. Se algum já estiver divergente, registrar como evidência indisponível ou rejeitada, sem reconstruir silenciosamente.

## Gate de saída

Testes não alteram dados históricos. Sobrescrita e alteração de um byte são detectadas. Manifesto novo aponta para evidências recuperáveis.

Aplicar os gates comuns e a aceitação desta fase. A chamada abaixo é um
**contrato futuro a implementar**, não um comando já existente:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/science_matrix.py --acceptance-phase P41 --config experiments/p41-config.json --output /tmp/evobyte-p41-acceptance.json
```

Guardar configuração completa, comando real e artefato recuperável. Uma
fase técnica mede sua condição técnica; não fabrica números de velocidade.
Revisão científica, quando exigida acima, antecede a promoção do resultado.

## Risco principal

Guardar apenas um checksum sem os dados recuperáveis não permite reprodução.

## Commit & Push (obrigatório)

Começar de árvore limpa na branch declarada, a partir do predecessor aceito.
Stage apenas caminhos revisados com `git add` explícito. Escrever
`/tmp/evobyte-p41-pr.md` com problema, mudança, comandos reais, resultados,
artefatos e limitações. Todos os gates precisam estar verdes antes deste
bloco. Se esta fase precisar de subentregas, cada uma tem commit próprio e
não marca a fase inteira Done. Não executar merge automático.

```bash
git diff --cached --check
git commit -m "feat(research): implement p41 immutable-artifacts"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p41 immutable-artifacts" --body-file /tmp/evobyte-p41-pr.md
git status --short
```

Usar main somente se o predecessor já estiver integrado; caso contrário,
usar sua branch aceita como base do PR e registrar a dependência. Nunca
push direto à main, force-push ou bypass de hooks.
