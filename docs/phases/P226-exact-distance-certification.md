# P226 — Certificação exata de distância dos candidatos (SAT/ILP + prova no kernel quando viável)

**Status:** Proposed (**condicional**).
**Programa:** Progresso Científico Verificável (P221–P228, D049).
**Dependência:** (a) P225 `Done` com ≥ 1 sobrevivente **ou** (b) P223 assinada com ≥ 1 linha `CANDIDATO_ACIMA_DA_TABELA` do censo (n ≤ 32). Sem (a) nem (b): `Não aplicável`.
**Owner:** agente executor; o revisor (Claude) audita; o humano decide o que submeter.
**Branch:** `codex/p226-exact-distance-certification` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`src/evobyte/sat_distance_solver.py`](../../src/evobyte/sat_distance_solver.py), [`docs/research/p221-formal-honesty-report.md`](../research/p221-formal-honesty-report.md), [`scripts/gen_p221_lean.py`](../../scripts/gen_p221_lean.py).

## Por que esta fase existe

Um limite superior `d_ub` não sustenta nada. Só uma **distância exata** (ou um limite inferior
certificado igual ao superior) torna um código reportável. Esta fase transforma até **3**
candidatos em objetos com certificado independente, ou documenta que não foi possível.

## Pergunta falsificável da fase

> Para cada candidato (≤ 3), o limite inferior `d_lb` coincide com `d_ub`, certificado por (i)
> prova no kernel Lean quando n ≤ 32, ou (ii) solver SAT/ILP com log de prova verificável
> externamente, e reverificado pelo script stdlib?

## Escopo

**Criar:** `scripts/certify_p226_candidate.py`, `lean_proofs/Generated/BivariateCandidates.lean` (somente se houver candidato com n ≤ 32), `experiments/p226-certificates/*.json`, `tests/test_p226_certificates.py`, `docs/research/p226-certification-report.md`.
**Proibido:** certificar mais de 3 candidatos; aceitar `d_lb` sem log de prova ou prova Lean; chamar "exato" um resultado `timeout`.

## Trabalho ordenado (por candidato, em ordem de `k·d²/n` decrescente)

1. Reconfira `k` e `d_ub` com a função stdlib de P221 (e a testemunha). Divergência ⇒ PARE.
2. **n ≤ 32:** gere o módulo Lean com o mesmo molde de P221 (`rank_*`, `commute*`, `no_logical_weight_le(d-1)_*` via `decide +kernel`, teorema de testemunha de peso `d`). Tempo máximo 60 min por candidato; gate de axiomas = `scripts/verify_lean_p221.sh` adaptado. Estourou o tempo ⇒ registre `LEAN_TIMEOUT` e vá ao passo 3.
3. **n > 32 ou Lean inviável:** use `ExactSATDistanceSolver` (ou `pysat` com `cadical153`) para provar UNSAT de "existe lógico de peso ≤ d−1". Se o solver suportar log de prova (DRAT/LRAT), grave-o e verifique com `drat-trim`/`cake_lpr` **se instalado** (`which drat-trim cake_lpr`); se nenhum estiver instalado registre `PROVA_NAO_VERIFICADA_EXTERNAMENTE` e **não** use o adjetivo "certificado" no relatório (use "resultado de solver").
   - Orçamento: 6 h por candidato, em background, com checkpoint a cada 30 min. Estourou ⇒ `d_lb` = melhor limite provado (com valor), status `GAP_ABERTO`.
4. Certificado JSON v5 (campos: `l,m,A,B,n,k,d_lb,d_ub,metodo,tempo_s,hash_log,verificador`), com SHA-256 e verificador stdlib que recomputa `k`, valida a testemunha de peso `d_ub` e reconfere comutação.
5. Relatório: por candidato, status ∈ {`EXATO_LEAN`, `EXATO_SAT_LOG_VERIFICADO`, `EXATO_SAT_SEM_VERIFICACAO_EXTERNA`, `GAP_ABERTO`}, tempos, hardware.

## Regras de parada

- Qualquer divergência entre censo/frontier e a recomputação independente.
- `sorry`/`axiom`/`native_decide` em Lean.
- Tentação de cortar o orçamento para "fechar a fase": proibido; registre `GAP_ABERTO`.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_p226_certificates.py -q
python3 -S scripts/verify_bivariate_certificate.py experiments/p226-certificates/*.json   # ou o verificador v5 criado nesta fase
bash scripts/verify_lean_p221.sh   # + módulo novo, se existir
make lint
python3 -m pytest tests -q -m "not slow" | tail -2
git status --short
```

## Commit & Push (obrigatório; NÃO fazer merge)

```bash
git add scripts/certify_p226_candidate.py experiments/p226-certificates tests/test_p226_certificates.py \
  docs/research/p226-certification-report.md docs/phases/P226-exact-distance-certification.md \
  $(test -f lean_proofs/Generated/BivariateCandidates.lean && echo lean_proofs/Generated/BivariateCandidates.lean)
git commit -m "feat(certify): exact distance certificates for BB candidates (P226)"
git push -u origin codex/p226-exact-distance-certification
gh pr create --base main --title "feat(certify): exact distance certificates for BB candidates (P226)" \
  --body "Certificados exatos ou GAP_ABERTO; sem alegação de novidade antes da assinatura humana."
```
