# P42 — Corrigir a certificação matemática

**Status:** Done.
**Pré-requisito:** P41, com as rotas negativas explícitas do runbook.
**Branch:** `codex/p42-exact-certification`.
**Resultado:** ACCEPTED — 4/4 identidades P35 revalidadas por certificado exato
em novos registros (original intacto); controles falsos rejeitados; regra
prospectiva verificada (positivos ⇒ exact_certificate).

## Objetivo e escopo

Corrigir a certificação matemática. Alterações permitidas: src/evobyte/verifier.py, benchmarks/math_specialist.py e tests/test_verifier_l2.py.
Fora de escopo: outras fases, mudança não registrada de hipótese, dados
históricos reescritos e promoção automática de descoberta.

Leia [o runbook](../FORMAL_SEARCH_PLAN.md) antes de implementar. Ele define
gates comuns, limites, esquema de evidência e rotas negativas. Executar uma
microtarefa por ciclo; não implementar todas as fases neste PR.

## Trabalho ordenado

1. Unificar nomes e hipóteses dos símbolos entre programa e alvo na equivalência simbólica. Revalidar os quatro candidatos P35 em novos artefatos, sem editar o registro original.
2. Usar igualdade exata sobre inteiros/racionais ou identidade simbólica com domínio explícito. MSE baixo continua sendo filtro; não vira certificado. Frações com denominador zero, domínio inválido e overflow são rejeitadas.
3. Adicionar regressões de identidade verdadeira, identidade falsa que coincide em pontos de treino, diferença de hipóteses de símbolos e certificado numérico inválido. Rotular numerical_evidence e exact_certificate separadamente.

## Gate de saída

As quatro identidades são aceitas ou rejeitadas por verificação exata reproduzível; controles falsos são rejeitados. Nenhum positivo de treinamento nasce apenas de tolerância numérica.

Aplicar os gates comuns e a aceitação desta fase. A chamada abaixo é um
**contrato futuro a implementar**, não um comando já existente:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/science_matrix.py --acceptance-phase P42 --config experiments/p42-config.json --output /tmp/evobyte-p42-acceptance.json
```

Guardar configuração completa, comando real e artefato recuperável. Uma
fase técnica mede sua condição técnica; não fabrica números de velocidade.
Revisão científica, quando exigida acima, antecede a promoção do resultado.

## Risco principal

Simplificação simbólica pode exigir condições de domínio; registrar e verificar essas condições.

## Commit & Push (obrigatório)

Começar de árvore limpa na branch declarada, a partir do predecessor aceito.
Stage apenas caminhos revisados com `git add` explícito. Escrever
`/tmp/evobyte-p42-pr.md` com problema, mudança, comandos reais, resultados,
artefatos e limitações. Todos os gates precisam estar verdes antes deste
bloco. Se esta fase precisar de subentregas, cada uma tem commit próprio e
não marca a fase inteira Done. Não executar merge automático.

```bash
git diff --cached --check
git commit -m "feat(research): implement p42 exact-certification"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p42 exact-certification" --body-file /tmp/evobyte-p42-pr.md
git status --short
```

Usar main somente se o predecessor já estiver integrado; caso contrário,
usar sua branch aceita como base do PR e registrar a dependência. Nunca
push direto à main, force-push ou bypass de hooks.
