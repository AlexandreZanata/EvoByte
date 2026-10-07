# P69 — H09 — Sincronizar ilhas por erros complementares

**Status:** Building (entregas 1–3: migração, busca + comparação,
interface + config congelada; entrega 4 pendente: medição em árvore limpa
+ registro. Diagnóstico: outcome NULL — todos certificam, diversidade
sem ganho não promove.)
**Dependência:** P68 Done porém não integrado (PR #96 aberto); branch a
partir de `codex/p68-adversarial-conjectures`, PR contra ela.
**Owner:** agente executor; revisor matemático/estatístico nos gates indicados.
**Pré-requisito:** P68 com entrega técnica aceita; módulos experimentais anteriores sem ganho permanecem desligados. Para P61–P70 exige também a bancada P60 aceita.
**Branch:** `codex/p69-residue-synchronized-islands`.

## Hipótese, objetivo e escopo

Trocar fragmentos segundo assinaturas de resíduos pode produzir mais certificados que migrar elites.

Alterações permitidas: src/evobyte/islands.py, benchmarks/open_problems.py e rastreamento existente.
Fora do escopo: outras hipóteses, reescrita de dados históricos, maior hardware,
novidade mundial presumida e alteração do checker para favorecer candidatos.

Ler [o contrato P58–P72](../FORMAL_SEARCH_PLAN.md#programa-especulativo-p58p72).
Uma microtarefa por ciclo; implementar, congelar e medir em entregas separadas
quando necessário, cada qual com gate próprio. Código novo não mede sua
confirmação final enquanto a revisão estiver suja.

## Trabalho ordenado

1. Usar quatro ilhas lógicas na mesma GPU, mantendo o total de população/VRAM constante. Um stream inicialmente; quatro ilhas não exigem quatro processos CUDA.

2. Congelar migração por assinaturas de resíduo/divisibilidade e comparar migração de elites, migração aleatória e nenhuma migração. Cada braço recebe os mesmos recursos e tempo total.

3. Registrar os dois pais de cada recombinação e rejeitar combinações fora do domínio. Medir diversidade útil, custo de sincronização e certificados por problema.

## Gate de saída

Ancestralidade completa e contadores corretos; comparação mantém população total constante. Mais diversidade sem ganho certificado não promove a hipótese.

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

Interface de aceitação **implementada na entrega 3** (`run_p69_island_audit`):

```text
python3 benchmarks/science_matrix.py --acceptance-phase P69 --config experiments/p69-config.json --output /tmp/evobyte-p69-acceptance.json
```

A fase implementa somente sua capacidade, reutilizando módulos existentes.
Antes de medir, congelar configuração e run.sh com comando realmente testado.
`/tmp` é saída transitória; raw, pesos, checkpoint e manifesto precisam de
cópia durável recuperável com hashes. Não marcar Done por escrever este plano.

## Risco

Mais ilhas podem fragmentar a busca e sincronização pode custar mais que o benefício.

## Commit & Push (obrigatório)

Árvore limpa no início; branch da base aceita. Revisar diff e fazer stage
somente de caminhos explícitos. Escrever `/tmp/evobyte-p69-pr.md` com
problema, mudança, comandos, resultados, limites e referências recuperáveis.
Nenhum commit/push após gate vermelho. Um commit por microtarefa concluída;
implementação diagnóstica não marca confirmação científica Done.

```bash
git diff --cached --check
git commit -m "feat(research): implement p69 residue-synchronized-islands"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p69 residue-synchronized-islands" --body-file /tmp/evobyte-p69-pr.md
git status --short
```

Usar main como base apenas se o predecessor estiver integrado; senão usar
a branch aceita do predecessor e registrar a dependência. A entrega só de
medição/documentação usa `docs(research): record p69 experiment`.
Nunca push direto à main, force-push, bypass de hooks ou merge automático.
