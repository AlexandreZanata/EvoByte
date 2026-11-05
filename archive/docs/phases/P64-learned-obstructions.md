# P64 — H03 — Aprender regiões proibidas e tentar prová-las

**Status:** Done (entregas 1–4: regras + prova, economia + scan,
interface + comando congelado, medição ACCEPTED em árvore limpa
`run_id=b25f80931994a537` com outcome NULL íntegro; registro em
`docs/research/p64-obstruction-record.md`). H03 encerrada sem promoção;
P65 liberada.
**Dependência:** P63 Done porém não integrado (PR #91 aberto); branch a
partir de `codex/p63-verifier-feedback`, PR contra ela.
**Owner:** agente executor; revisor matemático/estatístico nos gates indicados.
**Pré-requisito:** P63 com entrega técnica aceita; módulos experimentais anteriores sem ganho permanecem desligados. Para P61–P70 exige também a bancada P60 aceita.
**Branch:** `codex/p64-learned-obstructions`.

## Hipótese, objetivo e escopo

Condições de impossibilidade demonstradas podem eliminar regiões grandes com pouco modelo.

Alterações permitidas: benchmarks/open_problems.py, src/evobyte/generator.py e fronteira formal em src/evobyte/verifier.py.
Fora do escopo: outras hipóteses, reescrita de dados históricos, maior hardware,
novidade mundial presumida e alteração do checker para favorecer candidatos.

Ler [o contrato P58–P72](../FORMAL_SEARCH_PLAN.md#programa-especulativo-p58p72).
Uma microtarefa por ciclo; implementar, congelar e medir em entregas separadas
quando necessário, cada qual com gate próprio. Código novo não mede sua
confirmação final enquanto a revisão estiver suja.

## Trabalho ordenado

1. Gerar pequenas regras sobre paridade, divisibilidade e intervalos usando erros development. A rede sugere a regra; não decide sua verdade.

2. Tentar demonstrar cada regra no domínio declarado ou enumerar completamente um domínio finito pequeno. Um timeout de busca não é label impossível.

3. Regra sem prova serve apenas de prioridade com pelo menos 10% de exploração não filtrada. Somente regra provada pode eliminar candidatos permanentemente; comparar custo da prova com busca poupada.

## Gate de saída

Toda exclusão permanente tem certificado verificável; nenhum conhecido válido é descartado. Publicar cobertura e limites da regra. Sem prova, relatar priorização heurística, nunca impossibilidade matemática.

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

Interface de aceitação **implementada na entrega 3** (`run_p64_obstruction_audit`):

```text
python3 benchmarks/science_matrix.py --acceptance-phase P64 --config experiments/p64-config.json --output /tmp/evobyte-p64-acceptance.json
```

A fase implementa somente sua capacidade, reutilizando módulos existentes.
Antes de medir, congelar configuração e run.sh com comando realmente testado.
`/tmp` é saída transitória; raw, pesos, checkpoint e manifesto precisam de
cópia durável recuperável com hashes. Não marcar Done por escrever este plano.

## Risco

Aprender que algo é raro não demonstra que seja impossível.

## Commit & Push (obrigatório)

Árvore limpa no início; branch da base aceita. Revisar diff e fazer stage
somente de caminhos explícitos. Escrever `/tmp/evobyte-p64-pr.md` com
problema, mudança, comandos, resultados, limites e referências recuperáveis.
Nenhum commit/push após gate vermelho. Um commit por microtarefa concluída;
implementação diagnóstica não marca confirmação científica Done.

```bash
git diff --cached --check
git commit -m "feat(research): implement p64 learned-obstructions"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p64 learned-obstructions" --body-file /tmp/evobyte-p64-pr.md
git status --short
```

Usar main como base apenas se o predecessor estiver integrado; senão usar
a branch aceita do predecessor e registrar a dependência. A entrega só de
medição/documentação usa `docs(research): record p64 experiment`.
Nunca push direto à main, force-push, bypass de hooks ou merge automático.
