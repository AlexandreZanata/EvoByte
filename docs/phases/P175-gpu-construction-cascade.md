# P175 — Cascata de construção em GPU (batching PyTorch/CUDA com medição real)

**Status:** Proposed.
**Programa:** Descoberta na Fronteira (P171–P190, D042). Trilhas A, B e fundação comum.
**Dependência:** P173 concluída (construtor + `evaluate_priority` CPU); branch a partir de `codex/p173-constructive-bytecode-priority-engine`.
**Owner:** agente executor; revisor de sistemas (medir, nunca estimar).
**Branch:** `codex/p175-gpu-construction-cascade`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [regras do programa P171–P190](README.md#programa-de-descoberta-na-fronteira-p171p190-d042), [`docs/phases/P173-constructive-bytecode-priority-engine.md`](P173-constructive-bytecode-priority-engine.md).

## Por que esta fase existe

O construtor guloso da P173 avalia candidatos um a um na CPU. Para campanhas de fronteira
(P176/P177), a avaliação precisa escalar: portar a pontuação de prioridades para batch em GPU
(PyTorch/CUDA) e **medir** a aceleração real contra CPU — com pico de VRAM registrado — em
vez de afirmá-la.

## Pergunta falsificável da fase

> O batching em GPU da avaliação de prioridades do construtor guloso é estritamente mais
> rápido que a CPU (speedup medido > 1,0×) nos mesmos candidatos, sementes e prioridades,
> com pico de VRAM medido e reportado?

## Fatos de partida

| Fato | Fonte |
|---|---|
| `evaluate_priority(programa, features, context)` existe e é determinístico na CPU | P173 (`src/evobyte/constructive.py`) |
| `torch` instalado com CUDA (`torch 2.14.0+cu130` neste ambiente; o executor re-mede) | `python3 -c "import torch; print(torch.cuda.is_available())"` |
| Padrão de medição de pico VRAM: `torch.cuda.max_memory_allocated()` com `reset_peak_memory_stats()` | Padrão do repo (P154/P155 mediram `vram_peak_mb`) |
| Sem GPU disponível, o gate de medição é pulado com status explícito (não é falha, não é vitória) | Regra desta fase |

## Escopo

**Arquivos que você pode criar:**
- `src/evobyte/constructive_torch.py` (batching CUDA da pontuação de prioridades; fallback CPU idêntico)
- `benchmarks/gpu_construction_ablation.py` (CPU vs GPU, mesma semente/candidatos/prioridade; JSON com speedup e pico VRAM)
- `experiments/p175-gpu-ablation.json` (resultado medido)
- `tests/test_gpu_construction.py` (só equivalência e micro-batch; suíte < 3 s; teste de GPU marcado `slow` se > 2 s)
- `docs/research/p175-gpu-construction-report.md`

**Arquivos que você pode editar:**
- `docs/phases/P175-gpu-construction-cascade.md`: só a linha de Status e o bloco final de execução.

**Proibido:**
- afirmar speedup sem medição pareada na mesma máquina;
- usar GPU nos testes unitários como caminho obrigatório (todo teste passa sem CUDA; o teste de medição real vive no script de benchmark);
- mudar a semântica do construtor CPU (o batch GPU deve produzir as **mesmas** pontuações, bit a bit onde o dtype permitir, ou dentro de tolerância declarada `1e-5` para float32).

## Trabalho ordenado

### Passo 1 — Branch

```bash
git status --short
git switch codex/p173-constructive-bytecode-priority-engine
git switch -c codex/p175-gpu-construction-cascade
python3 -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

### Passo 2 — `src/evobyte/constructive_torch.py`

```python
"""GPU-batched priority scoring for the greedy constructor (P175)."""

def score_batch_torch(programs, features_batch, contexts_batch, device=None) -> list[float]:
    """Pontua um batch de (programa, features, contexto).
    - Se CUDA disponível e `device` não for "cpu": executa em batch no device.
    - Caso contrário: delega para `constructive.evaluate_priority` (CPU), um a um.
    Retorna floats Python na mesma ordem. Nunca levanta por falta de GPU."""

def peak_vram_mb(device=None) -> float | None:
    """`torch.cuda.max_memory_allocated()/2**20` após `reset_peak_memory_stats()`;
    `None` sem CUDA."""
```

Regras: o caminho CPU do batch **deve** chamar exatamente `evaluate_priority` (sem duplicar
lógica); tolerância GPU-vs-CPU documentada (`1e-5` absoluto em float32); sem estado global.

### Passo 3 — `benchmarks/gpu_construction_ablation.py`

`--output experiments/p175-gpu-ablation.json [--device cuda:0|cpu]`: gera N=2000 triplas
`(programa, features, contexto)` com semente fixa, pontua em CPU e em GPU (se disponível),
mede `time.perf_counter()` e `peak_vram_mb`, e grava
`{"cpu_sec":, "gpu_sec":, "speedup":, "peak_vram_mb":, "max_abs_diff":, "n":, "seed":}`.
Sem CUDA: grava `{"gpu_available": false, "speedup": null}` e sai com código 0 (medição
ausente ≠ falha, e jamais vitória).

### Passo 4 — Testes `tests/test_gpu_construction.py` (todos < 0,2 s; suíte < 3 s)

1. `test_batch_matches_single_cpu`: 16 triplas fixas; `score_batch_torch(..., device="cpu")`
   é bit-idêntico a `evaluate_priority` uma a uma.
2. `test_batch_order_and_length_preserved`: ordem e tamanho da saída preservados; entrada
   malformada (feature `NaN`, programa vazio) retorna `-inf`, nunca levanta.
3. `test_peak_vram_reports_or_none`: retorna `None` sem CUDA ou `float >= 0.0` com CUDA;
   nunca levanta.
4. `test_gpu_parity_small_batch`: **marcado `@pytest.mark.slow`**; pula sem CUDA; com CUDA,
   compara batch GPU vs CPU em 32 triplas dentro da tolerância declarada.

### Passo 5 — Relatório `docs/research/p175-gpu-construction-report.md`

Speedup medido (ou `null` com motivo), pico de VRAM, `max_abs_diff` CPU-vs-GPU, hardware
exato (`nvidia-smi`-like + `torch.__version__` + `cuda_version`), e a consequência para as
campanhas (qual caminho as P176/P177 usam por padrão, com a regra de fallback).

## Regras de parada (PARE, não commite, reporte)

- Divergência CPU-vs-GPU além da tolerância declarada.
- Qualquer teste > 0,2 s fora do marcado `slow`; suíte (sem `slow`) > 3 s.
- Speedup afirmado sem medição pareada no mesmo JSON de saída.
- Falha no pytest ou no `make verify`.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_gpu_construction.py -q -m "not slow"   # FAST LOOP, ~1s
python3 benchmarks/gpu_construction_ablation.py --output experiments/p175-gpu-ablation.json
python3 -m pytest tests/test_gpu_construction.py -q                 # FINAL GATE, < 3s + slow se houver GPU
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add src/evobyte/constructive_torch.py benchmarks/gpu_construction_ablation.py \
  experiments/p175-gpu-ablation.json tests/test_gpu_construction.py \
  docs/research/p175-gpu-construction-report.md \
  docs/phases/P175-gpu-construction-cascade.md
git diff --cached --check
git commit -m "feat(evo): implement p175 gpu construction cascade with measured speedup"
git push -u origin HEAD
gh pr create --base codex/p173-constructive-bytecode-priority-engine \
  --title "feat(evo): p175 gpu construction cascade" \
  --body-file /tmp/evobyte-p175-pr.md
git status --short
```

O corpo do PR (`/tmp/evobyte-p175-pr.md`) traz: problema, comportamento resultante, comandos de
validação exatos, números medidos (speedup, pico VRAM, `max_abs_diff`) ou `null` justificado,
limitações e o link do relatório.
