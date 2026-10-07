# P67 — H06 — Criar novas instruções matemáticas verificadas

**Status:** Building (entregas 1–2: mineração + comparação de bibliotecas
com custos; congelamento/medição pendentes).
**Dependência:** P66 Done porém não integrado (PR #94 aberto); branch a
partir de `codex/p66-composite-search-jumps`, PR contra ela.
**Owner:** agente executor; revisor matemático/estatístico nos gates indicados.
**Pré-requisito:** P66 com entrega técnica aceita; módulos experimentais anteriores sem ganho permanecem desligados. Para P61–P70 exige também a bancada P60 aceita.
**Branch:** `codex/p67-verified-macros`.

## Hipótese, objetivo e escopo

Blocos reutilizáveis podem encurtar candidatos e reduzir o custo de busca sem ampliar o modelo.

Alterações permitidas: src/evobyte/bytecode.py, src/evobyte/grammar.py, docs/BYTECODE.md e tests/test_bytecode.py.
Fora do escopo: outras hipóteses, reescrita de dados históricos, maior hardware,
novidade mundial presumida e alteração do checker para favorecer candidatos.

Ler [o contrato P58–P72](../FORMAL_SEARCH_PLAN.md#programa-especulativo-p58p72).
Uma microtarefa por ciclo; implementar, congelar e medir em entregas separadas
quando necessário, cada qual com gate próprio. Código novo não mede sua
confirmação final enquanto a revisão estiver suja.

## Trabalho ordenado

1. Extrair até 32 sequências recorrentes de construções development. Canonicalizar entradas/saídas e demonstrar equivalência entre macro e expansão, incluindo domínio e constantes.

2. Começar com referências a blocos do bytecode existente, expandidos antes da execução. Se alterar opcode/codec/semântica, obter ADR, incrementar OPCODE_VERSION e conservar o intérprete anterior antes de medir.

3. Comparar biblioteca aprendida, biblioteca clássica de mesmo tamanho e biblioteca aleatória; incluir custo de mineração, verificação e expansão. Proibir mineração no final.

## Gate de saída

Todas as macros equivalentes à expansão em seus domínios; round-trip/versionamento passam. Ganho de compactação e ganho de certificado são medidas separadas.

Para P61–P70, NULL/INCONCLUSIVE íntegro encerra o teste da hipótese sem
promovê-la e permite a próxima hipótese da bancada. Falha de correção,
dados, aprovação exigida ou isolamento é BLOCKED e interrompe avanço.
P58–P60 exigem aprovação integral; resultado negativo não substitui gate.

Gates comuns, mais testes específicos e aceitação real da fase:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
```

Interface de aceitação **planejada, ainda não implementada para P67**:

```text
python3 benchmarks/science_matrix.py --acceptance-phase P67 --config experiments/p67-config.json --output /tmp/evobyte-p67-acceptance.json
```

A fase implementa somente sua capacidade, reutilizando módulos existentes.
Antes de medir, congelar configuração e run.sh com comando realmente testado.
`/tmp` é saída transitória; raw, pesos, checkpoint e manifesto precisam de
cópia durável recuperável com hashes. Não marcar Done por escrever este plano.

## Risco

Uma instrução poderosa sem cobrar sua implementação e descoberta cria uma vantagem fictícia.

## Commit & Push (obrigatório)

Árvore limpa no início; branch da base aceita. Revisar diff e fazer stage
somente de caminhos explícitos. Escrever `/tmp/evobyte-p67-pr.md` com
problema, mudança, comandos, resultados, limites e referências recuperáveis.
Nenhum commit/push após gate vermelho. Um commit por microtarefa concluída;
implementação diagnóstica não marca confirmação científica Done.

```bash
git diff --cached --check
git commit -m "feat(research): implement p67 verified-macros"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p67 verified-macros" --body-file /tmp/evobyte-p67-pr.md
git status --short
```

Usar main como base apenas se o predecessor estiver integrado; senão usar
a branch aceita do predecessor e registrar a dependência. A entrega só de
medição/documentação usa `docs(research): record p67 experiment`.
Nunca push direto à main, force-push, bypass de hooks ou merge automático.
