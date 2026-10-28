# P222 — Censo exaustivo e exato de códigos bicíclicos bivariados pequenos

**Status:** Proposed.
**Programa:** Progresso Científico Verificável (P221–P228, D049).
**Dependência:** P221 concluída e integrada em `main`.
**Owner:** agente executor; o revisor (Claude) audita antes do merge.
**Branch:** `codex/p222-bb-code-exhaustive-census` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/research/p221-formal-honesty-report.md`](../research/p221-formal-honesty-report.md), [`tests/test_p221_independent_recompute.py`](../../tests/test_p221_independent_recompute.py).

## Por que esta fase existe

Até aqui só tínhamos instâncias soltas. Um **censo exaustivo com distância exata** dá (a) um
conjunto de verdade-terrestre (ground truth) para medir métodos de busca (P224) e (b) um
conjunto de dados verificável e completo que um terceiro pode conferir. Nenhuma alegação de
descoberta é feita aqui: a comparação com a literatura é a fase P223, com portão humano.

## Pergunta falsificável da fase

> Enumerando **todos** os pares (A, B) com |A|, |B| ∈ {3, 4}, A ∋ (0,0), sobre Z_ℓ × Z_m com
> 2 ≤ ℓ·m ≤ 16 (ℓ ≤ m), o censo calcula k exato e d exato (ou prova d > 7) para cada código com
> k > 0, reproduz [[16,2,4]] e [[20,2,6]] como o máximo d dos seus (n,k), e todo resultado
> listado passa por reverificação independente (stdlib)?

## Definições (congeladas — não altere)

- Grupo: Z_ℓ × Z_m com 2 ≤ ℓ·m ≤ 16 e ℓ ≤ m (ℓ ≥ 1 não é incluído). Qubits: n = 2ℓm.
- Códigos: H_X = (A | B), H_Z = (B* | A*) com `*` = x→x⁻¹, y→y⁻¹ (mesma convenção de P221).
- Redução de simetria **rigorosa**: multiplicar A e B por um mesmo monômio não muda o espaço de linhas; logo supõe-se (0,0) ∈ A. **Nenhuma outra redução** (não suponha (0,0) ∈ B).
- Espaço: A = {(0,0)} ∪ S com |S| ∈ {2, 3} escolhido entre os demais ℓm−1 pontos; B qualquer subconjunto de tamanho 3 ou 4 dos ℓm pontos.
- Para cada código: k = n − rank(H_X) − rank(H_Z). Se k = 0 descarte (registrar só a contagem).
- Para k > 0: d = menor peso de operador lógico, procurado por peso w = 1..7; se nenhum até 7, registrar `d_exact: null, d_gt: 7`.

## Código de referência (testado pelo revisor; copie e organize em `src/evobyte/bb_census.py`)

```python
import itertools, numpy as np

def reg_rows(l, m, P):
    L = l * m; rows = []
    for i in range(l):
        for j in range(m):
            v = 0
            for (a, b) in P:
                v ^= 1 << (L - 1 - (((i + a) % l) * m + ((j + b) % m)))
            rows.append(v)
    return rows

def checks(l, m, A, B):
    L = l * m
    star = lambda P: {((-a) % l, (-b) % m) for (a, b) in P}
    ra, rb = reg_rows(l, m, A), reg_rows(l, m, B)
    rsa, rsb = reg_rows(l, m, star(A)), reg_rows(l, m, star(B))
    hx = [(a << L) | b for a, b in zip(ra, rb)]
    hz = [(a << L) | b for a, b in zip(rsb, rsa)]   # (B* | A*)
    return hx, hz

def basis_of(rows):
    basis = []
    for v in rows:
        for b in basis: v = min(v, v ^ b)
        if v: basis.append(v)
    return basis

def in_span(v, basis):
    for b in basis: v = min(v, v ^ b)
    return v == 0

_MASKS = {}
def masks_of_weight(n, w):
    if (n, w) not in _MASKS:
        _MASKS[(n, w)] = np.fromiter(
            (sum(1 << (n - 1 - s) for s in S) for S in itertools.combinations(range(n), w)),
            dtype=np.uint64)
    return _MASKS[(n, w)]

def parity64(x):
    for s in (32, 16, 8, 4, 2, 1): x = x ^ (x >> np.uint64(s))
    return (x & np.uint64(1)).astype(bool)

def exact_distance(hx, hz, n, wmax):
    """returns (k, d) with d=None meaning d > wmax; k<=0 returns (k, None)"""
    bx, bz = basis_of(hx), basis_of(hz)
    k = n - len(bx) - len(bz)
    if k <= 0: return k, None
    for w in range(1, wmax + 1):
        M = masks_of_weight(n, w)
        for (chk, other) in ((hz, bx), (hx, bz)):
            ok = np.ones(len(M), dtype=bool)
            for h in chk: ok &= ~parity64(M & np.uint64(h))
            for e in M[ok]:
                if not in_span(int(e), other): return k, w
    return k, None
```
Medido pelo revisor: [[20,2,6]] ⇒ `(2, 6)`; [[16,2,4]] ⇒ `(2, 4)`; ℓ=5, m=2, todos os 39.600 pares ⇒ 20,5 s, contagens `{k=2: 12800, k=4: 4800, k=12: 40}`, d máximo `{2: 6, 4: 4, 12: 2}`.

## Escopo

**Criar:**
- `src/evobyte/bb_census.py` — funções acima + `enumerate_space(l, m)` + `run_census(max_lm, wmax=7, workers=...)`.
- `scripts/run_p222_census.py` — CLI que escreve `experiments/p222-bb-census.json` e `experiments/p222-bb-census-summary.json`.
- `tests/test_bb_census.py`.
- `docs/research/p222-census-report.md`.

**Editar:** `docs/phases/P222-bb-code-exhaustive-census.md` (status/evidências), `docs/phases/README.md` (apenas o item P222, se necessário).

**Proibido:** compartilhar estado entre processos além do resultado; descartar linhas inconvenientes; mudar `wmax`; usar `evobyte` fora deste módulo para o cálculo de distância (a verificação independente é feita na reverificação).

## Trabalho ordenado

1. **Branch e baseline:** `git status --short` vazio; `git switch -c codex/p222-bb-code-exhaustive-census`; `python3 -m pytest tests -q -m "not slow" | tail -2` (registre o baseline).
2. **Módulo + testes unitários** (`tests/test_bb_census.py`): (a) `[[20,2,6]]` ⇒ `(2,6)`; (b) `[[16,2,4]]` ⇒ `(2,4)`; (c) para ℓ=5, m=2 a enumeração tem exatamente 39.600 pares; (d) comutação `H_X H_Z^T = 0` em 200 pares aleatórios (seed 42); (e) Bravyi (ℓ=m=6, A={(3,0),(0,1),(0,2)}, B={(0,3),(1,0),(2,0)}): `k = 12` (só posto; sem distância).
3. **Execução com `multiprocessing.Pool(16)`**, particionando por (ℓ, m, A). Saída determinística (ordene as linhas por `(n, k, l, m, A, B)`). Linha JSON: `{"l","m","A","B","n","k","d_exact","d_gt"}`.
   - Ordem de execução: ℓm ≤ 10 → ≤ 12 → ≤ 14 → ≤ 16. Se ℓm = 16 passar de 40 min de parede ou 20 GB RAM: PARE a escalada, registre até onde foi (não corte pares dentro de um ℓm).
4. **Resumo:** tabela `best_d[(n,k)]` com contagem de códigos que atingem o máximo e um **exemplo** (primeiro por ordem canônica). Também a contagem de `k=0` e de `d_gt`.
5. **Reverificação independente:** para o exemplo de cada `(n,k)` com `d ≥ 4` (e todos com `d_gt`), reconfirme `k` e `d` com a função `distance` de `tests/test_p221_independent_recompute.py` (stdlib; sem `evobyte`). Qualquer discrepância ⇒ PARE.
6. **Calibração de saída:** o resumo deve conter `(n=16,k=2) → d=4` e `(n=20,k=2) → d=6` como máximos; se algum for maior, PARE e reporte (não é "descoberta": é sinal de bug, ou de erro de tabela anterior — o revisor decide).
7. **Relatório** `docs/research/p222-census-report.md`: o que foi enumerado, contagens, tabela `best_d`, tempos, hardware (`nproc`, RAM), commit, seed (não há aleatório: diga "determinístico"), hash SHA-256 de `experiments/p222-bb-census.json`. **Sem comparação com literatura e sem a palavra "recorde"/"descoberta"** (isso é P223).

## Regras de parada (PARE, não commite, reporte com saída bruta)

- Teste de calibração (a)–(e) falha.
- Reverificação independente discorda do censo em qualquer linha.
- Resultado não determinístico entre duas execuções de ℓm ≤ 10 (compare hashes).
- Estouro de 20 GB de RAM ou 40 min por ℓm.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_bb_census.py -q
python3 scripts/run_p222_census.py --max-lm 10 --out /tmp/a.json && python3 scripts/run_p222_census.py --max-lm 10 --out /tmp/b.json && cmp /tmp/a.json /tmp/b.json
python3 scripts/run_p222_census.py --max-lm 16   # (ou até onde couber, conforme a regra do passo 3)
make lint
python3 -m pytest tests -q -m "not slow" | tail -2
git status --short
```

## Commit & Push (obrigatório; NÃO fazer merge — o revisor aprova)

```bash
git add src/evobyte/bb_census.py scripts/run_p222_census.py tests/test_bb_census.py \
  experiments/p222-bb-census.json experiments/p222-bb-census-summary.json \
  docs/research/p222-census-report.md docs/phases/P222-bb-code-exhaustive-census.md
git commit -m "feat(census): exhaustive exact census of small bivariate bicycle codes (P222)"
git push -u origin codex/p222-bb-code-exhaustive-census
gh pr create --base main --title "feat(census): exhaustive exact census of small bivariate bicycle codes (P222)" \
  --body "Censo exato (k,d) com reverificação independente; sem alegação de novidade."
```
(Se `experiments/p222-bb-census.json` passar de 50 MB, grave em `.jsonl.gz` e commite só o resumo + SHA-256 do arquivo grande, documentando onde ele fica.)
