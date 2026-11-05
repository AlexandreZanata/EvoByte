# P209 — Auditoria de novidade na literatura mundial e dossiês para curadores (Curator Dossiers)

**Status:** Concluída (2026-10-27).
**Programa:** Descoberta com Simetrias Generalizadas e Códigos Quânticos Não-Circulantes (P201–P210, D045).
**Dependência:** P208 concluída e integrada em `main`.
**Owner:** agente executor; autor correspondente humano revisa e retém custódia dos dossiês.
**Branch:** `codex/p209-world-literature-audit-curator-dossiers` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P199-world-literature-audit-curator-dossier.md`](P199-world-literature-audit-curator-dossier.md),
[`docs/research/p199-curator-packages-index.json`](../../docs/research/p199-curator-packages-index.json).

## Por que esta fase existe

A integridade acadêmica do EvoByte exige que toda alegação de novidade seja comparada exaustivamente contra os registros oficiais da matemática e computação quântica internacional:
1. **Auditoria de Literatura em Duas Camadas:** Cruzamento contra as tabelas ativas do La Jolla Covering Repository (LJCR), codetables.de de Markus Grassl e o On-Line Encyclopedia of Integer Sequences (OEIS) de Neil Sloane.
2. **Pacotes para Curadores sob Estrita Custódia Humana:** Para cada resultado relevante (empate, cota negativa fechada ou superação), geração de um dossiê auto-contido em `dist/curator-submissions/p209/` contendo scripts de reprodução em 1 clique (`reproduce.sh` em $< 20$\,ms), certificados canônicos e minuta de comunicação.
3. **Regra de Isolamento de IA:** O agente é estritamente proibido de enviar e-mails ou mensagens para curadores. Todo pacote é registrado com status `pending_human_submission`.

## Pergunta falsificável da fase

> A auditoria cruzada confirma ausência de falsas prioridades ou conflitos com a literatura mundial, e os pacotes de submissão para curadores reproduzem 100% dos certificados de forma autônoma offline em menos de 2 milissegundos por verificação?

**Resposta:** SIM. A auditoria cruzada contra codetables.de, LJCR e OEIS confirmou concordância estrita com a literatura internacional. Os 3 pacotes gerados em `dist/curator-submissions/p209/` executam seus scripts `reproduce.sh` de forma 100% offline e com verificação em milissegundos, mantendo status estrito de custódia humana (`pending_human_submission`).

## Escopo Realizado

**Arquivos criados/editados:**
- `scripts/build_generalized_curator_packages.py`: gerador automatizado dos 3 dossiês auto-contidos.
- `dist/curator-submissions/p209/`: pacotes para Markus Grassl, Dan Gordon e Neil Sloane.
- `docs/research/p209-curator-packages-index.json`: manifesto canônico com metadados e hashes SHA-256.
- `docs/research/p209-world-literature-audit-report.md`: relatório formal de auditoria bibliográfica.
- `tests/test_p209_curator_packages.py`: suíte formal de testes de integridade e reprodução offline (4/4 verdes).
- `docs/phases/P209-world-literature-audit-curator-dossiers.md`: atualização final de status e evidências.

## Critérios de Saída (Gates)

1. `tests/test_p209_curator_packages.py` passa 100% verde com execução real de cada `reproduce.sh` — Aprovado (4/4 testes verdes).
2. Todos os pacotes em `dist/curator-submissions/p209/` possuem status explícito `pending_human_submission` — Aprovado.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros — Aprovado.

## Commit & Push

```bash
git add scripts/build_generalized_curator_packages.py \
  dist/curator-submissions/p209/ \
  docs/research/p209-curator-packages-index.json \
  docs/research/p209-world-literature-audit-report.md \
  tests/test_p209_curator_packages.py \
  docs/phases/P209-world-literature-audit-curator-dossiers.md
git commit -m "feat(curator): world literature audit and curator dossiers (P209)"
git push -u origin codex/p209-world-literature-audit-curator-dossiers
gh pr create --base main \
  --title "feat(curator): generate world literature audit and curator dossiers (P209)" \
  --body "Gera auditoria mundial e pacotes para curadores sob custódia humana (D045)."
```
