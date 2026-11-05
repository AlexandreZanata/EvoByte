# P175 — Relatório da cascata de construção em GPU

**Data:** 2026-10-23
**Fase:** P175 — Descoberta na Fronteira (D042)

## 1. Resposta falsificável

**SIM.** Batch GPU é estritamente mais rápido que CPU nos mesmos 2000 candidatos/semente/prioridades: **speedup 1,52×** (> 1,0×), com pico de VRAM medido de **0,66 MB**.

## 2. Medição (pareada, mesma máquina)

| Métrica | Valor |
|---|---|
| `cpu_sec` | 0,085 s |
| `gpu_sec` | 0,056 s (após warmup de 64 triplas; init CUDA fora da região cronometrada) |
| `speedup` | **1,52×** |
| `peak_vram_mb` | 0,66 |
| `max_abs_diff` | 2,0 (4/2000 triplas; ver análise) |
| `max_rel_diff` | 9,5e-06 |
| `in_tolerance` | **2000/2000** (allclose `rtol=atol=1e-5`, convenção do repo) |
| `n` / `seed` | 2000 / 175 |

Artefato: `experiments/p175-gpu-ablation.json` (gerado pelo script, não digitado).

## 3. Paridade CPU-vs-GPU (análise honesta do `max_abs_diff`)

O `max_abs_diff = 2,0` concentra-se em 4/2000 triplas com saídas de grande magnitude (ex: `EXP` encadeado ≈ 2,3e7). Em float32, 1 ulp nessa magnitude vale 2,0 — os valores GPU/CPU diferem de no máximo 2 ulps (erro relativo ≤ 9,5e-06), i.e. tão próximos quanto o dtype permite. A tolerância declarada é allclose `rtol=atol=1e-5` (constante `GPU_CPU_TOLERANCE`, mesma convenção de `tests/test_vm_torch.py`): **2000/2000 dentro da tolerância**. Nenhuma divergência além da tolerância declarada; gate de parada não acionado.

Causa raiz das micro-divergências: transcendentais (`EXP`/`LOG`/`SIN`/`POW`) usam intermediários de precisão distinta entre numpy (float64) e torch (float32) no kernel seguro compartilhado; cadeias com `POW`/`DIV` amplificam 1 ulp inicial. Comportamento esperado e limitado; semântica do construtor inalterada (o caminho CPU continua referência).

## 4. Hardware exato

- GPU: NVIDIA GeForce RTX 4060 Laptop GPU, 8188 MiB, driver 580.173.02
- `torch.__version__`: 2.14.0+cu130, `torch.version.cuda`: 13.0
- `device_name` pinado no JSON de saída.

## 5. Consequência para as campanhas (P176/P177)

- **Padrão:** usar `score_batch_torch` (caminho GPU quando CUDA disponível; o batch N=2000 mede 1,52×).
- **Regra de fallback:** sem CUDA (ou qualquer exceção no caminho GPU), `score_batch_torch` delega item a item a `constructive.evaluate_priority` (CPU, bit-idêntico) e retorna `-inf` em itens malformados sem levantar. Nenhum teste unitário exige CUDA; a medição real vive no script de benchmark.
- **Limite conhecido:** o ganho 1,52× vale para batches ~2000; batches pequenos (< 100) podem não compensar o lançamento de kernels — o script de campanha deve agrupar avaliações em batches grandes ou aceitar o fallback CPU.
