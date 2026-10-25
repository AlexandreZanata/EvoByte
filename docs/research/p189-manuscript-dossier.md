# P189 — Dossiê do Manuscrito Científico da Fronteira

**Fase:** P189 — Manuscrito científico: a descoberta inédita ou o avanço metodológico H2
**Programa:** Descoberta na Fronteira (P171–P190, D042)
**Data:** 2026-10-25
**Tipo Declarado do Manuscrito:** `nulos honestos`
**Status de Revisão Humana:** `human_review: pending`
**PDF Gerado:** [`docs/frontier-paper/main.pdf`](file:///home/iiii/PESSOAL-PROJETOS-ALEXANDRE/EvoByte/docs/frontier-paper/main.pdf) (8 páginas, 250 537 bytes)

---

## 1. Decisão e Justificativa do Tipo de Manuscrito

A decisão do tipo de manuscrito segue rigorosamente a regra programática prescrita em `docs/phases/P189-frontier-discovery-manuscript.md` (§ Passo 1):

> Tipo do manuscrito = **descoberta** se algum `BEATEN` + `CONFIRMED` P186; senão **H2** se veredito literal `H2_SUPPORTED`; senão **nulos honestos**. Registrar a decisão e seguir — sem reclassificar depois.

### Vereditos Literais Coletados

| Campanha / Hipótese | Arquivo de Origem | Veredito Literal | Descobertas / Recordes |
|---|---|---|---|
| Covering Designs (P176) | `experiments/p176-covering-results.json` | `verdict_counts: {"DISCOVERY_BEATEN": 0, "NULL_RESULT": 40}` | 0 |
| Weak Schur Numbers (P177) | `experiments/p177-weak-schur-results.json` | `verdict_counts: {"DISCOVERY_BEATEN": 0, "NULL_RESULT": 3}` | 0 |
| Quantum Codes QECC (P182) | `experiments/p182-qecc-results.json` | `campaign_status: "NULL_RESULT"`, `total_records_discovered: 0` | 0 |
| Hipótese H2 FunSearch (P174) | `experiments/p174-h2-results.json` | `verdict: "H2_NOT_SUPPORTED"` | 0 (tamanho 288 vs 512) |
| Auditoria Dupla de Novidade (P186) | `experiments/p186-novelty-audit.json` | `overall_verdict: "NO_ACTIVE_DISCOVERY_CLAIMS"`, `confirmed: 0` | 0 |

### Conclusão Vinculante

Como `CONFIRMED == 0` na auditoria P186 e o veredito literal de H2 é `H2_NOT_SUPPORTED`, o manuscrito é **estritamente classificado como `nulos honestos` (Honest Null Results)**. Qualquer alegação de quebra de recorde ou descoberta positiva violaria diretamente o código deontológico de `AGENTS.md`.

---

## 2. Rastreabilidade Exata de Números (Número $\to$ JSON + Chave)

Todos os números citados no manuscrito LaTeX ([`main.tex`](file:///home/iiii/PESSOAL-PROJETOS-ALEXANDRE/EvoByte/docs/frontier-paper/main.tex)) derivam de chaves exatas em arquivos JSON versionados:

| Item / Número no Manuscrito | Contexto no Texto | Arquivo JSON de Origem | Chave ou Expressão Exata |
|---|---|---|---|
| `288` | Tamanho máximo cap set (Bytecode) | `experiments/p174-h2-results.json` | `max_bytecode` |
| `275` | Tamanho máximo cap set (Random) | `experiments/p174-h2-results.json` | `max_random` |
| `278` | Tamanho máximo cap set (SA) | `experiments/p174-h2-results.json` | `max_sa` |
| `219.0` | Média de avaliações (Bytecode) | `experiments/p174-h2-results.json` | `sum(t['evaluations'] for t in trials if algo=='Bytecode') / 3` |
| `1947.0` | Média de avaliações (Random) | `experiments/p174-h2-results.json` | `sum(t['evaluations'] for t in trials if algo=='Random') / 3` |
| `1881` | Média de avaliações (SA) | `experiments/p174-h2-results.json` | `round(sum(t['evaluations'] for t in trials if algo=='SA') / 3)` |
| `9` | Ensaios H2 Cap Set | `experiments/p174-h2-results.json` | `len(trials)` |
| `12,140` | Avaliações medidas na calibração H2 | `experiments/p174-h2-results.json` | `sum(t['evaluations'] for t in trials)` |
| `540.72 s` | Tempo total de execução H2 | `experiments/p174-h2-results.json` | `sum(t['elapsed_sec'] for t in trials)` |
| `1.52x` | Speedup GPU vs CPU na cascata S0-S3 | `experiments/p175-gpu-ablation.json` | `speedup` ($1.51888...$) |
| `0.0559 s` | Tempo GPU para 2 000 avaliações | `experiments/p175-gpu-ablation.json` | `gpu_sec` |
| `0.0850 s` | Tempo CPU para 2 000 avaliações | `experiments/p175-gpu-ablation.json` | `cpu_sec` |
| `2,000` | Amostra de avaliações no ablation GPU | `experiments/p175-gpu-ablation.json` | `n` |
| `40` | Alvos na campanha de Covering | `experiments/p176-covering-results.json` | `len(targets)` |
| `360` | Ensaios na campanha de Covering | `experiments/p176-covering-checkpoint.json` | `len(completed)` |
| `1,958,802` | Avaliações medidas na campanha de Covering | `experiments/p176-covering-checkpoint.json` | `sum(t['evaluations'] for t in completed.values())` |
| `824.41 s` | Tempo de busca na campanha de Covering | `experiments/p176-covering-checkpoint.json` | `sum(t['elapsed_sec'] for t in completed.values())` |
| `0` | Recordes batidos em Covering | `experiments/p176-covering-results.json` | `verdict_counts.DISCOVERY_BEATEN` |
| `40` | Resultados nulos em Covering | `experiments/p176-covering-results.json` | `verdict_counts.NULL_RESULT` |
| `3` | Alvos na campanha Weak Schur | `experiments/p177-weak-schur-results.json` | `len(targets)` |
| `36` | Ensaios na campanha Weak Schur | `experiments/p177-weak-schur-checkpoint.json` | `len(completed)` |
| `2,693,907` | Avaliações medidas em Weak Schur | `experiments/p177-weak-schur-checkpoint.json` | `sum(t['evaluations'] for t in completed.values())` |
| `246.86 s` | Tempo de busca em Weak Schur | `experiments/p177-weak-schur-checkpoint.json` | `sum(t['elapsed_sec'] for t in completed.values())` |
| `8` | Menor nº violações para $WS(5) \ge 208$ | `experiments/p177-weak-schur-results.json` | `targets[0]['best_violations']` |
| `40` | Menor nº violações para $WS(6) \ge 651$ | `experiments/p177-weak-schur-results.json` | `targets[1]['best_violations']` |
| `454` | Menor nº violações para $WS(7) \ge 2147$ | `experiments/p177-weak-schur-results.json` | `targets[2]['best_violations']` |
| `0` | Recordes batidos em Weak Schur | `experiments/p177-weak-schur-results.json` | `verdict_counts.DISCOVERY_BEATEN` |
| `3` | Resultados nulos em Weak Schur | `experiments/p177-weak-schur-results.json` | `verdict_counts.NULL_RESULT` |
| `7` | Alvos abertos na campanha QECC | `experiments/p182-qecc-results.json` | `len(target_verdicts)` |
| `21` | Ensaios na campanha QECC | `experiments/p182-qecc-results.json` | `len(campaign_runs)` |
| `1,050` | Avaliações medidas em QECC | `experiments/p182-qecc-results.json` | `sum(r['evaluations'] for r in campaign_runs)` |
| `87.45 s` | Tempo decorrido na campanha QECC | `experiments/p182-qecc-results.json` | `sum(r['elapsed_seconds'] for r in campaign_runs)` |
| `4` | Ensaios de calibração QECC | `experiments/p182-qecc-results.json` | `len(calibration_runs)` |
| `80` | Avaliações de calibração QECC | `experiments/p182-qecc-results.json` | `sum(r['evaluations'] for r in calibration_runs)` |
| `0.06 s` | Tempo de calibração QECC | `experiments/p182-qecc-results.json` | `sum(r['elapsed_seconds'] for r in calibration_runs)` |
| `0` | Recordes batidos em QECC | `experiments/p182-qecc-results.json` | `total_records_discovered` |
| `51` | Total consolidado de alvos investigados | Todas as campanhas somadas | $1 + 40 + 3 + 7 = 51$ |
| `426` | Total consolidado de ensaios de campanha | Todas as campanhas somadas | $9 + 360 + 36 + 21 = 426$ |
| `4,665,899` | Total consolidado de avaliações medidas | Todas as campanhas somadas | $12140 + 1958802 + 2693907 + 1050 = 4665899$ |
| `0` | Total consolidado de recordes batidos | Todas as campanhas somadas | $0 + 0 + 0 + 0 = 0$ |
| `3` | Teoremas de calibração Lean 4 verificados | `lean_proofs/Generated/FrontierDiscoveryCertificates.lean` | 3 declarações provadas por `decide` |
| `3/3` | Revisões humanas de fidelidade formal aprovadas | `docs/research/lean-fidelity-reviews.json` | `count(reviews == 'faithful') == 3` |
| `50` | Alegações auditadas na auditoria de novidade | `experiments/p186-novelty-audit.json` | `summary.total_claims_audited` |
| `0` | Alegações confirmadas como recorde inédito | `experiments/p186-novelty-audit.json` | `summary.confirmed` |
| `50` | Alegações arquivadas como not applicable | `experiments/p186-novelty-audit.json` | `summary.not_applicable` |
| `3` | Pacotes para curadores compilados | `docs/research/p187-curator-packages-index.json` | `len(packages)` |
| `18` | Arquivos auditados nos pacotes de curadores | `docs/research/p187-curator-packages-index.json` | `total_files` |
| `646` | Arquivos no pacote arquival Zenodo | `dist/zenodo-bundle-frontier/` | Relatório P188 / Manifesto Zenodo |
| `8.11 MB` | Tamanho descomprimido do pacote Zenodo | `dist/zenodo-bundle-frontier/` | Relatório P188 |
| `1.85 MB` | Tamanho do tarball comprimido | `dist/zenodo-bundle-frontier/` | Relatório P188 |
| `17/17` | Testes unitários no container offline | Execução Docker `--network none` | Relatório P188 |

---

## 3. Deliberação de Omissões e Escopo

As seguintes omissões foram aplicadas deliberadamente no manuscrito:

1. **Ausência de Alegações Positivas de Descoberta:**
   Nenhum texto no manuscrito insinua ou reivindica superação de limites conhecidos nas tabelas de Gordon, Grassl ou OEIS. As tabelas da literatura permanecem 100% não superadas pelos métodos testados.

2. **Ausência de Extrapolações Teóricas Não-Medidas:**
   O manuscrito não afirma que é "impossível" quebrar as cotas com mais computação; limita-se estritamente a descrever que, sob o envelope de busca pré-registrado e os operadores heurísticos avaliados, nenhuma solução válida com custo inferior foi obtida.

3. **Ausência de Submissão por Agentes Automatizados:**
   O agente executor não submete o manuscrito a periódicos, servidores de preprints (arXiv) ou plataformas de publicação. O manuscrito é mantido com status `human_review: pending` para avaliação pelo autor humano.

---

## 4. Declaração de Revisão Humana

```yaml
human_review: pending
manuscript_path: docs/frontier-paper/main.pdf
manuscript_sha256: c60b3d8d05cef55f7f4d8812768240aa8c11d0d8266136c035d14f324c64884b
reviewer: Alexandre Zanata
role: Corresponding Author
submission_decision: pending_human_review
```
