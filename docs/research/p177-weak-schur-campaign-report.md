# P177 — Relatório da campanha de Schur fraco com simetria cíclica

**Data:** 2026-10-24
**Fase:** P177 — Descoberta na Fronteira (D042)

## 1. Resumo executivo

- **Alvos:** `weak_schur_5/6/7` (`role = record`); tentativa = `best_known_value + 1` inteiros (208, 651, 2147) em todos, sem redefinição de meta.
- **Ensaios:** 36 (3 alvos × 2 algoritmos × 3 sementes × 2 modos `free`/`symmetric_p3`), orçamento dual por ensaio: **10,0 s OU 100 000 avaliações**.
- **Avaliações totais:** 2 693 907 deltas; tempo somado 246,9 s; 0 chamadas de certificação (nenhum ensaio atingiu 0 violações).
- **Vereditos:** `DISCOVERY_BEATEN` **0** · `NULL_RESULT` **3** · `INCOMPLETE` 0.

## 2. Tabela de vereditos por alvo e modo

`best_viol` = menor nº de triplas fracas monocromáticas entre os ensaios do modo (0 = válido).

| alvo | k | attempt m | verdict | best_viol free | best_viol symmetric_p3 | certificado |
|---|---|---|---|---|---|---|
| weak_schur_5 | 5 | 208 | NULL_RESULT | 8 | 1156 | — |
| weak_schur_6 | 6 | 651 | NULL_RESULT | 40 | 11664 | — |
| weak_schur_7 | 7 | 2147 | NULL_RESULT | 454 | 42025 | — |

Melhores ensaios livres (mais próximos de válido): WS5 8 violações, WS6 40, WS7 454 — todos ainda inválidos; nenhum objeto abaixo/igual à cota com validade. SHAs por trial em `experiments/p177-weak-schur-results.json` (`best_sha256`).

## 3. Comparação simétrico-vs-livre

O modo livre ficou 10–100× abaixo do simétrico em violações em todos os alvos — e ambos nulos. Isso era esperado por um argumento elementar, que registro aqui como refutação da heurística **nesta forma** (mais forte que o disclaimer exigido):

> Para `m >= 3p`, **toda** coloração p-periódica de `{1..m}` contém violação fraca: os múltiplos `p, 2p, 3p` caem na mesma classe de cor (slot `(i-1) mod p = p-1`) com `p + 2p = 3p` distintos. Logo o modo `symmetric_p3` é provadamente nulo nestes `m` — o que os 18 ensaios simétricos confirmam empiricamente.

Consequência: um `NULL_RESULT` no modo simétrico **não** prova inexistência de partição válida (nem poderia, pela restrição); trabalho futuro com simetria precisa de períodos que cresçam com `m` (p ~ m) ou outra simetria — período fixo está refutado como via de recorde.

## 4. Frase literal aplicável (vale para cada um dos 3 alvos sem recorde)

> A busca estocástica sob o orçamento pré-registrado não superou a cota publicada. O resultado nulo é publicado de acordo com a regra de integridade científica de AGENTS.md.

## 5. Integridade

- Manifesto: `experiments/p177-weak-schur-manifest.json`, `created_at` 2026-10-24T00:26:36+00:00, anterior ao `started_at` da campanha; SHA-256 `157cab33991c…` registrado no JSON de resultados.
- Checkpoint incremental: `experiments/p177-weak-schur-checkpoint.json` (36/36 ensaios; sem perda).
- Orçamento: `budget_sec_per_seed` 10,0 s + `max_evaluations_per_trial` 100 000 por (alvo, algoritmo, semente, modo); sementes 42/101/202; regra de veredito congelada no manifesto.
- Tamanhos de quebra exatamente `best_known_value + 1` lidos do catálogo (teste `test_break_size_is_best_plus_one`).
- Verificador independente `frontier_catalogue.verify_weak_schur_partition` (P171) armado para certificação imediata; portões P171 (aceita `[1,1,2,1,2,2,2,1]`, rejeita `[1,1,2,1,2,2,1,2]`) re-verificados antes da campanha; 0 certificados emitidos.

## 6. Limitações

- Orçamento de sondagem (10 s/ensaio): nulos válidos sob este orçamento, sem alegar esgotamento.
- Operadores simples (SA/têmpera sobre recolorações, HC com restarts); sem SAT, sem quebra de simetria além da periódica, sem constructions algébricos.
- Modo simétrico com período fixo refutado acima; modo livre é busca local pura sem orientação estrutural.
