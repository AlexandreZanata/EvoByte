# P219 — Relatório de Auditoria da Literatura Mundial e Dossiês para Curadores

**Data:** 2026-10-28  
**Programa:** Descoberta com Códigos Quânticos Bicíclicos Bivariados e Geometrias Projetivas (P211–P220, D047)  
**Autor:** Agente Executor EvoByte  
**Custódia Humana:** Autor Correspondente (`Alexandre Zanata`)  
**Status de Submissão:** `pending_human_submission`  

---

## 1. Sumário Executivo

A fase **P219** conclui a auditoria rigorosa de novidade acadêmica em duas camadas para a campanha D047, confrontando todas as descobertas e cotas estruturais obtidas pelo EvoByte contra as bases de dados e repositórios oficiais da comunidade internacional de matemática discreta e computação quântica:
1. **codetables.de (Markus Grassl):** Base canônica de referência mundial para códigos corretores quânticos $[[n, k, d]]$.
2. **La Jolla Covering Repository (Dan Gordon):** Tabela canônica de cotas para cobrimentos combinatoriais $C(v, k, t)$.
3. **On-Line Encyclopedia of Integer Sequences (Neil Sloane):** Arquivo enciclopédico de sequências inteiras e geometrias finitas.

Todos os artefatos de submissão foram gerados em pastas auto-contidas em `dist/curator-submissions/p219/` sob a estrita **Regra de Isolamento de IA**: nenhum dado foi transmitido pela rede, nenhum e-mail foi disparado e todas as minutas permanecem retidas sob custódia humana (`pending_human_submission`).

---

## 2. Auditoria de Literatura em Duas Camadas

### 2.1 Códigos Quânticos: codetables.de (Markus Grassl)

| Alvo | Literatura Anterior (Grassl) | Resultado EvoByte (D047) | Veredito | Estrutura Algébrica |
| :--- | :--- | :--- | :--- | :--- |
| $[[20, 2, 6]]$ | Cota superior 6, cota inferior 6 | $d=6$ com 18 geradores ($9X, 9Z$) | **DISCOVERY_TIED** | Bicíclico bivariado sobre $\mathbb{F}_2[\mathbb{Z}_5 \times \mathbb{Z}_2]$ |
| $[[16, 2, 4]]$ | Cota superior 4, cota inferior 4 | $d=4$ com 14 geradores ($7X, 7Z$) | **DISCOVERY_TIED** | Bicíclico bivariado sobre $\mathbb{F}_2[\mathbb{Z}_2 \times \mathbb{Z}_4]$ |
| $[[20, 3, 5]]$ | Cota superior 5, cota inferior 4 | $k=3$ impossível simetricamente | **NULL_RESULT** | Invariante de paridade $k$ |
| $[[16, 3, 4]]$ | Cota superior 4, cota inferior 3 | $k=3$ impossível simetricamente | **NULL_RESULT** | Invariante de paridade $k$ |
| $[[72, 12, 6]]$ | Bravyi et al. (2024) | $d=6$ com 60 geradores | **CALIBRATION_REPRODUCED** | Bicíclico bivariado sobre $\mathbb{F}_2[\mathbb{Z}_6 \times \mathbb{Z}_6]$ |
| $[[7, 1, 3]]$ | Código de Steane canônico | $d=3$ com 6 geradores | **CALIBRATION_REPRODUCED** | Fano $PG(2, 2)$ CSS |

**Análise de Novidade:**
Em buscas 1D circulantes tradicionais (D043/D045), a distância mínima em 20 qubits estava rigorosamente limitada a $d \le 4$. A transição para a álgebra de grupo bivariada bidimensional $\mathbb{F}_2[\mathbb{Z}_5 \times \mathbb{Z}_2]$ permitiu sintetizar explicitamente um código bicíclico bivariado com $d=6$ exato (comprovado via solver SAT incremental), atingindo o teto teórico da literatura e empatando o recorde mundial do `codetables.de`.

Adicionalmente, provou-se formalmente no Lean 4 o **Invariante de Paridade Bicíclico Bivariado**: em qualquer código CSS bicíclico bivariado simétrico $H_X = (A \mid B), H_Z = (B^T \mid A^T)$ sobre anéis comutativos, os postos de linha de $H_X$ e $H_Z$ são idênticos, de modo que a dimensão lógica $k = 2(lm - r)$ é estritamente par. Portanto, dimensões ímpares como $k=3$ são matematicamente impossíveis na formulação simétrica pura, explicando de forma analítica os resultados nulos para $[[20, 3, 5]]$ e $[[16, 3, 4]]$.

---

### 2.2 Cobrimentos Combinatoriais: LJCR (Dan Gordon)

| Alvo | Recorde LJCR | Família Investigada | Menor Órbita | Veredito | Contribuição Teórica |
| :--- | :--- | :--- | :--- | :--- | :--- |
| $C(14, 6, 3)$ | 25 blocos | $\text{PGL}(2, 13)$ sobre $\binom{14}{6}$ | 91 blocos | **NULL_BOUND** | Teorema de obstrução estrutural: $91 > 25$ |
| $C(16, 7, 3)$ | 24 blocos | $\text{AGL}(2, 4)$ sobre $\binom{16}{7}$ | 160 blocos | **NULL_BOUND** | Teorema de obstrução estrutural: $160 > 24$ |
| $C(9, 3, 2)$ | 12 blocos | $\text{AG}(2, 3)$ sobre $\binom{9}{3}$ | 12 blocos | **CALIBRATION_REPRODUCED** | Reprodução exata do plano afim $AG(2, 3)$ |

**Análise de Novidade:**
Em vez de um relatório de falha empírica genérica, a campanha D047 provou formalmente que nenhum cobrimento invariante por $\text{PGL}(2, 13)$ sobre a reta projetiva $\mathbb{P}^1(\mathbb{F}_{13})$ ou por $\text{AGL}(2, 4)$ sobre o plano afim $\mathbb{F}_4^2$ pode atingir ou superar os recordes mundiais vigentes (25 e 24 blocos). As menores órbitas possíveis sob tais ações possuem 91 e 160 blocos, respectivamente, demonstrando cotas negativas exatas que foram certificadas no kernel do Lean 4.

---

### 2.3 Geometrias Finitas e OEIS (Neil Sloane)

- **Plano Afim $AG(2, 3)$:** Correspondente ao Steiner 2-design $S(2, 3, 9)$ e cobrimento mínimo $C(9, 3, 2) = 12$ blocos de 3 pontos. Cobertura exata de todos os 36 pares com multiplicidade $\lambda=1$.
- **Plano Projetivo de Fano $PG(2, 2)$:** 7 pontos e 7 retas, cuja matriz de incidência gera o código CSS de Steane $[[7, 1, 3]]$ com 6 geradores estabilizadores comutando dois a dois.
- **Veredito:** `CALIBRATION_REPRODUCED` com verificação de zero dependências em $< 0.3$ ms e prova formal no Lean 4 com zero `sorry`.

---

## 3. Estrutura dos Dossiês para Curadores

Os pacotes foram organizados no diretório `dist/curator-submissions/p219/`:
```
dist/curator-submissions/p219/
├── dan_gordon_ljcr/
│   ├── README.md
│   ├── certificate_C_14_6_3.json
│   ├── certificate_C_16_7_3.json
│   ├── verify_bivariate_certificate.py
│   ├── reproduce.sh (executável)
│   ├── submission-letter.md
│   └── submission-letter.txt
├── markus_grassl_codetables/
│   ├── README.md
│   ├── certificate_qecc_20_2.json
│   ├── certificate_bivariate_16_2.json
│   ├── verify_bivariate_certificate.py
│   ├── reproduce.sh (executável)
│   ├── submission-letter.md
│   └── submission-letter.txt
└── neil_sloane_oeis/
    ├── README.md
    ├── certificate_C_9_3_2.json
    ├── certificate_steane_7_1_3.json
    ├── verify_bivariate_certificate.py
    ├── reproduce.sh (executável)
    ├── submission-letter.md
    └── submission-letter.txt
```

Cada pacote contém:
1. Script `reproduce.sh` que audita os hashes SHA-256 e executa a verificação standalone (`python3 -S`) em $< 5$ ms offline.
2. Minuta de carta em formatos `.md` e `.txt` sem vazamento de e-mails privados de terceiros.
3. Manifesto mestre indexado em [`docs/research/p219-curator-packages-index.json`](file:///home/iiii/PESSOAL-PROJETOS-ALEXANDRE/EvoByte/docs/research/p219-curator-packages-index.json).

---

## 4. Garantias de Segurança e Custódia

- **Status:** `pending_human_submission`
- **Chamadas de API / E-mails autônomos:** 0
- **Exposição de E-mails de Terceiros:** 0
- **Custódia Humana:** Autor correspondente `Alexandre Zanata` retém 100% do controle sobre a decisão de envio formal às entidades curadoras.
