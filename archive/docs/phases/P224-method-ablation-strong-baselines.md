# P224 — Ablação do método contra baselines fortes (com verdade-terrestre do censo)

**Status:** Proposed.
**Programa:** Progresso Científico Verificável (P221–P228, D049).
**Dependência:** P222 concluída e integrada em `main` (P223 pode estar pendente de assinatura; esta fase não depende dela).
**Owner:** agente executor; o revisor (Claude) audita antes do merge.
**Branch:** `codex/p224-method-ablation-strong-baselines` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/HYPOTHESIS.md`](../HYPOTHESIS.md), [`docs/research/p222-census-report.md`](../research/p222-census-report.md), [`src/evobyte/bivariate_campaign.py`](../../src/evobyte/bivariate_campaign.py).

## Por que esta fase existe

H1 e H2 já terminaram NOT SUPPORTED/nulas, e o único avanço real do programa D047 veio da
**escolha da estrutura algébrica** (Z_ℓ×Z_m), não da busca evolutiva. Falta medir isso de forma
limpa: com o censo P222 sabemos a resposta exata, então dá para medir quanto cada método
realmente acrescenta num problema onde a verdade-terrestre é conhecida.

## Pergunta falsificável da fase

> Em alvos (ℓ, m, k\*, d\*) com solução conhecida pelo censo, a busca do EvoByte alcança uma
> taxa de sucesso maior que a do melhor baseline simples, sob o mesmo orçamento de parede,
> com Fisher exato unilateral p < 0,05 após Holm sobre os 3 alvos?

## Pré-registro (congelar ANTES de rodar — passo 2 faz commit separado)

- **Alvos (3):** escolha, a partir de `experiments/p222-bb-census.json`, os 3 pares `(ℓ, m, k\*, d\*)` com `d\*` = d máximo daquele (n,k), **fração de soluções** `f = (#códigos com k=k\* e d≥d\*) / (#pares do espaço)` e `1e-4 ≤ f ≤ 1e-2`, e n ≥ 20. Regra de desempate: menor `f`, depois menor n. Se houver menos de 3 alvos que satisfaçam, use os que houver e registre.
- **Métodos (mesmo espaço de busca, mesma função de avaliação, mesmo orçamento):**
  - `M0 random`: amostragem uniforme sem reposição de (A,B).
  - `M1 anneal`: recozimento simulado sobre (A,B): vizinhança = trocar um ponto de A ou B por outro ponto livre; energia = `(k != k*) * 10 + max(0, d* - d_cap)` onde `d_cap` é o d exato até `wmax = d*`; T0 = 3, resfriamento geométrico 0,999 por passo, reinício a cada 2000 passos sem melhora.
  - `M2 evobyte`: a busca **efetivamente usada** por `bivariate_campaign.py` para BB. **Antes de rodar**, leia `evaluate_qecc_20_2_bivariate` e escreva no relatório, em uma frase, o que ela faz (enumeração? amostragem? evolução?). Se for enumeração/amostragem, `M2 := M0` e o veredito sobre "evolução" é `NOT_TESTABLE` (não reimplemente e chame de EvoByte).
  - `M3 genetic`: (μ+λ)=(20+20), cruzamento = trocar B entre pais, mutação = M1; torneio de tamanho 3. Rotule "GA genérico", **não** "EvoByte".
- **Orçamento:** 10 s de parede por execução, 1 processo por execução, 20 sementes (42..61) por (alvo, método). Total ≤ 3×4×20 = 240 execuções ≈ 40 min (rode 8 em paralelo).
- **Métrica primária:** sucesso = achou (A,B) com `k = k*` e `d ≥ d*`, verificado por `exact_distance` de `src/evobyte/bb_census.py` **e** reconferido pela função stdlib de P221. Secundária: tempo até o acerto.
- **Estatística:** para cada alvo, Fisher exato unilateral (implemente com `math.comb`, hipergeométrica; sem scipy) de `M2` contra o **melhor** entre M0, M1, M3 (melhor = maior taxa de sucesso observada, empate = menor tempo mediano). Holm com α=0,05 sobre os 3 alvos.
- **Veredito (único, mecânico):**
  - `EVOBYTE_ADDS_VALUE`: M2 ≠ M0 (método realmente evolutivo) **e** os 3 testes rejeitam após Holm **e** a diferença de taxa de sucesso ≥ 20 pontos percentuais em todos.
  - `NO_ADDED_VALUE`: caso contrário e M2 ≠ M0.
  - `NOT_TESTABLE`: M2 = M0.
  - Em qualquer caso, informe qual baseline foi o melhor em cada alvo.

## Escopo

**Criar:** `src/evobyte/bb_search_methods.py` (M0, M1, M3 e o adaptador de M2), `scripts/run_p224_ablation.py`, `experiments/p224-prereg.json` (alvos, parâmetros, seeds, `git rev-parse HEAD` do commit de pré-registro), `experiments/p224-results.json`, `tests/test_bb_search_methods.py`, `docs/research/p224-ablation-report.md`.
**Editar:** `docs/phases/P224-method-ablation-strong-baselines.md`.
**Proibido:** alterar o pré-registro depois da execução; descartar sementes; trocar o orçamento; usar o censo dentro de qualquer método (só para escolher alvos e conferir).

## Trabalho ordenado

1. Branch; `git status --short` vazio.
2. Escolha os alvos pela regra acima, escreva `experiments/p224-prereg.json` e **commite sozinho** (`docs(prereg): freeze P224 ablation targets and protocol`). Registre o hash do commit no JSON de resultados.
3. Implemente os métodos; testes: (a) cada método respeita o orçamento (±0,5 s); (b) seed determinística ⇒ mesma sequência de candidatos nas primeiras 100 avaliações; (c) cada método nunca avalia o mesmo (A,B) duas vezes na mesma execução (M0) ou, para M1/M3, mantém A ∋ (0,0) e |A|,|B| válidos.
4. Execute o protocolo completo. Registre hardware (`nproc`, GPU não é usada), versões, commit, seeds.
5. Calcule o veredito **somente** com o script (não escreva à mão).
6. Relatório: tabela alvo×método (sucessos/20, tempo mediano), p-valores brutos e ajustados, o veredito, a frase sobre o que `M2` realmente é, e a declaração "esta ablação vale para este espaço de busca pequeno; não generaliza".

## Regras de parada

- Pré-registro alterado após ver resultados ⇒ PARE e reporte.
- Menos de 20 sementes completas por célula ⇒ PARE.
- Qualquer sucesso não reconfirmado pela verificação independente ⇒ PARE.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_bb_search_methods.py -q
python3 scripts/run_p224_ablation.py --verify-only   # reconfere todos os sucessos registrados
make lint
python3 -m pytest tests -q -m "not slow" | tail -2
git status --short
```

## Commit & Push (obrigatório; NÃO fazer merge)

```bash
git add src/evobyte/bb_search_methods.py scripts/run_p224_ablation.py \
  experiments/p224-prereg.json experiments/p224-results.json \
  tests/test_bb_search_methods.py docs/research/p224-ablation-report.md \
  docs/phases/P224-method-ablation-strong-baselines.md
git commit -m "feat(ablation): preregistered strong-baseline ablation on census ground truth (P224)"
git push -u origin codex/p224-method-ablation-strong-baselines
gh pr create --base main --title "feat(ablation): preregistered strong-baseline ablation on census ground truth (P224)" \
  --body "Mede o valor agregado do método contra baselines simples com verdade-terrestre."
```
