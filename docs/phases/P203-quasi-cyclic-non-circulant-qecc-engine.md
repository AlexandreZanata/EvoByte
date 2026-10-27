# P203 — Gerador e verificador de códigos quânticos quase-cíclicos e não-circulantes (Lifted Product & Quasi-Cyclic QECC)

**Status:** Proposed.
**Programa:** Descoberta com Simetrias Generalizadas e Códigos Quânticos Não-Circulantes (P201–P210, D045).
**Dependência:** P202 concluída e integrada em `main`.
**Owner:** agente executor.
**Branch:** `codex/p203-quasi-cyclic-non-circulant-qecc-engine` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P192-symmetry-groups-orbit-reduction.md`](P192-symmetry-groups-orbit-reduction.md),
[`src/evobyte/qecc_verifier.py`](../../src/evobyte/qecc_verifier.py).

## Por que esta fase existe

A prova da Proposição 4.1 no D044 delimitou matematicamente que códigos puramente circulantes não superam $d=3$ para $[[14, 3]]$ e $[[16, 5]]$. A única maneira de construir códigos estabilizadores com $d \ge 4$ nesses blocos é quebrar a simetria circulante elementar.
Isso pode ser realizado através de arquiteturas quase-cíclicas estruturadas:
1. **Códigos Quase-Cíclicos com Matrizes de Permutação Acopladas:** A matriz de paridade $H_X$ e $H_Z$ é composta por blocos circulantes modificados por permutações de arestas $P \neq I$ ou deslocamentos bicirculantes acoplados ($A, B$).
2. **Construções de Produto Levantado (Lifted Product / Generalized Bicycle):** Códigos CSS baseados em pares de polinômios de Laurent $(a(x), b(x))$ sobre álgebras de grupo não-triviais que garantem $A B^T = B^T A$ (comutatividade simplética) enquanto maximizam o peso do menor elemento no subespaço ortogonal simplético.

Esta fase implementa o motor gerador e validador especializado de matrizes de estabilizadores quase-cíclicas não-circulantes.

## Pergunta falsificável da fase

> O motor de códigos quase-cíclicos acoplados gera famílias de estabilizadores comutantes válidos (comutatividade simplética 100% garantida por construção algébrica) que ultrapassam o limite circulante $d \le 3$ em testes de amostragem em instâncias de calibração?

## Escopo

**Arquivos a criar/editar:**
- `src/evobyte/quasi_cyclic_qecc.py`: classes `QuasiCyclicStabilizer`, gerador de produto levantado e álgebra bicirculante.
- `docs/research/p203-quasi-cyclic-qecc-report.md`: relatório formal de parametrização e tempos de comutação.
- `tests/test_quasi_cyclic_qecc.py`: suíte formal de testes de comutatividade e distância.
- `docs/phases/P203-quasi-cyclic-non-circulant-qecc-engine.md`: atualização de status e evidências.

## Critérios de Saída (Gates)

1. `tests/test_quasi_cyclic_qecc.py` passa 100% verde.
2. Garantia de 100% de comutatividade simplética por construção estrutural nas matrizes geradas.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add src/evobyte/quasi_cyclic_qecc.py \
  docs/research/p203-quasi-cyclic-qecc-report.md \
  tests/test_quasi_cyclic_qecc.py \
  docs/phases/P203-quasi-cyclic-non-circulant-qecc-engine.md
git commit -m "feat(quantum): implement quasi-cyclic non-circulant qecc engine (P203)"
git push -u origin codex/p203-quasi-cyclic-non-circulant-qecc-engine
gh pr create --base main \
  --title "feat(quantum): implement quasi-cyclic non-circulant qecc engine (P203)" \
  --body "Implementa motor de códigos quânticos quase-cíclicos e produto levantado sob D045."
```
