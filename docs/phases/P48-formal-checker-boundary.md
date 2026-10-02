# P48 — Adicionar a fronteira de prova formal

**Status:** Proposed.
**Pré-requisito:** P47, com as rotas negativas explícitas do runbook.
**Branch:** `codex/p48-formal-checker-boundary`.

## Objetivo e escopo

Adicionar a fronteira de prova formal. Alterações permitidas: src/evobyte/verifier.py, integração fora do ciclo e uma pasta isolada de provas Lean com toolchain/dependências fixadas.
Fora de escopo: outras fases, mudança não registrada de hipótese, dados
históricos reescritos e promoção automática de descoberta.

Leia [o runbook](../FORMAL_SEARCH_PLAN.md) antes de implementar. Ele define
gates comuns, limites, esquema de evidência e rotas negativas. Executar uma
microtarefa por ciclo; não implementar todas as fases neste PR.

## Trabalho ordenado

1. Manter checadores exatos Python para testemunhas numéricas. Integrar Lean somente fora do ciclo GPU, com versões e imports fixados, timeout e processo separado. Formalizar primeiro identidades conhecidas simples sobre ℚ e um certificado numérico existente.
2. Conferir o enunciado contra um desafio imutável. Rejeitar sorry, axioma adicionado para assumir a resposta e dependências não permitidas. Registrar axiomas usados e repetir checagem com checker independente quando suportado pelo ambiente fixado.
3. Executar controles: prova válida, igualdade falsa, enunciado trocado e prova por hipótese não autorizada. Saída do compilador é diagnóstico; sucesso exige certificado realmente conferido. Se o checker não estiver disponível, fase fica BLOCKED, sem simular aceitação.

## Gate de saída

Controles válidos aceitos e todos os falsos rejeitados; certificado corresponde ao enunciado original. Revisão humana aprova a tradução do enunciado. Teste finito não recebe rótulo proven-theorem.

Aplicar os gates comuns e a aceitação desta fase. A chamada abaixo é um
**contrato futuro a implementar**, não um comando já existente:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/science_matrix.py --acceptance-phase P48 --config experiments/p48-config.json --output /tmp/evobyte-p48-acceptance.json
```

Guardar configuração completa, comando real e artefato recuperável. Uma
fase técnica mede sua condição técnica; não fabrica números de velocidade.
Revisão científica, quando exigida acima, antecede a promoção do resultado.

## Risco principal

O verificador confirma o enunciado formal e suas hipóteses, não corrige uma tradução errada.

## Commit & Push (obrigatório)

Começar de árvore limpa na branch declarada, a partir do predecessor aceito.
Stage apenas caminhos revisados com `git add` explícito. Escrever
`/tmp/evobyte-p48-pr.md` com problema, mudança, comandos reais, resultados,
artefatos e limitações. Todos os gates precisam estar verdes antes deste
bloco. Se esta fase precisar de subentregas, cada uma tem commit próprio e
não marca a fase inteira Done. Não executar merge automático.

```bash
git diff --cached --check
git commit -m "feat(research): implement p48 formal-checker-boundary"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p48 formal-checker-boundary" --body-file /tmp/evobyte-p48-pr.md
git status --short
```

Usar main somente se o predecessor já estiver integrado; caso contrário,
usar sua branch aceita como base do PR e registrar a dependência. Nunca
push direto à main, force-push ou bypass de hooks.
