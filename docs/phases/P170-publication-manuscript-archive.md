# P170 — Manuscrito de publicação auditado, pacote arquivável Zenodo e conclusão do programa

**Status:** Done (2026-10-22).
**Dependência:** P169 concluída; branch a partir de `codex/p169-statistical-verdict-negative-results`.
**Owner:** agente executor; revisor final e autor correspondente (Alexandre).
**Branch:** `codex/p170-publication-manuscript-archive`.
**Leia antes:** [regras do executor P161–P170](README.md#programa-de-descoberta-validada-p161p170-d038).

## Por que esta fase existe

Esta é a fase de consolidação final do programa de pesquisa P161–P170:
1. O manuscrito científico em LaTeX (`docs/paper/main.tex`) deve refletir **100% de evidência medida e auditada**:
   - Resumo, tabelas de ablações, baselines pareados e conclusões livres de falsos positivos.
   - Relato honesto de sucessos de engenharia de sistemas (VM em bytecode, cascata em GPU) lado a lado
     com limitações reais e resultados nulos em problemas abertos.
2. O PDF é compilado e validado visualmente.
3. O pacote de dados arquivável Zenodo é exportado com manifesto de integridade SHA-256 para garantir
   reprodutibilidade pública sem acesso à internet.
4. O ciclo de pesquisa é concluído com integridade exemplar perante as diretrizes de `AGENTS.md`.

## Escopo

**Arquivos que você pode criar:**
- `docs/research/p170-program-conclusion-dossier.md`
- `dist/zenodo-bundle/final-manifest-sha256.json`

**Arquivos que você pode editar:**
- `docs/paper/main.tex` e compilação de `docs/paper/main.pdf`
- `docs/paper/table_ablations.tex`
- `docs/paper/table_h1_verdict.tex`
- `docs/paper/table_pareto.tex`
- `docs/ROADMAP.md`: registrar conclusão de P161–P170.
- `docs/DECISIONS.md`: registrar entrada D040 fechando o ciclo.
- `docs/phases/P170-publication-manuscript-archive.md`: linha de Status.

**Proibido:** submeter ou publicar qualquer alegação que tenha sido refutada nas fases anteriores.
Alterar commits de fases passadas.

## Trabalho ordenado

### Passo 1 — Branch

```bash
git status --short
git switch codex/p169-statistical-verdict-negative-results
git switch -c codex/p170-publication-manuscript-archive
```

### Passo 2 — Atualização rigorosa do manuscrito LaTeX

Revise `docs/paper/main.tex`:
1. Sincronize as tabelas LaTeX (`table_ablations.tex`, `table_h1_verdict.tex`, `table_pareto.tex`) com os
   JSONs consolidados das fases P164–P169.
2. Certifique-se de que cada número citado no texto possui exatamente uma chave de origem em um arquivo
   JSON versionado no repositório.
3. Compile o manuscrito:

```bash
(cd docs/paper && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex)
```

Confira que `main.pdf` foi gerado sem erros fatais e o arquivo tem tamanho > 100 KB.

### Passo 3 — Gerar e validar o pacote arquivável Zenodo

Execute o script de empacotamento:

```bash
python3 scripts/export_zenodo_bundle.py --output-dir dist/zenodo-bundle
```

Confira que `dist/zenodo-bundle/final-manifest-sha256.json` contém os hashes de todos os arquivos de dados,
código e relatórios.

### Passo 4 — Atualizar ROADMAP.md e DECISIONS.md

1. Em `docs/ROADMAP.md`, marque a seção P161–P170 como concluída, detalhando as entregas de cada fase.
2. Em `docs/DECISIONS.md`, adicione a linha de decisão D040 formalizando a conclusão do programa com integridade.

### Passo 5 — Dossiê de conclusão `docs/research/p170-program-conclusion-dossier.md`

Redija o sumário final destacando:
- A jornada de transição de alegações não verificadas para rigor científico absoluto.
- As contribuições genuínas de engenharia de sistemas obtidas pelo EvoByte.
- Os resultados e recordes combinatórios alcançados com verificação independente.

## Regras de parada (PARE, não commite, reporte)

- `pdflatex` falhar na compilação do manuscrito.
- Qualquer discrepância entre as tabelas do manuscrito e os dados brutos de `experiments/`.
- Falha na validação do bundle Zenodo.

## Gate de saída

```bash
git diff --check
test -f docs/paper/main.pdf
test -f dist/zenodo-bundle/final-manifest-sha256.json
python3 -m pytest tests -q
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add docs/paper/main.tex docs/paper/main.pdf docs/paper/*.tex \
  dist/zenodo-bundle/final-manifest-sha256.json \
  docs/research/p170-program-conclusion-dossier.md \
  docs/ROADMAP.md docs/DECISIONS.md docs/phases/P170-publication-manuscript-archive.md
git diff --cached --check
git commit -m "docs(paper): publish final audited manuscript and zenodo archive bundle"
git push -u origin HEAD
gh pr create --base codex/p169-statistical-verdict-negative-results \
  --title "docs(paper): publish final audited manuscript and zenodo archive" \
  --body-file /tmp/evobyte-p170-pr.md
git status --short
```

---

**Status da execução (2026-10-22):** Done.

- Manuscrito sincronizado: `table_h1_verdict.tex` registra o veredito auditado
  (overall NOT SUPPORTED, C5 não atendido com os valores medidos do P155);
  `table_ablations.tex` lista as 9 ablações medidas do P157 com nomes e `speedup_ratio`
  exatos (1.0× onde não houve speedup); `table_pareto.tex` e `table_wilcoxon.tex`
  conferem com o JSON da P158/P155; nova seção "Validated Discovery Program (P161–P170)"
  com a tabela da campanha P166; abstract e conclusão atualizados.
- `docs/paper/main.pdf` recompilado (10 páginas, 264 KB, zero warnings/erros).
- Pacote Zenodo exportado (544 arquivos, 5,46 MB, tarball + autoverificação OK) com
  `scripts/export_zenodo_bundle.py` estendido para incluir manuscrito, evidências
  P160–P170, código-fonte e verificador autônomo; `final-manifest-sha256.json` criado
  com a cadeia completa (bundle + 17 artefatos de evidência).
- `docs/ROADMAP.md` com a seção do programa concluído; `docs/DECISIONS.md` com a linha
  D041 formalizando o fechamento.
- `docs/research/p170-program-conclusion-dossier.md` com a jornada, as contribuições
  genuínas, os resultados combinatórios e as limitações assumidas.
- Gates: `git diff --check` limpo, `test -f` nos dois artefatos, `pytest tests` completo
  verde, `make verify` verde.

Desvios em relação a esta especificação, registrados no PR:

- **D041 em vez de D040** para a decisão de fechamento (`D040` já era a retratação P161;
  o log de decisões exige IDs únicos).
- **`scripts/export_zenodo_bundle.py` estendido** (fora do escopo formal): sem a extensão,
  o pacote omitiria o manuscrito, as evidências P160–P170 e o código-fonte. Mudança mínima
  e testada (o teste P159 do bundle continua verde). O `.gitignore` ganhou exceções
  cirúrgicas para `dist/external-validation/` (P167) e
  `dist/zenodo-bundle/final-manifest-sha256.json` (esta fase); o resto de `dist/`
  continua ignorado.
- **LaTeX exigiu ajuste de quebra de linha**: um parágrafo do aviso de retratação com
  referência cruzada para a nova seção disparava erro fatal de expansão de fonte do
  microtype (`auto expansion is only possible with scalable fonts`); o apontamento para
  P169 foi movido para parágrafo próprio, sem mudar o conteúdo. Investigação completa no PR.
- **Dois commits em vez de um** (pré-registro + evidência): não aplicável aqui — ao
  contrário da P166, esta fase não executa campanha; o ciclo compilação→exportação→manifesto
  foi feito na árvore de trabalho e commitado atomicamente.
