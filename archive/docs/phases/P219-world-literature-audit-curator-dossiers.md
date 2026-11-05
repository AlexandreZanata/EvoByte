# P219 — Auditoria de novidade na literatura mundial e dossiês para curadores (Curator Dossiers)

**Status:** Concluída (Done).
**Programa:** Descoberta com Códigos Quânticos Bicíclicos Bivariados e Geometrias Projetivas (P211–P220, D047).
**Dependência:** P218 concluída e integrada em `main`.
**Owner:** agente executor; autor correspondente humano exerce a custódia das submissões.
**Branch:** `codex/p219-world-literature-audit-curator-dossiers` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P209-world-literature-audit-curator-dossiers.md`](P209-world-literature-audit-curator-dossiers.md),
[`docs/phases/P199-world-literature-audit-curator-dossier.md`](P199-world-literature-audit-curator-dossier.md).

## Por que esta fase existe

Todo resultado científico que atinja recordes mundiais ou estabeleça cotas negativas estruturais deve ser auditado contra as principais autoridades mundiais da área:
1. **Auditoria Cruzada na Literatura Mundial:**
   - Tabelas de Códigos Quânticos de Markus Grassl (`codetables.de`).
   - Repositório La Jolla Covering Repository de Dan Gordon (`LJCR`).
   - On-Line Encyclopedia of Integer Sequences de Neil Sloane (`OEIS`).
2. **Empacotamento Sob Custódia Humana:** Geração de pacotes de submissão arquivais (`dist/curator-submissions/p219/`) contendo matrizes em formato padrão, verificador standalone, cadeia de custódia SHA-256 e status `pending_human_submission`. O agente automatizado nunca envia dados externamente de forma autônoma sem revisão humana direta.

## Pergunta falsificável da fase

> É possível gerar pacotes de submissão autocontidos para cada curador externo com verificação standalone de 0 dependências, SHA-256 congelados e relatório auditado de conformidade sem qualquer envio autônomo não autorizado?

**Resposta:** SIM. Os 3 pacotes de submissão foram gerados em `dist/curator-submissions/p219/` com verificação standalone de 0 dependências (`python3 -S`), hashes SHA-256 auditados em `docs/research/p219-curator-packages-index.json`, zero chamadas de API externas e custódia humana estrita (`pending_human_submission`).

## Escopo

**Arquivos criados/editados:**
- `scripts/build_bivariate_curator_packages.py`: empacotador de dossiês para curadores.
- `dist/curator-submissions/p219/`: pacotes estruturados prontos para inspeção humana (`markus_grassl_codetables`, `dan_gordon_ljcr`, `neil_sloane_oeis`).
- `docs/research/p219-world-literature-audit-report.md`: relatório formal de auditoria contra codetables.de, LJCR e OEIS.
- `docs/research/p219-curator-packages-index.json`: índice canônico de SHA-256 dos pacotes gerados.
- `tests/test_p219_curator_packages.py`: suíte de validação da integridade dos pacotes.
- `docs/phases/P219-world-literature-audit-curator-dossiers.md`: atualização de status e evidências.

## Critérios de Saída (Gates) — Resultados

1. `tests/test_p219_curator_packages.py` passa 100% verde validando integridade e hashes dos pacotes (4/4 em 0.52s).
2. Cada pacote contém `README.md`, certificados, verificador standalone e metadados de custódia humana.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add scripts/build_bivariate_curator_packages.py \
  dist/curator-submissions/p219/ \
  docs/research/p219-world-literature-audit-report.md \
  docs/research/p219-curator-packages-index.json \
  tests/test_p219_curator_packages.py \
  docs/phases/P219-world-literature-audit-curator-dossiers.md
git commit -m "feat(curator): world literature audit and curator dossiers (P219)"
git push -u origin codex/p219-world-literature-audit-curator-dossiers
gh pr create --base main \
  --title "feat(curator): world literature audit and curator dossiers (P219)" \
  --body "Gera dossiês de curadores para códigos bivariados sob D047."
```
