# P221 — Honestidade formal: recálculo independente e Lean sobre os objetos reais

**Status:** Done.
**Programa:** Progresso Científico Verificável (P221–P228, D049).
**Dependência:** P220 concluída e integrada em `main` (inclui `docs/research/claims-ledger-d047.md` e D048).
**Owner:** agente executor; o revisor (Claude) audita antes do merge.
**Branch:** `codex/p221-formal-honesty-independent-recompute` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/research/claims-ledger-d047.md`](../research/claims-ledger-d047.md), [`lean_proofs/Generated/BivariateDiscovery.lean`](../../lean_proofs/Generated/BivariateDiscovery.lean), [`scripts/verify_lean_p218.sh`](../../scripts/verify_lean_p218.sh).

## Por que esta fase existe

Auditoria independente (2026-10-28) mediu que os teoremas Lean de P218 não provam o que o
manuscrito diz: `bivariate_bicycle_parity_invariant` prova só `2*(lm-r) ≠ 3` (aritmética em ℕ),
e `pgl2_13_orbit_obstruction`/`agl2_4_orbit_obstruction` rodam `decide` sobre listas de
tamanhos de órbita **escritas à mão**. Esta fase troca esses enunciados por provas sobre os
objetos reais, ou rebaixa o rótulo honestamente, e acrescenta recálculo independente em Python.

## Pergunta falsificável da fase

> O kernel do Lean, sem axiomas além de `propext`/`Classical.choice`/`Quot.sound`, prova
> posto(HX)=posto(HZ)=9, k=2 e **ausência de operador lógico de peso ≤ 5** para o código
> [[20,2,6]] real; e um script Python que NÃO importa `evobyte` reproduz posto, k e d dos
> dois códigos e as órbitas dos dois grupos?

## Fatos de partida (já medidos pelo revisor; confirme, não presuma)

| Fato | Valor medido |
|---|---|
| [[20,2,6]]: ℓ=5, m=2, A=(0,0),(0,1),(1,1),(2,1), B=(0,1),(1,1),(2,0),(2,1) (pares expoente de x,y) | postos 9 e 9, k=2, d=6 |
| [[16,2,4]]: ℓ=2, m=4, A=(0,0),(0,2),(1,0),(1,3), B=(0,1),(1,0),(1,2),(1,3) | postos 7 e 7, k=2, d=4 |
| Órbitas de AGL(2,4) (ordem 2880) em 7-subconjuntos de 16 pontos | 10 órbitas: 160, 240, 480, 960, 960, 1440, 1440, 1440, 1440, 2880 |
| Órbitas de AΓL(2,4) (ordem 5760, com Frobenius) | 9 órbitas: 160, 240, 480, 960, 960, 1440, 1440, 2880, 2880 |
| Órbitas de PGL(2,13) em 6-subconjuntos de 14 pontos | {91, 182, 546, 1092, 1092} (soma 3003) |
| Protótipo Lean: `decide` do posto roda em < 5 s; `decide +kernel` de "nenhum lógico de peso ≤ 5" roda em ≈ 100 s | axiomas `[propext]` |

## Escopo

**Criar:**
- `tests/test_p221_independent_recompute.py` — usa só `itertools`/stdlib; **proibido** `import evobyte`.
- `tests/test_p221_orbit_recompute.py` — idem, orbitas por BFS com geradores implementados do zero.
- `scripts/gen_p221_lean.py` — gera o bloco Lean (linhas das matrizes) a partir de A,B,ℓ,m.
- `lean_proofs/Generated/BivariateReal.lean` — novo módulo (NÃO sobrescreva `BivariateDiscovery.lean`).
- `docs/research/p221-formal-honesty-report.md`.

**Editar:**
- `lean_proofs/Generated/BivariateDiscovery.lean` e `formal/lean/EvoByte/BivariateDiscovery.lean`: acrescentar docstring `-- SCOPE: arithmetic-only` ao `parity_invariant` e `-- SCOPE: data-lemma (orbit sizes hand-written; see BivariateReal)` aos dois `*_orbit_obstruction`. Não renomeie nada (outros arquivos referenciam os nomes: rode `grep -rn "parity_invariant\|orbit_obstruction" .` antes).
- `lean_proofs/Generated.lean`: acrescentar `import Generated.BivariateReal` se o arquivo importar os demais módulos.
- `docs/DECISIONS.md`: **acrescentar** a linha D049 (texto abaixo).
- `docs/phases/P221-formal-honesty-independent-recompute.md`: Status e evidências.

**Proibido:** alterar decisões passadas; usar `sorry`, `axiom`, `native_decide` (introduz `Lean.ofReduceBool`); mudar thresholds de teste.

## Trabalho ordenado (um micro-passo por commit lógico; confirme a saída esperada antes de seguir)

### Passo 1 — Branch e D049

```bash
git status --short            # deve ser vazio
git switch main && git switch -c codex/p221-formal-honesty-independent-recompute
grep -c "D049" docs/DECISIONS.md   # esperado: 0
```
Acrescente ao final da tabela de `docs/DECISIONS.md` (formato das linhas existentes; data = data real de hoje):
`| <AAAA-MM-DD> | D049 | Plano P221–P228: progresso científico verificável (honestidade formal, censo certificado de códigos BB, auditoria de novidade com portão humano, ablação do método, escala, certificação exata, mineração de conjecturas, submissão) | D048 concluiu RESULTADO NULO HONESTO: nenhuma descoberta; auditoria mediu teoremas Lean de escopo limitado e alvos de tabela saturados | P221 corrige formalização; P222–P224 medem o que o método realmente agrega; P225–P227 só executam se os portões humanos de P223/P224 permitirem; P228 conclui sem prometer descoberta |`

### Passo 2 — Recálculo independente dos códigos (Python puro)

Em `tests/test_p221_independent_recompute.py`, implemente (sem importar `evobyte`):

```python
import itertools

def build(l, m, A, B):
    n = l * m
    idx = lambda i, j: (i % l) * m + (j % m)
    def mat(P, T=False):
        M = [[0] * n for _ in range(n)]
        for (a, b) in P:
            for i in range(l):
                for j in range(m):
                    r, c = idx(i, j), idx(i + a, j + b)
                    if T: M[c][r] ^= 1
                    else: M[r][c] ^= 1
        return M
    Am, Bm, AT, BT = mat(A), mat(B), mat(A, True), mat(B, True)
    HX = [Am[i] + Bm[i] for i in range(n)]
    HZ = [BT[i] + AT[i] for i in range(n)]
    return HX, HZ

def bits(rows): return [int("".join(map(str, r)), 2) for r in rows]
def par(x): return bin(x).count("1") & 1

def basis_of(vs):
    basis = []
    for v in vs:
        for b in basis: v = min(v, v ^ b)
        if v: basis.append(v)
    return basis

def in_span(v, basis):
    for b in basis: v = min(v, v ^ b)
    return v == 0

def distance(HX, HZ, n):
    hx, hz = bits(HX), bits(HZ)
    bx, bz = basis_of(hx), basis_of(hz)
    assert all(par(a & b) == 0 for a in hx for b in hz)
    for w in range(1, n + 1):
        for S in itertools.combinations(range(n), w):
            e = sum(1 << (n - 1 - s) for s in S)
            if all(par(e & h) == 0 for h in hz) and not in_span(e, bx): return len(bx), len(bz), w
            if all(par(e & h) == 0 for h in hx) and not in_span(e, bz): return len(bx), len(bz), w
```
Atenção: `build` usa `n = l*m` por bloco; o número de qubits é `2*l*m`, e é esse valor que se passa a `distance(HX, HZ, n)` (20 para o primeiro código, 16 para o segundo).
Testes: `[[20,2,6]]` ⇒ `(9, 9, 6)`; `[[16,2,4]]` ⇒ `(7, 7, 4)`; em ambos `k = n - rx - rz == 2`.
Gate do passo: `python3 -m pytest tests/test_p221_independent_recompute.py -q` verde. Se o resultado diferir: **PARE** e reporte a saída bruta.

### Passo 3 — Recálculo independente das órbitas

Em `tests/test_p221_orbit_recompute.py`, sem `evobyte`:
- PGL(2,13) em P¹(F13)={0..12,∞=13}: geradores `z→z+1`, `z→2z` (2 é não-resíduo quadrático mod 13), `z→-1/z` (∞↔0). Órbitas dos 3003 6-subconjuntos por união de classes via BFS com os 3 geradores. Esperado: tamanhos ordenados `[91, 182, 546, 1092, 1092]`.
- AGL(2,4): implemente GF(4) (elementos 0,1,2,3 com adição = XOR; multiplicação por tabela de `x²=x+1`; `2·2=3, 2·3=1, 3·3=2`). Geradores: translações `(1,0)`, `(0,1)`, `(2,0)`, `(0,2)` e matrizes `[[1,1],[0,1]]`, `[[0,1],[1,0]]`, `[[2,0],[0,1]]`. Órbitas dos 11440 7-subconjuntos. Esperado: `[160, 240, 480, 960, 960, 1440, 1440, 1440, 1440, 2880]`.
- Se o seu gerador de grupo produzir um conjunto de tamanhos diferente, **PARE** (provável erro de gerador); não ajuste o "esperado".
- Assertar também `min(órbitas) > 25` e `> 24` respectivamente.

### Passo 4 — Lean real: `BivariateReal.lean`

Gere com `scripts/gen_p221_lean.py` as listas `hx`, `hz` (Nat, bit mais significativo = coluna 0, como em `bits()` acima) para os dois códigos. Estrutura **testada pelo revisor** (`Nat` bitmask; `decide` para posto e comutação; `decide +kernel` para o lema de distância):

```lean
namespace EvoByte.BivariateReal

def hx20 : List Nat := [ ... ]   -- gerado
def hz20 : List Nat := [ ... ]   -- gerado

def insertVec (basis : List Nat) (v : Nat) : List Nat :=
  let w := basis.foldl (fun v b => min v (v ^^^ b)) v
  if w = 0 then basis else basis ++ [w]
def gf2Rank (rows : List Nat) : Nat := (rows.foldl insertVec []).length

def pc (x : Nat) : Nat := (List.range 20).foldl (fun a i => a + (x >>> i) % 2) 0
def par (x : Nat) : Nat := pc x % 2
def inSpan (basis : List Nat) (v : Nat) : Bool :=
  (basis.foldl (fun v b => min v (v ^^^ b)) v) == 0
def bx20 : List Nat := hx20.foldl insertVec []
def bz20 : List Nat := hz20.foldl insertVec []

/-- e é erro lógico: X-type (comuta com HZ, fora de rowspace HX) ou Z-type (simétrico). -/
def isLogical20 (e : Nat) : Bool :=
  (hz20.all (fun h => par (e &&& h) == 0) && !(inSpan bx20 e)) ||
  (hx20.all (fun h => par (e &&& h) == 0) && !(inSpan bz20 e))

def ofWeight : Nat → Nat → List Nat
  | _, 0 => [0]
  | 0, _+1 => []
  | n+1, w+1 => ofWeight n (w+1) ++ (ofWeight n w).map (· ||| (1 <<< n))
def lowMasks20 : List Nat :=
  (List.range 6).foldl (fun acc w => acc ++ (if w = 0 then [] else ofWeight 20 w)) []

-- SCOPE: kernel-checked property of the concrete [[20,2]] matrices
theorem rank_hx20 : gf2Rank hx20 = 9 := by decide
theorem rank_hz20 : gf2Rank hz20 = 9 := by decide
theorem commute20 : hx20.all (fun a => hz20.all (fun b => par (a &&& b) == 0)) = true := by decide
set_option maxRecDepth 100000 in
theorem lowmasks20_count : lowMasks20.length = 21699 := by decide +kernel
set_option maxRecDepth 100000 in
theorem no_logical_weight_le5_20 : lowMasks20.all (fun e => !isLogical20 e) = true := by decide +kernel
-- teste de sanidade: o ofWeight cobre peso 6 e existe lógico de peso 6 (d ≤ 6)
-- gere `wit20` em Python (máscara do lógico de peso 6 encontrado no Passo 2) e prove:
-- theorem logical_weight6_20 : isLogical20 wit20 = true ∧ pc wit20 = 6 := by decide

#print axioms rank_hx20
#print axioms no_logical_weight_le5_20
end EvoByte.BivariateReal
```
Repita para [[16,2,4]] (n=16: `List.range 16`, `ofWeight 16`, pesos 1..3; contagem `16+120+560=696`; e testemunha de peso 4) em um segundo bloco `...16`.
Notas: (a) `decide` simples estoura recursão no lema de distância — use `decide +kernel` com `maxRecDepth`; (b) `decide +kernel` do [[20,2]] leva ~100 s; rode em background se necessário; (c) o enunciado completo "d = 6" combina `no_logical_weight_le5_20` (d ≥ 6) com `logical_weight6_20` (d ≤ 6) e `rank_*` (k=2). Documente isso em docstring.

Gate do passo: `cd lean_proofs && lake build Generated.BivariateReal` sai com código 0; `grep -nw sorry lean_proofs/Generated/BivariateReal.lean` vazio; `#print axioms` mostra só `propext`/`Classical.choice`/`Quot.sound` (nunca `Lean.ofReduceBool`).
Se o tempo de `decide +kernel` do [[20,2]] passar de 20 minutos: **PARE** e reporte o tempo (não troque por `native_decide`).

### Passo 5 — Gate de axiomas e script

Copie `scripts/verify_lean_p218.sh` para `scripts/verify_lean_p221.sh` trocando o módulo para `Generated.BivariateReal` e o arquivo; rode-o.

### Passo 6 — Relatório honesto

`docs/research/p221-formal-honesty-report.md` com: (1) tabela "o que o Lean agora prova / o que continua só computacional (SAT)" — posto, k, comutação, d≥6 e d≤6 do [[20,2,6]] e do [[16,2,4]] provados no kernel; invariante de paridade geral e obstruções de órbita **não** provadas no Lean (apenas recomputadas em Python); (2) tempos medidos; (3) tamanhos de órbita de AGL(2,4) vs AΓL(2,4) medidos; (4) declaração: "nenhuma alegação nova de descoberta". Cole números **somente** da saída real dos comandos.

## Evidências e Resultados Medidos

- **Recálculo independente Python:** `tests/test_p221_independent_recompute.py` verde em 0.24 s. [[20,2,6]] com postos 9/9, k=2, d=6; [[16,2,4]] com postos 7/7, k=2, d=4.
- **Recálculo independente de órbitas:** `tests/test_p221_orbit_recompute.py` verde em 0.40 s. PGL(2,13) com 5 órbitas [91, 182, 546, 1092, 1092]; AGL(2,4) com 10 órbitas [160, 240, 480, 960, 960, 1440, 1440, 1440, 1440, 2880]. Mínimos > 25 e > 24 confirmados.
- **Módulo Lean real:** `lean_proofs/Generated/BivariateReal.lean` compilado via `lake build` em 138 s com 0 sorry e axiomas estritamente `[propext]`. Prova posto, k, comutação simplética, inexistência de erro de baixo peso (`decide +kernel`) e existência de testemunha de peso exato.
- **Scripts de verificação:** `scripts/verify_lean_p221.sh` e `scripts/verify_lean_p218.sh` passam 100% verde com axiomas válidos.
- **Decisão D049:** Registrada em `docs/DECISIONS.md`.
- **Relatório de Honestidade:** `docs/research/p221-formal-honesty-report.md` com delimitações exatas e declaração de ausência de nova descoberta.

## Regras de parada (PARE, não commite, reporte com a saída bruta)

- Qualquer valor medido diferente da tabela de fatos de partida.
- Qualquer `sorry`, `axiom`, `native_decide`, `Lean.ofReduceBool`.
- `lake build` falhando após 2 tentativas de correção sintática.
- Necessidade de renomear teoremas existentes ou enfraquecer um teste.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_p221_independent_recompute.py tests/test_p221_orbit_recompute.py tests/test_lean_p218.py -q
bash scripts/verify_lean_p221.sh
bash scripts/verify_lean_p218.sh
make lint
python3 -m pytest tests -q -m "not slow" 2>&1 | tail -2
git status --short
```

## Commit & Push (obrigatório; NÃO fazer merge — o revisor aprova)

```bash
git add tests/test_p221_independent_recompute.py tests/test_p221_orbit_recompute.py \
  scripts/gen_p221_lean.py scripts/verify_lean_p221.sh \
  lean_proofs/Generated/BivariateReal.lean lean_proofs/Generated.lean \
  lean_proofs/Generated/BivariateDiscovery.lean formal/lean/EvoByte/BivariateDiscovery.lean \
  docs/research/p221-formal-honesty-report.md docs/DECISIONS.md \
  docs/phases/P221-formal-honesty-independent-recompute.md
git commit -m "feat(formal): kernel-checked rank and distance for real bivariate codes (P221)"
git push -u origin codex/p221-formal-honesty-independent-recompute
gh pr create --base main --title "feat(formal): kernel-checked rank and distance for real bivariate codes (P221)" \
  --body "Troca lemas vazios por provas sobre as matrizes reais; recálculo independente; registra D049."
```
