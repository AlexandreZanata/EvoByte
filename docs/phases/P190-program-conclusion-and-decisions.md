# P190 — Conclusão do programa Descoberta na Fronteira e registro D042

**Status:** Completed.
**Programa:** Descoberta na Fronteira (P171–P190, D042). Trilhas A, B e fundação comum.
**Dependência:** P171–P189 concluídas (ou explicitamente registradas como não aplicáveis com motivo); branch a partir de `main`.
**Owner:** agente executor; autor correspondente humano valida o relatório de impacto.
**Branch:** `codex/p190-program-conclusion-and-decisions`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [regras do programa P171–P190](README.md#programa-de-descoberta-na-fronteira-p171p190-d042), [`docs/phases/P188-zenodo-archive-reproducibility-container.md`](P188-zenodo-archive-reproducibility-container.md), [`docs/phases/P189-frontier-discovery-manuscript.md`](P189-frontier-discovery-manuscript.md).

## Por que esta fase existe

Programas terminam com decisão registrada, branches limpos e relatório de impacto honesto —
não com trabalho espalhado e silêncio. Esta fase: (1) verifica que cada fase P171–P189 tem
artefato commitado ou registro explícito de não-aplicabilidade; (2) registra a decisão D042
fechando o programa; (3) fecha os PRs/branches do programa; (4) publica o relatório final de
impacto científico: o que foi descoberto (se algo), o que foi refutado e o que permanece aberto.

## Pergunta falsificável da fase

> O programa P171–P190 termina com: decisão D042 registrada, zero branches de trabalho
> remanescentes além de `main`, todos os artefatos finais verificáveis por terceiros, e um
> relatório que um revisor externo consegue auditar sem falar com a equipe?

## Fatos de partida (a verificar na execução, não a presumir)

| Fato | Como verificar |
|---|---|
| D042 está livre em `docs/DECISIONS.md` | `grep -o "D042" docs/DECISIONS.md` deve retornar vazio; se ocupado, usar o próximo livre e registrar o desvio |
| Fases P171–P189 concluídas ou justificadas | `git log --oneline --grep="p17\|p18\|p19"`, artefatos em `docs/research/`, `experiments/`, `dist/` |
| `main` verde no CI | `gh run list --branch main --limit 3` (todos `success`) |

## Escopo

**Arquivos que você pode criar:**
- `docs/research/p190-program-conclusion-impact-report.md`

**Arquivos que você pode editar:**
- `docs/DECISIONS.md`: **somente** acrescentar a linha D042 (formato das linhas existentes; data ISO).
- `docs/ROADMAP.md`: **somente** a seção do programa P171–P190 (marcar concluído por trilha).
- `docs/phases/README.md`: **somente** o índice/estado do programa P171–P190, se existir seção correspondente.
- `docs/phases/P190-program-conclusion-and-decisions.md`: só a linha de Status e o bloco final de execução.

**Proibido:**
- alterar decisões passadas (só acrescentar a linha D042);
- fechar PRs com CI vermelho para "limpar a lista" (PR aberto com CI verde mergeia; com CI vermelho, corrige-se ou documenta-se o motivo e mantém-se aberto);
- deletar branch com trabalho não mergeado sem registrar onde foi parar.

## Trabalho ordenado

### Passo 1 — Branch e inventário

```bash
git status --short   # precisa estar vazio (exceto arquivos intencionais desta fase)
git switch main && git pull --ff-only 2>/dev/null || git switch main
git switch -c codex/p190-program-conclusion-and-decisions
git branch -a | grep -E "p17[1-9]|p18|p19" ; echo "---prs---"
gh pr list --state open --limit 30
```

### Passo 2 — Auditoria de completude (mecânica, sem julgamento)

Para cada fase P171–P189, registrar em tabela: Status (`Done` com commit / `Não aplicável: motivo` /
`Pendente: bloqueador`), artefato principal (path + existe?), PR (número + estado). Qualquer
`Pendente` sem bloqueador documentado é STOP (não se conclui programa com fase fantasma).

### Passo 3 — D042 em `docs/DECISIONS.md`

Acrescentar **uma** linha no formato das existentes:

`| <AAAA-MM-DD> | D042 | Conclusão do programa Descoberta na Fronteira (P171–P190): <veredito em 1 frase> | <contexto em 1 frase> | <consequências em 1 frase> |`

O veredito em 1 frase **deve** ser um destes, conforme medido (nunca inventado):
`DESC OBERTA INÉDITA VALIDADA: <o quê, onde verificado>` |
`AVANÇO H2 CONFIRMADO: <métrica, onde verificado>` |
`RESULTADO NULO HONESTO: nenhuma descoberta; limites delimitados em <artefatos>`.

### Passo 4 — Fechar PRs e branches (só o que satisfaz os requisitos)

Ordem, um por vez, verificando antes de cada merge:

```bash
# para cada PR aberto do programa, nesta ordem de dependência:
gh pr view <N> --json mergeable,mergeStateStatus,statusCheckRollup
# exigir: mergeable + CLEAN + quick SUCCESS; então:
gh pr merge <N> --merge
git push origin --delete <branch> && git branch -D <branch>
```

Regras duras:
- CI vermelho → **não mergear**; corrigir na branch de origem (novo commit) ou documentar o bloqueador no relatório e manter o PR aberto com o motivo.
- Branch sem PR ou PR fechado sem merge → verificar se o trabalho está em `main` por outro caminho; se sim, deletar a branch local/remota e registrar; se não, **não deletar** e reportar.
- Ao final: `git ls-remote --heads origin` deve listar só `main` (além de branches de outros programas ativos, que **não** se toca — listar e preservar).

### Passo 5 — Relatório `docs/research/p190-program-conclusion-impact-report.md`

Tabela fase→entrega→artefato→PR, o veredito final em linguagem não-técnica e técnica, o que
permanece aberto (com ponteiros para os artefatos), e a declaração de integridade: o que foi
alegado, o que foi refutado, o que não foi tentado.

## Regras de parada (PARE, não commite, reporte)

- Qualquer fase P171–P189 sem artefato nem justificativa registrada.
- CI vermelho em qualquer PR do programa no momento do merge.
- D042 já ocupado por outra decisão (usar o próximo livre e registrar).
- Falha no pytest ou no `make verify`.

## Gate de saída

```bash
git diff --check
gh pr list --state open --limit 30   # nenhum PR do programa aberto
git ls-remote --heads origin         # só main (+ outros programas ativos, preservados)
python3 -m pytest tests -q -m "not slow" 2>&1 | tail -2
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add docs/DECISIONS.md docs/ROADMAP.md docs/phases/README.md \
  docs/research/p190-program-conclusion-impact-report.md \
  docs/phases/P190-program-conclusion-and-decisions.md
git diff --cached --check
git commit -m "docs(decisions): register p190 d042 frontier program conclusion"
git push -u origin HEAD
gh pr create --base main \
  --title "docs: p190 program conclusion and d042" \
  --body-file /tmp/evobyte-p190-pr.md
git status --short
```

O corpo do PR (`/tmp/evobyte-p190-pr.md`) traz: problema, comportamento resultante, comandos de
validação exatos (inventário de fases, CIs, branches restantes), o veredito final em 1 frase e
o link do relatório de impacto.

## Registro de Execução

- **Decisão D042 Registrada:** [`docs/DECISIONS.md`](../DECISIONS.md) formalizando a conclusão do programa P171–P190 com `RESULTADO NULO HONESTO` (nenhuma quebra de recorde mundial, H2 refutado com 288 vs 512).
- **Roadmap e Fases Sincronizados:** [`docs/ROADMAP.md`](../ROADMAP.md) e [`docs/phases/README.md`](README.md) atualizados com o índice completo de P171–P190 marcado como concluído.
- **Relatório de Impacto:** [`docs/research/p190-program-conclusion-impact-report.md`](../research/p190-program-conclusion-impact-report.md) consolidando a auditoria de todas as 20 fases, vereditos técnicos/não-técnicos e declaração de integridade.
