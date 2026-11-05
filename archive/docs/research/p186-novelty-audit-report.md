# P186 — Relatório de Auditoria Dupla de Novidade contra Literatura Mundial

**Programa:** Descoberta na Fronteira (*P171–P190, D042*). Trilhas A, B e fundação comum.
**Fase:** P186 — Auditoria Dupla de Novidade e Prioridade contra a Literatura Mundial (Pré-Anúncio).
**Data da Auditoria:** 2026-10-25.
**Artefato de Auditoria:** [`experiments/p186-novelty-audit.json`](../../experiments/p186-novelty-audit.json).
**Veredito Geral:** `NO_ACTIVE_DISCOVERY_CLAIMS` (Nenhuma alegação ativa de novidade).
**Assinaturas Registradas:**
- **Verificador Mecânico:** `EvoByte-FrontierVerifier-v2`
- **Revisor Humano:** `human:Alexandre`

---

## 1. Contexto e Pergunta Falsificável

A fase **P186** implementa o protocolo de auditoria dupla e independente que antecede qualquer anúncio público de novidade ou descoberta científica no repositório EvoByte:

> **Pergunta Falsificável:**
> *Para cada `DISCOVERY_BEATEN` registrado, existe evidência datada e snapshotada de que (a) o objeto certificado supera a cota publicada congelada e (b) nenhuma publicação posterior (até a data da auditoria) já a superava?*

Em conformidade com a regra explícita de P186:
> *"Se nenhum `DISCOVERY_BEATEN` existir: a auditoria cobre os certificados de **empate** e os **quase-recordes** (melhores candidatos), para garantir que nenhum recorde foi perdido por erro de comparação."*

---

## 2. Declaração Literal de Veredito

> **NENHUMA ALEGAÇÃO DE NOVIDADE SOBREVIVEU:** todas as 50 metas auditadas das campanhas pré-registradas (P176, P177, P182) registraram `NULL_RESULT` e todos os quase-recordes e calibrações foram auditados com rigor, confirmando que nenhum recorde foi perdido por erro de comparação e nenhuma alegação espúria foi promovida.

---

## 3. Resumo Executivo das Campanhas Auditadas

| Campanha | Domínio | Arquivo de Entrada | Metas Auditadas | Recordes Reclamados (`DISCOVERY_BEATEN`) | Quase-Recordes / Empates Auditados | Veredito da Campanha |
|---|---|---|---|---|---|---|
| **P176** | Covering Designs $C(v, k, t)$ | `experiments/p176-covering-results.json` | 40 | 0 | 40 | `NULL_RESULT` (todas não batidas) |
| **P177** | Números Fracos de Schur $WS(k)$ | `experiments/p177-weak-schur-results.json` | 3 | 0 | 3 | `NULL_RESULT` (todas não batidas) |
| **P182** | Códigos Estabilizadores Quânticos $[[n, k, d]]$ | `experiments/p182-qecc-results.json` | 7 | 0 | 7 | `NULL_RESULT` (todas não batidas) |
| **Total** | — | — | **50** | **0** | **50** | `NO_ACTIVE_DISCOVERY_CLAIMS` |

### Totais da Auditoria:
- **Total de Alegações/Metas Auditadas:** 50
- **CONFIRMED:** 0
- **DOWNGRADED:** 0
- **NOT_APPLICABLE:** 50 (40 cobrimentos nulos, 3 Schur fraco nulos, 7 QECC nulos)

---

## 4. Auditoria B: Reconsultas Datadas da Literatura Mundial

Todas as fontes externas primárias e secundárias do catálogo congelado foram reconsultadas na data de hoje (`2026-10-25`), com snapshots brutos armazenados em `data/raw/novelty/` (ignorado pelo git) e hashes SHA-256 verificados:

| Identificador da Fonte | URL Oficial Reconsultada | Data de Acesso | SHA-256 do Snapshot | Status da Reconsulta | Comparação com Catálogo P171 Congelado |
|---|---|---|---|---|---|
| `oeis-A072842` | `https://oeis.org/search?q=id:A072842&fmt=text` | 2026-10-25 | `703ead14a0aa95a0...` | `reconsulted_ok` | Idêntico ao hash congelado de 2026-10-22 |
| `oeis-A118771` | `https://oeis.org/search?q=id:A118771&fmt=text` | 2026-10-25 | `0ab6b7a4cf9a10f5...` | `reconsulted_ok` | Idêntico ao hash congelado de 2026-10-22 |
| `oeis-A090245` | `https://oeis.org/search?q=id:A090245&fmt=text` | 2026-10-25 | `33faf08316d3fb4f...` | `reconsulted_ok` | Idêntico ao hash congelado de 2026-10-22 |
| `oeis-A030126` | `https://oeis.org/search?q=id:A030126&fmt=text` | 2026-10-25 | `6ae2bfd71096db12...` | `reconsulted_ok` | Atualizado (adicionado comentário bibliográfico sem alteração de cotas) |
| `ljcr-coverdata-459bcaf` | `https://raw.githubusercontent.com/dmgordo/LJCR/...` | 2026-10-25 | `0984bb8b4c89fe07...` | `reconsulted_ok` | Idêntico ao hash congelado de 2026-10-22 (commit pinned `459bcaf`) |

**Conclusão da Auditoria B:**
Nenhuma publicação posterior ao catálogo congelado (P171 / P180) superou as cotas de referência. As cotas congeladas permanecem o estado da arte reconhecido na literatura mundial na data da auditoria.

---

## 5. Auditoria A: Verificação dos Quase-Recordes e Sanidade de Comparação

Para garantir a ausência de falsos negativos (i.e., candidatos gerados durante as buscas que poderiam ter batido a cota congelada sem que o pipeline registrasse), o auditor analisou os melhores candidatos de cada meta:

### 5.1 Coberturas Combinatórias (P176 — 40 metas)
- Para todas as 40 metas de cobertura testadas com tamanhos $B < \text{published\_size}$, o número de subconjuntos $t$ não cobertos (`best_uncovered`) foi estritamente positivo ($\ge 1$).
- Nenhum candidato com tamanho inferior à cota publicada cobriu todos os pares/triplas.
- **Veredito:** `NOT_APPLICABLE` (ausência de descoberta; verificado que não houve falso negativo).

### 5.2 Partições de Schur Fraco (P177 — 3 metas)
- Para $k=5$, a cota congelada é $WS(5) \ge 207$. No tamanho 208, foram encontradas 14 violações monocromáticas irredutíveis.
- Para $k=6$ e $k=7$, nenhuma partição válida de tamanho superior à cota congelada foi gerada nos orçamentos pré-registrados.
- **Veredito:** `NOT_APPLICABLE` (ausência de descoberta; verificado que não houve falso negativo).

### 5.3 Códigos Estabilizadores QECC (P182 — 7 metas abertas)
- Para todas as 7 metas abertas da tabela de Grassl ($[[14,3]], [[16,5]], [[17,3]], [[18,3]], [[19,10]], [[20,2]], [[20,3]]$), os orçamentos de evolução registraram $0$ códigos com distância superior ou igual a $d_{hi}$.
- **Veredito:** `NOT_APPLICABLE` (ausência de descoberta; verificado que não houve falso negativo).

---

## 6. Verificação de Integridade dos Testes Unitários

O conjunto de testes unitários em [`tests/test_novelty_dual_audit.py`](../../tests/test_novelty_dual_audit.py) valida:
1. `test_audit_confirms_clear_record`: fixture com objeto que supera cota congelada e literatura estável resulta em `CONFIRMED`.
2. `test_audit_downgrades_stale_claim`: snapshot novo com cota superior ao objeto resulta em `DOWNGRADED` com motivo explícito.
3. `test_null_when_no_beaten`: entradas de campanhas nulas resultam em 0 `CONFIRMED` e todas `NOT_APPLICABLE`.
4. `test_every_claim_has_dated_evidence`: todas as entradas referenciam snapshot com URL, data ISO e SHA-256.
5. `test_missing_human_signature_prevents_confirmed`: proibição estrita de confirmação sem assinatura humana registrada.
6. `test_invalid_candidate_object_downgraded`: rejeição mecânica na Auditoria A caso o verificador independente aponte falha estrutural.
7. `test_cli_execution`: execução offline via CLI em sub-processo.

Tempo de execução da suíte: **0,24 s** (todos os testes $< 0,07\text{ s}$, bem abaixo do limite de $0,2\text{ s}$ por teste e $3\text{ s}$ da suíte).

---

## 7. Assinaturas Formais

Conforme a regra obrigatória de P186 (nenhum anúncio sem as duas assinaturas):

| Papel | Identidade | Status da Assinatura | Declaração |
|---|---|---|---|
| **Verificador Mecânico** | `EvoByte-FrontierVerifier-v2` | Registrado | Auditorias A e B executadas de forma determinística; 0 erros de comparação detectados. |
| **Revisor Humano** | `human:Alexandre` | Registrado | Concordância com o rebaixamento/declaração de nulidade e ausência de recordes espúrios. |

**Conclusão Final:**
A auditoria dupla foi concluída com êxito e transparência total. O repositório segue em integridade máxima para a fase P187 (Dossiê de submissão aos curadores).
