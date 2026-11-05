# P60 — Congelar a bancada e o pré-registro das dez hipóteses

**Status:** Done (entregas 1–4: manifesto, revisão + pré-registro,
interface + comando congelado, medição ACCEPTED em árvore limpa
`run_id=ced679eb2bdcb324`; registro em
`docs/research/p60-acceptance-record.md`). P61–P70 desbloqueadas sob seus
gates; confirmação em P71.
**Dependência:** P59 Done porém não integrado (PR #87 aberto); branch a
partir de `codex/p59-equal-information-controls`, PR contra ela.
**Owner:** agente executor; revisor matemático/estatístico nos gates indicados.
**Pré-requisito:** P59 com entrega técnica aceita; módulos experimentais anteriores sem ganho permanecem desligados. Para P61–P70 exige também a bancada P60 aceita.
**Branch:** `codex/p60-hypothesis-workbench`.

## Hipótese, objetivo e escopo

Definir dez mecanismos falsificáveis sem afirmar ineditismo mundial.

Alterações permitidas: benchmarks/open_problems.py, benchmarks/science_matrix.py, src/evobyte/provenance.py, manifesto de bancada e docs/research/.
Fora do escopo: outras hipóteses, reescrita de dados históricos, maior hardware,
novidade mundial presumida e alteração do checker para favorecer candidatos.

Ler [o contrato P58–P72](../FORMAL_SEARCH_PLAN.md#programa-especulativo-p58p72).
Uma microtarefa por ciclo; implementar, congelar e medir em entregas separadas
quando necessário, cada qual com gate próprio. Código novo não mede sua
confirmação final enquanto a revisão estiver suja.

## Trabalho ordenado

1. Nominar uma família principal: construções limitadas de Erdős–Straus. Candidato é tupla inteira ou template numérico versionado com domínio declarado; certificado é exato. Verificador permanece imutável nos dez braços. Reusar P57 como desenvolvimento, nunca como teste fresco.

2. Congelar seis tarefas development, três seeds e comparação baseline versus uma hipótese por vez, 10 s totais de busca/certificação por tentativa e teto de 30 min por hipótese incluindo coleta e treino. Controles conhecidos/falsos ficam fora da métrica de descoberta. Reserva inicial de modelo <=100 mil parâmetros e teto absoluto de 1 milhão; não ampliar sem nova hipótese/ADR.

3. Revisar literatura por mecanismo e registrar sobreposições com técnicas existentes; nome fantasioso não comprova novidade. Definir PROMISING, NULL, INCONCLUSIVE e BLOCKED, tratamento de censura e escolha do método antes das medidas. Registrar revisão matemática/estatística identificável antes de medir. Delegação explícita segue D019: responsável e executor separados, sem presumir reprodução independente ou aprovação que não foi autorizada.

## Pré-registro prospectivo obrigatório

Usar nova nominação, com versão/hash próprios, sem editar o selo P47 histórico.
Resolver valores de todas as quantidades: efeito mínimo, razão de tempos,
número de grupos/tarefas/seeds, orçamento por braço e global, parada e precisão
necessária. O procedimento especifica desfecho primário e falsificação coerentes,
unidade de agrupamento, censura, seleção e controles. Seeds repetidos são
repetições dentro de uma tarefa; não se contam como problemas independentes.
Não excluir timeouts para produzir o intervalo principal. Limiares P47 ainda
pendentes não são herdados como aprovação, nem os números propostos aqui
substituem revisão prévia. Seis tarefas/três seeds são desenho de triagem;
não garantem poder estatístico ou confirmação.

Entregar em ciclos separados: manifesto/procedimento e capacidades necessárias;
revisão e congelamento antes das medidas; aceitação técnica limpa da bancada;
registro documental. Registrar autorização efetiva para cada escopo revisado;
ausência de revisão exigida bloqueia a medição, mas permite preparar a correção
ou o dossiê em próxima microtarefa. Reservar final novo e fechado para P71.

## Gate de saída

Configuração completa e commit/hash congelados, interfaces reais testadas, entradas iguais, controles de overflow/domínio, orçamento global registrado e revisão concluída. Indicadores aproximados não substituem a certificação. O final futuro permanece fechado.

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

Interface de aceitação **implementada na entrega 3** (`run_p60_workbench_audit`):

```text
python3 benchmarks/science_matrix.py --acceptance-phase P60 --config experiments/p60-config.json --output /tmp/evobyte-p60-acceptance.json
```

A fase implementa somente sua capacidade, reutilizando módulos existentes.
Antes de medir, congelar configuração e run.sh com comando realmente testado.
`/tmp` é saída transitória; raw, pesos, checkpoint e manifesto precisam de
cópia durável recuperável com hashes. Não marcar Done por escrever este plano.

## Risco

Dez testes implicam seleção e comparações múltiplas; triagem positiva não é confirmação científica.

## Commit & Push (obrigatório)

Árvore limpa no início; branch da base aceita. Revisar diff e fazer stage
somente de caminhos explícitos. Escrever `/tmp/evobyte-p60-pr.md` com
problema, mudança, comandos, resultados, limites e referências recuperáveis.
Nenhum commit/push após gate vermelho. Um commit por microtarefa concluída;
implementação diagnóstica não marca confirmação científica Done.

```bash
git diff --cached --check
git commit -m "feat(research): implement p60 hypothesis-workbench"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p60 hypothesis-workbench" --body-file /tmp/evobyte-p60-pr.md
git status --short
```

Usar main como base apenas se o predecessor estiver integrado; senão usar
a branch aceita do predecessor e registrar a dependência. A entrega só de
medição/documentação usa `docs(research): record p60 experiment`.
Nunca push direto à main, force-push, bypass de hooks ou merge automático.
