# P223 — Auditoria de novidade com portão humano obrigatório

**Status:** Proposed.
**Programa:** Progresso Científico Verificável (P221–P228, D049).
**Dependência:** P222 concluída e integrada em `main`.
**Owner:** agente executor prepara a folha; **Alexandre Zanata (humano) decide**; o revisor (Claude) audita.
**Branch:** `codex/p223-novelty-audit-human-gate` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/research/p222-census-report.md`](../research/p222-census-report.md), [`docs/research/claims-ledger-d047.md`](../research/claims-ledger-d047.md).

## Por que esta fase existe

A lição de D042–D048: empatar com a tabela não é descoberta, e o próprio snapshot de tabela do
projeto não foi conferido por humano (o valor "d=4 ótimo" para [[16,2]] é suspeito). Um agente
automático **não pode** declarar novidade. Esta fase prepara a evidência e **para** até haver
assinatura humana. Sem a assinatura, nenhuma fase posterior que dependa de "novidade" executa.

## Pergunta falsificável da fase

> Para cada (n,k) do censo P222, existe uma linha na folha de novidade com o valor da tabela
> **conferido por humano** na fonte primária, e o status final de cada linha é
> `RECONSTRUCAO`, `ABAIXO_DA_TABELA` ou `CANDIDATO_ACIMA_DA_TABELA` — sem nenhuma célula
> preenchida só pelo agente?

## Escopo

**Criar:**
- `scripts/build_p223_novelty_sheet.py` — gera a folha a partir de `experiments/p222-bb-census-summary.json`.
- `docs/research/p223-novelty-sheet.md` — tabela: `n | k | d_censo | exemplo (l,m,A,B) | d_tabela (HUMANO) | fonte+data (HUMANO) | status (HUMANO) | notas`.
- `docs/research/p223-literature-leads.md` — pistas de literatura **marcadas `AGENTE_NAO_VERIFICADO`**.
- `docs/research/p223-human-signoff.md` — preenchido **somente pelo humano** (o agente cria o modelo vazio com as instruções abaixo).
- `tests/test_p223_novelty_sheet.py`.

**Proibido:** o agente preencher as colunas `d_tabela`, `fonte+data`, `status`; escrever "recorde", "novo", "descoberta" em qualquer arquivo; enviar e-mail ou submeter algo a curadores.

## Trabalho ordenado

1. Branch; `git status --short` vazio.
2. Gere a folha com as colunas HUMANO em branco (`__PENDENTE__`). Linhas: todos os `(n,k)` do resumo P222 com `d ≥ 3`, ordenados por `n`, depois `k`.
3. `docs/research/p223-literature-leads.md`: o agente lista **no máximo 15** fontes que parecem relevantes, cada uma com título, autores, ano, link e a frase `AGENTE_NAO_VERIFICADO`. Fontes mínimas a procurar: tabelas de Markus Grassl para códigos quânticos (codetables.de); Bravyi et al. 2024 (bivariate bicycle); trabalhos posteriores sobre BB generalizados/coprimos e códigos de dois blocos em álgebras de grupo (Lin & Pryadko; Wang & Mueller; Eberhardt & Steffan; e outros que a busca encontrar). Se a página da tabela não abrir ou não mostrar o valor, escreva `PAGINA_INACESSIVEL` — **não** chute.
4. Modelo de assinatura `p223-human-signoff.md` com: (a) instrução ao humano: "para cada linha da folha, abra a fonte primária, preencha `d_tabela`, `fonte+data` e `status`; liste abaixo qualquer linha `CANDIDATO_ACIMA_DA_TABELA` e a busca na literatura (termos, data) que sustenta que o código não é conhecido"; (b) campos: `Data`, `Assinado por`, `Linhas CANDIDATO_ACIMA_DA_TABELA`, `Observações`.
5. Teste: `tests/test_p223_novelty_sheet.py` verifica (i) a folha tem uma linha por (n,k) do resumo; (ii) as colunas HUMANO são `__PENDENTE__` ou preenchidas (nunca vazias); (iii) nenhum arquivo da fase contém as palavras proibidas (`recorde`, `descoberta`, `new record`, `novel`); (iv) o hash do resumo P222 citado confere.
6. **PARE aqui.** Commit local + push + PR com o título abaixo, descrição dizendo "aguardando assinatura humana". A fase só é `Done` depois que o humano preencher `p223-human-signoff.md` e o revisor aprovar o PR.

## Árvore de decisão (aplicada pelo revisor após a assinatura)

| Resultado da assinatura | Próximo passo |
|---|---|
| Nenhuma linha `CANDIDATO_ACIMA_DA_TABELA` | P225/P226 **não** executam como "busca de recorde"; P224 e P227 seguem; P228 conclui com `RESULTADO NULO HONESTO` + censo verificado |
| ≥ 1 linha `CANDIDATO_ACIMA_DA_TABELA` com n ≤ 32 | prova de distância no kernel Lean reutilizando o gerador de P221 (nova fase escrita pelo revisor) + P228 |
| Humano marca a região como "saturada pela literatura" | P225 só executa se o humano indicar uma região (n, k) aberta; senão P225 é `Não aplicável: motivo` |

## Regras de parada

- O agente não consegue gerar a folha sem editar o resumo P222 ⇒ PARE.
- Qualquer vontade de "estimar" um valor de tabela ⇒ PARE (deixe `__PENDENTE__`).

## Gate de saída (executor)

```bash
git diff --check
python3 -m pytest tests/test_p223_novelty_sheet.py -q
make lint
python3 -m pytest tests -q -m "not slow" | tail -2
git status --short
```

## Commit & Push (obrigatório; NÃO fazer merge)

```bash
git add scripts/build_p223_novelty_sheet.py tests/test_p223_novelty_sheet.py \
  docs/research/p223-novelty-sheet.md docs/research/p223-literature-leads.md \
  docs/research/p223-human-signoff.md docs/phases/P223-novelty-audit-human-gate.md
git commit -m "docs(novelty): novelty sheet with mandatory human sign-off gate (P223)"
git push -u origin codex/p223-novelty-audit-human-gate
gh pr create --base main --title "docs(novelty): novelty sheet with mandatory human sign-off gate (P223)" \
  --body "Folha de novidade; colunas de tabela e status aguardam assinatura humana."
```
