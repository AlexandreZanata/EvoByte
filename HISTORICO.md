# Histórico do EvoByte (Ciclo Legado v1: P00 — P234)

Este documento registra o histórico técnico, científico e metodológico desenvolvido no projeto **EvoByte** entre setembro e novembro de 2026, arquivado na branch [`archive/legacy-history`](https://github.com/AlexandreZanata/EvoByte/tree/archive/legacy-history) e na tag [`archive-v1-legacy`](https://github.com/AlexandreZanata/EvoByte/releases/tag/archive-v1-legacy).

---

## 1. Visão Geral e Hipótese Inicial

O projeto EvoByte foi concebido para testar uma hipótese central de computação científica:
> *A busca evolutiva massivamente paralela em bytecode ultra-compacto com verificação determinística em cascata pode descobrir programas simbólicos e estruturas matemáticas com ordem de magnitude maior de eficiência em relação a buscas estocásticas não estruturadas.*

Ao longo de 234 microfases (P00 a P234) e 51 decisões registradas em `DECISIONS.md` (D001 a D051), o projeto evoluiu de uma máquina de busca genérica para síntese formal em provadores interativos (Lean 4) e exploração estruturada de Códigos Quânticos Corretores de Erros (QECC) com garantias exatas.

---

## 2. Linha do Tempo e Principais Programas

### 2.1 Fase Fundacional e Sistemas (P00 — P14)
- **Bytecode v0:** Arquitetura de 16 instruções de 4 bytes (tamanho fixo de 64 bytes por indivíduo), 8 registradores, 16 opcodes matemáticos e banco de constantes.
- **Motores de Execução:** Interpretador de referência determinístico em CPU (NumPy) e interpretador residente em GPU (PyTorch).
- **Verificador em Cascata:** Filtros progressivos L1 (amostragem rápida / domínio seguro) e L2 (verificação de domínio estrita) com término antecipado.
- **Resultados:** Redescoberta empírica da 3ª Lei de Kepler; teste de geradores neurais micro vs. algoritmos genéticos (D010).

### 2.2 Trilha Quântica Q-Forge e Auditoria de Evidências (Q00 — Q13, P15 — P39)
- **Representação Pauli:** Codificação simplética de operadores de Pauli ($X, Z$) em palavras de bits compactas.
- **Oráculos e Hamiltonianos:** Avaliação de estados fundamentais e circuitos quânticos de baixa profundidade.
- **Auditoria de Integridade (D013–D016):** Identificação de gargalos em medições preliminares, introdução de isolamento estrito de splits de treino/extrapolação e proibição de interpolações não medidas.

### 2.3 Síntese Algébrica Diofantina e Formalização em Lean 4 (P40 — P112)
- **Problema de Erdős-Straus e Schinzel:** Busca por identidades polinomiais para frações egípcias $4/n = 1/x + 1/y + 1/z$ e generalizações $a/n$.
- **Compilador para Lean 4:** Geração automática de provas no kernel formal do Lean 4 / Mathlib.
- **Meta-Táticas e Fibrados Algébricos:** Criação das meta-táticas `evobyte_solve` e `dioph_surface`, explorando parametrizações de superfícies cúbicas e anéis de quatérnios de Hurwitz.
- **Produção Formal:** Mais de 1.900 teoremas compilados no kernel Lean 4 com zero tokens `sorry`.

### 2.4 Combinatória Aditiva, Ramsey, Grafos e Discrepância (P113 — P144)
- **Conjuntos de Sidon:** Busca e formalização de conjuntos $B_2[1]$, energia aditiva e desigualdades de Plünnecke-Ruzsa.
- **Teoria Extremal de Grafos:** Formalização dos teoremas de Mantel-Turán, grafos de Paley e cotas de Zarankiewicz.
- **Progressões Aritméticas e Discrepância:** Conjuntos livres de 3-AP de Salem-Spencer, cotas de Roth, problema da discrepância de Erdős (EDP) e sistemas de recobrimento de Hough.

### 2.5 Auditoria Crítica, Retratações Honestas e Rigor Metodológico (P145 — P170)
- **Decisão D040 / D041:** Auditoria detalhada que identificou que 49 identidades diofantinas eram válidas em $\mathbb{Q}$ mas não garantiam inteiros em $\mathbb{Z}$, e retificou alegações frente a baselines fortes (PySR e Classical-SR).
- **Ledger de Alegações:** Criação de trava mecânica (`claim_audit.py`) para impedir afirmações sem certificado fiel.
- **Resultado Nulo Honesto:** Publicação de pacote arquivável com cadeia imutável SHA-256 e manuscrito de resultados nulos metodologicamente rigorosos.

### 2.6 Códigos Quânticos Corretores de Erros (QECC) e Simetrias (P171 — P221)
- **Descoberta na Fronteira (P171–P190):** Investigação de covering designs (LJCR) e números de Schur fracos (OEIS).
- **Barreira Circulante (P191–P200, D044):** Prova estrutural de que códigos CSS puramente circulantes possuem distância $d \le 3$ em blocos de 14 e 16 qubits (Proposição 4.1).
- **Quebra de Simetria (P201–P210, D046):** Introdução de grupos afins $AGL(1, q)$, diédricos $D_m$ e códigos quase-cíclicos, empatando recordes mundiais em $[[14, 3, 4]]$ e $[[16, 5, 4]]$ (tabelas de Markus Grassl).
- **Códigos Bicíclicos Bivariados (BB) e Produtos Levantados 2D (P211–P221, D047/D048):**
  - Espaço de busca sobre álgebras bivariadas $\mathbb{F}_2[Z_\ell \times Z_m]$.
  - Verificação exata de distância mínima através de redução para SAT (solver CaDiCaL) e decodificação via BP-OSD.
  - Certificação no kernel Lean 4 (P221) com recálculo estrito de postos e distâncias para os códigos reais.

### 2.7 Censo Exaustivo e Transição de Baixo Custo (P222, P229 — P234)
- **P222 (Censo Parcial):** Realização de censo exaustivo determinístico para parâmetros $\ell \cdot m \le 10$, catalogando 30.285 instâncias com cálculos de comutação, posto simplético e distância mínima.
- **D051 e ADR-0011:** Decisão de arquivar a abordagem computacionalmente pesada de enumeração universal e pré-registrar uma proposta de baixo custo orientada a propriedades algébricas certificadas, verificação rápida e identidades exatas.

---

## 3. Resumo das Decisões Principais (DECISIONS.md)

| ID | Data | Resumo da Decisão |
|---|---|---|
| **D001** | 2026-09-29 | Licença MIT integral para reprodutibilidade aberta. |
| **D002** | 2026-09-29 | Referência CPU determinística (NumPy); PyTorch antes de Triton/CUDA. |
| **D003** | 2026-09-29 | Bytecode v0 de 64 bytes e registradores fixos. |
| **D004** | 2026-09-29 | Verificação em cascata com corte antecipado em falhas de domínio. |
| **D010** | 2026-09-29 | Abandono de gerador neural micro no laço principal devido a sobrecusto sem ganho. |
| **D022** | 2026-10-13 | Transição para provas formais no kernel Lean 4 (P73–P80). |
| **D040** | 2026-10-21 | Retratação formal e auditoria rigorosa de identidades e baselines empíricos. |
| **D042** | 2026-10-25 | Registro de Resultado Nulo Honesto nas buscas de fronteira (P171–P190). |
| **D044** | 2026-10-26 | Empate de recorde mundial em $C(15, 8, 4) = 30$ e cota negativa $d \le 3$ em CSS circulante. |
| **D046** | 2026-10-27 | Empate de recorde mundial em QECC $[[14, 3, 4]]$ e $[[16, 5, 4]]$ via simetrias generalizadas. |
| **D048** | 2026-10-28 | Conclusão do programa bivariado P211–P220 e reconhecimento de limites de novidade. |
| **D049** | 2026-10-28 | Programa de progresso científico verificável com Lean e recálculo sobre objetos reais. |
| **D051** | 2026-11-05 | Arquivamento de P222 com estado parcial e proposta do ciclo de baixo custo P229–P234. |

---

## 4. Como Acessar o Repositório Legado

O histórico integral do repositório pode ser explorado a qualquer momento:

```bash
# Obter e inspecionar a branch arquivada
git fetch origin archive/legacy-history
git checkout archive/legacy-history

# Ou navegar pela tag permanente
git checkout archive-v1-legacy
```

Todos os 200+ commits anteriores, relatórios de pesquisa, especificações de fases (`docs/phases/`), implementações e suítes de testes estão intactos nessas referências.
