# P213 — Gerador e verificador de códigos quânticos bicíclicos bivariados (Bivariate Bicycle & 2D Lifted Product Engine)

**Status:** Proposed.
**Programa:** Descoberta com Códigos Quânticos Bicíclicos Bivariados e Geometrias Projetivas (P211–P220, D047).
**Dependência:** P212 concluída e integrada em `main`.
**Owner:** agente executor.
**Branch:** `codex/p213-bivariate-bicycle-2d-lifted-product-engine` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P203-quasi-cyclic-non-circulant-qecc-engine.md`](P203-quasi-cyclic-non-circulant-qecc-engine.md),
[`src/evobyte/quasi_cyclic_qecc.py`](../../src/evobyte/quasi_cyclic_qecc.py).

## Por que esta fase existe

Códigos bicíclicos bivariados (Bravyi et al., 2024) definem matrizes de verificação de paridade $H_X = (A \mid B)$ e $H_Z = (B^T \mid A^T)$ geradas por dois polinômios bivariados $A(x, y)$ e $B(x, y)$ no anel $\mathbb{F}_2[x, y] / \langle x^l - 1, y^m - 1 \rangle$.
Como translações 2D comutam, a condição simplética $H_X H_Z^T = A B + B A = 0 \pmod 2$ é identicamente satisfeita.
O número de qubits físicos é $n = 2lm$. O número de qubits lógicos $k$ e a distância de código $d$ dependem da estrutura de anel e de divisores comuns dos polinômios $A$ e $B$.
Esta fase implementa o gerador parametrizado de códigos bicíclicos bivariados e lifted products 2D, integrando o cálculo exato do número de qubits lógicos $k = \dim(\ker H_X \cap \ker H_Z) - \operatorname{rank}(H_X)$ e a filtragem de peso esparso.

## Pergunta falsificável da fase

> O gerador bivariado produz matrizes estabilizadoras com comutatividade simplética exata de 100%, cálculo determinístico de $k$ em tempo $< 5$ ms por candidato e suporte à parametrização de alvos com $n \in [18, 72]$ qubits?

## Escopo

**Arquivos a criar/editar:**
- `src/evobyte/bivariate_bicycle.py`: gerador de matrizes $H_X, H_Z$ a partir de polinômios bivariados $A, B$, cálculo de $k$, verificação simplética e lifted products 2D.
- `docs/research/p213-bivariate-bicycle-engine-report.md`: validação teórica de dimensões lógicas e densidades esparsas.
- `tests/test_bivariate_bicycle.py`: suíte unitária de corretude algébrica e dimensional.
- `docs/phases/P213-bivariate-bicycle-2d-lifted-product-engine.md`: atualização de status e evidências.

## Critérios de Saída (Gates)

1. `tests/test_bivariate_bicycle.py` passa 100% verde com testes de comutatividade simplética e posto lógico $k$.
2. Verificação de reprodutibilidade exata em instâncias de referência conhecidas da literatura.
3. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add src/evobyte/bivariate_bicycle.py \
  docs/research/p213-bivariate-bicycle-engine-report.md \
  tests/test_bivariate_bicycle.py \
  docs/phases/P213-bivariate-bicycle-2d-lifted-product-engine.md
git commit -m "feat(qecc): implement bivariate bicycle and 2D lifted product engine (P213)"
git push -u origin codex/p213-bivariate-bicycle-2d-lifted-product-engine
gh pr create --base main \
  --title "feat(qecc): implement bivariate bicycle and 2D lifted product engine (P213)" \
  --body "Implementa motor de códigos bicíclicos bivariados sob D047."
```
