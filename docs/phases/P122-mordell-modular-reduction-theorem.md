# P122 — Teorema estrutural de redução modular de Mordell sobre Fin 840 em N

**Status:** Proposed.
**Dependência:** P121 concluída; branch a partir de `codex/p121-nat-positivity-divisibility-lifting`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P121 concluída com teoremas existenciais em $\mathbb{N}$ conectados a `IsUnitFractionSol`.
**Branch:** `codex/p122-mordell-modular-reduction-theorem`.

## Hipótese, objetivo e escopo

Substituir avaliações aritméticas de frações isoladas (`(1:ℚ) - 6/840 = 139/140`) pela formalização real do **Teorema de Redução Modular de Mordell** sobre $\mathbb{N}$ em `lean_proofs/Generated/MordellReductionTheorem.lean`. Provar um teorema estrutural unificado que despacha por divisão euclidiana (`n = 24 * k + r` e `n = 840 * k + r`) e demonstra no kernel do Lean 4 que:
1. Para todo $n \in \mathbb{N}$ com $n \ge 2$ e $n \bmod 24 \notin \{1\}$, ou mais geralmente $n \bmod 840 \notin \{1, 121, 169, 289, 361, 529\}$ (e $n$ suficientemente grande / $k \ge 1$), vale `∃ x y z : ℕ, IsUnitFractionSol 4 n x y z`.
2. A validade universal da Conjectura de Erdős–Straus para todo $n \ge 2$ é formalmente equivalente à sua validade restrita aos 6 resíduos quadráticos coprimos módulo 840 (`mordell_reduction_equivalence`).

Alterações permitidas: `lean_proofs/`, `src/evobyte/algebraic.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p122-config.json`, `experiments/p122-run.sh`.
Fora do escopo: igualdades numéricas triviais de frações desconectadas do quantificador universal sobre $n \in \mathbb{N}$; uso de `sorry`.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoremas-estruturais-em--e-descoberta-em-problemas-de-domínio-finito-aberto-p121p128).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Formalizar em `lean_proofs/Generated/MordellReductionTheorem.lean` o predicado de resíduo excepcional `IsMordellExceptionalMod24` / `IsMordellExceptionalMod840` e provar o teorema estrutural de cobertura por análise exaustiva de resíduos (`omega` + aplicação dos teoremas de `StructuralNatIdentities.lean`).
2. Provar o teorema de equivalência formal `erdos_straus_iff_exceptional_residues`: se todo $n \ge 2$ nas classes excepcionais admite `IsUnitFractionSol 4 n x y z`, então todo $n \ge 2$ admite `IsUnitFractionSol 4 n x y z`.
3. Adicionar interface de auditoria P122 em `benchmarks/science_matrix.py` (`run_p122_mordell_reduction_audit`) verificando a compilação e a estrutura lógica do teorema de equivalência.

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry`, prova completa do teorema de redução modular e auditoria P122 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P122 --config experiments/p122-config.json --output /tmp/evobyte-p122-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p122 mordell modular reduction theorem"
git push -u origin HEAD
gh pr create --base codex/p121-nat-positivity-divisibility-lifting --title "feat(formal): implement p122 mordell modular reduction theorem" --body-file /tmp/evobyte-p122-pr.md
```
