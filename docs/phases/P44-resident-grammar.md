# P44 — Manter a evolução estruturada na GPU

**Status:** Proposed.
**Pré-requisito:** P43, com as rotas negativas explícitas do runbook.
**Branch:** `codex/p44-resident-grammar`.

## Objetivo e escopo

Manter a evolução estruturada na GPU. Alterações permitidas: src/evobyte/grammar.py, src/evobyte/resident.py e tests/test_resident_evolution.py.
Fora de escopo: outras fases, mudança não registrada de hipótese, dados
históricos reescritos e promoção automática de descoberta.

Leia [o runbook](../FORMAL_SEARCH_PLAN.md) antes de implementar. Ele define
gates comuns, limites, esquema de evidência e rotas negativas. Executar uma
microtarefa por ciclo; não implementar todas as fases neste PR.

## Trabalho ordenado

1. Substituir a mutação por indivíduo em Python/NumPy por operações Torch em lote sobre tensores, conservando validade, dependências de registradores e semântica da gramática atual.
2. Preservar uma referência CPU determinística para testar validade e execução. Não exigir sequência RNG idêntica entre CPU e CUDA; exigir reprodutibilidade por backend e conformidade semântica.
3. Perfilar geração, mutação, execução e seleção. Transferências de finalistas/checkpoints são permitidas fora do ciclo; nenhum .cpu(), .numpy() ou .item() por indivíduo no ciclo residente.

## Gate de saída

Casos determinísticos CPU/GPU concordam; invalidez é rejeitada. Perfil de várias gerações não mostra transferência integral da população para CPU. Se não houver CUDA, marcar NOT_MEASURED e bloquear alegação residente.

Aplicar os gates comuns e a aceitação desta fase. A chamada abaixo é um
**contrato futuro a implementar**, não um comando já existente:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/science_matrix.py --acceptance-phase P44 --config experiments/p44-config.json --output /tmp/evobyte-p44-acceptance.json
```

Guardar configuração completa, comando real e artefato recuperável. Uma
fase técnica mede sua condição técnica; não fabrica números de velocidade.
Revisão científica, quando exigida acima, antecede a promoção do resultado.

## Risco principal

Não redesenhar o bytecode nem introduzir Triton nesta correção.

## Commit & Push (obrigatório)

Começar de árvore limpa na branch declarada, a partir do predecessor aceito.
Stage apenas caminhos revisados com `git add` explícito. Escrever
`/tmp/evobyte-p44-pr.md` com problema, mudança, comandos reais, resultados,
artefatos e limitações. Todos os gates precisam estar verdes antes deste
bloco. Se esta fase precisar de subentregas, cada uma tem commit próprio e
não marca a fase inteira Done. Não executar merge automático.

```bash
git diff --cached --check
git commit -m "feat(research): implement p44 resident-grammar"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p44 resident-grammar" --body-file /tmp/evobyte-p44-pr.md
git status --short
```

Usar main somente se o predecessor já estiver integrado; caso contrário,
usar sua branch aceita como base do PR e registrar a dependência. Nunca
push direto à main, force-push ou bypass de hooks.
