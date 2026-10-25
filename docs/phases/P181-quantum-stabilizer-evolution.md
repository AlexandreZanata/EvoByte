# P181 — Evolução de estabilizadores com Q-Forge para superar cotas de Grassl

**Status:** Completed.
**Programa:** Descoberta na Fronteira (P171–P190, D042). Trilhas A, B e fundação comum.
**Dependência:** P179 (verificador) e P180 (catálogo QECC) concluídas; branch a partir de `codex/p180-grassl-bounds-frontier-catalogue`.
**Owner:** agente executor; revisor formal (álgebra simplética) nos gates de correção.
**Branch:** `codex/p181-quantum-stabilizer-evolution`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [regras do programa P171–P190](README.md#programa-de-descoberta-na-fronteira-p171p190-d042), [`docs/phases/P179-quantum-stabilizer-code-verifier.md`](P179-quantum-stabilizer-code-verifier.md), `src/evobyte/quantum/{pauli,evolution_q,circuit}.py` (ler as APIs reais antes de codar).

## Por que esta fase existe

Com verificador exato (P179) e catálogo de gaps abertos (P180), falta o motor de busca que
proponha conjuntos estabilizadores candidatos: evolução sobre matrizes simpléticas binárias
e circuitos estabilizadores, reaproveitando o Q-Forge do repositório (`mutate_candidate`,
`crossover_candidates`, `tournament_select`, `Pauli`, `commutes_with`) em vez de reinventar
operadores genéticos quânticos.

## Pergunta falsificável da fase

> A evolução de conjuntos estabilizadores encontra, sob orçamento fixo, algum conjunto com
> distância estritamente maior que o `best_known_value` do catálogo para qualquer alvo de
> recorde — com cada candidato julgado exclusivamente pelo verificador independente da P179?

## Fatos de partida

| Fato | Fonte |
|---|---|
| `pauli.py`: `Pauli`, `multiply`, `commutes_with`, `single`, `identity`, `decode_human` | `src/evobyte/quantum/pauli.py` (ler antes) |
| `evolution_q.py`: `mutate_candidate`, `crossover_candidates`, `tournament_select`, `ConservedArchive`, `evolve_conserved_operator` | `src/evobyte/quantum/evolution_q.py` (ler antes) |
| `circuit.py`: `CircuitInstruction`, `encode_circuit`, `decode_circuit`, `validate_circuit`, `is_valid_circuit` | `src/evobyte/quantum/circuit.py` (ler antes) |
| Verificador exato com `code_distance` | P179 |
| Alvos com gap aberto | Catálogo P180 (`qecc_frontier_v1.json`, `role = record`) |

## Escopo

**Arquivos que você pode criar:**
- `src/evobyte/stabilizer_search.py` (representação simplética + reparo + fitness via P179)
- `benchmarks/run_stabilizer_search.py` (protocolo de busca por alvo, com orçamento e checkpoint)
- `tests/test_stabilizer_search.py` (só lógica e micro-espaços; suíte < 3 s)
- `docs/research/p181-stabilizer-search-report.md`

**Arquivos que você pode editar:**
- `docs/phases/P181-quantum-stabilizer-evolution.md`: só a linha de Status e o bloco final de execução.

**Proibido:**
- reimplementar Pauli/comutação já existentes em `quantum/pauli.py` (reutilizar, não duplicar);
- julgar distância por qualquer coisa que não seja o verificador P179;
- buscas/evoluções dentro de `tests/` (tudo > 0,2 s é proibido).

## Trabalho ordenado

### Passo 1 — Branch e leitura obrigatória

```bash
git status --short
git switch codex/p180-grassl-bounds-frontier-catalogue
git switch -c codex/p181-quantum-stabilizer-evolution
sed -n '1,120p' src/evobyte/quantum/pauli.py
sed -n '1,120p' src/evobyte/quantum/evolution_q.py
test -f docs/research/targets/qecc_frontier_v1.json || { echo "P180 NAO CONCLUIDA"; exit 1; }
```

### Passo 2 — `src/evobyte/stabilizer_search.py`

Representação: matriz binária `(n-k) × 2n` (metade X | metade Z) + reparo de comutatividade
por eliminação GF(2) com descarte honesto (se o reparo falhar, o candidato é inválido —
nunca "quase-válido").

```python
"""Stabilizer-set search reusing Q-Forge operators (P181)."""

def random_stabilizer_set(n, k, rng): ...
def mutate_stabilizer_set(candidate, rng):      # usa quantum.evolution_q.mutate_candidate onde couber
def crossover_stabilizer_sets(a, b, rng): ...   # usa quantum.evolution_bit crossover onde couber
def repair_commutation(candidate): -> (ok: bool, fixed)
def fitness_stabilizer_set(candidate, n, k) -> tuple[float, bool]:
    """(score, is_record_candidate): score = d medido pelo verificador P179
    (0 se inválido); is_record_candidate = válido E d > best_known_value do alvo."""
```

Fitness lexicográfica documentada: primeiro validade, depois `d`, depois `-peso_total`
(desempate determinístico). Sem LLM, sem rede.

### Passo 3 — `benchmarks/run_stabilizer_search.py`

`--target {target_id} --seconds S --seeds a,b,c --output ...json [--checkpoint ...]`:
para cada semente, evolução sob orçamento duplo (tempo OU avaliações); **todo** candidato com
`d > best_known_value` é revalidado pelo verificador P179 imediatamente e, se confirmado,
gravado com o objeto + SHA-256 (não para a busca: um recorde não cancela as demais sementes).

### Passo 4 — Testes `tests/test_stabilizer_search.py` (todos < 0,2 s; suíte < 3 s)

1. `test_repair_keeps_commuting_sets`: conjunto comutante permanece comutante após reparo;
   conjunto com erro simples é corrigido ou declarado inválido (nunca silenciosamente "aceito").
2. `test_fitness_uses_p179_verifier_only`: com `unittest.mock` no verificador, fitness 0 para
   inválido e `d` do verificador para válido (prova que a decisão vem do oráculo, não de heurística).
3. `test_mutation_crossover_preserve_shape`: formas `(n-k) × 2n` preservadas; semente fixa → trajetória reproduzível.
4. `test_malformed_rejected`: matriz com dimensão errada, símbolo inválido, `k > n` → inválido, sem exceção.
5. `test_qforge_operators_reused`: o módulo importa e chama operadores de `quantum.evolution_q`/`quantum.pauli` (checagem de import + `unittest.mock` de chamada), em vez de duplicá-los.

### Passo 5 — Relatório `docs/research/p181-stabilizer-search-report.md`

Representação, reparo, fitness, protocolo do benchmark, calibração (o motor reencontra
Steane/Shor a partir de inicialização aleatória? medir e reportar honestamente — se não
reencontrar em orçamento razoável, é evidência contra o motor, não falha escondida) e limitações.

## Regras de parada (PARE, não commite, reporte)

- Qualquer distância usada no fitness vier de outro lugar que não o verificador P179.
- Qualquer teste > 0,2 s ou suíte > 3 s; qualquer evolução dentro de `tests/`.
- Falha no pytest ou no `make verify`.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_stabilizer_search.py -q -m "not slow"   # FAST LOOP, ~1s
python3 -m pytest tests/test_stabilizer_search.py -q                 # FINAL GATE, < 3s
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add src/evobyte/stabilizer_search.py benchmarks/run_stabilizer_search.py \
  tests/test_stabilizer_search.py docs/research/p181-stabilizer-search-report.md \
  docs/phases/P181-quantum-stabilizer-evolution.md
git diff --cached --check
git commit -m "feat(quantum): implement p181 stabilizer evolution with q-forge"
git push -u origin HEAD
gh pr create --base codex/p180-grassl-bounds-frontier-catalogue \
  --title "feat(quantum): p181 stabilizer evolution" \
  --body-file /tmp/evobyte-p181-pr.md
git status --short
```

O corpo do PR (`/tmp/evobyte-p181-pr.md`) traz: problema, comportamento resultante, comandos de
validação exatos, números medidos (calibração Steane/Shor, micro-benchmarks), limitações e o
link do relatório.
