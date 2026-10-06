# P63 — H08 — Orientar o modelo por códigos de rejeição

**Status:** Proposed.
**Owner:** agente executor; revisor matemático/estatístico nos gates indicados.
**Pré-requisito:** P62 com entrega técnica aceita; módulos experimentais anteriores sem ganho permanecem desligados. Para P61–P70 exige também a bancada P60 aceita.
**Branch:** `codex/p63-verifier-feedback`.

## Hipótese, objetivo e escopo

Códigos estruturados de rejeição podem oferecer orientação mais útil que um score único.

Alterações permitidas: src/evobyte/verifier.py, src/evobyte/generator.py, benchmarks/open_problems.py e testes de verifier.
Fora do escopo: outras hipóteses, reescrita de dados históricos, maior hardware,
novidade mundial presumida e alteração do checker para favorecer candidatos.

Ler [o contrato P58–P72](../FORMAL_SEARCH_PLAN.md#programa-especulativo-p58p72).
Uma microtarefa por ciclo; implementar, congelar e medir em entregas separadas
quando necessário, cada qual com gate próprio. Código novo não mede sua
confirmação final enquanto a revisão estiver suja.

## Trabalho ordenado

1. Expor códigos fixos para denominador zero, limite violado, resíduo não nulo, domínio inválido e prova incompleta; no ciclo só IDs/tensores, sem texto ou parsing. Não alterar enunciado, axiomas ou regra de aceitação.

2. Comparar o mesmo modelo/budget com códigos reais, códigos embaralhados e score escalar. Todas as consultas ao verificador entram no custo e têm limite registrado.

3. Treinar apenas em development; procurar reparos que produzam certificado. Persistir trajetória de rejeições e programa final para replay.

## Gate de saída

Checker falso permanece falso sob todos os feedbacks. Ablation embaralhada e comparação escalar permitem atribuir efeito ao feedback; contabilizar os três braços dentro do teto de 30 min.

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

Interface de aceitação **planejada, ainda não implementada para P63**:

```text
python3 benchmarks/science_matrix.py --acceptance-phase P63 --config experiments/p63-config.json --output /tmp/evobyte-p63-acceptance.json
```

A fase implementa somente sua capacidade, reutilizando módulos existentes.
Antes de medir, congelar configuração e run.sh com comando realmente testado.
`/tmp` é saída transitória; raw, pesos, checkpoint e manifesto precisam de
cópia durável recuperável com hashes. Não marcar Done por escrever este plano.

## Risco

Explorar uma falha do checker não conta como resolver a matemática; finalistas passam por verificação independente.

## Commit & Push (obrigatório)

Árvore limpa no início; branch da base aceita. Revisar diff e fazer stage
somente de caminhos explícitos. Escrever `/tmp/evobyte-p63-pr.md` com
problema, mudança, comandos, resultados, limites e referências recuperáveis.
Nenhum commit/push após gate vermelho. Um commit por microtarefa concluída;
implementação diagnóstica não marca confirmação científica Done.

```bash
git diff --cached --check
git commit -m "feat(research): implement p63 verifier-feedback"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p63 verifier-feedback" --body-file /tmp/evobyte-p63-pr.md
git status --short
```

Usar main como base apenas se o predecessor estiver integrado; senão usar
a branch aceita do predecessor e registrar a dependência. A entrega só de
medição/documentação usa `docs(research): record p63 experiment`.
Nunca push direto à main, force-push, bypass de hooks ou merge automático.
