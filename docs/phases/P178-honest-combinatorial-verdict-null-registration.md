# P178 — Veredito honesto das campanhas combinatórias e registro de nulos

**Status:** Proposed.
**Programa:** Descoberta na Fronteira (P171–P190, D042). Trilhas A, B e fundação comum.
**Dependência:** P176 e P177 concluídas **e mergeadas em `main`** (o executor precisa dos dois resumos commitados); branch a partir de `main`.
**Owner:** agente executor; revisor estatístico nos gates de veredito.
**Branch:** `codex/p178-honest-combinatorial-verdict-null-registration`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [regras do programa P171–P190](README.md#programa-de-descoberta-na-fronteira-p171p190-d042), [`docs/phases/P176-preregistered-covering-designs-campaign.md`](P176-preregistered-covering-designs-campaign.md), [`docs/phases/P177-weak-schur-symmetric-campaign.md`](P177-weak-schur-symmetric-campaign.md).

## Por que esta fase existe

Campanhas sem veredito estatístico formal viram anedota. Esta fase consolida os resultados
brutos das campanhas P176 (covering) e P177 (Schur fraco) com testes pareados
não-paramétricos (Wilcoxon) e controle FWER Holm-Bonferroni (α = 0,01), e registra o
veredito honesto: descoberta autêntica com certificado, ou `NULL_RESULT` formal por alvo —
sem p-hacking, sem redefinição pós-hoc de métricas.

## Pergunta falsificável da fase

> Após correção Holm-Bonferroni a α = 0,01, algum algoritmo supera outro de forma
> estatisticamente significativa nos pares alvo×tamanho×semente das campanhas P176/P177, e
> algum alvo produziu `DISCOVERY_BEATEN` certificado?

## Fatos de partida (todos lidos dos artefatos; re-verificar antes de concluir)

| Fato | Fonte |
|---|---|
| Trials brutos, orçamentos, sementes, vereditos por alvo | `experiments/p176-covering-results.json`, `experiments/p177-weak-schur-results.json` |
| Regra de veredito de cada campanha | Manifestos P176/P177 (ler os arquivos, não presumir) |
| Método estatístico padrão do programa | Wilcoxon pareado + Holm a 0.01 (P158/P169; `scipy.stats.wilcoxon`) |
| `scipy` instalado | Ambiente do repo (verificar com import) |

## Escopo

**Arquivos que você pode criar:**
- `src/evobyte/frontier_verdict.py` (Wilcoxon pareado + Holm + consolidação de vereditos)
- `tests/test_frontier_verdict.py` (só lógica estatística em fixtures; suíte < 3 s)
- `experiments/p178-frontier-verdict.json` (veredito consolidado)
- `docs/research/p178-frontier-verdict-report.md`

**Arquivos que você pode editar:**
- `docs/phases/P178-honest-combinatorial-verdict-null-registration.md`: só a linha de Status e o bloco final de execução.

**Proibido:**
- alterar dados de entrada dos JSONs para alcançar significância (p-hacking);
- relatar valores de p não corrigidos como se fossem significativos;
- testes que rodem campanhas, buscas ou Wilcoxon sobre os dados brutos completos se demorar > 0,2 s por teste (use subconjuntos fixos pequenos ou fixtures sintéticas).

## Trabalho ordenado

### Passo 1 — Branch e pré-condições

```bash
git status --short
git switch main && git pull --ff-only 2>/dev/null || git switch main
git switch -c codex/p178-honest-combinatorial-verdict-null-registration
test -f experiments/p176-covering-results.json || { echo "P176 NAO CONCLUIDA/MERGEADA"; exit 1; }
test -f experiments/p177-weak-schur-results.json || { echo "P177 NAO CONCLUIDA/MERGEADA"; exit 1; }
```

### Passo 2 — `src/evobyte/frontier_verdict.py`

```python
"""Consolidated statistical verdicts for frontier campaigns (P178)."""

def paired_wilcoxon_holm(scores_a, scores_b, comparison_name, family_size=1, alpha=0.01):
    """Wilcoxon pareado bilateral + correção Bonferroni-Holm de passo único
    (conservadora; documentar). Retorna dict com W, p_raw, p_holm, direção e veredito
    (SUPPORTED_* se p_holm <= alpha, senão NOT_SUPPORTED_NULL; tudo igual -> INCONCLUSIVE_IDENTICAL).
    Amostras de tamanhos diferentes levantam ValueError."""

def consolidate_frontier_verdicts(p176_path, p177_path, output_path, alpha=0.01):
    """Lê os dois resumos, executa baterias pareadas por (alvo, tamanho) com sementes
    emparelhadas SA-vs-HillClimbing (e vs Random onde houver), mais um teste agrupado,
    e grava o veredito: status, family_alpha, hipóteses, mathematical_record_discovery
    (CONFIRMED se algum DISCOVERY_BEATEN, senão NULL_RESULT), targets_summary."""
```

Regras: pareamento estrito por alvo, tamanho e semente (mesmo orçamento); direção pela média
das diferenças; `family_size` = número de comparações do subconjunto; o agrupado usa
`family_size = 1` e é rotulado como exploratório no relatório.

### Passo 3 — Testes `tests/test_frontier_verdict.py` (todos < 0,2 s; suíte < 3 s)

1. `test_wilcoxon_identical_samples`: amostras iguais → `p_raw == 1.0`, `no_difference`, `INCONCLUSIVE_IDENTICAL`.
2. `test_wilcoxon_separated_samples`: 25 pares com diferença constante → `p_holm <= 0.01`, `is_significant`.
3. `test_sample_size_mismatch_raises`: tamanhos desiguais → `ValueError`.
4. `test_consolidate_empty_graceful`: JSONs mínimos vazios → `status` avaliado, sem hipóteses, `NULL_RESULT`.
5. `test_consolidate_on_p176_p177`: roda sobre os resumos reais; para cada hipótese, se `p_holm > 0.01` então `NOT_SUPPORTED_NULL` (nunca o contrário); o artefato existe e é JSON válido.
6. `test_no_unadjusted_significance_claim`: o relatório final não contém nenhuma afirmação de significância sem `p_holm` (checagem textual simples das frases de veredito do relatório).

### Passo 4 — Relatório `docs/research/p178-frontier-verdict-report.md`

Obrigatório:
- tabela completa de comparações pareadas (`N`, `W`, `p_raw`, `p_Holm`, direção, veredito);
- as duas frases literais de veredito:
  - "A hipótese de superioridade estrita de busca evolutiva em bytecode é [SUPPORTED / REJECTED]."
  - "A hipótese de descoberta de novos recordes matemáticos é [CONFIRMED / NULL RESULT]."
  (preencher conforme medido; sem bytecode nas campanhas P176/P177, a primeira frase só pode
  ser REJECTED/NOT SUPPORTED por ausência de evidência — declarar isso explicitamente);
- cadeia de custódia (hashes dos resumos de entrada e do artefato de saída).

## Regras de parada (PARE, não commite, reporte)

- Declarar vitória estatística quando $p_{\text{Holm}} > 0.01$.
- Qualquer teste > 0,2 s ou suíte > 3 s; qualquer campanha dentro de `tests/`.
- Falha no pytest ou no `make verify`.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_frontier_verdict.py -q -m "not slow"   # FAST LOOP, ~1s
python3 -m pytest tests/test_frontier_verdict.py -q                 # FINAL GATE, < 3s
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add src/evobyte/frontier_verdict.py tests/test_frontier_verdict.py \
  experiments/p178-frontier-verdict.json docs/research/p178-frontier-verdict-report.md \
  docs/phases/P178-honest-combinatorial-verdict-null-registration.md
git diff --cached --check
git commit -m "feat(statistical): implement p178 honest frontier verdict and null registration"
git push -u origin HEAD
gh pr create --base main \
  --title "feat(statistical): p178 honest verdict" \
  --body-file /tmp/evobyte-p178-pr.md
git status --short
```

O corpo do PR (`/tmp/evobyte-p178-pr.md`) traz: problema, comportamento resultante, comandos de
validação exatos, números medidos (hipóteses, vereditos literais), limitações e o link do relatório.
