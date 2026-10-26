# P199 — Auditoria de novidade na literatura mundial e dossiê para curadores

**Status:** Proposed.
**Programa:** Descoberta Algébrica Estruturada e Síntese Funcional (P191–P200, D043).
**Dependência:** P198 concluída.
**Owner:** agente executor; autor correspondente humano revisa a carta de submissão.
**Branch:** `codex/p199-world-literature-audit-curator-dossier`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P186-world-literature-novelty-dual-audit.md`](P186-world-literature-novelty-dual-audit.md),
[`docs/phases/P187-curator-submission-dossier.md`](P187-curator-submission-dossier.md).

## Por que esta fase existe

Antes de qualquer anúncio público de progresso científico, a integridade da pesquisa exige uma **auditoria de novidade independente em duas camadas**:
1. **Camada Automática:** Verificação cruzada contra as bases mundiais indexadas (LJCR de Dan Gordon, codetables.de de Markus Grassl e OEIS de Neil Sloane).
2. **Camada de Custódia Humana:** O agente de IA **nunca** submete dados diretamente a curadores externos. Toda comunicação é empacotada em uma pasta estandardizada (`dist/curator-submissions/`) contendo o certificado, o script de reprodução em 3 comandos (`reproduce.sh`) e a minuta de carta para revisão pelo autor correspondente humano.

Se o resultado da campanha for nulo, o dossiê formaliza o registro do nulo honesto; se for uma quebra de recorde confirmada, o pacote de submissão é preparado com status `pending_human_submission`.

## Pergunta falsificável da fase

> A auditoria contra a literatura mundial confirma zero overlap com construções triviais já conhecidas, e o pacote em `dist/curator-submissions/` reproduz perfeitamente todas as validações em modo offline em menos de 10 segundos?

## Escopo

**Arquivos a criar/editar:**
- `experiments/p199-novelty-audit.json`: auditoria detalhada de cada alvo investigado.
- `scripts/build_p199_curator_package.py`: gerador do pacote de submissão aos curadores oficiais.
- `docs/research/p199-curator-dossier-report.md`: relatório e registro de custódia.
- `tests/test_p199_curator_package.py`: testes unitários garantindo que o pacote é auto-contido e sem vazamento de e-mails privados.

## Critérios de Saída (Gates)

1. `tests/test_p199_curator_package.py` passa 100% verde.
2. Cada pacote de curador contém `README.md`, certificado/notícia de nulo, verificador standalone, `reproduce.sh` executável e carta de submissão.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.
