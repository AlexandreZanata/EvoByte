# P70 — H10 — Buscar fórmulas para famílias de soluções

**Status:** Building (entregas 1–3: templates, proponente + comparação,
interface + config congelada; entrega 4 pendente: medição em árvore limpa
+ registro. Diagnóstico: outcome NULL — só os 3 controles provam.)
**Dependência:** P69 Done porém não integrado (PR #97 aberto); branch a
partir de `codex/p69-residue-synchronized-islands`, PR contra ela.
**Owner:** agente executor; revisor matemático/estatístico nos gates indicados.
**Pré-requisito:** P69 com entrega técnica aceita; módulos experimentais anteriores sem ganho permanecem desligados. Para P61–P70 exige também a bancada P60 aceita.
**Branch:** `codex/p70-parametric-proof-search`.

## Hipótese, objetivo e escopo

Um proponente pequeno pode descobrir um template que resolve muitos casos e admite uma prova curta.

Alterações permitidas: src/evobyte/grammar.py, benchmarks/open_problems.py, Lean e verificadores existentes.
Fora do escopo: outras hipóteses, reescrita de dados históricos, maior hardware,
novidade mundial presumida e alteração do checker para favorecer candidatos.

Ler [o contrato P58–P72](../FORMAL_SEARCH_PLAN.md#programa-especulativo-p58p72).
Uma microtarefa por ciclo; implementar, congelar e medir em entregas separadas
quando necessário, cada qual com gate próprio. Código novo não mede sua
confirmação final enquanto a revisão estiver suja.

## Trabalho ordenado

1. Nominar templates racionais de baixo grau, coeficientes limitados e classes n = m*k+r, com m em conjunto finito revisado. Congelar tamanho, domínio e condições; usar identidades conhecidas apenas como controles/treino.

2. Comparar proponente, busca estruturada e derivação algébrica clássica usando apenas filtros determinísticos comuns da base P59. Não empilhar modelos experimentais anteriores neste piloto; combinações exigem novo pré-registro e ablation. Custos de todos os componentes contam.

3. Para finalistas provar igualdade, denominadores não nulos, positividade e coordenadas inteiras no domínio inteiro declarado. Verificar que o enunciado provado coincide com a nominação; revisão humana precede alegação de família geral.

## Gate de saída

Família aceita somente com prova apropriada e condições explícitas; exemplos finitos permanecem candidate. Se nenhum template novo passar, relatar NULL/rediscovery sem modificar a gramática depois do resultado.

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

Interface de aceitação **implementada na entrega 3** (`run_p70_template_audit`):

```text
python3 benchmarks/science_matrix.py --acceptance-phase P70 --config experiments/p70-config.json --output /tmp/evobyte-p70-acceptance.json
```

A fase implementa somente sua capacidade, reutilizando módulos existentes.
Antes de medir, congelar configuração e run.sh com comando realmente testado.
`/tmp` é saída transitória; raw, pesos, checkpoint e manifesto precisam de
cópia durável recuperável com hashes. Não marcar Done por escrever este plano.

## Risco

Uma identidade racional correta pode não produzir inteiros positivos e portanto não resolver Erdős–Straus.

## Commit & Push (obrigatório)

Árvore limpa no início; branch da base aceita. Revisar diff e fazer stage
somente de caminhos explícitos. Escrever `/tmp/evobyte-p70-pr.md` com
problema, mudança, comandos, resultados, limites e referências recuperáveis.
Nenhum commit/push após gate vermelho. Um commit por microtarefa concluída;
implementação diagnóstica não marca confirmação científica Done.

```bash
git diff --cached --check
git commit -m "feat(research): implement p70 parametric-proof-search"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p70 parametric-proof-search" --body-file /tmp/evobyte-p70-pr.md
git status --short
```

Usar main como base apenas se o predecessor estiver integrado; senão usar
a branch aceita do predecessor e registrar a dependência. A entrega só de
medição/documentação usa `docs(research): record p70 experiment`.
Nunca push direto à main, force-push, bypass de hooks ou merge automático.
