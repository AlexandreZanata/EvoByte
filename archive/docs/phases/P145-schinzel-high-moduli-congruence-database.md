# P145 — Banco formal de classes de congruência resistentes de Schinzel e recobrimentos modulares de alta ordem

**Status:** Done.
**Dependência:** P144 concluída; branch a partir de `codex/p144-discrepancy-covering-grand-dossier`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P144 concluída com biblioteca formal de discrepância e recobrimentos consolidada sob D037.
**Branch:** `codex/p145-schinzel-high-moduli-congruence-database`.

## Hipótese, objetivo e escopo

Mapear exaustivamente e catalogar em tipos dependentes no Lean 4 (`lean_proofs/Generated/SchinzelHighModuliSignatures.lean`) as classes de congruência residuais de Schinzel para frações ternárias $a/n = 1/x + 1/y + 1/z$ com numeradores $a \in \{5, 6, 7, 8\}$ sob módulos de alta ordem $M \in \{840, 2520, 5040\}$. Isolar rigorosamente as órbitas modulares não cobertas pelas identidades clássicas da literatura (Erdős, Sierpiński, Schinzel, Mordell), formalizando as assinaturas de obstrução e as condições de solubilidade diofantina local em $\mathbb{Z}/M\mathbb{Z}$.

Alterações permitidas: `lean_proofs/`, `src/evobyte/algebraic.py`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p145-config.json`, `experiments/p145-run.sh`, `docs/phases/P145-schinzel-high-moduli-congruence-database.md`.
Fora do escopo: alegações de solução analítica universal da conjectura de Schinzel para todo $n$; modificação de axiomas padrão do Lean 4.

Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Implementar catálogo de tipos e predicados formais para classes residuais resistentes de Schinzel $a \in \{5, 6, 7, 8\}$ sob módulos $M \in \{840, 2520, 5040\}$ em `lean_proofs/Generated/SchinzelHighModuliSignatures.lean`.
2. Expandir `src/evobyte/algebraic.py` com algoritmos exatos de decomposição modular em anéis de congruência e identificação das órbitas resistentes não cobertas pela literatura clássica.
3. Adicionar interface de auditoria P145 em `benchmarks/science_matrix.py` (`run_p145_schinzel_high_moduli_audit`) com compilação hermética sem `sorry`.

## Gate de saída

Compilação integral no Lean 4 com 0 `sorry` e auditoria P145 aceita em árvore limpa:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P145 --config experiments/p145-config.json --output /tmp/evobyte-p145-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p145 schinzel high moduli congruence database"
git push -u origin HEAD
gh pr create --base codex/p144-discrepancy-covering-grand-dossier --title "feat(formal): implement p145 schinzel high moduli congruence database" --body-file /tmp/evobyte-p145-pr.md
```
