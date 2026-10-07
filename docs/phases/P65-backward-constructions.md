# P65 — H04 — Inventar respostas e procurar pontes para o alvo

**Status:** Done (entregas 1–4: biblioteca + pontes, seletor + comparação,
interface + comando congelado, medição ACCEPTED em árvore limpa
`run_id=cf7562112ad0818c` com outcome NULL íntegro; registro em
`docs/research/p65-bridge-record.md`). H04 encerrada sem promoção; P66
liberada.
**Dependência:** P64 Done porém não integrado (PR #92 aberto); branch a
partir de `codex/p64-learned-obstructions`, PR contra ela.
**Owner:** agente executor; revisor matemático/estatístico nos gates indicados.
**Pré-requisito:** P64 com entrega técnica aceita; módulos experimentais anteriores sem ganho permanecem desligados. Para P61–P70 exige também a bancada P60 aceita.
**Branch:** `codex/p65-backward-constructions`.

## Hipótese, objetivo e escopo

Construções corretas geradas antes do alvo podem fornecer pontes curtas para uma tarefa difícil.

Alterações permitidas: src/evobyte/grammar.py, benchmarks/open_problems.py e verificadores exatos/formais existentes.
Fora do escopo: outras hipóteses, reescrita de dados históricos, maior hardware,
novidade mundial presumida e alteração do checker para favorecer candidatos.

Ler [o contrato P58–P72](../FORMAL_SEARCH_PLAN.md#programa-especulativo-p58p72).
Uma microtarefa por ciclo; implementar, congelar e medir em entregas separadas
quando necessário, cada qual com gate próprio. Código novo não mede sua
confirmação final enquanto a revisão estiver suja.

## Trabalho ordenado

1. Gerar pequenas identidades/construções exatas com parâmetros e armazenar representação compacta com hipóteses e limites. Não apresentar identidades tautológicas como avanço.

2. Reusar transformações verificadas para tentar mapear a construção para uma tarefa development; um modelo pequeno escolhe pontes a partir de features públicas.

3. Cobrar geração da biblioteca, busca da ponte e certificação. Comparar biblioteca aleatória, biblioteca estruturada sem modelo e busca direta; congelar tamanho máximo antes da coleta.

## Gate de saída

Cada ponte aceita preserva as hipóteses e prova o alvo fixado, não um enunciado substituído. Sem ponte, resultado NULL. Casos reencontrados continuam rediscovery até revisão de novidade.

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

Interface de aceitação **implementada na entrega 3** (`run_p65_bridge_audit`):

```text
python3 benchmarks/science_matrix.py --acceptance-phase P65 --config experiments/p65-config.json --output /tmp/evobyte-p65-acceptance.json
```

A fase implementa somente sua capacidade, reutilizando módulos existentes.
Antes de medir, congelar configuração e run.sh com comando realmente testado.
`/tmp` é saída transitória; raw, pesos, checkpoint e manifesto precisam de
cópia durável recuperável com hashes. Não marcar Done por escrever este plano.

## Risco

Uma biblioteca gigantesca pode esconder o custo real atrás de uma inferência barata.

## Commit & Push (obrigatório)

Árvore limpa no início; branch da base aceita. Revisar diff e fazer stage
somente de caminhos explícitos. Escrever `/tmp/evobyte-p65-pr.md` com
problema, mudança, comandos, resultados, limites e referências recuperáveis.
Nenhum commit/push após gate vermelho. Um commit por microtarefa concluída;
implementação diagnóstica não marca confirmação científica Done.

```bash
git diff --cached --check
git commit -m "feat(research): implement p65 backward-constructions"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p65 backward-constructions" --body-file /tmp/evobyte-p65-pr.md
git status --short
```

Usar main como base apenas se o predecessor estiver integrado; senão usar
a branch aceita do predecessor e registrar a dependência. A entrega só de
medição/documentação usa `docs(research): record p65 experiment`.
Nunca push direto à main, force-push, bypass de hooks ou merge automático.
