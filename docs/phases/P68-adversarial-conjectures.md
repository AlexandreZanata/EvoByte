# P68 — H07 — Fazer dois modelos pequenos atacar construções

**Status:** Building (entrega 1 neste ciclo: jogo atacante + refutações
certificadas; atacante aprendido, congelamento e medição pendentes).
**Dependência:** P67 Done porém não integrado (PR #95 aberto); branch a
partir de `codex/p67-verified-macros`, PR contra ela.
**Owner:** agente executor; revisor matemático/estatístico nos gates indicados.
**Pré-requisito:** P67 com entrega técnica aceita; módulos experimentais anteriores sem ganho permanecem desligados. Para P61–P70 exige também a bancada P60 aceita.
**Branch:** `codex/p68-adversarial-conjectures`.

## Hipótese, objetivo e escopo

Um atacante de contraexemplos pode melhorar a seleção de templates candidatos.

Alterações permitidas: src/evobyte/generator.py, benchmarks/open_problems.py e fronteira formal.
Fora do escopo: outras hipóteses, reescrita de dados históricos, maior hardware,
novidade mundial presumida e alteração do checker para favorecer candidatos.

Ler [o contrato P58–P72](../FORMAL_SEARCH_PLAN.md#programa-especulativo-p58p72).
Uma microtarefa por ciclo; implementar, congelar e medir em entregas separadas
quando necessário, cada qual com gate próprio. Código novo não mede sua
confirmação final enquanto a revisão estiver suja.

## Trabalho ordenado

1. Usar um proponente e um atacante pequenos com teto combinado de 1 milhão de parâmetros. O proponente emite template/condições; o atacante escolhe instâncias dentro do domínio público para tentar refutá-lo. Refutar um template não equivale a refutar a conjectura de Erdős–Straus.

2. Comparar atacante aprendido, atacante aleatório e busca sistemática clássica com custo total igual. Toda refutação recebe certificado exato e alimenta apenas development.

3. Templates que sobrevivem continuam conjecturas. Somente prova formal de identidade, integridade/positividade e condições declaradas permite uso como família válida.

## Gate de saída

Contraexemplos exatos reproduzíveis e ausência de vazamento. Sobrevivência a testes não ganha rótulo de teorema; sem candidatos provados a conclusão pode ser INCONCLUSIVE.

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

Interface de aceitação **planejada, ainda não implementada para P68**:

```text
python3 benchmarks/science_matrix.py --acceptance-phase P68 --config experiments/p68-config.json --output /tmp/evobyte-p68-acceptance.json
```

A fase implementa somente sua capacidade, reutilizando módulos existentes.
Antes de medir, congelar configuração e run.sh com comando realmente testado.
`/tmp` é saída transitória; raw, pesos, checkpoint e manifesto precisam de
cópia durável recuperável com hashes. Não marcar Done por escrever este plano.

## Risco

Dois modelos podem compartilhar o mesmo ponto cego; o checker fixo continua obrigatório.

## Commit & Push (obrigatório)

Árvore limpa no início; branch da base aceita. Revisar diff e fazer stage
somente de caminhos explícitos. Escrever `/tmp/evobyte-p68-pr.md` com
problema, mudança, comandos, resultados, limites e referências recuperáveis.
Nenhum commit/push após gate vermelho. Um commit por microtarefa concluída;
implementação diagnóstica não marca confirmação científica Done.

```bash
git diff --cached --check
git commit -m "feat(research): implement p68 adversarial-conjectures"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p68 adversarial-conjectures" --body-file /tmp/evobyte-p68-pr.md
git status --short
```

Usar main como base apenas se o predecessor estiver integrado; senão usar
a branch aceita do predecessor e registrar a dependência. A entrega só de
medição/documentação usa `docs(research): record p68 experiment`.
Nunca push direto à main, force-push, bypass de hooks ou merge automático.
