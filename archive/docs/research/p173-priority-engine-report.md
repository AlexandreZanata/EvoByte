# P173 — Relatório do Motor Construtivo em Bytecode e Prioridades Sintetizadas

**Data:** 2026-10-22
**Status:** Concluído com evidência empírica
**Fase:** P173 — Descoberta na Fronteira (D042)
**Alvo de validação:** Construção determinística do cubo $\{0,1\}^3$ em $\mathbb{F}_3^3$

---

## 1. Resumo Executivo

A fase P173 implementa a fundação da Trilha B (Hipótese H2: síntese construtiva em bytecode comparável ao FunSearch). Foram desenvolvidos:
1. **Evolução da ISA (v0 $\to$ v1):** Bump seguro de `OPCODE_VERSION = 1` com adição dos opcodes `0x10` (`CTX`) e `0x11` (`FEAT`), preservando 100% de compatibilidade retroativa com programas e checkpoints v0.
2. **Avaliador de Prioridade (`evaluate_priority`):** Executa programas v1 carregando feições do elemento nos registradores $r_0..r_6$, zerando $r_7$ e retornando o escalar de prioridade $r_7$.
3. **Construtor Guloso Determinístico (`greedy_construct`):** Construtor sem dependência de gerador pseudo-aleatório interno, operando por seleção gulosa de candidatos de maior prioridade com critério determinístico de desempate por menor índice.
4. **Reprodução Instantânea do Cubo:** O construtor montou o 8-cap $\{0,1\}^3$ em $\mathbb{F}_3^3$ em **0,00011 s** (188 avaliações de prioridade), respeitando estritamente a restrição de ausência de triplas colineares com margem de ~900× sobre o teto de 0,1 s.

---

## 2. Evolução da Tabela de Opcodes (v0 $\to$ v1)

A versão v1 da ISA do EvoByte é um superset estrito da v0. Nenhum opcode v0 foi renumerado ou modificado:

| Opcode | Mnemônico | Operandos | Semântica | Versão |
|---|---|---|---|---|
| `0x00` | `NOP` | — | Sem operação | v0 |
| `0x01` | `ADD` | `dst, a, b` | $r_{dst} = r_a + r_b$ | v0 |
| `0x02` | `SUB` | `dst, a, b` | $r_{dst} = r_a - r_b$ | v0 |
| `0x03` | `MUL` | `dst, a, b` | $r_{dst} = r_a \cdot r_b$ | v0 |
| `0x04` | `DIV` | `dst, a, b` | $r_{dst} = r_a / r_b$ (protegido contra zero) | v0 |
| `0x05` | `SIN` | `dst, a, _` | $r_{dst} = \sin(r_a \pmod{2\pi})$ | v0 |
| `0x06` | `COS` | `dst, a, _` | $r_{dst} = \cos(r_a \pmod{2\pi})$ | v0 |
| `0x07` | `EXP` | `dst, a, _` | $r_{dst} = \exp(r_a)$ (clampeado em $[-20, 20]$) | v0 |
| `0x08` | `LOG` | `dst, a, _` | $r_{dst} = \log(\|r_a\|)$ (protegido contra zero) | v0 |
| `0x09` | `POW` | `dst, a, b` | $r_{dst} = \|r_a\|^{[r_b]_{-6}^6}$ | v0 |
| `0x0A` | `ABS` | `dst, a, _` | $r_{dst} = \|r_a\|$ | v0 |
| `0x0B` | `SQRT` | `dst, a, _` | $r_{dst} = \sqrt{\|r_a\|}$ | v0 |
| `0x0C` | `NEG` | `dst, a, _` | $r_{dst} = -r_a$ | v0 |
| `0x0D` | `MIN` | `dst, a, b` | $r_{dst} = \min(r_a, r_b)$ | v0 |
| `0x0E` | `MAX` | `dst, a, b` | $r_{dst} = \max(r_a, r_b)$ | v0 |
| `0x0F` | `CSEL` | `dst, a, b` | $r_{dst} = r_a + \text{bank}[b \ \& \ 0x0F]$ | v0 |
| `0x10` | `CTX` | `dst, _, b` | $r_{dst} = \text{context}[b \ \& \ 0x0F]$ (0.0 se fora de limites) | **v1** |
| `0x11` | `FEAT` | `dst, _, b` | $r_{dst} = \text{features}[b \ \& \ 0x0F]$ (0.0 se fora de limites) | **v1** |

---

## 3. Garantias de Compatibilidade Retroativa

1. **Golden Test v0:** O programa v0 `ADD r7, r0, r1` executado sobre $(x_0=3.5, x_1=2.25)$ produz o resultado exato bit-idêntico de $5.75$ sem ativação de flags de invalidação.
2. **Validador Estático (`is_valid`):** Programas compostos exclusivamente por opcodes `0x00–0x0F` continuam sendo integralmente aprovados sob `is_valid`. Os novos opcodes `0x10` e `0x11` são classificados como não-arriscados (resfriam a cadeia de operações de domínio sensível).
3. **Persistência e Checkpoints:** `src/evobyte/archive.py::load_checkpoint` foi parametrizado para aceitar estados com `opcode_version \in {0, 1}`, garantindo que artefatos salvos em campanhas anteriores permaneçam legíveis e executáveis.
4. **Suíte Completa:** Todos os 1020 testes unitários do repositório foram executados e aprovados sem regressões.
5. **Superset v1 nos caminhos GPU/lote:** `vm_torch` (batch, single, population), `cascade` (filtro S0), `grammar.batch_is_valid_torch` e `resident.gpu_mutate` aceitam `0x00–0x11`; `evolution.STRUCTURED_OP_RATIOS` estendido com massa 0,01 para `CTX`/`FEAT` (distribuição v0 preservada a menos de renormalização); perfil compacto P49 congelado em `opcode_version 0` (válido sob v1 via `validate_compact_candidate` que aceita `{0, 1}`).

---

## 4. Medições de Desempenho e Corretude

| Teste | Descrição | Resultado | Tempo Medido | Limite |
|---|---|---|---|---|
| `test_opcode_version_bumped_and_v0_compatible` | Golden test v0 e leitura de checkpoints | Aprovado | < 0,005 s | 0,2 s |
| `test_ctx_feat_opcodes_execute` | Leitura de CTX/FEAT e rejeição de opcode 0x12 | Aprovado | < 0,005 s | 0,2 s |
| `test_priority_scores_cube_statically` | Ordenação bit-idêntica entre Python e Bytecode | Aprovado | < 0,005 s | 0,2 s |
| `test_greedy_builds_cube_instant` | Construção de $\{0,1\}^3$ (8 pontos) em $\mathbb{F}_3^3$ | Aprovado | 0,00011 s | 0,1 s |
| `test_greedy_never_adds_infeasible` | Rejeição estrita de candidatos inviáveis | Aprovado | < 0,005 s | 0,2 s |

---

## 5. Limitações e Próximos Passos

- **Escopo desta fase:** O construtor opera em CPU puro de forma puramente determinística.
- **Evolução de Prioridades (P174):** A busca e mutação de programas de prioridade que descubram soluções sem heurística humana pré-definida é o escopo da fase P174.
- **Aceleração em GPU (P175):** O cascateamento e paralelização massiva da construção em GPU serão endereçados na fase P175.
