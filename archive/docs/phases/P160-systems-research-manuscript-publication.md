# P160 — Redação e consolidação do manuscrito científico de sistemas e publicação

**Status:** Proposed.
**Dependência:** P159 concluída; branch a partir de `codex/p159-clean-environment-container-reproducibility`.
**Owner:** agente executor; revisor formal/sistemas nos gates indicados.
**Pré-requisito:** P159 concluída com reprodutibilidade hermética e dados brutos depositáveis.
**Branch:** `codex/p160-systems-research-manuscript-publication`.

## Hipótese, objetivo e escopo

Redigir e consolidar o manuscrito científico completo de sistemas e computação evolutiva (*"EvoByte: Massively Parallel Evolutionary Discovery of Symbolic Programs via Ultra-Compact Bytecode and Cascade Verification"*) em formato LaTeX pronto para submissão a conferência/periódico de ponta (ex.: GECCO, NeurIPS, IEEE TEVC ou JMLR). O manuscrito deve conter: fundamentação teórica da hipótese H1, arquitetura da VM de 64 bytes e cascata S0–S3, resultados de CVPS e fronteira de Pareto com baselines (GP/PySR), ablações experimentais (speedup de 14.6x), o drop do gerador neural P12, e o link de acesso ao repositório público auditado e reprodutível.

Alterações permitidas: `docs/paper/`, `docs/research/p160-manuscript-dossier.md`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p160-config.json`, `experiments/p160-run.sh`.
Fora do escopo: alegações não fundamentadas nos dados medidos de P154–P158.

Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Estruturar o projeto LaTeX do artigo em `docs/paper/` (código-fonte `.tex`, bibliografia `.bib` e figuras vetoriais geradas diretamente dos dados brutos).
2. Escrever seções completas: Introdução, Arquitetura da VM e Cascata, Metodologia Experimental, Resultados e Baselines, Estudo de Ablações, Discussão e Trabalhos Relacionados.
3. Compilar o PDF final sem erros e conferir rastreabilidade de todas as tabelas e gráficos contra os hashes brutos.
4. Elaborar dossiê final de submissão em `docs/research/p160-manuscript-dossier.md` e interface de auditoria em `benchmarks/science_matrix.py` (`run_p160_manuscript_audit`).

## Gate de saída

Compilação do artigo e auditoria final P160 aceita em árvore limpa:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P160 --config experiments/p160-config.json --output /tmp/evobyte-p160-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(paper): implement p160 systems research manuscript publication"
git push -u origin HEAD
gh pr create --base codex/p159-clean-environment-container-reproducibility --title "feat(paper): implement p160 systems research manuscript publication" --body-file /tmp/evobyte-p160-pr.md
```
