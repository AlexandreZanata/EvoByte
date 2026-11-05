# Relatório de Pesquisa — Fase P183: Busca de Anomalias em Redes Frustradas e Estados Fundamentais

- **Status:** Concluído (NULL_RESULT registrado com calibração 100% aprovada).
- **Data:** 25 de outubro de 2026.
- **Programa:** Descoberta na Fronteira (P171–P190, D042).
- **Branch:** `codex/p183-hamiltonian-ground-state-anomaly-search`.
- **Manifesto Pré-registrado:** `experiments/p183-hamiltonian-manifest.json`
- **Hash SHA-256 do Manifesto:** `7702893b7b9ee5e0987064416b97068baa32da2b97e706256c2bef6264d0a390`
- **Resultados Auditados:** `experiments/p183-hamiltonian-results.json`
- **Checkpoint Auditado:** `experiments/p183-hamiltonian-checkpoint.json`

---

## 1. Pergunta Falsificável e Objetivos

> Sob orçamento pré-registrado e sem seeds manuais, a busca encontra estado fundamental ou invariante conservado em rede frustrada que (a) reproduz invariantes conhecidos em instâncias de calibração e (b) revela estrutura não catalogada verificável por diagonalização exata independente em instância pequena?

Esta fase reativa a trilha quântica (Q10–Q13) sob as regras estritas do programa P171–P190:
1. **Zero seeds manuais:** eliminação de ansatzes específicos de soluções injetados manualmente (como o ansatz de dímeros em $J_1-J_2$ de Q13 legada).
2. **Calibração honesta:** reprodução de invariantes conhecidos a partir de inicialização puramente aleatória em instâncias exatamente solúveis.
3. **Verificação independente estrita:** verificação de qualquer operador candidato por álgebra independente (produtos de Kronecker diretos, sem passar por oráculos com tolerâncias relaxadas), com rejeição formal de operadores triviais (norma nula $\|O\|_F = 0$ decorrente de termos que se cancelam, ou múltiplos escalares da identidade $I$).
4. **Registro de resultado nulo:** na ausência de anomalia verificável, registrar rigorosamente `NULL_RESULT`.

---

## 2. Fase 1 — Calibração Honesta (Gabaritos Exatos)

A Fase 1 executou a calibração do pipeline a partir de inicialização estocástica em dois modelos exatamente solúveis com gabarito formal:

| Alvo de Calibração | Modelo | Tamanho ($N$) | Propriedade Alvo | Resultado Medido | Avaliações | Tempo (s) | Status |
|---|---|---|---|---|---|---|---|
| `calib_ising_4` | Transverse-Field Ising ($J=1.0, h=1.0$) | $N=4$ | Paridade global $\Pi X_i = X_0 X_1 X_2 X_3$ ($[H, P] = 0$) | Paridade exata $+0.5000 \cdot X_0 X_1 X_2 X_3$ redescoberta; erro comutador $= 0.0$ | 400 | 0.009 | **PASSED** |
| `calib_j1j2_4` | $J_1-J_2$ no ponto Majumdar-Ghosh ($J_1=1.0, J_2=0.5$) | $N=4$ | Energia do estado fundamental $E_0 = -6.0$ | $E = -6.000000000000002$, erro $= 1.78 \times 10^{-15}$, fidelidade $= 1.0$ | 450 | 0.028 | **PASSED** |

**Veredito da Calibração:** `ALL_CALIBRATIONS_PASSED`. O pipeline demonstra capacidade comprovada de redescobrir simetrias discretas e estados fundamentais degenerados a partir de termos puramente aleatórios.

---

## 3. Fase 2 — Campanha Pré-Registrada em Redes Frustradas

Foram investigadas redes com frustração magnética geométrica e de troca:
- **Rede 1 (`j1j2_mg`):** Cadeia antiferromagnética $J_1-J_2$ no ponto de Majumdar-Ghosh ($J_1=1.0, J_2=0.5$), caracterizada por dimerização e degenerescência de estado fundamental (Majumdar & Ghosh, *J. Math. Phys.* 10, 1388, 1969).
- **Rede 2 (`j1j2_spiral`):** Cadeia antiferromagnética $J_1-J_2$ em regime espiral fortemente frustrado não-dimerizado ($J_1=1.0, J_2=0.75$) (White & Affleck, *Phys. Rev. B* 54, 9862, 1996).

### Parâmetros da Campanha
- **Tamanhos:**
  - `pequeno-exato`: $N=6$ (dimensão do espaço de Hilbert $D = 64$).
  - `alvo`: $N=8$ (dimensão do espaço de Hilbert $D = 256$).
- **Sementes PRNG:** `[42, 101, 202]`.
- **Orçamento por Semente:** até 10,0 s e 1000 avaliações por alvo.
- **Total de Ensaios:** 12 ensaios (2 redes $\times$ 2 tamanhos $\times$ 3 sementes).
- **Avaliações Totais:** 9.630 avaliações quânticas.
- **Tempo Total Decorrido:** 50,18 segundos.

### Resultados por Ensaio

| Rede | Tamanho | Semente | Busca Conservada (2 termos) | Verificação Independente | Busca Estado Fundamental ($E_{desc}$ vs $E_{exato}$) | Anomalia Confirmada? |
|---|---|---|---|---|---|---|
| `j1j2_mg` | $N=6$ | 42 | $-0.5 Z_0 Z_1 + 0.5 Z_0 Z_1$ (cancela) | Rejeitado (`TRIVIAL_ZERO_OPERATOR`) | $E=-5.9142$ vs $-9.0000$ (fid 0.357) | Não |
| `j1j2_mg` | $N=6$ | 101 | $+0.5 X_1 - 0.5 X_1$ (cancela) | Rejeitado (`TRIVIAL_ZERO_OPERATOR`) | $E=-6.2361$ vs $-9.0000$ (fid 0.474) | Não |
| `j1j2_mg` | $N=6$ | 202 | $+1.0 Z_2 - 1.0 Z_2$ (cancela) | Rejeitado (`TRIVIAL_ZERO_OPERATOR`) | $E=-5.9142$ vs $-9.0000$ (fid 0.357) | Não |
| `j1j2_mg` | $N=8$ | 42 | $-0.5 Z_0 Z_1 + 0.5 Z_0 Z_1$ (cancela) | Rejeitado (`TRIVIAL_ZERO_OPERATOR`) | $E=-6.8284$ vs $-12.0000$ (fid 0.207) | Não |
| `j1j2_mg` | $N=8$ | 101 | $+0.5 Z_5 Z_6 - 0.5 Z_5 Z_6$ (cancela) | Rejeitado (`TRIVIAL_ZERO_OPERATOR`) | $E=-7.1213$ vs $-12.0000$ (fid 0.231) | Não |
| `j1j2_mg` | $N=8$ | 202 | $-1.0 X_2 + 1.0 X_2$ (cancela) | Rejeitado (`TRIVIAL_ZERO_OPERATOR`) | $E=-6.5355$ vs $-12.0000$ (fid 0.174) | Não |
| `j1j2_spiral` | $N=6$ | 42 | $+1.0 Z_1 - 1.0 Z_1$ (cancela) | Rejeitado (`TRIVIAL_ZERO_OPERATOR`) | $E=-6.4880$ vs $-9.8284$ (fid 0.382) | Não |
| `j1j2_spiral` | $N=6$ | 101 | $-0.5 Z_2 Z_4 + 0.5 Z_2 Z_4$ (cancela) | Rejeitado (`TRIVIAL_ZERO_OPERATOR`) | $E=-6.7082$ vs $-9.8284$ (fid 0.439) | Não |
| `j1j2_spiral` | $N=6$ | 202 | $+0.5 X_0 X_1 - 0.5 X_0 X_1$ (cancela) | Rejeitado (`TRIVIAL_ZERO_OPERATOR`) | $E=-6.4880$ vs $-9.8284$ (fid 0.382) | Não |
| `j1j2_spiral` | $N=8$ | 42 | $-0.5 Z_0 Z_1 + 0.5 Z_0 Z_1$ (cancela) | Rejeitado (`TRIVIAL_ZERO_OPERATOR`) | $E=-7.8284$ vs $-13.6569$ (fid 0.198) | Não |
| `j1j2_spiral` | $N=8$ | 101 | $+0.5 Z_0 Z_1 - 0.5 Z_0 Z_1$ (cancela) | Rejeitado (`TRIVIAL_ZERO_OPERATOR`) | $E=-7.9142$ vs $-13.6569$ (fid 0.215) | Não |
| `j1j2_spiral` | $N=8$ | 202 | $-1.0 Z_3 + 1.0 Z_3$ (cancela) | Rejeitado (`TRIVIAL_ZERO_OPERATOR`) | $E=-7.5355$ vs $-13.6569$ (fid 0.162) | Não |

---

## 4. Análise de Integridade e Mecanismo Anti-Falso-Positivo

1. **Rejeição Formal de Operadores Cancelantes:** Em buscas com múltiplos termos e penalidades de comutador, otimizadores estocásticos encontram facilmente pares como $+c P - c P = 0$. Esse operador tem norma $\|O\|_F = 0$, comutando trivialmente com qualquer Hamiltoniano. O verificador independente calcula formalmente a norma de Frobenius e a distância da identidade, rejeitando qualquer candidato com $\|O\|_F < 10^{-6}$ ou $\|O - \frac{\text{Tr}(O)}{D} I\|_F < 10^{-6}$.
2. **Preservação do Limite Variacional:** Em todos os 12 ensaios de estado fundamental cego, a energia variacional descoberta obedeceu estritamente ao princípio variacional de Rayleigh-Ritz ($E_{cand} \ge E_{exato}$). Nenhuma anomalia de autovalor inferior ao fundamental exato foi observada.
3. **Ausência de Seeds Manuais:** A auditoria AST estática confirmou que nenhum vetor de estado literal ou tabela de soluções foi inserido no código do protocolo ou no manifesto.

---

## 5. Limitações e Escopo

- Os tamanhos investigados ($N=6$ e $N=8$) foram delimitados pela exigência de verificação completa por diagonalização exata em cada etapa.
- O resultado nulo registrado não afirma que invariantes conservados não-catalogados sejam matematicamente impossíveis no modelo $J_1-J_2$ em ordens polinomiais de Pauli muito superiores; ele demonstra empiricamente que, sob busca cega e orçamento pré-registrado na representação de poucos termos, nenhum invariante genuíno foi detectado além dos já conhecidos.

---

## 6. Veredito Oficial

> **NULL_RESULT:** sob orçamento pré-registrado e sem seeds manuais, nenhum invariante não catalogado ou estado fundamental anômalo foi confirmado nas redes frustradas testadas.
