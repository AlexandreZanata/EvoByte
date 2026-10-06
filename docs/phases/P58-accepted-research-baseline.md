# P58 — Reconciliar evidências e liberar uma base de pesquisa

**Status:** Building (microtarefa A: auditor implementado + diagnóstico; aceitação final e revisão humana pendentes).
**Resultado parcial:** auditor `run_p58_acceptance_baseline_audit` rejeita fonte
suja, raw ausente e aprovação pendente e recheca os 932 certificados P57
com o checker exato; dossiê atual BLOCKED (revisão de escopo pendente).
**Owner:** agente executor; revisor matemático/estatístico nos gates indicados.
**Pré-requisito:** P57 registrado como resultado histórico; árvore limpa e predecessor identificado.
**Branch:** `codex/p58-accepted-research-baseline`.

## Hipótese, objetivo e escopo

Gate técnico; nenhuma nova hipótese matemática.

Alterações permitidas: src/evobyte/provenance.py, benchmarks/science_matrix.py, testes de integridade e relatórios de revisão existentes.
Fora do escopo: outras hipóteses, reescrita de dados históricos, maior hardware,
novidade mundial presumida e alteração do checker para favorecer candidatos.

Ler [o contrato P58–P72](../FORMAL_SEARCH_PLAN.md#programa-especulativo-p58p72).
Uma microtarefa por ciclo; implementar, congelar e medir em entregas separadas
quando necessário, cada qual com gate próprio. Código novo não mede sua
confirmação final enquanto a revisão estiver suja.

## Trabalho ordenado

1. Auditar P40–P57 sem mudar seus registros: hashes, dados recuperáveis, revisão efetivamente executada e aprovação científica. Preservar o rótulo provisório de P56 e as pendências P46/P47/P48/P54; Done documental não concede aprovação.

2. Recuperar dados brutos/weights/checkpoints de /tmp e arquivos ignorados para um destino durável escolhido no manifesto. Verificar tamanho/hash; dado ausente é MISSING_EVIDENCE. Não refazer silenciosamente um resultado nem reabrir os finais P38/P56.

3. Em microtarefa própria, fazer o auditor bloquear claims finais oriundos de código sujo, ausência de dados e avanço por gate pendente. Conferir novamente os 932 certificados P57 com checker exato. O revisor humano aprova enunciado e escopo da nova base, com registro identificável.

## Gate de saída

Auditor rejeita fixtures de fonte suja, raw ausente e aprovação pendente; certificados recuperados são checados. A entrada em P59 requer revisão científica aplicável concluída e uma revisão de código aceita. Se a aprovação faltar, entregar o dossiê e manter BLOCKED.

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

Interface de aceitação **planejada, ainda não implementada para P58**:

```text
python3 benchmarks/science_matrix.py --acceptance-phase P58 --config experiments/p58-config.json --output /tmp/evobyte-p58-acceptance.json
```

A fase implementa somente sua capacidade, reutilizando módulos existentes.
Antes de medir, congelar configuração e run.sh com comando realmente testado.
`/tmp` é saída transitória; raw, pesos, checkpoint e manifesto precisam de
cópia durável recuperável com hashes. Não marcar Done por escrever este plano.

## Risco

Uma repetição em processo novo não transforma uma revisão de código suja em experimento reproduzido de revisão limpa.

## Commit & Push (obrigatório)

Árvore limpa no início; branch da base aceita. Revisar diff e fazer stage
somente de caminhos explícitos. Escrever `/tmp/evobyte-p58-pr.md` com
problema, mudança, comandos, resultados, limites e referências recuperáveis.
Nenhum commit/push após gate vermelho. Um commit por microtarefa concluída;
implementação diagnóstica não marca confirmação científica Done.

```bash
git diff --cached --check
git commit -m "feat(research): implement p58 accepted-research-baseline"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p58 accepted-research-baseline" --body-file /tmp/evobyte-p58-pr.md
git status --short
```

Usar main como base apenas se o predecessor estiver integrado; senão usar
a branch aceita do predecessor e registrar a dependência. A entrega só de
medição/documentação usa `docs(research): record p58 experiment`.
Nunca push direto à main, force-push, bypass de hooks ou merge automático.
