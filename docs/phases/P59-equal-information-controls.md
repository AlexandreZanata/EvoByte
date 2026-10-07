# P59 — Estabelecer comparações com a mesma informação

**Status:** Building (entregas 1–2 entregues: fronteira/sentinelas e trial
pareado ES + ledger + escopo; entregas 3–4 pendentes).
**Dependência:** predecessor P58 aceito porém não integrado (PR #86 aberto);
branch a partir de `codex/p58-accepted-research-baseline`, PR contra ela.
**Owner:** agente executor; revisor matemático/estatístico nos gates indicados.
**Pré-requisito:** P58 R1–R4 aceita no escopo técnico D019 e predecessor
integrado; módulos experimentais anteriores sem ganho permanecem desligados.
P47 histórica não é pré-registro vigente; P54/P56 não sustentam superioridade.
**Branch:** `codex/p59-equal-information-controls`.

## Hipótese, objetivo e escopo

Gate de justiça experimental, não promessa de vitória de IA.

Alterações permitidas: benchmarks/math_specialist.py, benchmarks/open_problems.py, src/evobyte/grammar.py e testes de busca.
Fora do escopo: outras hipóteses, reescrita de dados históricos, maior hardware,
novidade mundial presumida e alteração do checker para favorecer candidatos.

Ler [o contrato P58–P72](../FORMAL_SEARCH_PLAN.md#programa-especulativo-p58p72).
Uma microtarefa por ciclo; implementar, congelar e medir em entregas separadas
quando necessário, cada qual com gate próprio. Código novo não mede sua
confirmação final enquanto a revisão estiver suja.

## Trabalho ordenado

1. Separar problema público, alvo privado de certificação e dados de treino. Para regressão simbólica todos recebem os mesmos pares x/y e domínio; a fórmula-alvo só chega ao verificador. _try_exact_horner_program(formula) é controle de compilação separado, nunca adversário de descoberta com informação privilegiada.

2. Para Erdős–Straus todos recebem n, limites, mesmo espaço de candidatos e mesmo warm-start quando houver. Incluir enumerador CPU, busca GPU existente e baseline clássico por fatoração/construção adequado à classe; famílias inaplicáveis não sustentam superioridade.

3. Adicionar teste sentinela: trocar a fórmula privada sem alterar amostras, seed e configuração não muda as propostas geradas antes de verificar. Registrar custos de treino, geração, inferência, filtros, verificadores e tracking; nenhuma parcela é subtraída do orçamento total do braço.

## Entregas por ciclo

1. Implementar fronteira de informação e regressões sentinelas usando fixtures
   conhecidas/development; não acessar P38/P56 nem gerar dados finais P71.
2. Implementar baselines comparáveis e contabilização integral; famílias sem
   baseline aplicável recebem restrição explícita de comparação.
3. Revisar e congelar configuração completa, fontes, espaço de candidatos,
   warm-start, custos e interface de aceitação realmente implementada.
4. Medir controles em árvore limpa e revisão aceita; registrar evidência em
   ciclo documental posterior. A confirmação de hipótese fica para P60/P71.

Um controle de engenharia pode demonstrar igualdade de inputs sem declarar
ganho estatístico. O compilador Horner permanece controle de resposta conhecida
e seus custos são reportados separadamente. Não reabrir a P54 para refazer uma
comparação retrospectiva nem exigir nova aprovação dos seus resultados para
corrigir o vazamento na implementação atual.

## Gate de saída

Entradas públicas idênticas verificadas; controle de vazamento passa; baselines fortes reproduzem controles. Relatório distingue compilação de uma resposta conhecida e descoberta a partir de entradas públicas.

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

Interface de aceitação **planejada, ainda não implementada para P59**:

```text
python3 benchmarks/science_matrix.py --acceptance-phase P59 --config experiments/p59-config.json --output /tmp/evobyte-p59-acceptance.json
```

A fase implementa somente sua capacidade, reutilizando módulos existentes.
Antes de medir, congelar configuração e run.sh com comando realmente testado.
`/tmp` é saída transitória; raw, pesos, checkpoint e manifesto precisam de
cópia durável recuperável com hashes. Não marcar Done por escrever este plano.

## Risco

Mesmos segundos com informações diferentes não constituem comparação justa.

## Commit & Push (obrigatório)

Árvore limpa no início; branch da base aceita. Revisar diff e fazer stage
somente de caminhos explícitos. Escrever `/tmp/evobyte-p59-pr.md` com
problema, mudança, comandos, resultados, limites e referências recuperáveis.
Nenhum commit/push após gate vermelho. Um commit por microtarefa concluída;
implementação diagnóstica não marca confirmação científica Done.

```bash
git diff --cached --check
git commit -m "feat(research): implement p59 equal-information-controls"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p59 equal-information-controls" --body-file /tmp/evobyte-p59-pr.md
git status --short
```

Usar main como base apenas se o predecessor estiver integrado; senão usar
a branch aceita do predecessor e registrar a dependência. A entrega só de
medição/documentação usa `docs(research): record p59 experiment`.
Nunca push direto à main, force-push, bypass de hooks ou merge automático.
