# P58 — Reconciliar evidências e liberar uma base de pesquisa

**Status:** Building / BLOCKED para P59; correção documental D019 planejada,
auditor e dossiê ainda precisam executar as microtarefas abaixo.
**Resultado parcial:** auditor `run_p58_acceptance_baseline_audit` rejeita fonte
suja, raw ausente e aprovação pendente e recheca os 932 certificados P57
com o checker exato; 18 evidências de aceitação P40–P57 recuperadas de
`/tmp` para `experiments/p58-recovered-acceptance/` byte-idênticas com
hash registrado (cópias sem selo prévio, seguem provisionais); medição em
árvore limpa registra selos 3/3, certificados 932/932, raw 3/3 e recovery
18/18 + 0 missing. Revisão posterior identificou validação incompleta das
aprovações, limiares P47 ausentes, revisão estatística P54 não prévia e
P56 provisória. Esses itens exigem tratamento explícito; seis flags não
constituem aceitação. Os resultados históricos permanecem preservados.
**Owner:** agente executor; revisor matemático/estatístico nos gates indicados.
**Pré-requisito:** P57 registrado como resultado histórico; árvore limpa e predecessor identificado.
**Branch:** `codex/p58-accepted-research-baseline`.

## Hipótese, objetivo e escopo

Gate técnico; nenhuma nova hipótese matemática.

Alterações permitidas: src/evobyte/provenance.py, benchmarks/science_matrix.py,
testes de integridade, experiments/p58-config.json, experiments/p58-run.sh,
manifesto de recuperação e relatórios de revisão em docs/research/.
Fora do escopo: outras hipóteses, reescrita de dados históricos, maior hardware,
novidade mundial presumida e alteração do checker para favorecer candidatos.

Ler [o contrato P58–P72](../FORMAL_SEARCH_PLAN.md#programa-especulativo-p58p72).
Uma microtarefa por ciclo; implementar, congelar e medir em entregas separadas
quando necessário, cada qual com gate próprio. Código novo não mede sua
confirmação final enquanto a revisão estiver suja.

## Trabalho ordenado

1. Auditar P40–P57 sem mudar seus registros: hashes, dados recuperáveis, revisão efetivamente executada e aprovação científica. Preservar o rótulo provisório de P56 e as pendências P46/P47/P48/P54; Done documental não concede aprovação.

2. Recuperar dados brutos/weights/checkpoints de /tmp e arquivos ignorados para um destino durável escolhido no manifesto. Verificar tamanho/hash; dado ausente é MISSING_EVIDENCE. Não refazer silenciosamente um resultado nem reabrir os finais P38/P56.

3. Executar a sequência corretiva abaixo, uma entrega por ciclo. Não trocar
as seis flags para `approved` como implementação da revisão.

## Microtarefas corretivas (D019)

**R1 — Contrato das decisões e auditor. Entregue em 57c6c88.** Exigir exatamente
uma decisão para cada ID: `p46-catalogue-review`, `p47-nomination-review`,
`p48-translation-review`, `p54-statistical-review`, `p56-independent-review`
e `p58-scope-review`. Exigir responsável, executor, data, escopo, justificativa,
origem da autorização, revisão examinada e caminho/hash dos pareceres e suas
evidências. Validar arquivos, hashes e consistência entre decisão e uso permitido;
não aceitar um nome ou status isolado. Exigir também revisão de código aceita
com registro identificável. Identificar o responsável que autorizou a delegação
e o executor real; distinguir esse registro da independência científica.

O contrato deve distinguir `accepted_for_base` de aprovação científica do
resultado histórico. Cada decisão declara uma disposição verificável:
`reference_only`, `excluded_from_claims` ou `approved_for_current_use`, e os
usos permitidos/proibidos. Uma restrição só fecha o item da base se a configuração
efetivamente exclui o uso vedado. Lista ausente/vazia, ID faltante/duplicado,
registro sem evidência, hash alterado, rejeição no escopo atual, aprovação
pendente exigida pelo uso ou revisão de código ausente continuam BLOCKED.
Testar esses casos e a base restrita válida; manter regressões de fonte suja,
raw ausente, selo quebrado e certificado inválido. Não alterar o checker.
R1 entrega capacidade e diagnóstico, sem liberar P59.

**R2 — Dossiê rastreável e recuperação. Próxima microtarefa.** Versionar pareceres atuais e manifesto
de artefatos duráveis com tamanhos/hashes. Conferir destino de recuperação dos
pesos ignorados pelo Git, para que outro checkout possa recuperá-los sem depender
de `/tmp`; presença local não demonstra recuperação externa. Fonte externa
inacessível deve ter data/erro registrados e uso restrito ao snapshot disponível.
Não afirmar estado aberto atual sem fonte confirmada. Concluir revisão dos
objetos matemáticos e controles efetivamente usados pela base.

**R3 — Disposição dos seis itens e revisão de código.** Revisar o código R1 em
ciclo próprio e aplicar o contrato D019: P46 como referência datada quando não
revalidada; P47 incompleta excluída como pré-registro vigente; P48 limitada aos
dois desafios e evidência conferida; P54 DROP, modelo desligado e estatística
exploratória; P56 provisória, final consumido; P58 com escopo técnico explícito.
Registrar revisão e delegação em nome de Alexandre conforme autorização expressa,
com execução pelo agente identificada. Nenhuma disposição certifica retrospectivamente
limiares, revisão prévia, independência, ganho ou descoberta. Se um uso atual
depender de aprovação ainda ausente, restringir esse uso ou manter BLOCKED.
Congelar configuração e comando; todo campo deve estar resolvido.

**R4 — Medição final read-only.** Em revisão aceita e árvore limpa, executar a
interface existente abaixo, rechecar 932 certificados e salvar saída externa.
Exigir ACCEPTED no escopo da base, seis decisões íntegras, revisão de código
aceita e zero falhas técnicas; nenhuma escrita em entrada versionada ou abertura
de final. Só depois registrar resultado/hash em ciclo documental próprio.
P59 fica elegível após essa aceitação e entrega Commit & Push; integração do
predecessor continua necessária para trabalhar como base aceita.

## Gate de saída

Auditor rejeita as fixtures R1; certificados e recuperação passam. A entrada em
P59 requer R1–R4 concluídas, revisão aplicável ao uso atual e revisão de código
aceitas. Pendência histórica pode ser preservada com disposição restritiva
auditada; não pode ser omitida nem usada como evidência aprovada. O contrato
atual ainda não implementa essas disposições: escrever o plano não libera P59.

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

Interface de aceitação **existente; contrato R1 de decisões ainda a implementar**:

```text
python3 benchmarks/science_matrix.py --acceptance-phase P58 --config experiments/p58-config.json --output /tmp/evobyte-p58-acceptance.json
```

A fase implementa somente sua capacidade, reutilizando módulos existentes.
Antes de medir, congelar configuração e run.sh com comando realmente testado.
`/tmp` é saída transitória; raw, pesos, checkpoint e manifesto precisam de
cópia durável recuperável com hashes. Não marcar Done por escrever este plano.

## Risco

Uma repetição em processo novo não transforma uma revisão de código suja em experimento reproduzido de revisão limpa.
Aceitar uma base técnica com restrições não aceita as conclusões históricas;
qualquer promoção exige seus gates científicos prospectivos ou independentes.

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
