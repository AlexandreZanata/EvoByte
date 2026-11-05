# P180 — Relatório do catálogo de fronteira QECC a partir das tabelas de Grassl

**Data:** 2026-10-25
**Fase:** P180 — Descoberta na Fronteira (D042)
**Status:** Concluído

## 1. Proveniência e Fontes Primárias

Todas as cotas de limitantes e alvos candidatos derivam de snapshots brutos baixados e arquivados localmente em `data/raw/quantum/`, devidamente documentados com checksum SHA-256 e data de acesso em `docs/research/targets/qecc_sources_v1.json`:

| `source_id` | URL / Referência | SHA-256 (prefixo) | Acessado em | Status |
|---|---|---|---|---|
| `grassl-codetables-bounds` | `https://codetables.de/QECC/Tables_color.php?q=4&n0=1&n1=30&k0=0&k1=10` | `52c8a9c9c41ad8fa` | 2026-10-25T16:23:37Z | verified_snapshot |
| `grassl-codetables-20-2` | `https://codetables.de/QECC.php?q=4&n=20&k=2` | `85a30663ec80ac6f` | 2026-10-25T16:23:24Z | verified_snapshot |
| `grassl-codetables-20-3` | `https://codetables.de/QECC.php?q=4&n=20&k=3` | `df71b4f69a085f4e` | 2026-10-25T16:25:14Z | verified_snapshot |
| `grassl-codetables-14-3` | `https://codetables.de/QECC.php?q=4&n=14&k=3` | `47188e2033fbd022` | 2026-10-25T16:24:00Z | verified_snapshot |
| `grassl-codetables-16-5` | `https://codetables.de/QECC.php?q=4&n=16&k=5` | `2a74240fb793bb88` | 2026-10-25T16:24:00Z | verified_snapshot |
| `grassl-codetables-17-3` | `https://codetables.de/QECC.php?q=4&n=17&k=3` | `fa62cfe2fed23e13` | 2026-10-25T16:25:14Z | verified_snapshot |
| `grassl-codetables-18-3` | `https://codetables.de/QECC.php?q=4&n=18&k=3` | `b7a370e26b83eedf` | 2026-10-25T16:25:14Z | verified_snapshot |
| `grassl-codetables-19-10` | `https://codetables.de/QECC.php?q=4&n=19&k=10` | `88c7d050a1cce6fb` | 2026-10-25T16:25:14Z | verified_snapshot |
| `steane-1996` | `https://doi.org/10.1098/rspa.1996.0136` | `bf4553229b47e804` | 2026-10-24T10:33:00Z | peer_reviewed_literature |
| `shor-1995` | `https://doi.org/10.1103/PhysRevA.52.R2493` | `d9a33bb7f525bf4e` | 2026-10-24T10:33:00Z | peer_reviewed_literature |
| `laflamme-1996` | `https://doi.org/10.1103/PhysRevLett.77.198` | `e25f6e8ccae70044` | 2026-10-25T16:24:00Z | peer_reviewed_literature |

## 2. Alvos de Recorde com Gaps em Aberto

O catálogo congelado `docs/research/targets/qecc_frontier_v1.json` registrou 7 instâncias onde a distância mínima $d$ encontra-se com intervalo em aberto entre o limitante inferior ($d_{lo}$) com construção explícita publicada e o limitante superior ($d_{hi}$), satisfazendo $d_{lo} < d_{hi}$:

| Alvo (`target_id`) | Parâmetros $[[n,k]]$ | Limitantes $[d_{lo}, d_{hi}]$ | Gap | Status do Certificado Publicado |
|---|---|---|---|---|
| `qecc_14_3_open` | $[[14,3]]$ | $[4, 5]$ | 1 | Matriz $[11 \times 14]$ verificada (`check_stabilizer` ok) |
| `qecc_16_5_open` | $[[16,5]]$ | $[4, 5]$ | 1 | Matriz $[11 \times 16]$ verificada (`check_stabilizer` ok) |
| `qecc_17_3_open` | $[[17,3]]$ | $[5, 6]$ | 1 | Matriz $[14 \times 17]$ verificada (`check_stabilizer` ok) |
| `qecc_18_3_open` | $[[18,3]]$ | $[5, 6]$ | 1 | Matriz $[15 \times 18]$ verificada (`check_stabilizer` ok) |
| `qecc_19_10_open` | $[[19,10]]$ | $[3, 4]$ | 1 | Matriz $[9 \times 19]$ verificada (`check_stabilizer` ok) |
| `qecc_20_2_open` | $[[20,2]]$ | $[6, 7]$ | 1 | Matriz $[18 \times 20]$ verificada (`check_stabilizer` ok) |
| `qecc_20_3_open` | $[[20,3]]$ | $[6, 7]$ | 1 | Matriz $[17 \times 20]$ verificada (`check_stabilizer` ok) |

Todos os alvos acima possuem matriz de geradores estabilizadores publicada nas tabelas de Grassl, a qual foi convertida para strings de Pauli e verificada quanto à comutação mútua e posto $n - k$ sobre GF(2) via `evobyte.qecc_verifier.check_stabilizer`.

## 3. Calibrações Embutidas

O catálogo incorpora 5 códigos de calibração conhecidos com distância exata ($d_{lo} = d_{hi}$), todos verificados com sucesso por `code_distance` e `check_stabilizer` da P179:
1. `steane_7_1_3`: Código CSS $[[7,1,3]]$ de Steane, $d = 3$ ($0.0005\text{ s}$).
2. `shor_9_1_3`: Código $[[9,1,3]]$ de Shor de 9 qubits, $d = 3$ ($0.0012\text{ s}$).
3. `five_qubit_5_1_3`: Código perfeito $[[5,1,3]]$ de Laflamme et al., $d = 3$ ($0.0003\text{ s}$).
4. `error_detect_4_2_2`: Código de detecção de erros $[[4,2,2]]$, $d = 2$ ($0.0001\text{ s}$).
5. `repetition_3_1_1`: Código de repetição com bit-flip $[[3,1,1]]$, $d = 1$ ($0.0001\text{ s}$).

## 4. Limitações e O Que Não Foi Obtido

- **Qudits / Dimensões superiores**: Apenas códigos de qubits ($q=2$, campo GF($2^2$) aditivo) foram catalogados; códigos qudits com $q \ge 3$ foram excluídos do catálogo inicial.
- **Códigos não-estabilizadores**: O formalismo limita-se a códigos estabilizadores com fases $+1$; códigos não-aditivos (CWS / não-estabilizadores) não são cobertos.
- **Regiões de $n > 20$**: Embora existam lacunas em $n > 20$, os alvos prioritários foram congelados em $n \le 20$ em razão do envelope computacional do verificador exato de distância da P179 (varredura de centralizador otimizada para $n \le 12$, e validação pontual de construções até $n = 20$).

## 5. Declaração Obrigatória de Integridade

Nenhuma cota foi presumida; todo número tem fonte snapshotada.
