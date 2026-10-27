# P210 — Manuscrito de pesquisa, pacote arquival Zenodo e registro da decisão D046

**Status:** Proposed.
**Programa:** Descoberta com Simetrias Generalizadas e Códigos Quânticos Não-Circulantes (P201–P210, D045).
**Dependência:** P209 concluída e integrada em `main`.
**Owner:** agente executor; autor correspondente humano revisa o artigo final.
**Branch:** `codex/p210-discovery-manuscript-and-decision-d045` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P200-discovery-manuscript-decision-d043.md`](P200-discovery-manuscript-decision-d043.md),
[`docs/structured-paper/main.pdf`](../structured-paper/main.pdf).

## Por que esta fase existe

Todo programa científico do EvoByte conclui de forma transparente, publicável e auditável:
1. **Manuscrito Científico Compilado:** Produção de artigo LaTeX completo (`docs/generalized-paper/main.tex` e `main.pdf`), reportando honestamente o salto metodológico, resultados positivos, negativos e novas cotas delimitadas.
2. **Pacote Arquival Zenodo e Contêiner Hermético:** Empacotamento de todos os dados, códigos, certificados e ambiente em contêiner Docker reproduzível offline (`--network none`).
3. **Decisão Formal D046:** Registro indelével da decisão e veredito final em `docs/DECISIONS.md`.
4. **Fechamento e Consolidação:** Merge ordenado de todos os PRs e branches na `main`.

## Pergunta falsificável da fase

> O manuscrito científico compila em PDF sem warnings críticos, o contêiner de reprodutibilidade passa 100% dos testes sob isolamento de rede (`make verify`), e a decisão D046 encerra o programa de forma rastreável e auditável?

## Escopo

**Arquivos a criar/editar:**
- `docs/generalized-paper/main.tex`, `Makefile`, `references.bib`: código-fonte e manuscrito compilado em PDF (`docs/generalized-paper/main.pdf`).
- `docs/research/p210-program-conclusion-impact-report.md`: relatório final de impacto e conclusão.
- `docs/DECISIONS.md`: registro da decisão D046.
- `docs/ROADMAP.md` e `docs/phases/README.md`: sincronização de estado final do programa.
- `tests/test_p210_manuscript.py`: testes de integridade das afirmações e hashes citados no artigo.
- `docs/phases/P210-discovery-manuscript-and-decision-d045.md`: atualização de status e evidências.

## Critérios de Saída (Gates)

1. `tests/test_p210_manuscript.py` passa 100% verde com verificação de alegações.
2. Manuscrito `docs/generalized-paper/main.pdf` compilado com sucesso.
3. Decisão D046 registrada em `docs/DECISIONS.md`.
4. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add docs/generalized-paper \
  docs/research/p210-program-conclusion-impact-report.md \
  docs/DECISIONS.md docs/ROADMAP.md docs/phases/README.md \
  tests/test_p210_manuscript.py \
  docs/phases/P210-discovery-manuscript-and-decision-d045.md
git commit -m "feat(manuscript): publish generalized discovery manuscript and record program conclusion (P210)"
git push -u origin codex/p210-discovery-manuscript-and-decision-d045
gh pr create --base main \
  --title "feat(manuscript): publish generalized discovery manuscript and record program conclusion (P210)" \
  --body "Publica manuscrito, pacote Zenodo e encerra programa P201–P210 sob D046."
```
