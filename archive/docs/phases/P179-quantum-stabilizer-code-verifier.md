# P179 — Verificador independente de códigos estabilizadores QECC [[n,k,d]]

**Status:** Completed.
**Programa:** Descoberta na Fronteira (P171–P190, D042). Trilhas A, B e fundação comum.
**Dependência:** nenhuma fase anterior exigida além de `main` (módulo autocontido, só stdlib+NumPy); branch a partir de `main`.
**Owner:** agente executor; revisor formal (álgebra simplética) nos gates de correção.
**Branch:** `codex/p179-quantum-stabilizer-code-verifier`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [regras do programa P171–P190](README.md#programa-de-descoberta-na-fronteira-p171p190-d042).

## Por que esta fase existe

A Trilha quântica persegue códigos quânticos corretores de erros [[n,k,d]] que superem as
tabelas de Grassl. Nenhuma alegação de distância `d` pode depender de biblioteca externa ou
de fé: esta fase entrega um verificador independente, em Python puro (+ NumPy), que computa
a **distância exata** via varredura do comutador simplético do centralizador de Pauli —
calibrado nos códigos de Steane [[7,1,3]] e Shor [[9,1,3]], com `d = 3` medido em milissegundos.

## Pergunta falsificável da fase

> O verificador computa exatamente `d = 3` para os geradores canônicos de Steane [[7,1,3]] e
> Shor [[9,1,3]], rejeita geradores que não comutam / são dependentes / têm fase inválida, e
> termina em menos de 0,5 s por verificação?

## Fatos de partida (padrão-ouro, verificáveis por construção)

Geradores canônicos (convenção: letra por qubit, `I/X/Y/Z`; fases `+1` implícitas):

| Código | Geradores estabilizadores |
|---|---|
| Steane [[7,1,3]] | X: `IIIXXXX`, `IXXIIXX`, `XIXIXIX`; Z: `IIIZZZZ`, `IZZIIZZ`, `ZIZIZIZ` (linhas da matriz de paridade do código de Hamming [7,4,3]) |
| Shor [[9,1,3]] | Z: `ZZIIIIIII`, `IZZIIIIII`, `IIIZZIIII`, `IIIIZZIII`, `IIIIIIZZI`, `IIIIIIIZZ`; X: `XXXXXXIII`, `IIIXXXXXX` (3 blocos de 3) |

O planejador executou o algoritmo abaixo nestes dois códigos em 2026-10-22: comutam, posto
6 e 8, `k = 1` nos dois casos, **distância 3** nos dois casos (0,08 s e 1,42 s por força
bruta; 0,001 s e 0,003 s com busca limitada por peso). O executor re-mede e qualquer
divergência é STOP.

Formalismo (o que o verificador implementa, sem biblioteca além de NumPy):
- Pauli como par binário `(x|z)`; produto simplético `<a,b> = a.x·b.z + a.z·b.x (mod 2)`.
- Estabilizador válido ⟺ geradores comutam dois a dois e são independentes (`posto = n-k`).
- Centralizador `C(S)` = {P : `<P,g> = 0` ∀ g}; `d` = menor peso em `C(S) \ S`
  (varredura por peso crescente 1, 2, … com poda por comutação parcial; para por no
  primeiro lógico encontrado).
- Limitação declarada no relatório: formalismo binário assume fases `+1` (padrão das
  tabelas de Grassl para códigos estabilizadores); gerador com fase não-`+1` é rejeitado
  com `(False, "phase not supported")`, nunca silenciosamente aceito.

## Escopo

**Arquivos que você pode criar:**
- `src/evobyte/qecc_verifier.py` (só biblioteca padrão + NumPy; zero dependências novas)
- `tests/test_qecc_verifier.py` (só lógica e calibração; suíte < 3 s)
- `docs/research/p179-qecc-verifier-report.md`

**Arquivos que você pode editar:**
- `docs/phases/P179-quantum-stabilizer-code-verifier.md`: só a linha de Status e o bloco final de execução.

**Proibido:**
- importar qualquer coisa além de stdlib + NumPy no verificador (teste AST como na P171);
- calcular distância por amostragem, heurística ou limite inferior não exato;
- testes que varram espaços grandes sem poda (cada teste < 0,2 s; a calibração Shor completa com poda leva ~0,003 s).

## Trabalho ordenado

### Passo 1 — Branch

```bash
git status --short
git switch main && git pull --ff-only 2>/dev/null || git switch main
git switch -c codex/p179-quantum-stabilizer-code-verifier
```

### Passo 2 — `src/evobyte/qecc_verifier.py`

Contrato obrigatório (toda função retorna `(ok: bool, payload)`; entrada malformada é
`(False, "motivo")`, nunca exceção):

| Função | Semântica exata | Rejeita obrigatoriamente |
|---|---|---|
| `parse_pauli(s, n)` | string → tupla `(x, z)` binária | caractere fora de `IXYZ`; comprimento ≠ n |
| `commutes(a, b)` | produto simplético `== 0` | — |
| `check_stabilizer(generators)` | comutam dois a dois; posto `== n-k` via eliminação GF(2); fases `+1` | não-comutação (com o par); dependência linear; fase não suportada |
| `centralizer_contains(pauli, generators)` | `<p, g> == 0` ∀ g | — |
| `stabilizer_contains(pauli, generators)` | pertence ao span GF(2) das linhas | — |
| `code_distance(generators)` | menor peso `w ∈ {1..n}` com lógico de peso `w` (varredura por peso com poda); `(True, {"n":, "k":, "d":})` ou `(False, motivo)` | gerador inválido; `k < 0`; sem lógico até `n` → `(False, "no logical operator found")` |

Implementação da varredura por peso (obrigatória para o orçamento de tempo): para
`w = 1, 2, …`: enumerar combinações de posições × atribuições `XYZ` (com poda: descarte
parcial que já falha comutação é opcional, não obrigatória para `n ≤ 9`); o primeiro lógico
define `d`; combinações em ordem lexicográfica com `random.Random` **desligado** (determinístico).

### Passo 3 — Testes `tests/test_qecc_verifier.py` (todos < 0,2 s; suíte < 3 s)

1. `test_steane_distance_3`: geradores da tabela acima → `(True, d=3, k=1)`; cada gerador
   tem 7 letras de `IXYZ`.
2. `test_shor_distance_3`: geradores da tabela acima → `(True, d=3, k=1)`.
3. `test_rejects_noncommuting`: `[XXXXIII, ZZZIIII, ...]` (X e Z no mesmo qubit sem par) → `(False, ...)` e `d` não é alegado.
4. `test_rejects_dependent_and_malformed`: gerador duplicado → posto cai → rejeita; caractere `W`, tamanho errado, lista vazia → `(False, ...)`.
5. `test_weight_bounded_finds_logical_fast`: mede `elapsed < 0.5 s` para os dois códigos de calibração (usa `time.perf_counter`; falha se estourar).
6. `test_module_is_stdlib_plus_numpy`: AST do módulo só importa stdlib + `numpy`.

### Passo 4 — Relatório `docs/research/p179-qecc-verifier-report.md`

Algoritmo (produto simplético, posto GF(2), varredura por peso), tempos medidos de Steane/Shor,
limitações (fases, escala exponencial contida pela poda — inadequado além de ~12 qubits sem
melhorias, declarado abertamente) e a consequência: a P180 pode catalogar, a P181 pode buscar.

## Regras de parada (PARE, não commite, reporte)

- `d != 3` para Steane ou Shor (ou o verificador os rejeitar).
- Qualquer teste > 0,2 s ou suíte > 3 s.
- Import fora de stdlib+NumPy detectado.
- Falha no pytest ou no `make verify`.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_qecc_verifier.py -q -m "not slow"   # FAST LOOP, ~1s
python3 -m pytest tests/test_qecc_verifier.py -q                 # FINAL GATE, < 3s
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add src/evobyte/qecc_verifier.py tests/test_qecc_verifier.py \
  docs/research/p179-qecc-verifier-report.md \
  docs/phases/P179-quantum-stabilizer-code-verifier.md
git diff --cached --check
git commit -m "feat(quantum): implement p179 qecc stabilizer verifier"
git push -u origin HEAD
gh pr create --base main \
  --title "feat(quantum): p179 qecc stabilizer verifier" \
  --body-file /tmp/evobyte-p179-pr.md
git status --short
```

O corpo do PR (`/tmp/evobyte-p179-pr.md`) traz: problema, comportamento resultante, comandos de
validação exatos, números medidos (d=3/d=3, tempos), limitações (fases, escala) e o link do relatório.
