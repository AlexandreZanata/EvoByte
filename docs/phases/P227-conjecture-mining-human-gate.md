# P227 — Mineração de conjecturas sobre a família BB com portão humano

**Status:** Proposed.
**Programa:** Progresso Científico Verificável (P221–P228, D049).
**Dependência:** P222 integrada em `main` (P225/P226 opcionais: se existirem, use seus dados).
**Owner:** agente executor propõe e tenta refutar; **humano** decide novidade; o revisor (Claude) escreve as fases de prova.
**Branch:** `codex/p227-conjecture-mining-human-gate` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/research/p222-census-report.md`](../research/p222-census-report.md), [`docs/research/claims-ledger-d047.md`](../research/claims-ledger-d047.md).

## Por que esta fase existe

Matemática de verdade prova afirmações para **famílias inteiras**, não para instâncias. O
censo é uma mina de padrões (ex.: como `k` depende de ℓ, m e dos suportes de A e B; limites
de `d` em função de pesos). O agente propõe e **tenta refutar** conjecturas; só o humano pode
dizer se alguma é nova; a prova formal (Lean/Mathlib) é escrita em fase própria pelo revisor.
O agente executor **não** tenta provar.

## Pergunta falsificável da fase

> Existe pelo menos uma conjectura sobre (ℓ, m, A, B) que (i) é consistente com 100% dos
> dados do censo, (ii) sobrevive a um teste fora-da-amostra em (ℓ,m) não usados para
> formulá-la, e (iii) não aparece na literatura segundo busca registrada e assinatura humana?
> (Resposta "não" é aceitável e é registrada.)

## Escopo

**Criar:** `scripts/mine_p227_conjectures.py`, `docs/research/p227-conjecture-register.md`, `experiments/p227-conjecture-tests.json`, `tests/test_p227_conjectures.py`.
**Proibido:** declarar "teorema"; escrever prova; usar a palavra "novo".

## Trabalho ordenado

1. Divida o censo: **treino** = ℓm ≤ 12, **teste fora-da-amostra** = ℓm ∈ {13, 14, 15, 16} (se P222 só foi até 14, use 13–14). Registre a divisão em JSON antes de minerar (commit isolado).
2. Gere hipóteses **somente destes tipos** (lista fechada, para evitar p-hacking):
   - H-k: `k` como função de `(gcd(ℓ,m), |A|, |B|, #pontos de A ∩ B, rank dos polinômios em F2[x,y]/(x^ℓ−1,y^m−1))` — teste a fórmula `k = 2·dim(ker A ∩ ker B)` = `2·(ℓm − rank([A;B]))` e variantes (não é nova; serve de controle: **deve** ser confirmada 100%; o revisor já a confirmou em 400 códigos aleatórios). Como o censo descarta `k=0`, recalcule o controle diretamente sobre o espaço de busca, não a partir do JSON.
   - H-d: limites superiores de `d` em função de `k`, `n`, `|A|`, `|B|` do tipo `d ≤ f(n,k,pesos)` com `f` escolhida de uma lista fechada (Singleton quântico, `d ≤ |A|+|B|` quando `k>0` e não-degenerado, etc.).
   - H-sym: invariâncias do par `(k,d)` sob operações explícitas: `A↔B`, multiplicação de A por monômio, automorfismos de grupo `(x,y)→(y,x)` quando ℓ=m.
3. Para cada hipótese: (a) contraexemplo mais pequeno no treino, se houver ⇒ rejeitada; (b) caso sobreviva, teste no conjunto fora-da-amostra; (c) registre em `p227-conjecture-register.md`: enunciado, tipo, status `REFUTADA`/`CONFIRMADA_NO_CENSO`/`CONTROLE`, nº de casos testados, contraexemplo (se houver).
4. Para cada `CONFIRMADA_NO_CENSO` que **não** seja o controle H-k: a seção "pistas de literatura" com até 5 fontes (todas `AGENTE_NAO_VERIFICADO`) e um campo `Decisão humana: __PENDENTE__ (NOVA | CONHECIDA | TRIVIAL)`.
5. Teste de integridade: o controle H-k é confirmado em 100% das linhas; nenhuma hipótese fora da lista fechada aparece.
6. **PARE** no PR; o revisor lê o registro; se o humano marcar alguma conjectura como `NOVA`, o revisor escreve a fase de prova formal (não faz parte desta).

## Regras de parada

- O controle H-k falha em qualquer linha ⇒ há bug no censo ou no script: PARE (isso invalida P222 até ser entendido).
- Qualquer hipótese adicionada depois de olhar os dados de teste ⇒ PARE.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_p227_conjectures.py -q
make lint
python3 -m pytest tests -q -m "not slow" | tail -2
git status --short
```

## Commit & Push (obrigatório; NÃO fazer merge)

```bash
git add scripts/mine_p227_conjectures.py docs/research/p227-conjecture-register.md \
  experiments/p227-conjecture-tests.json tests/test_p227_conjectures.py \
  docs/phases/P227-conjecture-mining-human-gate.md
git commit -m "docs(conjectures): closed-list conjecture mining with out-of-sample tests (P227)"
git push -u origin codex/p227-conjecture-mining-human-gate
gh pr create --base main --title "docs(conjectures): closed-list conjecture mining with out-of-sample tests (P227)" \
  --body "Registro de conjecturas testadas; novidade depende de decisão humana."
```
