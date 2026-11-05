# Registro de Cobertura Modular P75 — Matriz de Classes de Congruência

**Data:** 2026-10-13
**Fase:** P75 (Matriz de cobertura de classes de congruência modulares)
**Veredito:** `ACCEPTED` (0 achados)
**Run ID:** `ec4a9cc20ecc8a44`
**Revisão (Git Commit):** `c09790fe5784a8d7a664affcba44cc45243dc368`
**Árvore Git:** Limpa (`dirty: ""`)
**Configuração:** `experiments/p75-config.json` (SHA-256: `413511335a6cadfbae82c0048e8cbe364c48b137dbb2c4cf6c9946d4f26be69f`)
**Comando:** `bash experiments/p75-run.sh`

---

## 1. Objetivo e Hipótese

Mapear exaustivamente a cobertura modular de Erdős–Straus para módulos $M \in \{24, 120, 840, 2520\}$ sob identidades polinomiais exatas em $\mathbb{Q}[k]$, identificando exatamente quais classes possuem identidades associadas e isolando com precisão formal as classes irredutíveis (resíduos quadráticos coprimos).

---

## 2. Resultados da Matriz de Cobertura Modular

| Módulo $M$ | Classes Totais | Classes Cobertas | Classes Resistentes | Cobertura (%) | Checksum Imutável (SHA-256) |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **24** | 24 | 23 | 1 | 95,8333% | `6bfd85f765f15962ed89fe5d14bc50bd4d3581ad497772e3d9ca0cceaccaccd5` |
| **120** | 120 | 118 | 2 | 98,3333% | `9995a8992a77ea358fcd98b1f5588d013b1c51749bf7f4dde423997a004aea63` |
| **840** | 840 | 834 | 6 | 99,2857% | `34ce9589bc7cd7684415a67ea86f1dd85ab765c8137d62c3b3d1818cdc287fa7` |
| **2520** | 2520 | 2502 | 18 | 99,2857% | `1eb742dbb926acacf6d14db47f3ddc1e6f11ebb63aaf7618ea43e9a7439b0aef` |

100% das 834 classes cobertas modulo 840 possuem identidades polinomiais exatas verificadas algebricamente ($4XYZ \equiv n(YZ + XZ + XY)$) que avaliam estritamente em inteiros positivos para todo $k \ge 0$.

---

## 3. Isolamento dos Resíduos Quadráticos Resistentes

Modulo 840 ($840 = 2^3 \times 3 \times 5 \times 7$), as exatamente 6 classes que sobrevivem a todas as identidades lineares são:
$$n \equiv 1, 121, 169, 289, 361, 529 \pmod{840}$$

Estas correspondem com precisão absoluta aos quadrados de números coprimos a 840:
- $1^2 \equiv 1$
- $11^2 = 121$
- $13^2 = 169$
- $17^2 = 289$
- $19^2 = 361$
- $23^2 = 529$

Como demonstrado por Mordell (1967), identidades polinomiais lineares não podem cobrir resíduos quadráticos em virtude da teoria de reciprocidade quadrática e divisibilidade modular.

---

## 4. Ambiente e Proveniência

- **SO:** Linux 7.1.5 x86_64
- **Python:** 3.12.2
- **PyTorch:** 2.14.0+cu130
- **NumPy:** 2.4.6
- **Tempo de Execução:** 3,52 s

---

## 5. Limitações e Próximos Passos

1. As 6 classes resistentes módulo 840 constituem o obstáculo estrutural fundamental da abordagem analítica de Mordell.
2. Com a matriz de cobertura e os resíduos resistentes formalmente mapeados e blindados com checksum imutável em P75, a fase **P76** implementará a exportação e compilação do catálogo de teoremas para Lean 4 (`P76Theorems.lean`), verificando com o kernel formal do Lean 4 a totalidade das identidades sintetizadas.
