# P200 — Manuscrito de pesquisa, pacote arquival Zenodo e registro da decisão D043

**Status:** Proposed.
**Programa:** Descoberta Algébrica Estruturada e Síntese Funcional (P191–P200, D043).
**Dependência:** P199 concluída.
**Owner:** agente executor; autor correspondente humano revisa o manuscrito final.
**Branch:** `codex/p200-discovery-manuscript-decision-d043`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P188-zenodo-archive-reproducibility-container.md`](P188-zenodo-archive-reproducibility-container.md),
[`docs/phases/P189-frontier-discovery-manuscript.md`](P189-frontier-discovery-manuscript.md), [`docs/phases/P190-program-conclusion-and-decisions.md`](P190-program-conclusion-and-decisions.md).

## Por que esta fase existe

Todo programa científico do EvoByte conclui de forma transparente e verificável:
1. **Manuscrito Científico Compilado:** Produção de artigo LaTeX completo (`docs/structured-paper/main.tex` e `main.pdf`), relatando honestamente os achados (seja uma quebra inédita de recorde ou a caracterização exata do limite atingido pelo método híbrido).
2. **Pacote Arquival Zenodo e Contêiner Hermético:** Empacotamento de todos os dados, códigos, certificados e ambiente em contêiner Docker reproduzível offline (`--network none`).
3. **Decisão Formal D043:** Registro indelével da decisão e veredito final em `docs/DECISIONS.md`.
4. **Fechamento e Consolidação:** Merge ordenado de todos os PRs e branches na `main`.

## Pergunta falsificável da fase

> O manuscrito compila em PDF sem warnings críticos, o contêiner de reprodutibilidade passa 100% dos testes sob isolamento de rede (`make verify`), e a decisão D043 encerra o programa de forma rastreável e auditável?

## Escopo

**Arquivos a criar/editar:**
- `docs/structured-paper/main.tex`, `Makefile`, `references.bib`: código-fonte e manuscrito compilado em PDF.
- `docs/research/p200-program-conclusion-impact-report.md`: relatório final de impacto.
- `docs/DECISIONS.md`: registro da decisão D043.
- `docs/ROADMAP.md` e `docs/phases/README.md`: sincronização de estado final do programa.
- `tests/test_p200_manuscript.py`: testes de integridade das afirmações e hashes citados no artigo.

## Critérios de Saída (Gates)

1. `tests/test_p200_manuscript.py` passa 100% verde com verificação de alegações.
2. Manuscrito `docs/structured-paper/main.pdf` compilado com sucesso.
3. Decisão D043 registrada em `docs/DECISIONS.md`.
4. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.
