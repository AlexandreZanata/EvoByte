# P71 — Confirmar as hipóteses selecionadas sem reabrir testes antigos

**Status:** Building (entrega 1 neste ciclo: final congelado + procedimento
+ interface de aceitação; medição em árvore limpa + pacote de reprodução
pendentes. Diagnóstico: H06/H08 INCONCLUSIVE, só DIRTY_SOURCE bloqueia.
Operador independente confirmado: IA independente em outra máquina.).
**Dependência:** P70 Done porém não integrado; branch a partir de
`codex/p70-parametric-proof-search`.
**Owner:** agente executor; revisor matemático/estatístico nos gates indicados.
**Pré-requisito:** P70 com entrega técnica aceita; módulos experimentais anteriores sem ganho permanecem desligados. Para P61–P70 exige também a bancada P60 aceita.
**Branch:** `codex/p71-independent-hypothesis-confirmation`.

## Hipótese, objetivo e escopo

Confirmar no máximo dois resultados de triagem; ainda sem declarar descoberta matemática.

Alterações permitidas: Configuração congelada, dados externos, checker já aceito e relatório; nenhuma alteração de algoritmo.
Fora do escopo: outras hipóteses, reescrita de dados históricos, maior hardware,
novidade mundial presumida e alteração do checker para favorecer candidatos.

Ler [o contrato P58–P72](../FORMAL_SEARCH_PLAN.md#programa-especulativo-p58p72).
Uma microtarefa por ciclo; implementar, congelar e medir em entregas separadas
quando necessário, cada qual com gate próprio. Código novo não mede sua
confirmação final enquanto a revisão estiver suja.

## Trabalho ordenado

1. Escolher no máximo dois métodos por regra P60, usando somente development. Antes de abrir dados finais congelar revisão limpa, pesos, macros, seeds, custos e procedimento estatístico; método composto precisa ablation de seus componentes.

2. Definir teste novo nunca usado, por exemplo primos 1 mod 24 em intervalo acima de 100000, somente após revisão de viabilidade/bounds. Usar ao menos seis grupos independentes e 20 seeds, baseline forte e inputs iguais. Teto de duas horas por método; se a configuração não couber, redefinir antes de acesso, nunca encurtar silenciosamente.

3. Revisor estatístico fixa análise pareada por grupo, censura e correção pela seleção entre dez hipóteses (Holm quando aplicável); não tratar seeds repetidos como problemas independentes. Outro operador reproduz resultados e checker exato/formal em revisão limpa.

Delegação e disposições técnicas D019 não substituem esse outro operador.
P38/P56 e dados P57 usados em desenvolvimento continuam inelegíveis como final.
Sem reprodução independente, registrar PROVISIONAL e impedir promoção para
P72; preservar dados e preparar o pacote de reprodução em microtarefa própria.

## Gate de saída

Resultados completos, positivos e negativos, dados recuperáveis e revisão independente. Sem poder/soluções suficientes é INCONCLUSIVE; sem operador independente é PROVISIONAL. Somente método com evidência aceita entra em P72.

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

Interface de aceitação **implementada na entrega 1** (`run_p71_confirmation_audit`):

```text
python3 benchmarks/science_matrix.py --acceptance-phase P71 --config experiments/p71-config.json --output /tmp/evobyte-p71-acceptance.json
```

A fase implementa somente sua capacidade, reutilizando módulos existentes.
Antes de medir, congelar configuração e run.sh com comando realmente testado.
`/tmp` é saída transitória; raw, pesos, checkpoint e manifesto precisam de
cópia durável recuperável com hashes. Não marcar Done por escrever este plano.

## Risco

Escolher o melhor entre dez pilotos e reportar seu ganho sem controle de seleção inflaciona a conclusão.

## Commit & Push (obrigatório)

Árvore limpa no início; branch da base aceita. Revisar diff e fazer stage
somente de caminhos explícitos. Escrever `/tmp/evobyte-p71-pr.md` com
problema, mudança, comandos, resultados, limites e referências recuperáveis.
Nenhum commit/push após gate vermelho. Um commit por microtarefa concluída;
implementação diagnóstica não marca confirmação científica Done.

```bash
git diff --cached --check
git commit -m "feat(research): implement p71 independent-hypothesis-confirmation"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p71 independent-hypothesis-confirmation" --body-file /tmp/evobyte-p71-pr.md
git status --short
```

Usar main como base apenas se o predecessor estiver integrado; senão usar
a branch aceita do predecessor e registrar a dependência. A entrega só de
medição/documentação usa `docs(research): record p71 experiment`.
Nunca push direto à main, force-push, bypass de hooks ou merge automático.
