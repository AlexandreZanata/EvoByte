# P66 — H05 — Atravessar a busca com saltos compostos

**Status:** Done (entregas 1–4: pacotes, distribuição guiada, interface +
comando congelado, medição ACCEPTED em árvore limpa
`run_id=5bed77c91ce3f0b5` com outcome NULL íntegro; registro em
`docs/research/p66-jump-record.md`). H05 encerrada sem promoção; P67
liberada.
**Dependência:** P65 Done porém não integrado (PR #93 aberto); branch a
partir de `codex/p65-backward-constructions`, PR contra ela.
**Owner:** agente executor; revisor matemático/estatístico nos gates indicados.
**Pré-requisito:** P65 com entrega técnica aceita; módulos experimentais anteriores sem ganho permanecem desligados. Para P61–P70 exige também a bancada P60 aceita.
**Branch:** `codex/p66-composite-search-jumps`.

## Hipótese, objetivo e escopo

Pacotes de edições podem atingir regiões úteis que mutações locais visitam pouco.

Alterações permitidas: src/evobyte/grammar.py, src/evobyte/islands.py e benchmark de construções.
Fora do escopo: outras hipóteses, reescrita de dados históricos, maior hardware,
novidade mundial presumida e alteração do checker para favorecer candidatos.

Ler [o contrato P58–P72](../FORMAL_SEARCH_PLAN.md#programa-especulativo-p58p72).
Uma microtarefa por ciclo; implementar, congelar e medir em entregas separadas
quando necessário, cada qual com gate próprio. Código novo não mede sua
confirmação final enquanto a revisão estiver suja.

## Trabalho ordenado

1. Definir pacotes de 2–4 edições válidas e aprender no máximo uma distribuição de pacotes. Manter distribuição de comprimentos e mesmo total de operações como controle.

2. Em busca de construções, intermediários podem falhar na equação, mas devem permanecer objetos representáveis; em busca de provas, nenhuma inferência inválida entra como prova.

3. Comparar pacote guiado, pacote aleatório e edições isoladas com orçamento igual, registrando alcance, duplicação e certificados. Nenhuma alegação de tunelamento quântico físico.

## Gate de saída

Transformações versionadas e replayáveis, domínio intacto e custo de edição reconciliado. Amplitude do salto sem ganho certificado não sustenta a hipótese.

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

Interface de aceitação **implementada na entrega 3** (`run_p66_jump_audit`):

```text
python3 benchmarks/science_matrix.py --acceptance-phase P66 --config experiments/p66-config.json --output /tmp/evobyte-p66-acceptance.json
```

A fase implementa somente sua capacidade, reutilizando módulos existentes.
Antes de medir, congelar configuração e run.sh com comando realmente testado.
`/tmp` é saída transitória; raw, pesos, checkpoint e manifesto precisam de
cópia durável recuperável com hashes. Não marcar Done por escrever este plano.

## Risco

Um salto maior pode apenas gastar mais operações ou gerar mais objetos inválidos.

## Commit & Push (obrigatório)

Árvore limpa no início; branch da base aceita. Revisar diff e fazer stage
somente de caminhos explícitos. Escrever `/tmp/evobyte-p66-pr.md` com
problema, mudança, comandos, resultados, limites e referências recuperáveis.
Nenhum commit/push após gate vermelho. Um commit por microtarefa concluída;
implementação diagnóstica não marca confirmação científica Done.

```bash
git diff --cached --check
git commit -m "feat(research): implement p66 composite-search-jumps"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p66 composite-search-jumps" --body-file /tmp/evobyte-p66-pr.md
git status --short
```

Usar main como base apenas se o predecessor estiver integrado; senão usar
a branch aceita do predecessor e registrar a dependência. A entrega só de
medição/documentação usa `docs(research): record p66 experiment`.
Nunca push direto à main, force-push, bypass de hooks ou merge automático.
