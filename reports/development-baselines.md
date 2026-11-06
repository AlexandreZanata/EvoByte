# Referências não aprendidas no desenvolvimento

**Protocolo:** P0-development-v1 (`3811a92fc15ecf4584edb604dbb26225a0915ba60d801ad41a128e7d4764ede7`)  
**Manifesto:** `configs/development-baselines.json`  
**Hash do manifesto:** `c9b6e0300afa293737270452da04db6106270e39dce71e77160aacb241b0a96e`  
**Commit da execução:** `9a0aa43cb1453c7be07b54b707cbe278ab4d769c`  
**Data:** 6 de novembro de 2026

Este relatório apresenta medidas de desenvolvimento. Validade não prova novidade
nem optimalidade. A revisão F3 independente ainda não foi realizada; o parecer
deve ser produzido em sessão separada em `reports/reviews/F3.md`.

---

## 1. Escopo e agenda

- Quatro referências: `random`, `greedy`, `local_uniform` e `local_manual`.
- Tamanhos de desenvolvimento: `n ∈ {8, 10, 12, 16}`.
- Dois blocos de semente: `0` e `1`, dentro da faixa 0–99 do P0.
- Cada execução tem orçamento de parede `B=60 s`.
- Total: 4 métodos × 4 tamanhos × 2 blocos = **32 execuções**, 1.920 s
  reservados no ledger de desenvolvimento.
- Nenhum tamanho de ajuste, piloto, confirmação ou reprodução foi executado.

Derivação de streams (por bloco, método e n):

```text
índice do método: random=0, greedy=1, local_uniform=2, local_manual=3
search_seed       = bloco * 100000 + n * 100 + índice * 10 + 1
perturbation_seed = search_seed + 1
run_id            = dev-b<bloco>-n<n>-<método>
```

Parâmetros locais usados nesta medição de desenvolvimento (primeira célula da
grade P0, **não** o motor final tunado): `k_max=1`, `S=50`; para
`local_manual`, `p=0.5`. A grade de ajuste ainda deve escolher o motor local em
F4; este relatório não antecipa essa decisão.

---

## 2. Execução e evidências

O executor serial (`runs/development-baselines/driver.py`, evidência local
ignorada pelo git) chamou a CLI `run` para cada item da agenda. Cada chamada usou:

- supervisor obrigatório, grupo de processos e Budget de 60 s;
- reserva de 60 s no ledger antes do spawn;
- configuração canônica, ambiente, eventos, checkpoint, inventário e certificado
  vazio de preflight;
- trabalhador que executou o motor aprovado e certificou o melhor candidato pelo
  contrato existente.

Evidências locais por execução:

```text
runs/development-baselines/development-baselines/<run_id>/
  config.json, environment.json, events.jsonl, checkpoint.json,
  worker.stdout.log, worker.stderr.log, inventory.json,
  empty-certificate/, candidate.json, envelope.json, certificate.json,
  search-events.jsonl, search-result.json
runs/development-baselines/results/<run_id>.json       # saída JSON da CLI
runs/development-baselines/ledger.json                 # ledger da campanha
runs/development-baselines/driver-summary.json
runs/development-baselines/campaign-summary.json
```

Comando da agenda (executado na raiz):

```bash
python runs/development-baselines/driver.py
```

Consulta do ledger:

```bash
python -m evobyte campaign \
  --manifest configs/development-baselines.json \
  --ledger runs/development-baselines/ledger.json
```

A CLI padrão deriva o ledger ao lado do manifesto; aqui o caminho
`runs/development-baselines/ledger.json` foi passado explicitamente para manter
toda a evidência volumosa sob `runs/`.

---

## 3. Resultados por execução

| método | n | bloco | m certificado | certificado | status | parede (s) | eventos |
|---|---:|---:|---:|---|---|---:|---:|
| `random` | 8 | 0 | 10 | CERTIFIED | completed | 55.4 | 310900 |
| `random` | 10 | 0 | 15 | CERTIFIED | completed | 54.8 | 174359 |
| `random` | 12 | 0 | 18 | CERTIFIED | completed | 54.5 | 108910 |
| `random` | 16 | 0 | 28 | CERTIFIED | completed | 54.3 | 47286 |
| `greedy` | 8 | 0 | 7 | CERTIFIED | completed | 55.7 | 413154 |
| `greedy` | 10 | 0 | 9 | CERTIFIED | completed | 55.2 | 269716 |
| `greedy` | 12 | 0 | 11 | CERTIFIED | completed | 54.9 | 185160 |
| `greedy` | 16 | 0 | 15 | CERTIFIED | completed | 54.5 | 101990 |
| `local_uniform` | 8 | 0 | — | — | timeout | 58.1 | — |
| `local_uniform` | 10 | 0 | 15 | CERTIFIED | completed | 56.9 | 706498 |
| `local_uniform` | 12 | 0 | 18 | CERTIFIED | completed | 56.3 | 572706 |
| `local_uniform` | 16 | 0 | 28 | CERTIFIED | completed | 55.5 | 329304 |
| `local_manual` | 8 | 0 | 10 | CERTIFIED | completed | 58.0 | 1001049 |
| `local_manual` | 10 | 0 | 15 | CERTIFIED | completed | 57.2 | 780426 |
| `local_manual` | 12 | 0 | 18 | CERTIFIED | completed | 56.4 | 587540 |
| `local_manual` | 16 | 0 | 28 | CERTIFIED | completed | 55.6 | 370622 |
| `random` | 8 | 1 | 10 | CERTIFIED | completed | 55.4 | 321611 |
| `random` | 10 | 1 | 15 | CERTIFIED | completed | 54.9 | 187685 |
| `random` | 12 | 1 | 18 | CERTIFIED | completed | 54.9 | 102015 |
| `random` | 16 | 1 | 28 | CERTIFIED | completed | 54.8 | 38714 |
| `greedy` | 8 | 1 | 7 | CERTIFIED | completed | 56.3 | 187708 |
| `greedy` | 10 | 1 | 9 | CERTIFIED | completed | 56.5 | 111530 |
| `greedy` | 12 | 1 | 11 | CERTIFIED | completed | 56.1 | 77056 |
| `greedy` | 16 | 1 | 15 | CERTIFIED | completed | 55.5 | 42242 |
| `local_uniform` | 8 | 1 | — | — | timeout | 58.1 | — |
| `local_uniform` | 10 | 1 | — | — | timeout | 58.1 | — |
| `local_uniform` | 12 | 1 | 18 | CERTIFIED | completed | 55.5 | 225596 |
| `local_uniform` | 16 | 1 | 28 | CERTIFIED | completed | 55.5 | 327122 |
| `local_manual` | 8 | 1 | — | — | timeout | 58.0 | — |
| `local_manual` | 10 | 1 | 15 | CERTIFIED | completed | 57.7 | 727680 |
| `local_manual` | 12 | 1 | 18 | CERTIFIED | completed | 56.7 | 542630 |
| `local_manual` | 16 | 1 | 28 | CERTIFIED | completed | 55.6 | 346348 |

Totais:

- 32 tentativas registradas no ledger;
- **28 certificados** (`CERTIFIED` pela referência e pelo runtime);
- **4 timeouts** sem certificado;
- nenhum overrun;
- nenhuma reserva aberta ao final;
- 1.792,85 s consumidos; 127,15 s de saldo no limite de 1.920 s.

---

## 4. Agregados certificados

Valores de referência do P0 para os tamanhos de desenvolvimento: `n=8: 10`,
`n=10: 15`, `n=12: 18`, `n=16: 28`. A igualdade abaixo é comparação com esses
valores publicados, não prova de optimalidade.

| método | n | m por bloco | média certificada | referência P0 |
|---|---:|---|---:|---:|
| `random` | 8 | 10, 10 | 10.0 | 10 |
| `random` | 10 | 15, 15 | 15.0 | 15 |
| `random` | 12 | 18, 18 | 18.0 | 18 |
| `random` | 16 | 28, 28 | 28.0 | 28 |
| `greedy` | 8 | 7, 7 | 7.0 | 10 |
| `greedy` | 10 | 9, 9 | 9.0 | 15 |
| `greedy` | 12 | 11, 11 | 11.0 | 18 |
| `greedy` | 16 | 15, 15 | 15.0 | 28 |
| `local_uniform` | 8 | timeout, timeout | — | 10 |
| `local_uniform` | 10 | 15, timeout | 15.0 (1 caso) | 15 |
| `local_uniform` | 12 | 18, 18 | 18.0 | 18 |
| `local_uniform` | 16 | 28, 28 | 28.0 | 28 |
| `local_manual` | 8 | 10, timeout | 10.0 (1 caso) | 10 |
| `local_manual` | 10 | 15, 15 | 15.0 | 15 |
| `local_manual` | 12 | 18, 18 | 18.0 | 18 |
| `local_manual` | 16 | 28, 28 | 28.0 | 28 |

Observações descritivas:

- `random` e as referências locais certificadas igualaram os valores de referência
  do P0 nos tamanhos medidos.
- `greedy` ficou abaixo da referência em todos os tamanhos, como esperado para
  uma regra míope; isso reduz sua competição como baseline.
- As referências locais têm lacunas de certificação em n=8 e n=10; a competência
  delas deve ser julgada pela revisão F3 com essas lacunas explícitas.

---

## 5. Falhas preservadas

Quatro execuções terminaram em `timeout` por ação do supervisor, sem certificado:

- `dev-b0-n8-local_uniform` (58.1 s, `search-events.jsonl` parcial de 114 MB);
- `dev-b1-n8-local_uniform` (58.1 s, 39 MB);
- `dev-b1-n10-local_uniform` (58.1 s, 32 MB);
- `dev-b1-n8-local_manual` (58.0 s, 111 MB).

Causa observada: o trabalhador concluía a busca em ~54 s, mas gravava a lista
completa de eventos da busca em `search-events.jsonl` (até 114 MB) antes de
certificar. Esse dump pós-busca ultrapassou a janela até o TERM do supervisor
(`29B/30 = 58 s`); o processo foi encerrado e o certificado/resultado do
trabalhador não foi produzido. O tempo real foi contabilizado no ledger como
`timeout`, sem devolução.

Nenhuma dessas quatro execuções foi repetida seletivamente para melhorar o
resultado. Elas permanecem como evidência e como limitação de instrumentação. A
correção do caminho de eventos é uma tarefa de reparo restrita, se necessária,
antes de nova medição; não foi feita nesta tarefa para não reescrever a agenda
após observar resultados.

---

## 6. Custo

- **Agenda de desenvolvimento:** 1.792,85 s no ledger (1.920 s reservados),
  dentro da quota de desenvolvimento de 2.880 s do P0.
- **Parede do executor:** 1.795,94 s.
- **Execuções:** 32 tentativas; 28 certificadas, 4 timeouts.
- **Overrun:** 0 s.
- **Smoke test do encadeamento:** uma execução curta separada de 6 s, sob a
  quota de testes/verificações, não faz parte das 32 tentativas.
- **Nenhuma GPU/Vram medida:** não houve uso de GPU; o ambiente registra GPU/CUDA
  indisponíveis com motivo.

---

## 7. Limitações e revisão pendente

- Parâmetros locais são a primeira célula da grade P0, não o motor final tunado.
- Quatro timeouts de instrumentação impedem certificar parte de n=8/10 nas
  referências locais.
- A busca para por parede real; a repetição exata entre hardwares não é prometida.
  Sementes, configuração, manifesto e commits estão registrados para reprodução
  descritiva.
- Nenhum resultado é declarado ótimo por este relatório; os valores P0 são
  referências publicadas.
- **Revisão F3 independente pendente.** `reports/reviews/F3.md` deve ser
  produzido em sessão separada, com identidade e parecer, inspecionando o
  manifesto, o ledger, os 28 certificados, os quatro timeouts, o executor e o
  custo. Até lá, F03-T05 permanece pendente.
