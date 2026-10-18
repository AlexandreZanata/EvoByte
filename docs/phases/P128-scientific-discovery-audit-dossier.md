# P128 — Auditoria anti-inflação de teoremas estruturais, confirmação cega e dossiê de descoberta científica

**Status:** Proposed.
**Dependência:** P127 concluída; branch a partir de `codex/p127-erdos-647-475-finite-certificates`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P121–P127 concluídas com os módulos estruturais em $\mathbb{N}$ e os alvos finitos abertos certificados no Lean 4.
**Branch:** `codex/p128-scientific-discovery-audit-dossier`.

## Hipótese, objetivo e escopo

Implementar um **auditor epistemológico anti-inflação** (`verify_scientific_discovery_quality`) em `src/evobyte/formal_bridge.py` e consolidar o dossiê científico final em `docs/research/p128-scientific-discovery-dossier.md`. Diferente de auditorias puramente quantitativas que contam qualquer declaração `theorem` igualmente, o auditor de P128 classifica estritamente cada teorema de toda a biblioteca `lean_proofs/Generated/` em quatro estratos auditáveis:
1. **`structural_universal_nat`:** Teoremas universalmente quantificados sobre $\mathbb{N}$ (`∀ k : ℕ` ou `∀ n : ℕ`) que provam o predicado matemático real (`IsUnitFractionSol`, redução modular de Mordell em `Fin 840`, obstrução de Schinzel–Yamamoto, ou fechamento multiparamétrico).
2. **`open_problem_structural_or_exhaustive`:** Teoremas de obstrução estrutural ($p$-ádica, divisores locais) ou cotas exaustivas/certificados para problemas do bucket `finite_search_candidates` (`erdos-307`, `erdos-287`, `erdos-647`, `erdos-475`).
3. **`algebraic_or_instance_certificate`:** Identidades intermediárias em $\mathbb{Q}[k]$ e certificados de instâncias finitas verificadas por `norm_num`/`decide`.
4. **`metadata_or_definitional`:** Lema de reflexividade sobre registros estáticos (`rfl` em metadados de partição), que são **excluídos** da métrica de avanço matemático.

Além disso, executar confirmação cega nos alvos estruturais e finitos sob controle Bonferroni-Holm ($\alpha = 0{,}01$) e registrar a cadeia criptográfica SHA-256 completa.

Alterações permitidas: `lean_proofs/`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p128-config.json`, `experiments/p128-run.sh`, `docs/research/p128-scientific-discovery-dossier.md`.
Fora do escopo: inflar métricas com teoremas triviais; reivindicar solução de conjectura aberta sem certificado formal verificado no kernel; uso de `sorry`.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoremas-estruturais-em--e-descoberta-em-problemas-de-domínio-finito-aberto-p121p128).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar em `src/evobyte/formal_bridge.py` o classificador estrito de teoremas (`classify_lean_theorems_by_scientific_stratum`) que separa teoremas estruturais em $\mathbb{N}$ e cotas de problemas finitos abertos de certificados pontuais e metadados triviais (`rfl`).
2. Executar a confirmação cega multiproblema cobrindo os novos módulos estruturais (`P121–P124`) e os alvos finitos (`P125–P127`) sob controle FWER (Bonferroni-Holm, $\alpha = 0{,}01$).
3. Elaborar o dossiê científico rigoroso em `docs/research/p128-scientific-discovery-dossier.md` reportando os estratos separados, os avanços reais obtidos em `erdos-307`, `erdos-287`, `erdos-647`, `erdos-475` e a hash chain SHA-256 final.
4. Adicionar interface de auditoria P128 em `benchmarks/science_matrix.py` (`run_p128_scientific_discovery_campaign_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry`, auditoria anti-inflação aprovada nos estratos 1 e 2, e aceitação P128 em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P128 --config experiments/p128-config.json --output /tmp/evobyte-p128-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p128 scientific discovery audit dossier"
git push -u origin HEAD
gh pr create --base codex/p127-erdos-647-475-finite-certificates --title "feat(formal): implement p128 scientific discovery audit dossier" --body-file /tmp/evobyte-p128-pr.md
```
