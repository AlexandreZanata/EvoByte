# F04-T05 — Grade de ajuste (16 local_manual + 8 local_linear, 600 s)

**Manifestos:** `configs/tuning.json` (manual, `c01eeb67…`, 16 runs, cap 9600 s);
`runs/tuning/linear-manifest.json` (linear, `c1e8cb99…`, 8 runs, cap 4800 s).
**Protocolo:** P0-development-v1 (`3811a92f…`). Ótimos publicados de referência:
n=18 → 34, n=20 → 41 (comparação apenas, sem alegação de ótimo).
**Janela:** 600 s por execução (busca até 540 s, TERM 580 s, KILL 590 s).
**Saída do contrato:** 24 tentativas lançadas (16+8), escolha determinística do
motor e de λ, com evidência preservada.

## 1. Execução

Driver `runs/tuning/driver.py` (não rastreado; harness local ignorado pelo
git): manifesto congelado → trava do ledger → `run` via supervisor com
`EventLogWriter` (política 50.000 eventos não-chave / 16 MiB, eventos-chave
preservados) → reconciliação do consumo real → verificação por run
(`status=completed`, `timed_out=false`, `worker_still_alive=false`,
`process_group_empty=true`, `overrun=0`, certificado CERTIFIED com hash do
candidato, sem `is_example`, log `start`…`stop`+`log_summary`,
`aborted=false`, `summary_written=true`, log ≤ 17 MiB) → disco ≥ 1 GiB durante /
≥ 2 GiB antes (verificado a cada run; ficou em ~33–34 GiB).

## 2. Manual — 16 lançamentos, 15 concluídos + 1 interrompido

| run_id | n | m | alvo | déficit | parede (s) | eventos/log bytes | status |
|---|---:|---:|---:|---|---:|---|---|
| tune-m-k1-S50-p5-n18 | 18 | 34 | 34 | 0.0000 | 540.3 | 50050 / 5.4 MiB | completed |
| tune-m-k1-S50-p5-n20 | 20 | 41 | 41 | 0.0000 | 540.3 | 50058 / 5.4 MiB | completed |
| tune-m-k1-S50-p10-n18 | 18 | 17 | 34 | 0.5000 | 540.2 | 50020 / 5.4 MiB | completed |
| tune-m-k1-S50-p10-n20 | 20 | — | 41 | — | 190.6 | parcial | **crashed (abort externo, sem retry)** |
| tune-m-k1-S200-p5-n18 | 18 | 34 | 34 | 0.0000 | 540.3 | 50050 / 5.4 MiB | completed |
| tune-m-k1-S200-p5-n20 | 20 | 41 | 41 | 0.0000 | 540.2 | 50058 / 5.4 MiB | completed |
| tune-m-k1-S200-p10-n18 | 18 | 17 | 34 | 0.5000 | 540.2 | 50020 / 5.4 MiB | completed |
| tune-m-k1-S200-p10-n20 | 20 | 19 | 41 | 0.5366 | 540.2 | 50022 / 5.4 MiB | completed |
| tune-m-k3-S50-p5-n18 | 18 | 34 | 34 | 0.0000 | 540.3 | 50048 / 5.6 MiB | completed |
| tune-m-k3-S50-p5-n20 | 20 | 41 | 41 | 0.0000 | 540.2 | 50055 / 5.6 MiB | completed |
| tune-m-k3-S50-p10-n18 | 18 | 17 | 34 | 0.5000 | 540.0 | 50020 / 5.6 MiB | completed |
| tune-m-k3-S50-p10-n20 | 20 | 19 | 41 | 0.5366 | 540.1 | 50022 / 5.6 MiB | completed |
| tune-m-k3-S200-p5-n18 | 18 | 34 | 34 | 0.0000 | 540.1 | 50048 / 5.6 MiB | completed |
| tune-m-k3-S200-p5-n20 | 20 | 41 | 41 | 0.0000 | 540.0 | 50055 / 5.6 MiB | completed |
| tune-m-k3-S200-p10-n18 | 18 | 17 | 34 | 0.5000 | 540.0 | 50020 / 5.6 MiB | completed |
| tune-m-k3-S200-p10-n20 | 20 | 19 | 41 | 0.5366 | 540.1 | 50022 / 5.6 MiB | completed |

**Escolha do motor (regra P0: menor média de déficit; desempate por menor tempo
mediano até a meta com censura em 540 s; desempate final pela tupla em ordem
crescente) — cálculo determinístico sobre réplicas concluídas:**

| (k_max,S,p) | réplicas | déficit médio | t mediano |
|---|---|---|---|
| (1,50,0.5) | 2 | 0.0000 | 29.9 |
| (1,50,1.0) | 1 | 0.5000 | 540.0 |
| **(1,200,0.5)** | 2 | **0.0000** | **0.3** |
| (1,200,1.0) | 2 | 0.5183 | 540.0 |
| (3,50,0.5) | 2 | 0.0000 | 3.9 |
| (3,50,1.0) | 2 | 0.5183 | 540.0 |
| (3,200,0.5) | 2 | 0.0000 | 0.45 |
| (3,200,1.0) | 2 | 0.5183 | 540.0 |

**Motor vencedor: k_max=1, S=200** (`p` aplica-se só ao seletor manual). A
escolha é robusta à lacuna: o único combo incompleto (1,50,1.0) já perde por
déficit (0.5 > 0.0) mesmo na melhor hipótese para a réplica ausente, pois
qualquer déficit admissível ≥ 0 deixa sua média ≥ 0.25.

## 3. Linear — 8 lançamentos, 7 concluídos + 1 interrompido

Treino do zero em cada execução no mesmo t0: dados nos 4 tamanhos de
desenvolvimento (1024 pares/estado-tamanho, geração ≤ 115 s, Budget próprio),
ajuste ridge (fit < 1 ms registrado), depois busca local com o motor vencedor.
Todas as 7 concluídas treinaram 4096 pares, `training_failed` em nenhuma.

| run_id | n | bloco | m | alvo | déficit | parede (s) | eventos | status |
|---|---|---|---|---|---|---|---|---|
| tune-l-lam1-n18-b101 | 18 | 101 | 34 | 34 | 0.0 | 540.4 | 50038 | completed |
| tune-l-lam1-n18-b102 | 18 | 102 | 34 | 34 | 0.0 | 540.3 | 50039 | completed |
| tune-l-lam1-n20-b101 | 20 | 101 | 41 | 41 | 0.0 | 540.2 | 50045 | completed |
| tune-l-lam1-n20-b102 | 20 | 102 | 41 | 41 | 0.0 | 540.3 | 50045 | completed |
| tune-l-lam10-n18-b101 | 18 | 101 | 34 | 34 | 0.0 | 540.2 | 50039 | completed |
| tune-l-lam10-n18-b102 | 18 | 102 | 34 | 34 | 0.0 | 540.3 | 50039 | completed |
| tune-l-lam10-n20-b101 | 20 | 101 | 41 | 41 | 0.0 | 540.2 | 50048 | completed |
| tune-l-lam10-n20-b102 | 20 | 102 | — | 41 | — | 330.0 | parcial | **crashed (abort externo, sem retry)** |

**Escolha de λ (PROVISÓRIA): λ=1.0** — déficit médio 0.0 em ambos; mediana de
tempo 7.5 s (λ=1.0, 3 réplicas) vs 8.6 s (λ=0.1, 4 réplicas). **Ressalva
explícita:** o braço λ=1.0 tem 3/4 réplicas; a comparação usa apenas resultados
concluídos. A escolha final exige adjudicação do revisor F3 (aceitar a leitura
sobre concluídos, ou exigir nova tarefa dedicada de medição da célula
ausente com agenda e custo próprios — sem rerun seletivo). **F04-T06 NÃO foi
iniciada.**

## 4. Falhas preservadas (2 interrupções externas, sem retry)

1. `tune-m-k1-S50-p10-n20` — driver abortado pelo operador; supervisor morto,
   worker órfão encerrado via killpg do grupo; reconciliado como `crashed`
   (190.6 s observados no checkpoint). Checkpoint (`status=running`), eventos
   parciais, stdout/stderr preservados; **sem `search-result.json` e sem
   certificado**, propositalmente. O arquivo
   `runs/tuning/results-manual/tune-m-k1-S50-p10-n20.json` com `exit=2
   LEDGER_MISMATCH` é resíduo de uma tentativa inicial abortada (manifesto
   apontava para o ledger do reparo) e **não** é resultado de execução —
   documentado aqui para não confundir, mantido intacto.
2. `tune-l-lam10-n20-b102` — idem; melhor parcial conhecida m=41 aos 127.2 s
   **não certificada e não usada** (apenas evidência do log); reconciliado como
   `crashed` (330.0 s de etime do worker no TERM). Sem `search-result.json` e
   sem certificado, propositalmente.

## 5. Custo e evidência

- Manual: 8294.2 s de 9600 s; linear: 4112.0 s de 4800 s;
  **total 12.406,2 s de 14.400 s (86,2%)**; 0 overrun em 24/24; 0 reservas
  abertas; F4 acumulado 15.070,35 s de 36.960 s; disco final com 34 GiB livres.
- Logs individuais ≤ 5.7 MiB (limite 17 MiB); `truncated=true` com descarte
  apenas de não-chave; nenhum `key_dropped`.
- Evidência por run em `runs/tuning/runs-{manual,linear}/tuning-{manual,linear}/<run_id>/`
  (config, env, checkpoint, events, search-events.jsonl, search-result.json onde
  houver, candidate, envelope, certificate onde houver, inventory).
- Comandos executados estão em `runs/tuning/driver*.log`; manifestos,
  ledgers e campaign-summaries em `runs/tuning/`.

## 6. Limites e ressalvas

- Sem rerun seletivo: as células ausentes só podem ser medidas em nova tarefa
  dedicada, se o revisor determinar.
- Nenhuma afirmação de optimalidade, novidade, superioridade ou cobertura
  completa de n=8/10.
- O harness de reparo local (`runs/development-policy/worker.py`) e o módulo
  rastreado `src/evobyte/search/eventlog.py` foram reutilizados; nenhum código
  do núcleo foi tocado nesta tarefa (ver `git diff --stat` no relatório da tarefa).
