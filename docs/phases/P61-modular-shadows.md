# P61 — H02 — Buscar usando sombras aritméticas

**Status:** Building (entrega 1 neste ciclo: filtro + regressões; comparação
pareada/congelamento/medição pendentes).
**Dependência:** P60 Done porém não integrado (PR #88 aberto); branch a
partir de `codex/p60-hypothesis-workbench`, PR contra ela.
**Owner:** agente executor; revisor matemático/estatístico nos gates indicados.
**Pré-requisito:** P60 com entrega técnica aceita; módulos experimentais anteriores sem ganho permanecem desligados. Para P61–P70 exige também a bancada P60 aceita.
**Branch:** `codex/p61-modular-shadows`.

## Hipótese, objetivo e escopo

Filtros modulares baratos podem reduzir o custo total de obter certificados na mesma busca.

Alterações permitidas: benchmarks/open_problems.py, referência NumPy e filtros Torch existentes; tests/test_open_problems.py.
Fora do escopo: outras hipóteses, reescrita de dados históricos, maior hardware,
novidade mundial presumida e alteração do checker para favorecer candidatos.

Ler [o contrato P58–P72](../FORMAL_SEARCH_PLAN.md#programa-especulativo-p58p72).
Uma microtarefa por ciclo; implementar, congelar e medir em entregas separadas
quando necessário, cada qual com gate próprio. Código novo não mede sua
confirmação final enquanto a revisão estiver suja.

## Trabalho ordenado

1. Representar a identidade por resíduos em primos pequenos congelados. Na tupla, usar a condição necessária 4xyz = n(xy+xz+yz) módulo p, reduzindo após cada multiplicação para evitar overflow.

2. Não dividir módulo p quando não há inverso. Caso inconclusivo segue ao checker exato. CRT só reconstrói um valor quando unicidade sob os limites foi demonstrada; resíduos compatíveis por si só não são certificado.

3. Comparar exatamente os mesmos candidatos com/sem filtro, incluindo CPU/GPU transferências. Testar todas as soluções conhecidas para ausência de rejeição falsa e medir eliminação de falsos, custo do filtro e custo até certificado.

## Gate de saída

Zero rejeição falsa no conjunto exaustivo pequeno e fixtures conhecidos, conformidade CPU/GPU e relatório pareado do custo total. Se custo subir ou nenhum certificado aparecer, registrar NULL/INCONCLUSIVE.

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

Interface de aceitação **planejada, ainda não implementada para P61**:

```text
python3 benchmarks/science_matrix.py --acceptance-phase P61 --config experiments/p61-config.json --output /tmp/evobyte-p61-acceptance.json
```

A fase implementa somente sua capacidade, reutilizando módulos existentes.
Antes de medir, congelar configuração e run.sh com comando realmente testado.
`/tmp` é saída transitória; raw, pesos, checkpoint e manifesto precisam de
cópia durável recuperável com hashes. Não marcar Done por escrever este plano.

## Risco

Uma condição modular necessária não basta para garantir igualdade nos inteiros.

## Commit & Push (obrigatório)

Árvore limpa no início; branch da base aceita. Revisar diff e fazer stage
somente de caminhos explícitos. Escrever `/tmp/evobyte-p61-pr.md` com
problema, mudança, comandos, resultados, limites e referências recuperáveis.
Nenhum commit/push após gate vermelho. Um commit por microtarefa concluída;
implementação diagnóstica não marca confirmação científica Done.

```bash
git diff --cached --check
git commit -m "feat(research): implement p61 modular-shadows"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p61 modular-shadows" --body-file /tmp/evobyte-p61-pr.md
git status --short
```

Usar main como base apenas se o predecessor estiver integrado; senão usar
a branch aceita do predecessor e registrar a dependência. A entrega só de
medição/documentação usa `docs(research): record p61 experiment`.
Nunca push direto à main, force-push, bypass de hooks ou merge automático.
