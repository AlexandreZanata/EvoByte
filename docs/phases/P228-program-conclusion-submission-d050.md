# P228 — Conclusão do programa, nota técnica e decisão D050

**Status:** Proposed.
**Programa:** Progresso Científico Verificável (P221–P228, D049).
**Dependência:** P221, P222, P223 (assinada), P224, P227 integradas; P225/P226 integradas **ou** marcadas `Não aplicável: <motivo>` no próprio arquivo de fase.
**Owner:** agente executor; **humano** decide submissão externa; o revisor (Claude) audita.
**Branch:** `codex/p228-program-conclusion-d050` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P190-program-conclusion-and-decisions.md`](P190-program-conclusion-and-decisions.md), todos os relatórios `docs/research/p22[1-7]-*.md`.

## Por que esta fase existe

Fechar o programa com um veredito mecânico, auditável e honesto, e embalar o que for
verdadeiro (censo certificado, ablação, conjecturas testadas) sem inflar.

## Pergunta falsificável da fase

> O veredito de D050 é uma das quatro categorias abaixo, derivado **mecanicamente** das
> evidências, e todo número do relatório aparece em algum artefato commitado?

## Veredito (escolha a primeira que se aplicar; o agente NÃO escolhe por preferência)

1. `DESCOBERTA INÉDITA VALIDADA: <o quê, onde verificado>` — **somente se** existir (i) linha `CANDIDATO_ACIMA_DA_TABELA` assinada pelo humano em P223, **e** (ii) certificado `EXATO_LEAN` ou `EXATO_SAT_LOG_VERIFICADO` em P226 para esse código, **e** (iii) o humano registrou em `docs/research/p228-human-novelty-confirmation.md` a busca de literatura final (data, termos, resultado). Falta qualquer item ⇒ não use esta categoria.
2. `CONJECTURA NOVA PENDENTE DE PROVA: <enunciado>` — se P227 tem conjectura marcada `NOVA` pelo humano (sem prova ainda).
3. `AVANÇO METODOLÓGICO MEDIDO: <métrica, onde verificado>` — se P224 = `EVOBYTE_ADDS_VALUE`.
4. `RESULTADO NULO HONESTO: nenhuma descoberta; censo exato verificado e limites delimitados em <artefatos>` — caso contrário.

## Escopo

**Criar:** `docs/research/p228-program-conclusion-impact-report.md`, `docs/research/p228-human-novelty-confirmation.md` (modelo vazio, só o humano preenche), `docs/research/technical-note-bb-census/main.tex` + `Makefile` + `references.bib` (nota técnica curta, ≤ 8 páginas), `tests/test_p228_claims.py`, `dist/p228-archive/` (manifesto SHA-256 do censo e dos certificados).
**Editar:** `docs/DECISIONS.md` (**apenas** acrescentar D050), `docs/ROADMAP.md` e `docs/phases/README.md` (estado do programa D049), `docs/phases/P228-program-conclusion-submission-d050.md`.
**Proibido:** alterar decisões passadas; criar categoria de veredito nova; enviar qualquer coisa a terceiros (e-mail, formulário, arXiv): tudo fica `pending_human_submission`.

## Trabalho ordenado

1. Branch; `git status --short` vazio; `grep -c "D050" docs/DECISIONS.md` = 0 (senão use o próximo livre e registre o desvio).
2. Auditoria de completude: tabela fase→status→artefato→PR para P221–P227. Fase sem artefato e sem `Não aplicável` ⇒ PARE.
3. Aplique a regra de veredito acima e escreva a linha D050 (formato das existentes).
4. Nota técnica LaTeX: título sugerido `An Exact Census of Small Bivariate Bicycle Codes with Independent Verification`. Seções: definição do espaço e das reduções rigorosas; método de distância exata; resultados (tabela best_d por (n,k)); reverificação independente e provas no kernel Lean (P221); ablação (P224) com o veredito literal; limitações (tabela de literatura não reconferida pelo agente; amostragem; o que **não** foi mostrado). Se o veredito for 1 ou 2, acrescente a seção do resultado, em linguagem factual e sem adjetivos de avaliação.
5. `tests/test_p228_claims.py`: (i) cada número da nota técnica citado como "medido" existe em `experiments/*.json` (use um marcador `\measured{chave}` e um dicionário gerado); (ii) palavras proibidas ausentes (`breakthrough`, `world record` fora de contexto negado, `first`, `novel` salvo se o veredito for 1); (iii) D050 contém exatamente uma das 4 categorias.
6. Arquivo: manifesto SHA-256 dos artefatos principais (`experiments/p222-*`, `p224-*`, `p226-certificates`, `p227-*`). Não faça upload a Zenodo (o humano decide).
7. Relatório de impacto: o que foi alegado, refutado, não tentado; o que o humano ainda deve decidir; próximos passos (apenas se houver candidato ou conjectura nova).

## Regras de parada

- Veredito 1 ou 2 escolhido sem os documentos humanos exigidos ⇒ PARE.
- Número no texto sem artefato correspondente ⇒ PARE.
- `make verify` ou pytest falhando ⇒ PARE.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_p228_claims.py -q
make -C docs/research/technical-note-bb-census
make verify
git status --short
```

## Commit & Push (obrigatório; NÃO fazer merge)

```bash
git add docs/research/p228-program-conclusion-impact-report.md docs/research/p228-human-novelty-confirmation.md \
  docs/research/technical-note-bb-census dist/p228-archive tests/test_p228_claims.py \
  docs/DECISIONS.md docs/ROADMAP.md docs/phases/README.md docs/phases/P228-program-conclusion-submission-d050.md
git commit -m "docs(program): conclude progress program with mechanical verdict D050 (P228)"
git push -u origin codex/p228-program-conclusion-d050
gh pr create --base main --title "docs(program): conclude progress program with mechanical verdict D050 (P228)" \
  --body "Veredito mecânico, nota técnica e arquivo com hashes; nada enviado a terceiros."
```
