# P179 — Relatório do verificador de códigos estabilizadores QECC [[n,k,d]]

**Data:** 2026-10-24
**Fase:** P179 — Descoberta na Fronteira (D042)

## 1. Algoritmo

- Pauli como par binário `(x|z)` em inteiros de bit-vetores; produto simplético
  `<a,b> = |a.x & b.z| + |a.z & b.x| (mod 2)` por `bit_count`.
- Estabilizador válido ⟺ geradores comutam dois a dois e posto GF(2) == nº de
  geradores (eliminação sobre inteiros), com `k = n − m ≥ 0`.
- Distância exata: varredura por peso `w = 1, 2, …`; combinações de posições em
  ordem lexicográfica × atribuições `XYZ` (determinístico, sem aleatoriedade);
  o primeiro Pauli em `C(S) \ S` (comuta com tudo, fora do span) define `d`.
- Fases: formalismo binário assume `+1`; gerador com fase não-`+1` (ou par
  `(fase, string)` com fase fora de `{1, "+1", "+"}`) é rejeitado com
  `(False, "phase not supported")`, nunca aceito silenciosamente.

## 2. Medições (calibração)

| código | geradores | n | k | d medido | tempo (mediana, 9 reps) | teto |
|---|---|---|---|---|---|---|
| Steane [[7,1,3]] | Hamming [7,4,3], X×3 + Z×3 | 7 | 1 | **3** | 0,0005 s | 0,5 s |
| Shor [[9,1,3]] | 6×Z par + 2×X bloco | 9 | 1 | **3** | 0,0012 s | 0,5 s |

Lógicos-testemunha: `XXXIIII` (Steane) e `XXXIIIIII` (Shor), ambos re-checados
como dentro do centralizador e fora do estabilizador. Controles: par X/Z sem
par não comuta → rejeitado com o par; gerador duplicado → posto cai → rejeitado;
`W`, tamanho errado, lista vazia, fase `-1` → `(False, motivo)`. Códigos extras
de sanidade: 5-qubit → d = 3; repetição [3,1,1] → d = 1.

## 3. Limitações declaradas

- Fases restritas a `+1` (padrão das tabelas de Grassl para estabilizadores).
- Escala exponencial contida pela poda por peso: `n = 9` leva ~1 ms; inadequado
  além de ~12 qubits sem melhorias (eliminação por blocos, meet-in-the-middle) —
  declarado abertamente, sem promessa de escala.
- Distância sempre exata por varredura completa até `n`; nunca amostragem.

## 4. Consequência

A P180 pode catalogar alvos `[[n,k,d]]` contra Grassl com este verificador como
portão independente; a P181 pode buscar com a garantia de que todo `d` alegado
é exato e reproduzível bit a bit (varredura determinística, sem RNG).
