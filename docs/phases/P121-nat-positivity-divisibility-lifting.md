# P121 — Levantamento formal Q[k] -> N^+ e provas de divisibilidade conectadas a IsUnitFractionSol

**Status:** Proposed.
**Dependência:** P120 concluída; branch a partir de `codex/p120-additive-combinatorics-grand-dossier`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P120 concluída com ambiente Lean 4 e Lake herméticos; predicado `IsUnitFractionSol` definido em `lean_proofs/Generated/OpenProblemSignatures.lean`.
**Branch:** `codex/p121-nat-positivity-divisibility-lifting`.

## Hipótese, objetivo e escopo

Substituir identidades polinomiais puramente racionais (`∀ k : ℚ, 4 * X * Y * Z = n * (Y*Z + X*Z + X*Y)`) por teoremas estruturais reais sobre os números naturais positivos $\mathbb{N}^+$ em `lean_proofs/Generated/StructuralNatIdentities.lean`. Provar o lema ponte fundamental (`nat_cleared_denom_to_unit_fraction_sol`) que demonstra que para quaisquer $a, n, x, y, z \in \mathbb{N}$ com $n > 0, x > 0, y > 0, z > 0$ satisfazendo a igualdade diofantina inteira $a x y z = n(yz + xz + xy)$, vale `IsUnitFractionSol a n x y z` em $\mathbb{Q}$. Em seguida, elevar todas as famílias paramétricas mod 24 e mod 840 para teoremas existenciais universais em $\mathbb{N}$:
$$\forall k : \mathbb{N},\; \exists x, y, z : \mathbb{N},\; \mathrm{IsUnitFractionSol}\; 4\; (m \cdot k + r)\; x\; y\; z.$$

Alterações permitidas: `lean_proofs/`, `src/evobyte/algebraic.py`, `src/evobyte/formal_bridge.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p121-config.json`, `experiments/p121-run.sh`.
Fora do escopo: teoremas triviais baseados apenas em `rfl` sobre metadados; identidades racionais desconectadas de `IsUnitFractionSol`; uso de `sorry` ou axiomas extras.

Ler [o plano formal](../FORMAL_SEARCH_PLAN.md#programa-de-teoremas-estruturais-em--e-descoberta-em-problemas-de-domínio-finito-aberto-p121p128).
Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Provar no Lean 4 (`lean_proofs/Generated/StructuralNatIdentities.lean`) o lema ponte `nat_cleared_denom_to_unit_fraction_sol` conectando a equação polinomial inteira em $\mathbb{N}^+$ ao predicado `IsUnitFractionSol a n x y z` (usando `positivity`, `field_simp`, `push_cast`, `ring`).
2. Implementar em `src/evobyte/formal_bridge.py` o gerador de provas estruturais em $\mathbb{N}$ que instancia explicitamente $X(k), Y(k), Z(k) : \mathbb{N}$, prova estrita positividade ($X(k) > 0, Y(k) > 0, Z(k) > 0$ via `omega`/`positivity`) e fecha `∃ x y z : ℕ, IsUnitFractionSol 4 (m * k + r) x y z`.
3. Adicionar interface de auditoria P121 em `benchmarks/science_matrix.py` (`run_p121_nat_positivity_lifting_audit`) exigindo verificação sintática e semântica de que os teoremas provam `IsUnitFractionSol` quantificado sobre $\forall k : \mathbb{N}$.

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry`, todos os teoremas concluindo `IsUnitFractionSol` sobre $\mathbb{N}$ e auditoria P121 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P121 --config experiments/p121-config.json --output /tmp/evobyte-p121-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p121 nat positivity divisibility lifting"
git push -u origin HEAD
gh pr create --base codex/p120-additive-combinatorics-grand-dossier --title "feat(formal): implement p121 nat positivity divisibility lifting" --body-file /tmp/evobyte-p121-pr.md
```
