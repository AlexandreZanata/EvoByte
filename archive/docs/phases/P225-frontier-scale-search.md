# P225 — Busca de fronteira em escala (n = 40–144) com limites superiores de distância

**Status:** Proposed (**condicional**).
**Programa:** Progresso Científico Verificável (P221–P228, D049).
**Dependência:** P223 assinada pelo humano **e** `docs/research/references/bb-known-parameters.json` fornecido pelo humano (ver "Condição de execução").
**Owner:** agente executor; o revisor (Claude) audita antes do merge.
**Branch:** `codex/p225-frontier-scale-search` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/research/p223-human-signoff.md`](../research/p223-human-signoff.md), [`docs/research/p224-ablation-report.md`](../research/p224-ablation-report.md), [`src/evobyte/bb_census.py`](../../src/evobyte/bb_census.py).

## Condição de execução (verifique primeiro; se falhar, marque a fase `Não aplicável: <motivo>` e PARE)

1. `docs/research/p223-human-signoff.md` está preenchido e assinado.
2. O humano criou `docs/research/references/bb-known-parameters.json`: lista de `{n, k, d_best_known, fonte}` para BB/two-block-group-algebra codes e para a tabela geral, **na faixa (n,k) que ele declarou "aberta"**. O agente **não** cria nem completa esse arquivo.
3. O veredito de P224 é `EVOBYTE_ADDS_VALUE` ou `NO_ADDED_VALUE` ou `NOT_TESTABLE`; ele define o método de busca usado aqui (abaixo): se `NO_ADDED_VALUE`/`NOT_TESTABLE`, use **o melhor baseline de P224** (M0/M1/M3), nunca "EvoByte".

## Por que esta fase existe

Instâncias pequenas estão saturadas; códigos BB com n entre ~40 e ~144 são um território ativo
onde enumeração + filtros baratos ainda podem apontar códigos com `k·d²/n` alto. Esta fase só
**gera candidatos com limite superior de distância**; ela não alega nada (certificar d é P226).

## Pergunta falsificável da fase

> Na faixa (n,k) declarada aberta pelo humano, quantos códigos BB de peso (3,3) têm `k>0` e
> limite superior de distância `d_ub ≥ d_best_known(n,k)`?  (Resposta pode ser "zero" — e isso é um resultado.)

## Escopo

**Criar:** `src/evobyte/bb_frontier.py`, `scripts/run_p225_frontier.py`, `tests/test_bb_frontier.py`, `experiments/p225-frontier-prereg.json`, `experiments/p225-frontier-results.json`, `docs/research/p225-frontier-report.md`.
**Proibido:** alegar novidade; chamar qualquer candidato de "recorde"; reduzir `d_best_known` do arquivo humano.

## Trabalho ordenado

1. Branch; pré-registro (commit isolado): lista de (ℓ,m) (ℓ≤m, 40 ≤ 2ℓm ≤ 144, dentro da faixa do humano), pesos (3,3), seed 42, orçamento total por (ℓ,m) = 20 min, N amostras máximas por (ℓ,m) = 3 000 000 (se o espaço `C(ℓm−1,2)·C(ℓm,3)` for menor, enumere tudo; senão amostre sem reposição com seed 42). Redução rigorosa: `(0,0) ∈ A` (mesma justificativa de P222).
2. Estágio 1 — **k exato** (posto GF(2) com `int` de 2ℓm bits), `multiprocessing.Pool(16)`. Descarte `k=0` e todo k que não esteja na faixa do humano.
3. Estágio 2 — **d_ub** por busca de palavra de baixo peso: primeiro `grep -n "osd\|OSD" src/evobyte/*.py`; se existir decodificador BP-OSD reutilizável, use-o; senão, descida gulosa com 5000 reinícios aleatórios: partindo de um elemento aleatório de `ker(H_Z)` fora de `rowspace(H_X)` (e simetricamente X↔Z), some linhas de `H_X` que reduzam o peso até não haver melhora. `d_ub = min(peso)` dos dois tipos. Todo `d_ub` vem com a testemunha (vetor) e é reconferido por teste de pertinência independente.
4. Filtro: manter só códigos com `d_ub ≥ d_best_known(n,k)` (arquivo humano). Rank por `k·d_ub²/n`. No máximo 10 por (n,k).
5. Para cada sobrevivente, grave `{l,m,A,B,n,k,d_ub,testemunha}`. **Nada de afirmar d**; apenas `d ≤ d_ub`.
6. Relatório: contagens por estágio (amostrados → k>0 → faixa → sobreviventes), tempos, throughput, e a tabela de sobreviventes. Se **zero** sobreviventes: diga isso como resultado (limite do espaço amostrado, **não** prova de inexistência quando houve amostragem).

## Regras de parada

- Arquivo humano ausente ou inconsistente ⇒ `Não aplicável`.
- Teste de calibração falha: Bravyi 2024 `[[72,12,·]]` (ℓ=m=6; A={(3,0),(0,1),(0,2)}, B={(0,3),(1,0),(2,0)}) deve dar k=12 no estágio 1 e `d_ub = 6` no estágio 2 (a distância verdadeira é 6; todo `d_ub` é ≥ à verdadeira, então `d_ub > 6` significa que o heurístico é fraco demais): se `d_ub > 6`, PARE e reporte (melhore o estágio 2 antes de seguir). Faça a mesma calibração com [[20,2,6]] (`d_ub = 6`).
- Memória > 24 GB ou tempo > 3 h total ⇒ PARE e reporte.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_bb_frontier.py -q
make lint
python3 -m pytest tests -q -m "not slow" | tail -2
git status --short
```

## Commit & Push (obrigatório; NÃO fazer merge)

```bash
git add src/evobyte/bb_frontier.py scripts/run_p225_frontier.py tests/test_bb_frontier.py \
  experiments/p225-frontier-prereg.json experiments/p225-frontier-results.json \
  docs/research/p225-frontier-report.md docs/phases/P225-frontier-scale-search.md
git commit -m "feat(frontier): scaled BB search with distance upper bounds (P225)"
git push -u origin codex/p225-frontier-scale-search
gh pr create --base main --title "feat(frontier): scaled BB search with distance upper bounds (P225)" \
  --body "Candidatos com d_ub; nenhuma alegação de novidade."
```
