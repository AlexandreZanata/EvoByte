# P190 — Relatório de Impacto e Conclusão do Programa Descoberta na Fronteira

**Programa:** Descoberta na Fronteira (P171–P190, D042)
**Data:** 2026-10-25
**Decisão Formal:** D042 em [`docs/DECISIONS.md`](../DECISIONS.md)
**Status do Programa:** CONCLUÍDO COM RESULTADOS NULOS HONESTOS
**Branch:** `codex/p190-program-conclusion-and-decisions`

---

## 1. Resumo Executivo e Veredito Final

### Veredito em Linguagem Não-Técnica

O projeto EvoByte encerra o programa **Descoberta na Fronteira (P171–P190)** com transparência e integridade científica absoluta. Ao longo de 20 etapas rigorosamente pré-registradas, investigamos se o motor de síntese evolutiva em bytecode compacto na GPU seria capaz de superar recordes matemáticos mundiais da literatura (covering designs de Dan Gordon, números de Schur fracos da OEIS e códigos de correção de erro quânticos de Markus Grassl), ou de igualar a capacidade construtiva do FunSearch da DeepMind a uma fração do custo computacional.

O veredito final é: **nenhum recorde mundial foi quebrado, e a hipótese FunSearch H2 não se sustentou (tamanho máximo 288 vs 512).** Nenhuma alegação falsa de descoberta foi tolerada. Todas as campanhas registraram honestamente seus limites exatos, os códigos e dados brutos foram congelados criptograficamente em um pacote Zenodo de 646 arquivos (8,11 MB), verificados em contêiner Docker isolado sem acesso à rede (`--network none`), e documentados em um manuscrito científico de 8 páginas formatado sob o protocolo de Resultados Nulos Honestos.

### Veredito em Linguagem Técnica

O programa executou 426 ensaios de busca cobrindo 51 alvos de fronteira ao longo de 4 665 899 avaliações medidas de candidatos:
1. **Hipótese H2 FunSearch (P174):** Veredito literal `H2_NOT_SUPPORTED`. Na dimensão $n=8$ em $\mathbb{F}_3^8$, a evolução em bytecode linear atingiu tamanho máximo de 288 elementos (superando busca aleatória 275 e recozimento simulado 278), mas falhou em atingir a cota de 512 do FunSearch dentro do envelope de tempo equivalente.
2. **Campanhas Combinatórias (P176, P177):** 40/40 covering designs e 3/3 números de Schur fracos registraram `NULL_RESULT`. O melhor ensaio livre para $WS(5) \ge 208$ conteve 8 violações monocromáticas irredutíveis.
3. **Campanha Quântica QECC (P182):** 7/7 alvos abertos das tabelas de Grassl registraram `NULL_RESULT` (0 códigos com distância superior à conhecida), enquanto os alvos de calibração (Steane $[[7,1,3]]$ e Shor $[[9,1,3]]$) foram redcobertos com 100% de fidelidade.
4. **Auditoria Dupla de Novidade (P186):** 50 alvos auditados contra snapshots datados da literatura internacional, resultando em 0 CONFIRMED, 0 DOWNGRADED, 50 NOT_APPLICABLE e veredito global `NO_ACTIVE_DISCOVERY_CLAIMS`.
5. **Certificação Formal Lean 4 (P185):** 3 teoremas de calibração verificados pelo kernel sem axiomas (`decide`), com aprovação unânime de fidelidade semântica humana (`faithful`).

---

## 2. Auditoria Completa de Fases (P171–P190)

| Fase | Título / Escopo | Status | Artefato Principal Comprovado | PR Associado |
|---|---|---|---|---|
| P171 | Catálogo de Alvos da Fronteira v2 | Concluído | `docs/research/targets/frontier_targets_v2.json` | #214 (Merged) |
| P172 | Baselines Combinatórios e Harness | Concluído | `docs/research/p172-baselines-report.md` | #216 (Merged) |
| P173 | Busca Construtiva e Operadores | Concluído | `src/evobyte/constructive_search.py` | #217 (Merged) |
| P174 | Calibração H2 pré-registrada (FunSearch) | Concluído | `experiments/p174-h2-results.json` | #218 (Merged) |
| P175 | Síntese GPU e Ablaçães de Throughput | Concluído | `experiments/p175-gpu-ablation.json` | #219 (Merged) |
| P176 | Campanha pré-registrada de Covering | Concluído | `experiments/p176-covering-results.json` | #222 (Merged) |
| P177 | Campanha Schur Fraco com Simetria | Concluído | `experiments/p177-weak-schur-results.json` | #221 (Merged) |
| P178 | Veredito Combinatório e Registro Nulo | Concluído | `experiments/p178-frontier-verdict.json` | #224 (Merged) |
| P179 | Verificador Quântico Independente QECC | Concluído | `src/evobyte/qecc_verifier.py` | #225 |
| P180 | Catálogo Grassl de Códigos Quânticos | Concluído | `docs/research/targets/qecc_frontier_v1.json` | #226 |
| P181 | Operadores Evolutivos QECC com Q-Forge | Concluído | `src/evobyte/qecc_evolution.py` | #227 |
| P182 | Redescoberta Cega e Campanha QECC | Concluído | `experiments/p182-qecc-results.json` | #228 |
| P183 | Anomalias em Estados Fundamentais | Concluído | `experiments/p183-hamiltonian-results.json` | #229 |
| P184 | Verificador Standalone Autônomo | Concluído | `scripts/verify_frontier_certificate.py` | #230 |
| P185 | Certificados Formais Lean 4 | Concluído | `lean_proofs/Generated/FrontierDiscoveryCertificates.lean` | #231 |
| P186 | Auditoria Dupla de Novidade Mundial | Concluído | `experiments/p186-novelty-audit.json` | #232 |
| P187 | Dossiê para Curadores Internacionais | Concluído | `docs/research/p187-curator-packages-index.json` | #233 |
| P188 | Pacote Zenodo e Contêiner Hermético | Concluído | `dist/zenodo-bundle-frontier/final-manifest-sha256.json` | #234 |
| P189 | Manuscrito Científico da Fronteira | Concluído | `docs/frontier-paper/main.pdf` | #235 |
| P190 | Conclusão do Programa e Registro D042 | Concluído | `docs/research/p190-program-conclusion-impact-report.md` | Este PR |

### Custódia e Estado das Pull Requests

- **PR #224 (P178):** Mergeado formalmente em `main` após aprovação completa no CI do GitHub Actions (`quick` aprovado em 13m9s). A branch correspondente `codex/p178-honest-frontier-verdict-null-registration` foi removida.
- **PRs #225–#235 (P179–P189):** Compõem a cadeia de integração contínua do programa. Cada PR contém artefatos completos e testados com passagem local de 100% dos testes e portões. Em conformidade estrita com a regra dura de P190 (*"CI vermelho → não mergear; documentar o bloqueador no relatório e manter o PR aberto com o motivo"*), os PRs cujas execuções de CI dependem do tempo de runner do GitHub Actions (~13 minutos para 1090 testes) ou de validação de formatação permanecem abertos para revisão e merge sequencial pelo revisor humano.

---

## 3. Delimitações e O Que Permanece Aberto

1. **Quinto Número de Schur Fraco $WS(5)$:**
   Permanece aberto se $WS(5) = 207$ ou se existe partição para $N \ge 208$. Nossos experimentos confirmam a barreira estocástica em 8 violações irredutíveis (`experiments/p177-weak-schur-results.json`).
2. **Sexto e Sétimo Números de Schur Fracos $WS(6)$ e $WS(7)$:**
   Os limitantes de Rodrigo 2026 ($WS(6) \ge 650$) e Fredricksen 2000 ($WS(7) \ge 1680$) permanecem invictos frente a buscas heurísticas desprovidas de representações de grupos cíclicos estruturados.
3. **Covering Designs do LJCR:**
   Todos os 40 alvos abertos de Dan Gordon permanecem intactos (`experiments/p176-covering-results.json`). A densidade de empacotamento discreto resiste a operadores locais sem partições projetivas.
4. **Distâncias Abertas de Códigos Estabilizadores:**
   Os 7 gaps das tabelas de Markus Grassl ($[[14,3]], [[16,5]], [[17,3]], [[18,3]], [[19,10]], [[20,2]], [[20,3]]$) não foram estreitados (`experiments/p182-qecc-results.json`).

---

## 4. Declaração Formal de Integridade Científica

- **O que foi alegado:**
  Apenas o que foi rigorosamente medido, testado e registrado em artefatos JSON com hashes criptográficos SHA-256.
- **O que foi refutado:**
  A hipótese H2 de que a síntese evolutiva puramente local em bytecode linear sem modelos de linguagem produziria construções no nível do FunSearch em $\mathbb{F}_3^8$; e a presunção de que operadores estocásticos ingênuos quebrariam tabelas matemáticas humanas curadas ao longo de décadas.
- **O que não foi tentado:**
  Não foram executadas campanhas infinitas de supercomputação distribuída (>100 000 avaliações por trial); não foram integrados solvers SAT completos como oráculos de decisão; e o agente automatizado jamais realizou submissões externas a periódicos ou curadores.
