# Registro de Experimento P76 — Crivo de Fatoração Racional e Decomposição de Divisores

**Data:** 2026-10-13
**Fase:** P76 (Crivo de fatoração racional e decomposição de divisores)
**Veredito:** `ACCEPTED` (0 achados)
**Run ID:** `0d9a07dd23bd6937`
**Revisão (Git Commit):** `63362433de81e0e169f2b17c2f5e72bc09d0b9dc`
**Árvore Git:** Limpa (`dirty: ""`)
**Configuração:** `experiments/p76-config.json` (SHA-256: `d1458b2c2e6cbe8356b6879652f11f6471c1a54f9921d0efed4aacbfac69aa52`)
**Comando:** `bash experiments/p76-run.sh`

---

## 1. Objetivo e Hipótese

A equação diofantina de Erdős–Straus $4/n = 1/x + 1/y + 1/z$ para resíduos resistentes (onde identidades polinomiais lineares não se aplicam) pode ser formulada como uma decomposição sobre divisores de $(nx)^2$:
$$(u y - nx)(u z - nx) = (nx)^2 \quad \text{onde} \quad u = 4x - n$$
e através da forma binária quadrática:
$$(4x - n)(4y - n) = n^2 + 4d \quad \text{com} \quad d = 4xy - n(x+y), \quad z = \frac{nxy}{d}$$

A hipótese investigada e confirmada é que um crivo determinístico sobre divisores $d \mid (nx)^2$ combinado com eliminação modular prévia reduz o espaço de busca em ordens de magnitude em relação à busca linear padrão por coordenadas, com **zero falsos negativos** e certificação diofantina exata.

---

## 2. Resultados Comparativos de Desempenho

O benchmark comparou a busca linear aritmética padrão contra o crivo de fatoração racional em 10 instâncias desafiadoras de números primos ($n \equiv 1 \pmod{24}$ e resíduos quadráticos resistentes módulo 840):

| Instância $n$ | Resíduo mod 840 | Candidatos Baseline | Candidatos Crivo | Redução de Candidatos | Tempo Baseline (s) | Tempo Crivo (s) | Speedup Mensurado |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1009** | 169 (resistente) | 8 | 2 | **4.0x** | 0.000005 | 0.000015 | 0.37x |
| **1033** | 193 | 500,009 | 22 | **22,727.7x** | 0.106035 | 0.000052 | **2,025.6x** |
| **1129** | 289 (resistente) | 1,000,011 | 33 | **30,303.4x** | 0.214911 | 0.000041 | **5,271.7x** |
| **1153** | 313 | 1,638 | 4 | **409.5x** | 0.000361 | 0.000008 | **44.0x** |
| **1201** | 361 (resistente) | 2,500,007 | 114 | **21,929.9x** | 0.534276 | 0.000077 | **6,913.5x** |
| **1249** | 409 | 500,024 | 7 | **71,432.0x** | 0.107508 | 0.000020 | **5,470.6x** |
| **1297** | 457 | 22 | 5 | **4.4x** | 0.000006 | 0.000010 | 0.57x |
| **1321** | 481 | 500,013 | 7 | **71,430.4x** | 0.107022 | 0.000021 | **5,086.1x** |
| **1489** | 649 | 500,108 | 13 | **38,469.8x** | 0.106989 | 0.000021 | **4,994.6x** |
| **1609** | 769 | 500,059 | 22 | **22,730.0x** | 0.107636 | 0.000020 | **5,312.5x** |
| **TOTAL** | — | **6,001,899** | **229** | **26,209.2x** | **1.2847 s** | **0.000286 s** | **4,499.5x** |

### Métricas Consolidadas:
- **Redução total de candidatos:** $26.209,2\times$ (meta mínima: $\ge 100\times$).
- **Aceleração total (Speedup):** $4.499,5\times$ (meta mínima: $\ge 3\times$).
- **Falsos Negativos:** **0** (100% de concordância nas soluções).
- **Validação Exata Diofantina:** 10/10 com residual inteiro $4xyz - n(xy + yz + zx) = 0$ e diferença de frações $0$.

---

## 3. Eficácia da Eliminação Modular

Para cada candidato a divisor $d \le nx$ de $(nx)^2$, a condição necessária e suficiente para que $y, z$ sejam inteiros positivos é $(nx + d) \equiv 0 \pmod u$, onde $u = 4x - n$.

O filtro por pequenos primos ($p \in \{2, 3, 5, 7, 11, 13\}$ com $p \mid u$) eliminou mais de **50% dos divisores candidatos** antes de computar divisões inteiras, permitindo que cada coordenada $x$ avaliasse tipicamente entre 2 e 30 candidatos por passo.

---

## 4. Decomposição de Formas Quadráticas Binárias

A relação $(4x - n)(4y - n) = n^2 + 4d$ com $d \mid nxy$ foi igualmente verificada sobre as instâncias amostradas:
- $n = 1009 \implies d = 11, A = 3, B = 339375 \implies (x, y, z) = (253, 85096, 1974822872)$
- $n = 1033 \implies d = 5, A = 67, B = 15927 \implies (x, y, z) = (275, 4240, 240895600)$
- $n = 1129 \implies d = 1129, A = 11, B = 116287 \implies (x, y, z) = (285, 29354, 8365890)$ (onde $d = n \mid n^2$)
- $n = 1153 \implies d = 17, A = 3, B = 443159 \implies (x, y, z) = (289, 111078, 2177239878)$
- $n = 1201 \implies d = 11, A = 339, B = 4255 \implies (x, y, z) = (385, 1364, 57335740)$

---

## 5. Proveniência e Hardware

- **Plataforma:** Linux 7.1.5 x86_64
- **Python:** 3.12.2
- **PyTorch:** 2.14.0+cu130
- **NumPy:** 2.4.6
- **GPU:** NVIDIA GeForce RTX 4060 Laptop GPU (Driver: 580.173.02)
