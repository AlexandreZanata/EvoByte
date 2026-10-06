# P72 — Nominar um resultado matemático e verificar novidade

**Status:** Proposed.
**Owner:** agente executor; revisor matemático/estatístico nos gates indicados.
**Pré-requisito:** P71 com entrega técnica aceita; módulos experimentais anteriores sem ganho permanecem desligados. Para P61–P70 exige também a bancada P60 aceita.
**Branch:** `codex/p72-novelty-nomination`.

## Hipótese, objetivo e escopo

Aplicar o método aceito a um alvo preciso; novidade depende de prova e literatura, não do tamanho da busca.

Alterações permitidas: benchmarks/open_problems.py, certificados/provas e docs/research/novelty-review.md.
Fora do escopo: outras hipóteses, reescrita de dados históricos, maior hardware,
novidade mundial presumida e alteração do checker para favorecer candidatos.

Ler [o contrato P58–P72](../FORMAL_SEARCH_PLAN.md#programa-especulativo-p58p72).
Uma microtarefa por ciclo; implementar, congelar e medir em entregas separadas
quando necessário, cada qual com gate próprio. Código novo não mede sua
confirmação final enquanto a revisão estiver suja.

## Trabalho ordenado

1. Escolher um único alvo do catálogo revisado ou um lema/construção definido precisamente. Confirmar estado atual e resultados parciais em fontes primárias; separar novo algoritmo, nova instância e novo teorema.

2. Congelar campanha, baseline, domínio e limite total de uma hora antes de iniciar. Somente usar componentes aceitos; rechecagem independente de todo resultado promovido e correspondência do enunciado são obrigatórias.

3. Comparar com literatura e obter revisão matemática independente. Registrar candidato, rediscovery, verified-construction, theorem ou budget-exhausted de acordo com a evidência. Qualquer expansão do domínio/hipótese começa novo ciclo; não publicar anúncio de descoberta automaticamente.

## Gate de saída

Dossiê reproduzível com certificado/prova e avaliação de novidade. Descoberta requer correção, novidade sustentada e reprodução/revisão independentes; resultado negativo íntegro encerra a campanha sem promoção.

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

Interface de aceitação **planejada, ainda não implementada para P72**:

```text
python3 benchmarks/science_matrix.py --acceptance-phase P72 --config experiments/p72-config.json --output /tmp/evobyte-p72-acceptance.json
```

A fase implementa somente sua capacidade, reutilizando módulos existentes.
Antes de medir, congelar configuração e run.sh com comando realmente testado.
`/tmp` é saída transitória; raw, pesos, checkpoint e manifesto precisam de
cópia durável recuperável com hashes. Não marcar Done por escrever este plano.

## Risco

Uma construção inédita na base local pode já existir na literatura; nenhum teste finito demonstra automaticamente uma conjectura universal.

## Commit & Push (obrigatório)

Árvore limpa no início; branch da base aceita. Revisar diff e fazer stage
somente de caminhos explícitos. Escrever `/tmp/evobyte-p72-pr.md` com
problema, mudança, comandos, resultados, limites e referências recuperáveis.
Nenhum commit/push após gate vermelho. Um commit por microtarefa concluída;
implementação diagnóstica não marca confirmação científica Done.

```bash
git diff --cached --check
git commit -m "feat(research): implement p72 novelty-nomination"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p72 novelty-nomination" --body-file /tmp/evobyte-p72-pr.md
git status --short
```

Usar main como base apenas se o predecessor estiver integrado; senão usar
a branch aceita do predecessor e registrar a dependência. A entrega só de
medição/documentação usa `docs(research): record p72 experiment`.
Nunca push direto à main, force-push, bypass de hooks ou merge automático.
