# P62 — H01 — Aprender a corrigir formatos de erro

**Status:** Building (entregas 1–3: primitivas, reparador + comparação,
interface + config congelada; entrega 4 pendente: medição em árvore limpa
+ registro. Diagnóstico: outcome NULL — learned 2/4 vs clássico 4/4.)
**Dependência:** P61 Done porém não integrado (PR #89 aberto); branch a
partir de `codex/p61-modular-shadows`, PR contra ela.
**Owner:** agente executor; revisor matemático/estatístico nos gates indicados.
**Pré-requisito:** P61 com entrega técnica aceita; módulos experimentais anteriores sem ganho permanecem desligados. Para P61–P70 exige também a bancada P60 aceita.
**Branch:** `codex/p62-structured-error-repair`.

## Hipótese, objetivo e escopo

O padrão exato de resíduos/divisibilidade pode orientar reparos melhor que escolher o menor erro numérico.

Alterações permitidas: benchmarks/open_problems.py, src/evobyte/generator.py e testes de certificado.
Fora do escopo: outras hipóteses, reescrita de dados históricos, maior hardware,
novidade mundial presumida e alteração do checker para favorecer candidatos.

Ler [o contrato P58–P72](../FORMAL_SEARCH_PLAN.md#programa-especulativo-p58p72).
Uma microtarefa por ciclo; implementar, congelar e medir em entregas separadas
quando necessário, cada qual com gate próprio. Código novo não mede sua
confirmação final enquanto a revisão estiver suja.

## Trabalho ordenado

1. Obter perturbações limitadas de certificados development e registrar resíduo inteiro exato, sinais e divisibilidade. Separar n/origem antes de treinar; não misturar soluções do mesmo problema nos splits.

2. Treinar um único reparador pequeno que escolhe edições inteiras limitadas, sem receber a solução privada da tarefa avaliada. Baselines: reparo aleatório e regra aritmética clássica sob a mesma vizinhança.

3. Congelar reparos permitidos e medir primeiro certificado por problema, custo de coleta/treino e ciclos de reparo. Proximidade residual só guia; aceitação usa checkers fixos.

## Gate de saída

Reparos respeitam domínio e limites, labels exatos e comparação com entradas iguais. Uma redução de resíduo sem mais certificados ou melhor custo não promove a hipótese.

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

Interface de aceitação **implementada na entrega 3** (`run_p62_repair_audit`):

```text
python3 benchmarks/science_matrix.py --acceptance-phase P62 --config experiments/p62-config.json --output /tmp/evobyte-p62-acceptance.json
```

A fase implementa somente sua capacidade, reutilizando módulos existentes.
Antes de medir, congelar configuração e run.sh com comando realmente testado.
`/tmp` é saída transitória; raw, pesos, checkpoint e manifesto precisam de
cópia durável recuperável com hashes. Não marcar Done por escrever este plano.

## Risco

O menor resíduo pode ser um beco sem saída; convergência numérica não é identidade.

## Commit & Push (obrigatório)

Árvore limpa no início; branch da base aceita. Revisar diff e fazer stage
somente de caminhos explícitos. Escrever `/tmp/evobyte-p62-pr.md` com
problema, mudança, comandos, resultados, limites e referências recuperáveis.
Nenhum commit/push após gate vermelho. Um commit por microtarefa concluída;
implementação diagnóstica não marca confirmação científica Done.

```bash
git diff --cached --check
git commit -m "feat(research): implement p62 structured-error-repair"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p62 structured-error-repair" --body-file /tmp/evobyte-p62-pr.md
git status --short
```

Usar main como base apenas se o predecessor estiver integrado; senão usar
a branch aceita do predecessor e registrar a dependência. A entrega só de
medição/documentação usa `docs(research): record p62 experiment`.
Nunca push direto à main, force-push, bypass de hooks ou merge automático.
