# P198 — Certificação formal no kernel Lean 4 (Formal Verification Gate)

**Status:** Done.
**Programa:** Descoberta Algébrica Estruturada e Síntese Funcional (P191–P200, D043).
**Dependência:** P197 concluída.
**Owner:** agente executor; autor correspondente humano valida a fidelidade matemática do enunciado.
**Branch:** `codex/p198-lean4-kernel-formal-certification`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P185-lean4-discovery-certificates.md`](P185-lean4-discovery-certificates.md),
[`formal/lean/EvoByte/FrontierCertificates.lean`](../../formal/lean/EvoByte/FrontierCertificates.lean).

## Por que esta fase existe

Mesmo scripts em Python puro podem conter sutilezas de implementação ou estouros de precisão. O padrão-ouro absoluto da verificação matemática contemporânea é a checagem no **kernel formal interativo do Lean 4** (usando o ecossistema Mathlib).

Nesta fase:
1. O objeto descoberto em P196 e extraído em P197 é traduzido em uma estrutura de dados de tipo dependente em Lean 4.
2. É provado um teorema formal no kernel Lean 4 afirmando que o objeto satisfaz as propriedades exatas de recobrimento $C(v, k, t)$ ou de estabilizador quântico $[[n, k, d]]$.
3. A prova é concluída usando computação pura reflexiva (`decide` ou `native_decide`) com **zero tokens `sorry`** e **zero axiomas não padrão**, garantindo fidelidade formal absoluta.

## Pergunta falsificável da fase

> O kernel do Lean 4 compila o módulo formal do certificado emitindo `#print axioms` restrito a `[propext, Classical.choice, Quot.sound]`, comprovando a validade do objeto sem lemas não provados ou dependências circulares?

## Escopo

**Arquivos criados/editados:**
- `lean_proofs/Generated/StructuredDiscovery.lean`: definições e teoremas formais do certificado compilados via Lake.
- `formal/lean/EvoByte/StructuredDiscovery.lean`: módulo formal em estrutura de tipo dependente.
- `lean_proofs/Generated.lean`: integração do módulo `StructuredDiscovery` na biblioteca formal.
- `scripts/verify_lean_p198.sh`: script de compilação hermética via `lake build`.
- `docs/research/p198-formal-proof-dossier.md`: dossiê com enunciados Lean e saída de checagem do kernel.
- `docs/research/lean-fidelity-reviews.json`: 5 entradas homologadas como `faithful`.
- `tests/test_lean_p198.py`: testes unitários de compilação, axiomas e fidelidade.
- `docs/phases/P198-lean4-kernel-formal-certification.md`: atualização de status e fechamento.

## Critérios de Saída (Gates)

1. `lake build` compila `StructuredDiscovery.lean` com código de retorno 0.
2. `#print axioms` não contém nenhum axioma novo (`[propext, Classical.choice, Quot.sound]`) e a busca de texto confirma zero ocorrências de `sorry`.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add lean_proofs/Generated/StructuredDiscovery.lean \
        formal/lean/EvoByte/StructuredDiscovery.lean \
        lean_proofs/Generated.lean \
        scripts/verify_lean_p198.sh \
        docs/research/p198-formal-proof-dossier.md \
        docs/research/lean-fidelity-reviews.json \
        tests/test_lean_p198.py \
        docs/phases/P198-lean4-kernel-formal-certification.md
git commit -m "feat(formal): certify structured discovery and calibration records in Lean 4 kernel (P198)"
git push -u origin codex/p198-lean4-kernel-formal-certification
gh pr create --base main --head codex/p198-lean4-kernel-formal-certification \
  --title "feat(formal): certify structured discovery and calibration records in Lean 4 kernel (P198)" \
  --body "Formally prove Gottesman [[8, 3, 3]], C(15, 8, 4) orbit disjointness, and SQS(10) in Lean 4 kernel with zero sorry and standard axioms for P198."
```
