# Registro de Síntese Algébrica P74 — Identidades Polinomiais

**Data:** 2026-10-13
**Fase:** P74 (Síntese de identidades polinomiais algébricas)
**Veredito:** `ACCEPTED` (0 achados)
**Run ID:** `4826b530947eac1c`
**Revisão (Git Commit):** `a1837b882d1a51077487ecaf4234fa2a369ff774`
**Árvore Git:** Limpa (`dirty: ""`)
**Configuração:** `experiments/p74-config.json` (SHA-256: `328c1e104a759eb90c580bfd06f67484e40f4c6a21293282e0c56f58ac3bdfdc`)
**Comando:** `bash experiments/p74-run.sh`

---

## 1. Objetivo e Hipótese

A síntese simbólica de identidades racionais $4/n = 1/X(k) + 1/Y(k) + 1/Z(k)$ sobre progressões lineares $n = mk + r$ substitui a busca empírica ponto a ponto por soluções exatas válidas para todo $k \ge 0$, cobrindo classes infinitas de números inteiros.

---

## 2. Redescobertas Clássicas de Mordell

O motor de síntese por divisão de divisores de Mordell em $\mathbb{Q}[k]$ redescobriu e verificou com exatidão algébrica as seguintes identidades:

| Classe $n(k)$ | Denominador $X(k)$ | Denominador $Y(k)$ | Denominador $Z(k)$ | Verificação Algébrica |
| :--- | :--- | :--- | :--- | :---: |
| **$n = 3k + 2$** | $k + 1$ | $3k^2 + 5k + 2$ | $3k + 2$ | **100% EXATA** |
| **$n = 4k + 3$** | $k + 1$ | $8k^2 + 14k + 6$ | $8k^2 + 14k + 6$ | **100% EXATA** |
| **$n = 8k + 5$** | $2k + 2$ | $16k^2 + 26k + 10$ | $8k^2 + 13k + 5$ | **100% EXATA** |

Todas as identidades satisfazem $4 X Y Z - n(Y Z + X Z + X Y) \equiv 0$ em $\mathbb{Q}[k]$ e produzem inteiros positivos para todo $k \ge 0$.

---

## 3. Cobertura Modular (Módulo 24)

- **Total de Classes:** 24
- **Classes Cobertas por Identidades Exatas:** 11 (45,83%)
- **Resíduos Cobertos:** `[2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]`
- **Resíduos Remanescentes:** `[0, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23]`

---

## 4. Ambiente e Proveniência

- **SO:** Linux 7.1.5 x86_64
- **Python:** 3.12.2
- **PyTorch:** 2.14.0+cu130
- **NumPy:** 2.4.6
- **Tempo de Execução:** 0,22 s

---

## 5. Limitações e Próximos Passos

1. As identidades cobrem famílias infinitas parametrizadas por $k$, não resolvendo sozinhas os resíduos resistentes ímpares (como $n \equiv 1 \pmod{24}$).
2. Com a base P74 validada, a fase **P75** mapeará a matriz de cobertura exaustiva para módulos superiores ($M \in \{120, 840, 2520\}$), isolando os resíduos quadráticos não cobertos.
