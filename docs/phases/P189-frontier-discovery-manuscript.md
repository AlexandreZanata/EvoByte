# P189 — Manuscrito científico: a descoberta inédita ou o avanço metodológico H2

**Status:** Completed.
**Programa:** Descoberta na Fronteira (P171–P190, D042). Trilhas A, B e fundação comum.
**Dependência:** P184–P188 concluídas (verificação externa, certificados Lean, novidade auditada, pacote); branch a partir de `main`.
**Owner:** agente executor (rascunho técnico completo); autor correspondente humano revisa e submete.
**Branch:** `codex/p189-frontier-manuscript`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [regras do programa P171–P190](README.md#programa-de-descoberta-na-fronteira-p171p190-d042), vereditos P178/P182, auditoria P186, dossiê P188.

## Por que esta fase existe

Ciência que não é escrita não existe. Este manuscrito LaTeX documenta, com 100% de evidência
medida e auditada, **um dos dois** desfechos — sem misturar os dois:
(A) a descoberta inédita validada (recorde com certificado + verificação externa +
novidade auditada + selo de curador, se houver), ou
(B) o avanço metodológico H2 (evolução em bytecode no nível FunSearch com fração do custo),
ou (C) — se nenhum dos dois se sustentar — o relatório honesto de resultados nulos com as
delimitações empíricas medidas. O tipo de manuscrito é **decidido pelos vereditos**, não
pelo desejo.

## Pergunta falsificável da fase

> O manuscrito compila sem erros, cada número citado rastreia exatamente uma chave de origem
> em JSON versionado, cada afirmação de novidade cita um `CONFIRMED` da P186, e o tipo
> declarado (descoberta / H2 / nulos honestos) corresponde aos vereditos registrados?

## Fatos de partida (todos lidos dos artefatos, nenhum presumido)

| Fato | Fonte |
|---|---|
| Vereditos das campanhas (o que foi/nao foi batido) | `experiments/p176-*`, `p177-*`, `p182-*` (+ P178/P186 consolidados) |
| Orçamento FunSearch e comparação H2 | `experiments/p174-h2-results.json` + manifesto (ou `not_obtained`) |
| Certificados formais e revisões humanas | P185 + `lean-fidelity-reviews.json` |
| Padrão de manuscrito auditado do programa | `docs/paper/main.tex` (P160/P170: abstract honesto, tabelas sincronizadas, seção de limitações) |

## Escopo

**Arquivos que você pode criar:**
- `docs/frontier-paper/main.tex` (novo manuscrito; não editar `docs/paper/`, que é o registro P160/P170)
- `docs/frontier-paper/references.bib`
- `docs/frontier-paper/Makefile` (alvo `pdf`: `pdflatex` 2×; alvo `check`: conta `sorry`/TODOS e grep de alegações sem fonte)
- `tests/test_frontier_manuscript.py` (só checagens estáticas de arquivo; suíte < 3 s)
- `docs/research/p189-manuscript-dossier.md` (tabela número→origem JSON + tipo do manuscrito justificado)

**Arquivos que você pode editar:**
- `docs/phases/P189-algorithms-manuscript.md` — não existe; **o nome correto do arquivo desta fase é `P189-frontier-discovery-manuscript.md`** (ver Observação). Editar só Status + bloco final.
- `docs/phases/P189-frontier-discovery-manuscript.md`: só a linha de Status e o bloco final de execução.

**Proibido:**
- tocar em `docs/paper/` (registro congelado P160/P170);
- afirmar novidade sem `CONFIRMED` da P186; afirmar H2 sem o veredito literal da P174;
- números sem chave de origem; `sorry`/TODO no `.tex`.

> [!IMPORTANT]
> **Observação de nomenclatura.** Se existir ambiguidade com `P189-algorithms-manuscript.md`
> (nome alternativo circulado no planejamento), vale **este** arquivo
> (`P189-frontier-discovery-manuscript.md`); o executor registra a alias no relatório e segue.

## Trabalho ordenado

### Passo 1 — Branch e decisão do tipo de manuscrito

```bash
git status --short
git switch main && git pull --ff-only 2>/dev/null || git switch main
git switch -c codex/p189-frontier-discovery-manuscript
mkdir -p docs/frontier-paper
python3 - <<'PY'
import json
kinds = {}
for p, key in [("experiments/p176-covering-results.json","covering"), ("experiments/p177-weak-schur-results.json","weak_schur"), ("experiments/p182-qecc-results.json","qecc")]:
    try:
        d = json.load(open(p)); kinds[key] = "BEATEN" if any(t.get("verdict")=="DISCOVERY_BEATEN" for t in d.get("verdicts",{}).values()) else "null"
    except FileNotFoundError: kinds[key] = "no_artefato"
h2 = json.load(open("experiments/p174-h2-results.json"))["verdict"] if __import__("pathlib").Path("experiments/p174-h2-results.json").exists() else "no_artefato"
print("campanhas:", kinds, "| H2:", h2)
PY
```

Tipo do manuscrito = **descoberta** se algum `BEATEN` + `CONFIRMED` P186; senão **H2** se veredito literal `H2_SUPPORTED`; senão **nulos honestos**. Registrar a decisão e seguir — sem reclassificar depois.

### Passo 2 — `docs/frontier-paper/main.tex` (+ `.bib`, `Makefile`)

Estrutura obrigatória: abstract honesto (tipo declarado na primeira frase), introdução com
falsificabilidade explícita, métodos (busca + verificação independente + pré-registro),
resultados (tabelas geradas dos JSONs — **nenhum número digitado**; gerar via script e colar
a saída, registrando o comando no dossiê), discussão honesta (o que **não** foi provado),
limitações, conclusão contida, referências (só citadas no texto).

`Makefile`: `pdf` (pdflatex 2×, falha em qualquer erro), `check` (falha se houver `sorry`,
`TODO`, ou as strings `novo recorde`/`quebramos` sem citação de `CONFIRMED` no mesmo parágrafo).

### Passo 3 — Dossiê `docs/research/p189-manuscript-dossier.md`

Tabela `número → arquivo JSON + chave` para **cada** número do manuscrito; justificativa do
tipo escolhido com os vereditos literais; lista do que foi deliberadamente **omitido** e por quê.

### Passo 4 — Testes `tests/test_frontier_manuscript.py` (todos < 0,2 s; suíte < 3 s)

Checagens mecânicas de arquivo (nenhuma compilação pesada aqui; o `pdflatex` roda no gate):

1. `test_no_sorry_or_todo_in_manuscript`: `main.tex` não contém `sorry` nem `TODO`.
2. `test_cites_and_refs_resolve`: todo `\cite{chave}` tem entrada no `.bib`; todo `\ref{rotulo}` tem `\label` correspondente.
3. `test_manuscript_type_matches_verdicts`: lê o tipo declarado no dossiê e os vereditos literais; se o tipo é `descoberta`, existe `CONFIRMED` na P186; se todos os vereditos são nulos, o tipo é `nulos honestos` (nunca o contrário).

### Passo 5 — Revisão humana (obrigatória, fora do pytest)

O PDF compilado passa por revisão humana antes de qualquer submissão (o agente **nunca**
submete). Registrar `human_review: pending/approved:<data>` no dossiê.

## Regras de parada (PARE, não commite, reporte)

- Tipo de manuscrito incompatível com os vereditos (ex: alegar recorde com `NULL_RESULT`).
- Número sem chave de origem; `CONFIRMED` ausente onde há alegação de novidade.
- `pdflatex` com erro; `make check` falhar.
- Revisão humana do PDF pendente não registrada (o agente marca `human_review: pending`).

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_frontier_manuscript.py -q -m "not slow"   # FAST LOOP, ~1s
make -C docs/frontier-paper check pdf
ls -la docs/frontier-paper/main.pdf && test $(stat -c%s docs/frontier-paper/main.pdf) -gt 100000
python3 -m pytest tests/test_frontier_manuscript.py -q                 # FINAL GATE, < 3s
git status --short
```

## Commit & Push (obrigatório)

```bash
git add docs/frontier-paper/main.tex docs/frontier-paper/references.bib docs/frontier-paper/Makefile \
  docs/frontier-paper/main.pdf tests/test_frontier_manuscript.py \
  docs/research/p189-manuscript-dossier.md \
  docs/phases/P189-frontier-discovery-manuscript.md
git diff --cached --check
git commit -m "docs(paper): implement p189 frontier discovery manuscript"
git push -u origin HEAD
gh pr create --base main \
  --title "docs(paper): p189 frontier manuscript" \
  --body-file /tmp/evobyte-p189-pr.md
git status --short
```

O corpo do PR (`/tmp/evobyte-p189-pr.md`) traz: problema, tipo do manuscrito e por quê, comandos de
validação exatos, tabela número→origem (resumo), limitações e o link do dossiê. **Nenhuma
submissão a periódico/conferência é feita pelo agente.**

## Registro de Execução

- **Tipo do Manuscrito:** `nulos honestos` (Honest Null Results), fundamentado nos vereditos literais de P176 (40/40 NULL_RESULT), P177 (3/3 NULL_RESULT), P182 (7/7 NULL_RESULT), P174 (H2_NOT_SUPPORTED) e na auditoria P186 (0 CONFIRMED, NO_ACTIVE_DISCOVERY_CLAIMS).
- **Artigo LaTeX:** [`docs/frontier-paper/main.tex`](../frontier-paper/main.tex) (8 páginas compiladas, 250 537 bytes > 100 KB em [`main.pdf`](../frontier-paper/main.pdf)), 0 keywords banidas (`sorry`, `TODO`, `FIXME`, `quebramos`), 100% citações e labels resolvidos.
- **Dossiê de Rastreabilidade:** [`docs/research/p189-manuscript-dossier.md`](../research/p189-manuscript-dossier.md) mapeando cada número citado a sua chave JSON de origem, com declaração de revisão humana `human_review: pending`.
- **Testes Estáticos:** [`tests/test_frontier_manuscript.py`](../../tests/test_frontier_manuscript.py) (3 testes passando em 0,12 s).
