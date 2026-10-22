# P173 — Motor construtivo em bytecode: prioridades sintetizadas e construtor guloso

**Status:** Proposed.
**Programa:** Descoberta na Fronteira (P171–P190, D042). Trilhas A, B e fundação comum.
**Dependência:** P172 concluída (baselines calibrados); branch a partir de `codex/p172-frontier-baselines-solver-harness`.
**Owner:** agente executor; revisor de sistemas (compatibilidade de bytecode é irreversível).
**Branch:** `codex/p173-constructive-bytecode-priority-engine`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [regras do programa P171–P190](README.md#programa-de-descoberta-na-fronteira-p171p190-d042), [`docs/phases/P172-frontier-baselines-solver-harness.md`](P172-frontier-baselines-solver-harness.md), `src/evobyte/bytecode.py` (`OPCODE_VERSION`, tabela de opcodes, `is_valid`).

## Por que esta fase existe

A Trilha B (hipótese H2) afirma que **evolução em bytecode** — sem LLM — descobre programas
construtores no nível do FunSearch. Para isso o EvoByte precisa de duas peças que não existem:
(1) uma ISA capaz de sintetizar funções de prioridade `score(elemento, contexto) -> float`, e
(2) um construtor guloso determinístico que monte objetos combinatórios elemento a elemento
guiado por essa prioridade. Esta fase constrói as duas, com bump de versão e compatibilidade
total com o interpretador v0.

## Pergunta falsificável da fase

> Um construtor guloso determinístico guiado por prioridade consegue montar exatamente o
> cubo `{0,1}³` (8 pontos, sem três colineares em F₃³) em menos de 0,1 s a partir de uma
> prioridade estática pré-definida, e um programa em bytecode v1 avalia a mesma prioridade
> com resultado bit-idêntico ao cálculo de referência?

## Fatos de partida

| Fato | Fonte |
|---|---|
| `OPCODE_VERSION = 0`, 16 opcodes `0x00–0x0F`, campo de opcode com 1 byte (há espaço para `0x10+`) | `src/evobyte/bytecode.py` (medido no repo) |
| `encode_instr`/`decode_instr` empacotam `[OP,DST,A,B]` em `uint32`; S0 exige forma, escrita em `r7` e cadeia arriscada ≤ 4 | `src/evobyte/bytecode.py::is_valid` |
| `archive.py::load_checkpoint` hoje **rejeita** versão diferente da corrente | `src/evobyte/archive.py` (ler o código antes de alterar) |
| `{0,1}³` não contém três pontos distintos com `a+b+c ≡ 0 (mod 3)` | Prova direta (P172; se `a≠b ∈ {0,1}³`, então `c = -(a+b)` tem coordenada 2 onde `a,b` diferem) |
| P171 verifica `cap_set` em F₃ⁿ por triplas distintas (`frontier_catalogue.verify_cap_set`) | Dependência P171 |

## Escopo

**Arquivos que você pode criar:**
- `src/evobyte/constructive.py` (construtor guloso genérico + `evaluate_priority` + CTX/FEAT)
- `tests/test_constructive_priority.py` (só lógica e micro-construções; suíte < 3 s)
- `docs/research/p173-priority-engine-report.md`

**Arquivos que você pode editar:**
- `src/evobyte/bytecode.py`: bump `OPCODE_VERSION` 0 → 1; adicionar opcodes `0x10` (`CTX`) e `0x11` (`FEAT`); estender `is_valid`; **manter** o caminho de decodificação/execução v0 intacto.
- `src/evobyte/archive.py`: aceitar checkpoints v0 **e** v1 (nunca quebrar leitura de estado antigo).
- `docs/phases/P173-constructive-bytecode-priority-engine.md`: só a linha de Status e o bloco final de execução.

**Proibido:**
- renumerar ou remover opcodes `0x00–0x0F`;
- mudar a semântica de qualquer opcode v0;
- testes que evoluam programas, rodem buscas ou meçam tempo de construção além do micro-teste do cubo (< 0,1 s);
- `torch`/`cuda` nesta fase (GPU é P175; aqui é CPU determinístico).

## Trabalho ordenado

### Passo 1 — Branch e pré-condição

```bash
git status --short
git switch codex/p172-frontier-baselines-solver-harness && git pull --ff-only 2>/dev/null || git switch codex/p172-frontier-baselines-solver-harness
git switch -c codex/p173-constructive-bytecode-priority-engine
grep -n "OPCODE_VERSION = 0" src/evobyte/bytecode.py   # deve existir; senão, PARE e reporte
```

### Passo 2 — Evolução da ISA (bump 0 → 1, superset estrito)

Em `src/evobyte/bytecode.py`:

1. `OPCODE_VERSION = 1`.
2. Adicionar ao final de `OPCODES`: `0x10: "CTX"`, `0x11: "FEAT"`.
   Semântica exata (implementar em `src/evobyte/vm.py::execute` e `vm_torch.py` se existir o caminho):
   - `CTX`: `r[dst] = ctx[b & 0x0F]` — lê o escalar `b`-ésimo do vetor de contexto (até 16
     escalares; fora do intervalo → `0.0`, nunca exceção).
   - `FEAT`: `r[dst] = feat[b & 0x0F]` — lê a feição `b`-ésima do elemento corrente
     (até 16 feições; fora do intervalo → `0.0`, nunca exceção).
3. `is_valid`: aceitar `0x10`/`0x11` como ops não-arriscados (quebram cadeia arriscada como
   qualquer op limitado); todo o resto idêntico para programas v0.
4. `archive.py::load_checkpoint`: aceitar `opcode_version` em `{0, 1}`; estados v0 continuam
   legíveis e executáveis (a tabela v1 é superset, nenhum opcode v0 mudou de número).

### Passo 3 — `src/evobyte/constructive.py`

Contrato obrigatório:

```python
"""Deterministic greedy constructor guided by priority programs (P173)."""

def evaluate_priority(program: np.ndarray, features: list[float], context: list[float]) -> float:
    """Carrega features em r0..r6, zera r7, executa o programa v1 e retorna r7.
    Entrada malformada (tamanho errado, NaN) retorna -inf, nunca levanta."""

def greedy_construct(candidates, priority_fn, is_feasible_fn, is_complete_fn, max_steps=None):
    """Determinístico: a cada passo pontua os candidatos restantes, escolhe o maior
    (desempate: menor índice), adiciona se feasible. Retorna (built_list, steps, evaluations).
    `priority_fn(move, context) -> float`; `context` é dict com estado parcial
    (ex: tamanho atual, cobertura, orçamento restante)."""
```

Regras: sem RNG dentro do construtor (a aleatoriedade, se houver, pertence ao chamador via
ordem dos candidatos); sem `torch`/`cuda`; `evaluations` conta chamadas reais à prioridade.

### Passo 4 — Testes `tests/test_constructive_priority.py` (todos < 0,2 s; suíte < 3 s)

1. `test_opcode_version_bumped_and_v0_compatible`: `OPCODE_VERSION == 1`; um programa v0 dourado
   (ex: `ADD r7, r0, r1` sobre entradas fixas) executa bit-idêntico ao vetor esperado **gravado
   no teste**; programa só-v0 passa no novo `is_valid`; `load_checkpoint` aceita estado com
   `opcode_version` 0 e 1.
2. `test_ctx_feat_opcodes_execute`: `CTX` lê `ctx[b & 0x0F]` (incluindo índice fora do intervalo
   → 0.0); `FEAT` análogo; opcode desconhecido (`0x12`) é rejeitado por `is_valid`.
3. `test_priority_scores_cube_statically`: prioridade estática em Python que pontua vetores
   0/1 acima dos demais; `evaluate_priority` com programa bytecode equivalente
   (ex: soma ponderada que replica a ordem) produz a **mesma ordenação** nos 27 pontos de F₃³.
4. `test_greedy_builds_cube_instant`: construtor guloso + prioridade estática sobre os 27
   pontos de F₃³, com `is_feasible` = "não cria reta" (via `frontier_catalogue.verify_cap_set`
   incremental ou checagem local): o conjunto construído é **exatamente** `{0,1}³` (8 pontos),
   em menos de 0,1 s medidos com `time.perf_counter`.
5. `test_greedy_never_adds_infeasible`: com `is_feasible` que rejeita um ponto específico,
   o construído nunca o contém, independente da prioridade.

### Passo 5 — Relatório `docs/research/p173-priority-engine-report.md`

Tabela de opcodes v0→v1, semântica de CTX/FEAT, prova de compatibilidade (golden test),
tempo medido do micro-teste do cubo, e limitações (construtor é CPU e determinístico;
evolução das prioridades é P174, GPU é P175).

## Regras de parada (PARE, não commite, reporte)

- Qualquer programa v0 dourado mudar de saída após o bump.
- `load_checkpoint` rejeitar estado v0.
- O cubo construído divergir de `{0,1}³` ou demorar ≥ 0,1 s.
- Qualquer teste individual > 0,2 s ou suíte > 3 s.
- Falha no pytest ou no `make verify`.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_constructive_priority.py -q -m "not slow"   # FAST LOOP, ~1s
python3 -m pytest tests/test_constructive_priority.py -q                 # FINAL GATE, < 3s
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add src/evobyte/bytecode.py src/evobyte/vm.py src/evobyte/vm_torch.py src/evobyte/archive.py \
  src/evobyte/constructive.py tests/test_constructive_priority.py \
  docs/research/p173-priority-engine-report.md \
  docs/phases/P173-constructive-bytecode-priority-engine.md
git diff --cached --check
git commit -m "feat(evo): implement p173 constructive bytecode priority engine"
git push -u origin HEAD
gh pr create --base codex/p172-frontier-baselines-solver-harness \
  --title "feat(evo): p173 constructive bytecode priority engine" \
  --body-file /tmp/evobyte-p173-pr.md
git status --short
```

O corpo do PR (`/tmp/evobyte-p173-pr.md`) traz: problema, comportamento resultante, comandos de
validação exatos, números medidos (tempo do cubo, compat v0), limitações (sem GPU, sem evolução)
e o link do relatório.
