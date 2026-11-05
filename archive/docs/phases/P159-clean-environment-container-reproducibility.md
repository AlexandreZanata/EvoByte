# P159 — Reprodutibilidade independente em contêiner hermético limpo

**Status:** Proposed.
**Dependência:** P158 concluída; branch a partir de `codex/p158-h1-statistical-verdict-pareto-analysis`.
**Owner:** agente executor; revisor formal/sistemas nos gates indicados.
**Pré-requisito:** P158 concluída com veredito de H1 aprovado.
**Branch:** `codex/p159-clean-environment-container-reproducibility`.

## Hipótese, objetivo e escopo

Validar a reprodutibilidade integral ponta-a-ponta do EvoByte em um ambiente limpo e isolado (contêiner Docker / OCI livre de dependências ocultas e de cache local). Executar `make verify` em ambiente hermético sem conexão com a internet. Empacotar todos os dados brutos de benchmark, sementes, artefatos e scripts de geração de figuras em formato pronto para depósito permanente em repositório de dados abertos (Zenodo / OSF) com manifestos SHA-256 completos.

Alterações permitidas: `Dockerfile`, `Makefile`, `scripts/export_zenodo_bundle.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p159-config.json`, `experiments/p159-run.sh`.
Fora do escopo: dependências não declaradas em `pyproject.toml`; dados não auditados.

Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Configurar receita de contêiner hermético em `Dockerfile` e target `make verify-container` no `Makefile`.
2. Executar validação de ponta a ponta sem rede a partir do pacote limpo.
3. Gerar pacote de dados abertos e manifestos SHA-256 via `scripts/export_zenodo_bundle.py`.
4. Adicionar interface de auditoria P159 em `benchmarks/science_matrix.py` (`run_p159_reproducibility_audit`).

## Gate de saída

Sucesso integral de reprodução em contêiner limpo e auditoria P159 aceita:

```bash
git diff --check
git status --short
make verify
python3 benchmarks/science_matrix.py --acceptance-phase P159 --config experiments/p159-config.json --output /tmp/evobyte-p159-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(infra): implement p159 clean environment container reproducibility"
git push -u origin HEAD
gh pr create --base codex/p158-h1-statistical-verdict-pareto-analysis --title "feat(infra): implement p159 clean environment container reproducibility" --body-file /tmp/evobyte-p159-pr.md
```
