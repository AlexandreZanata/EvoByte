# P234 — Decisão científica do ciclo

Estado `PROPOSED`, proposta de 2026-11-05. Uma tarefa por ciclo.
Executor solicitado pelo usuário — Gemini Flash 3.8.

[Contrato comum obrigatório](../research/next/EVOBYTE_NEXT_RESEARCH_PROGRAM.md)

## Dependência e objetivo

P233 aceita ou encerrada por revisão com resultado inconclusivo explícito. Evidências e pareceres disponíveis.

Produzir uma decisão baseada nos pilotos sem criar uma nova sequência longa de fases.

## Arquivos permitidos

- `docs/research/p234-scientific-decision.md`
- `docs/DECISIONS.md`
- `docs/phases/P234-scientific-decision.md`, somente estado e evidências desta tarefa.

Os arquivos de implementação/saída listados acima são entregáveis futuros.
Conferir sua existência antes de editar e preservar alterações prévias.

## Antes de começar

Ler `AGENTS.md`, o contrato comum e o documento de experimentos. Confirmar
os pré-requisitos da fase e a revisão aprovada. A base `origin/main` deve
conter o plano e os predecessores aceitos.

```bash
set -euo pipefail
test -z "$(git status --porcelain)"
git fetch origin main
git switch -c codex/p234-scientific-decision origin/main
```

Se já estiver na branch indicada e ela estiver limpa, conferir a base e
continuar nela. Se o nome existir em outra posição ou houver arquivos
locais pendentes, parar com o estado observado.

## Passos da tarefa

1. Ler as evidências P229–P233 e comparar as alegações com o que seus
   checkers realmente conferem. Identificar resultado de engenharia,
   propriedade matemática e situação bibliográfica separadamente.
2. Para cada linha, apresentar ao revisor quatro opções com evidência
   concreta — `CONTINUE`, `REFORMULATE`, `METHOD_OR_NEGATIVE`, `ABANDON`.
   Registrar custo, garantia, ganho por caso, limite e risco de redundância.
3. Escrever a recomendação e a pergunta científica seguinte em uma frase.
   A decisão humana recebe autor/data reais. Sem decisão humana, usar
   `DECISION_PENDING` e encerrar com o material pronto para revisão.
4. Se houver candidato original, registrar literatura, versão e diferença.
   O rótulo permanece `NOVELTY_PENDING` até revisão humana identificada.
   Preparar um artefato reproduzível conforme a decisão escolhida.
5. Acrescentar uma entrada D052 ao log apenas depois de conferir que o ID
   está livre. Registrar explicitamente se é proposta ou decisão aprovada.
   Se D052 já existir por outro trabalho, parar e pedir resolução do ID.
6. Descrever o próximo ciclo em nível de objetivo e gate. Novas fases
   executáveis serão escritas após a revisão do resultado atual.

## Gate específico

Conferir os links e hashes dos relatórios, a decisão por linha e a
identidade dos revisores. O gate documental exige correspondência exata
entre alegação e evidência. Veredito negativo ou decisão pendente são
resultados admissíveis quando escritos com seu estado real. Executar
os gates globais antes do commit documental.


## Parada e entrega

Parar em discrepância de hash/resultado, API ausente, erro de execução,
limite técnico excedido sem saída íntegra ou decisão matemática pendente.
Guardar logs e arquivos locais. Um veredito científico negativo previsto
no contrato é entregue com a evidência correspondente e passa por revisão.

Executar os gates comuns, incluindo `make verify` e formatação. Antes de
encerrar, reportar arquivos alterados, comandos e códigos de saída,
artefatos e hashes, veredito, limitações, commit e PR. A fase fica em revisão
até o aceite humano de seu gate final. O próximo ciclo depende desse aceite.

## Commit & Push

Somente depois de todos os gates verdes, revisar o diff e escrever o corpo
do PR em `/tmp/evobyte-p234-pr.md`, com resultado, comandos e limites reais.
Conferir a lista abaixo contra o escopo autorizado.

```bash
git diff --check
git add -- docs/research/p234-scientific-decision.md \
  docs/DECISIONS.md \
  docs/phases/P234-scientific-decision.md
git diff --cached --check
git diff --cached --stat
git commit -m "docs(research): record low-compute cycle decision"
git push -u origin codex/p234-scientific-decision
gh pr create --base main --head codex/p234-scientific-decision \
  --title "docs(research): record low-compute cycle decision" \
  --body-file /tmp/evobyte-p234-pr.md
git status --short
```

Se houver PR aberto para essa branch, atualizar seu corpo com `gh pr edit`
e o mesmo arquivo. O revisor realiza o aceite e a integração.
