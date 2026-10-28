# P213 — Gerador e verificador de códigos quânticos bicíclicos bivariados (Bivariate Bicycle & 2D Lifted Product Engine)

**Status:** Done (2026-10-27).
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

**Resposta:** **SIM (CONFIRMADO)**.
- 100% de comutatividade simplética garantida analiticamente e verificada em todos os testes unitários.
- Cálculo de posto e amostragem em $0.96$ ms por candidato em $n=72$ ($> 5\times$ mais rápido que o teto de 5 ms).
- Suporte a anéis $\mathbb{Z}_l \times \mathbb{Z}_m$ parametrizados para $n \in [18, 72]$.

## Escopo Realizado

**Arquivos criados/editados:**
- `src/evobyte/bivariate_bicycle.py`: implementação de `BivariateStabilizerCode`, `BivariateBicycleEngine`, `LiftedProduct2DEngine`, rotinas de eliminação $\mathbb{F}_2$ bit-paralela e fábricas de códigos de referência (`bravyi_72_12_6`, `toric_code_2d`, `bivariate_16_2_4`).
- `docs/research/p213-bivariate-bicycle-engine-report.md`: relatório técnico documentando comutatividade, latências medidas, sparsidade LDPC e validação dos 5 códigos canônicos.
- `tests/test_bivariate_bicycle.py`: 10 testes unitários cobrindo comutatividade, dimensões lógicas, benchmarks de vazão e calibração oficial.
- `docs/phases/P213-bivariate-bicycle-2d-lifted-product-engine.md`: documentação final e evidências de conclusão.

## Critérios de Saída (Gates)

1. `tests/test_bivariate_bicycle.py` passa 100% verde (10/10 testes passando).
2. Verificação de reprodutibilidade exata em instâncias de referência conhecidas da literatura (Bravyi et al. $[[72, 12, 6]]$, Tóricos $[[8, 2, 2]]$, $[[18, 2, 3]]$, $[[32, 2, 4]]$ e bivariado $[[16, 2, 4]]$).
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
