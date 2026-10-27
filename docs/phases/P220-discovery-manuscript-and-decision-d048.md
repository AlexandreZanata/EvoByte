# P220 — Manuscrito de pesquisa, pacote arquival Zenodo e registro da decisão D048

**Status:** Proposed.
**Programa:** Descoberta com Códigos Quânticos Bicíclicos Bivariados e Geometrias Projetivas (P211–P220, D047).
**Dependência:** P219 concluída e integrada em `main`.
**Owner:** agente executor; autor correspondente humano revisa o manuscrito final.
**Branch:** `codex/p220-discovery-manuscript-and-decision-d048` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P210-discovery-manuscript-and-decision-d045.md`](P210-discovery-manuscript-and-decision-d045.md),
[`docs/generalized-paper/main.pdf`](../generalized-paper/main.pdf).

## Por que esta fase existe

Todo programa científico do EvoByte conclui de forma transparente, publicável e auditável:
1. **Manuscrito Científico Compilado:** Produção de artigo LaTeX completo (`docs/bivariate-paper/main.tex` e `main.pdf`), relatando honestamente os resultados obtidos com códigos bicíclicos bivariados e geometrias projetivas.
2. **Pacote Arquival Zenodo e Contêiner Hermético:** Empacotamento de todos os dados, códigos, certificados e ambiente em contêiner Docker reproduzível offline (`--network none`).
3. **Decisão Formal D048:** Registro indelével da decisão e veredito final em `docs/DECISIONS.md`.
4. **Fechamento e Consolidação:** Merge ordenado de todos os PRs e branches na `main`.

## Pergunta falsificável da fase

> O manuscrito científico compila em PDF sem warnings críticos, o contêiner de reprodutibilidade passa 100% dos testes sob isolamento de rede (`make verify`), e a decisão D048 encerra o programa de forma rastreável e auditável?

## Escopo

**Arquivos a criar/editar:**
- `docs/bivariate-paper/main.tex`, `Makefile`, `references.bib`: código-fonte e manuscrito compilado em PDF (`docs/bivariate-paper/main.pdf`).
- `docs/research/p220-program-conclusion-impact-report.md`: relatório final de impacto e conclusão.
- `docs/DECISIONS.md`: registro da decisão D048.
- `docs/ROADMAP.md` e `docs/phases/README.md`: sincronização de estado final do programa.
- `tests/test_p220_manuscript.py`: testes de integridade das afirmações e hashes citados no artigo.
- `docs/phases/P220-discovery-manuscript-and-decision-d048.md`: atualização de status e evidências.

## Critérios de Saída (Gates)

1. `tests/test_p220_manuscript.py` passa 100% verde com verificação de alegações.
2. Manuscrito `docs/bivariate-paper/main.pdf` compilado com sucesso.
3. Decisão D048 registrada em `docs/DECISIONS.md`.
4. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add docs/bivariate-paper \
  docs/research/p220-program-conclusion-impact-report.md \
  docs/DECISIONS.md docs/ROADMAP.md docs/phases/README.md \
  tests/test_p220_manuscript.py \
  docs/phases/P220-discovery-manuscript-and-decision-d048.md
git commit -m "feat(manuscript): publish bivariate discovery paper (P220)"
git push -u origin codex/p220-discovery-manuscript-and-decision-d048
gh pr create --base main \
  --title "feat(manuscript): publish bivariate discovery manuscript and record program conclusion (P220)" \
  --body "Publica manuscrito, pacote Zenodo e encerra programa P211–P220 sob D048."
```
