# P187 — Dossiê Formal de Submissão aos Curadores Externos

**Programa:** Descoberta na Fronteira (*P171–P190, D042*). Trilhas A, B e fundação comum.
**Fase:** P187 — Dossiê de Submissão aos Curadores Externos (Selo Final).
**Data:** 2026-10-25.
**Índice Rastreado:** [`docs/research/p187-curator-packages-index.json`](p187-curator-packages-index.json).
**Auditoria de Referência:** [`experiments/p186-novelty-audit.json`](../../experiments/p186-novelty-audit.json).
**Status dos Pacotes:** `pending_human_submission`.

---

## 1. Declaração Mandatória de Não-Submissão por Agentes

> **Declaração de Integridade:**
> Nenhuma submissão foi enviada por agente; todo envio é ato humano posterior e registrado aqui.
> O agente autônomo apenas compila e audita os pacotes mecânicos com transparência total. O contato externo, submissão formal e acompanhamento editorial são prerrogativas exclusivas do autor correspondente humano.

---

## 2. Resumo dos Pacotes Compilados

Todos os pacotes foram gerados pelo script [`scripts/build_curator_package.py`](../../scripts/build_curator_package.py) e estão armazenados localmente em `dist/curator-submissions/` (ignorado pelo git; apenas o índice de hashes é versionado):

| Curador / Canal | Canal Oficial Público | Veredito P186 | Arquivos no Pacote | Status Inicial |
|---|---|---|---|---|
| **Dan Gordon** (`ljcr_gordon`) | `https://raw.githubusercontent.com/dmgordo/LJCR/` | `NULL_RESULT` (0 CONFIRMED, 40 metas) | 6 arquivos (`README`, `null-result-notice`, `verifier`, `reproduce.sh`, 2 minutas) | `pending_human_submission` |
| **Markus Grassl** (`grassl_codetables`) | `http://www.codetables.de/` | `NULL_RESULT` (0 CONFIRMED, 7 metas) | 6 arquivos (`README`, `null-result-notice`, `verifier`, `reproduce.sh`, 2 minutas) | `pending_human_submission` |
| **OEIS Editors** (`oeis_editors`) | `https://oeis.org/` | `NULL_RESULT` (0 CONFIRMED, 3 metas) | 6 arquivos (`README`, `null-result-notice`, `verifier`, `reproduce.sh`, 2 minutas) | `pending_human_submission` |

---

## 3. Minutas Formais de Comunicação

### 3.1 Curador 1: Dan Gordon (La Jolla Covering Repository — Covering Designs)

#### Versão Markdown (`submission-letter.md`):
```markdown
# Submission Letter — Dan Gordon (LJCR Covering Tables)

**Recipient:** Dan Gordon, Maintainer, La Jolla Covering Repository
**Author:** Alexandre Zanata (Corresponding Author, EvoByte Project)
**Date:** 2026-10-25
**Subject:** External confirmation and null-result notification for LJCR covering targets
**Audit Reference:** `experiments/p186-novelty-audit.json` (CONFIRMED: 0)

Dear Dr. Gordon,

We are writing to share the results of an algorithmic verification and search campaign conducted
by the EvoByte project on covering designs C(v, k, t).

Using your published covering tables (snapshot commit 459bcaf), we evaluated 40 active
parameter sets using heuristic and evolutionary search algorithms under strict pre-registered
computational budgets.

### What is Reported:
1. **Resilience of LJCR Bounds:** In all 40 investigated targets, our algorithms failed to find
   any covering design smaller than your published upper bounds (zero broken bounds; all targets
   registered NULL_RESULT).
2. **Independent Verifier:** We provide a zero-dependency Python verifier
   (`verify_frontier_certificate.py`) implementing colexicographical ranking over the combinatorial
   number system.

### What is NOT Claimed:
- We do NOT claim any new record or smaller covering design.
- P186 audit verdict confirms: CONFIRMED: 0.
- No modifications to the LJCR tables are required or requested.

This dossier is provided solely as an independent confirmation of the strength of the published
LJCR bounds.

Sincerely,
Alexandre Zanata
Corresponding Author, EvoByte Project
```

#### Versão Texto Puro (`submission-letter.txt`):
```text
Submission Letter — Dan Gordon (LJCR Covering Tables)

Recipient: Dan Gordon, Maintainer, La Jolla Covering Repository
Author: Alexandre Zanata (Corresponding Author, EvoByte Project)
Date: 2026-10-25
Subject: External confirmation and null-result notification for LJCR covering targets
Audit Reference: experiments/p186-novelty-audit.json (CONFIRMED: 0)

Dear Dr. Gordon,

We are writing to share the results of an algorithmic verification and search campaign conducted
by the EvoByte project on covering designs C(v, k, t).

Using your published covering tables (snapshot commit 459bcaf), we evaluated 40 active
parameter sets using heuristic and evolutionary search algorithms under strict pre-registered
computational budgets.

What is Reported:
1. Resilience of LJCR Bounds: In all 40 investigated targets, our algorithms failed to find
   any covering design smaller than your published upper bounds (zero broken bounds; all targets
   registered NULL_RESULT).
2. Independent Verifier: We provide a zero-dependency Python verifier
   (verify_frontier_certificate.py) implementing colexicographical ranking over the combinatorial
   number system.

What is NOT Claimed:
- We do NOT claim any new record or smaller covering design.
- P186 audit verdict confirms: CONFIRMED: 0.
- No modifications to the LJCR tables are required or requested.

This dossier is provided solely as an independent confirmation of the strength of the published
LJCR bounds.

Sincerely,
Alexandre Zanata
Corresponding Author, EvoByte Project
```

---

### 3.2 Curador 2: Markus Grassl (codetables.de — Códigos Quânticos QECC)

#### Versão Markdown (`submission-letter.md`):
```markdown
# Submission Letter — Markus Grassl (codetables.de)

**Recipient:** Markus Grassl, Maintainer, codetables.de
**Author:** Alexandre Zanata (Corresponding Author, EvoByte Project)
**Date:** 2026-10-25
**Subject:** External verification report on open quantum code parameters
**Audit Reference:** `experiments/p186-novelty-audit.json` (CONFIRMED: 0)

Dear Dr. Grassl,

We are writing to share independent verification data from the EvoByte evolutionary search
campaign on quantum stabilizer codes [[n, k, d]].

Focusing on 7 open targets from your tables ([[14,3]], [[16,5]], [[17,3]], [[18,3]], [[19,10]],
[[20,2]], [[20,3]]), our resident GPU evolution pipeline explored candidate stabilizer spaces
under pre-registered mutation and selection budgets.

### What is Reported:
1. **Bounds Stability:** All 7 open targets resulted in NULL_RESULT. No stabilizer configuration
   reached the upper bound d_hi, reaffirming the tightness of your published bounds.
2. **Standalone Verification:** Calibration codes ([[7,1,3]], [[9,1,3]], [[5,1,3]]) were verified
   using pure standard-library symplectic weight search.

### What is NOT Claimed:
- We do NOT claim any new record code or distance improvement.
- P186 audit verdict confirms: CONFIRMED: 0.
- No updates to codetables.de are requested.

This dossier is submitted solely as an external confirmation of your table bounds.

Sincerely,
Alexandre Zanata
Corresponding Author, EvoByte Project
```

#### Versão Texto Puro (`submission-letter.txt`):
```text
Submission Letter — Markus Grassl (codetables.de)

Recipient: Markus Grassl, Maintainer, codetables.de
Author: Alexandre Zanata (Corresponding Author, EvoByte Project)
Date: 2026-10-25
Subject: External verification report on open quantum code parameters
Audit Reference: experiments/p186-novelty-audit.json (CONFIRMED: 0)

Dear Dr. Grassl,

We are writing to share independent verification data from the EvoByte evolutionary search
campaign on quantum stabilizer codes [[n, k, d]].

Focusing on 7 open targets from your tables ([[14,3]], [[16,5]], [[17,3]], [[18,3]], [[19,10]],
[[20,2]], [[20,3]]), our resident GPU evolution pipeline explored candidate stabilizer spaces
under pre-registered mutation and selection budgets.

What is Reported:
1. Bounds Stability: All 7 open targets resulted in NULL_RESULT. No stabilizer configuration
   reached the upper bound d_hi, reaffirming the tightness of your published bounds.
2. Standalone Verification: Calibration codes ([[7,1,3]], [[9,1,3]], [[5,1,3]]) were verified
   using pure standard-library symplectic weight search.

What is NOT Claimed:
- We do NOT claim any new record code or distance improvement.
- P186 audit verdict confirms: CONFIRMED: 0.
- No updates to codetables.de are requested.

This dossier is submitted solely as an external confirmation of your table bounds.

Sincerely,
Alexandre Zanata
Corresponding Author, EvoByte Project
```

---

### 3.3 Curador 3: OEIS Editorial Board (Sequências Inteiras: A072842, A118771, A090245, A030126)

#### Versão Markdown (`submission-letter.md`):
```markdown
# Submission Letter — OEIS Editorial Board

**Recipient:** The Editorial Board, Online Encyclopedia of Integer Sequences (OEIS)
**Author:** Alexandre Zanata (Corresponding Author, EvoByte Project)
**Date:** 2026-10-25
**Subject:** Verification and null-result notes on Weak Schur numbers (A072842, A118771)
**Audit Reference:** `experiments/p186-novelty-audit.json` (CONFIRMED: 0)

Dear OEIS Editors,

We are submitting an independent verification report regarding sequence A072842 and A118771
(Weak Schur numbers WS(k)).

Using GPU-accelerated heuristic search and symmetric partition checking, the EvoByte project
evaluated the open frontiers at k=5 and k=6.

### What is Reported:
1. **Confirmation of Published Bounds:** In our pre-registered trials for k=5, partitioned
   colorings at size 208 persistently encountered >= 14 weak Schur violations, corroborating
   the stability of Rowley's 2025 bound WS(5) >= 207.
2. **Standalone Verifier:** We provide a verified Python script checking weak sum-free partitions
   according to OEIS definitions.

### What is NOT Claimed:
- We do NOT claim any new record term or sequence modification.
- P186 audit verdict confirms: CONFIRMED: 0.
- No new sequence entries or edits are requested.

This communication is provided for archival documentation and independent verification purposes.

Sincerely,
Alexandre Zanata
Corresponding Author, EvoByte Project
```

#### Versão Texto Puro (`submission-letter.txt`):
```text
Submission Letter — OEIS Editorial Board

Recipient: The Editorial Board, Online Encyclopedia of Integer Sequences (OEIS)
Author: Alexandre Zanata (Corresponding Author, EvoByte Project)
Date: 2026-10-25
Subject: Verification and null-result notes on Weak Schur numbers (A072842, A118771)
Audit Reference: experiments/p186-novelty-audit.json (CONFIRMED: 0)

Dear OEIS Editors,

We are submitting an independent verification report regarding sequence A072842 and A118771
(Weak Schur numbers WS(k)).

Using GPU-accelerated heuristic search and symmetric partition checking, the EvoByte project
evaluated the open frontiers at k=5 and k=6.

What is Reported:
1. Confirmation of Published Bounds: In our pre-registered trials for k=5, partitioned
   colorings at size 208 persistently encountered >= 14 weak Schur violations, corroborating
   the stability of Rowley's 2025 bound WS(5) >= 207.
2. Standalone Verifier: We provide a verified Python script checking weak sum-free partitions
   according to OEIS definitions.

What is NOT Claimed:
- We do NOT claim any new record term or sequence modification.
- P186 audit verdict confirms: CONFIRMED: 0.
- No new sequence entries or edits are requested.

This communication is provided for archival documentation and independent verification purposes.

Sincerely,
Alexandre Zanata
Corresponding Author, EvoByte Project
```

---

## 4. Protocolo de Acompanhamento (Follow-up Protocol)

1. **Responsável pela Submissão:**
   O autor correspondente humano (`Alexandre Zanata`). O envio é estritamente manual, utilizando os canais públicos oficiais de cada curador (formulários web ou repositórios públicos).

2. **Cronograma de Reconfirmação:**
   - **T+0:** Submissão formal realizada pelo autor correspondente.
   - **T+30 dias:** Verificação de confirmação de recebimento pelo curador.
   - **T+60 dias:** Follow-up educado se não houver resposta, ou registro de desfecho.

3. **Registro de Resposta e Atualização do Índice:**
   Qualquer comunicação ou desfecho recebido será registrado publicamente em `docs/research/p187-curator-packages-index.json`:
   - `status: pending_human_submission` $\to$ `status: submitted_by_human` (ao enviar).
   - `status: submitted_by_human` $\to$ `status: acknowledged_by_curator` (ao acusar recebimento).
   - `status: acknowledged_by_curator` $\to$ `status: confirmed_null_published` / `status: closed`.
   - Cada transição de estado registra timestamp UTC, canal utilizado e hash SHA-256 do comprovante de envio/resposta.

4. **Integridade da Ciência Aberta:**
   Como todas as campanhas de busca da fronteira (P176, P177, P182) concluíram com `NULL_RESULT`, a submissão transparente de resultados negativos e confirmações independentes consolida a integridade do método científico e previne desperdício de recursos por outros grupos de pesquisa.
