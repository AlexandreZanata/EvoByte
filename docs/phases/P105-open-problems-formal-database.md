# P105 — Banco de dados hermético de problemas abertos e tipagem formal dependente em Lean 4

**Status:** Done.
**Dependência:** P104 concluída; branch a partir de `codex/p105-p112-open-problems-program`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P104 concluída com campanha geométrica formal e consolidação na branch main; catálogo de 100 problemas abertos em `docs/research/open-problems.json` íntegro.
**Branch:** `codex/p105-open-problems-formal-database`.

## Hipótese, objetivo e escopo

Converter e tipar formalmente os problemas abertos catalogados (`docs/research/open-problems.json`) em tipos dependentes no kernel do Lean 4 (`lean_proofs/Generated/OpenProblemSignatures.lean`), criando assinaturas formais unificadas para proposições, construções e contraexemplos, sob particionamento hermético entre dados de desenvolvimento e partições cegas seladas.

Alterações permitidas: `lean_proofs/`, `src/evobyte/formal_bridge.py`, `src/evobyte/open_problems.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p105-config.json`, `experiments/p105-run.sh`.
Fora do escopo: download de pacotes não versionados; alteração de axiomas do kernel Lean 4; alegações de solução de problemas sem certificados formais.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-descoberta-formal-em-problemas-abertos-e-teoria-de-modelos-guiada-por-provas-em-lean-4-p105p112).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar parser e exportador de assinaturas com tipos dependentes em Lean 4 para problemas diofantinos e combinatórios abertos em `lean_proofs/Generated/OpenProblemSignatures.lean`.
2. Adicionar módulo de orquestração de banco hermético em `src/evobyte/open_problems.py` com separação estrita de partições públicas e testes cegos.
3. Adicionar interface de auditoria P105 em `benchmarks/science_matrix.py` (`run_p105_open_problems_database_audit`) com validação de compilação sem `sorry`.

## Gate de saída

Execução limpa de compilação das assinaturas de problemas abertos no Lean 4 com 0 `sorry` e interface de aceitação P105:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P105 --config experiments/p105-config.json --output /tmp/evobyte-p105-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p105 open problems formal database"
git push -u origin HEAD
gh pr create --base codex/p105-p112-open-problems-program --title "feat(formal): implement p105 open problems formal database" --body-file /tmp/evobyte-p105-pr.md
```
