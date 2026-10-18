# P123 — Formalização da obstrução quadrática de Schinzel-Yamamoto contra identidades lineares universais

**Status:** Proposed.
**Dependência:** P122 concluída; branch a partir de `codex/p122-mordell-modular-reduction-theorem`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P122 concluída com o teorema de redução modular de Mordell formalizado.
**Branch:** `codex/p123-quadratic-residue-polynomial-obstruction`.

## Hipótese, objetivo e escopo

Formalizar no Lean 4 (`lean_proofs/Generated/SchinzelObstructionTheorem.lean`) o teorema estrutural de obstrução algébrica (Schinzel / Yamamoto): demonstrar rigorosamente por que **nenhuma** identidade de divisibilidade linear do tipo $(4 x(k) - (m k + r)) \mid (m k + r)^2$ com coeficientes inteiros fixos e quociente linear positivo pode existir quando o resíduo $r$ é um quadrado perfeito coprimo com o módulo $m$ (em particular, $r \equiv 1 \pmod{24}$ e os 6 resíduos quadráticos módulo 840: $1, 11^2, 13^2, 17^2, 19^2, 23^2 \pmod{840}$). Isso transforma a "lista de resíduos resistentes" empírica em um **teorema de impossibilidade algébrica** provado no kernel do Lean 4.

Alterações permitidas: `lean_proofs/`, `src/evobyte/algebraic.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p123-config.json`, `experiments/p123-run.sh`.
Fora do escopo: alegações não provadas sobre obstruções analíticas; uso de `sorry`.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoremas-estruturais-em--e-descoberta-em-problemas-de-domínio-finito-aberto-p121p128).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Formalizar em `lean_proofs/Generated/SchinzelObstructionTheorem.lean` a caracterização completa dos resíduos coprimos em `ZMod 24` e `ZMod 840` que são quadrados perfeitos ($r \equiv b^2 \pmod{24} \iff r \equiv 1 \pmod{24}$ para $\gcd(r, 24) = 1$) e provar que os 6 resíduos resistentes módulo 840 são exatamente os quadrados de unidades em $(\mathbb{Z}/840\mathbb{Z})^\times$ menores que $840$.
2. Provar em Lean 4 o teorema de obstrução modular de Schinzel para templates lineares: em qualquer decomposição linear de Tipo I/II onde o condutor $d = 4a - m$ divide $r$, se $r \equiv 1 \pmod{24}$, então $d$ não pode mudar o caráter quadrático módulo 3 ou módulo 8 sem violar positividade ou integridade dos coeficientes.
3. Adicionar interface de auditoria P123 em `benchmarks/science_matrix.py` (`run_p123_quadratic_obstruction_audit`).

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry`, prova formal da caracterização e obstrução dos resíduos quadráticos e auditoria P123 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P123 --config experiments/p123-config.json --output /tmp/evobyte-p123-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p123 quadratic residue polynomial obstruction"
git push -u origin HEAD
gh pr create --base codex/p122-mordell-modular-reduction-theorem --title "feat(formal): implement p123 quadratic residue polynomial obstruction" --body-file /tmp/evobyte-p123-pr.md
```
