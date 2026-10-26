# Relatório Técnico P193: Motor de Síntese de Funções de Prioridade em Bytecode

**Data:** 2026-10-26
**Programa:** Descoberta Algébrica Estruturada e Síntese Funcional (P191–P200, D043)
**Fase:** P193 — Functional Priority Bytecode Engine
**Status:** Validado e auditado

---

## 1. Contexto e Motivação

No paradigma do FunSearch (DeepMind, *Nature* 2024; Romera-Paredes et al.), a evolução direta de configurações combinatórias discretas foi substituída pela evolução de **funções de prioridade contínuas**:
$$\pi_\theta: \mathcal{V} \to \mathbb{R}$$
onde cada elemento candidato ou bloco de órbita recebe um score escalar, e um construtor guloso determinístico monta o objeto combinatorial em ordem de prioridade respeitando as restrições livres de conflito.

Enquanto o FunSearch original utilizava LLMs baseados em processamento de linguagem natural (gerando código Python textual em dezenas de segundos por candidato, sujeito a alucinações sintáticas e latência de inferência de bilhões de parâmetros), o **EvoByte** implementa a síntese funcional no nível do seu micro-bytecode compacto v1:
- Programas de 64 bytes (16 instruções de 32 bits, 8 registradores float32).
- Execução vetorizada pura (NumPy/PyTorch) sem parsing de AST, sem strings e sem chamadas de API externas no loop quente.
- Tabela de lookup pré-computada e bitmasks de $O(1)$ para proibição de linhas afins em $\mathbb{F}_3^n$.

---

## 2. Pergunta Falsificável e Resultados dos Gates

> **Pergunta da Fase P193:**
> *A síntese de funções de prioridade em bytecode atinge throughput de pelo menos $50.000$ construções completas por segundo na GPU/CPU e redescobre com sucesso a calibração de cap set $n=3$ ($|C|=9$) e $n=4$ ($|C|=20$) em menos de 10 segundos?*

### Resumo dos Resultados Experimentais

| Métrica / Portão | Limiar Requerido | Valor Medido | Status |
| :--- | :--- | :--- | :--- |
| **Throughput CPU $n=3$** | $\ge 50.000$ constr/s | **$393.441,1$ constr/s** | Aprovado ($7,87\times$ superior) |
| **Throughput CPU $n=4$** | $\ge 50.000$ constr/s | **$87.868,9$ constr/s** | Aprovado ($1,75\times$ superior) |
| **Throughput GPU $n=3$** (RTX 4060) | $\ge 50.000$ constr/s | **$758.601,8$ constr/s** | Aprovado ($15,17\times$ superior) |
| **Throughput GPU $n=4$** (RTX 4060) | $\ge 50.000$ constr/s | **$2.918.148,2$ constr/s** | Aprovado ($58,36\times$ superior) |
| **Redescoberta $n=3$ ($|C|=9$)** | $< 10,0$ s | **$0,0073$ s** (64 evals) | Aprovado ($1.369\times$ mais rápido) |
| **Redescoberta $n=4$ ($|C|=20$)** | $< 10,0$ s | **$0,4528$ s** (4.618 evals) | Aprovado ($22,08\times$ mais rápido) |
| **Certificação Formal** | 100% livre de tríades | Certificado via `verify_cap_set` | Aprovado |

**Conclusão Falsificável:** Todos os critérios de saída foram estritamente cumpridos com larga margem.

---

## 3. Arquitetura do Motor Funcional

### 3.1. Avaliador Vetorizado de Bytecode (`FunctionalPriorityEvaluator`)
Executa o programa de 16 instruções simultaneamente sobre todos os $N$ pontos do espaço afim (ou batch de blocos de órbita). Os registradores são representados como matrizes $(N, 8)$ de `float32`.
- Opcodes aritméticos (`ADD`, `SUB`, `MUL`, `DIV`, `NEG`) protegidos contra overflow e NaN.
- Funções transcendentais (`EXP`, `LOG`, `POW`, `SQRT`) estritamente limitadas para garantir integridade numérica sem exceções.
- Suporte nativo ao banco de constantes de precisão estendida (`CONST_BANK`) e banco de features (`FEAT`).

### 3.2. Construtor Guloso com Bitmask de Terceiro Ponto (`FastGreedyCapSetBuilder`)
Em $\mathbb{F}_3^n$, para qualquer par de pontos distintos $p, q$, existe um único terceiro ponto que completa uma reta afim:
$$r = -(p + q) \pmod 3$$
O construtor pré-computa a tabela $T[p, q] = r$ e converte em bitmasks de deslocamento inteiro arbitrário `1 << r`.
À medida que pontos são admitidos na ordem de prioridade, a máscara proibida é atualizada em $O(k)$ operações bitwise (`forbidden |= row[q]`), permitindo checagem de admissibilidade em $O(1)$ sem alocações de memória.

### 3.3. Integração com Órbitas de Simetria (`CoveringOrbitPriorityBuilder`)
O motor estende o framework de órbitas de automorfismo desenvolvido em P192 (`CoveringOrbitEngine`):
- As classes de equivalência de subconjuntos sob ação de $\mathbb{Z}_v$ são vetorizadas em matrizes de características (tamanho da órbita, cobertura de $t$-subconjuntos, espectro de diferenças).
- O programa de bytecode pontua as órbitas candidatas e seleciona blocos base até cobertura completa de $C(v, k, t)$.
- Para $C(10, 3, 2)$, a seleção de 20 blocos a partir das 12 órbitas base é executada em apenas $0,083$ ms.

---

## 4. Evidência Experimental e Hardware

Os experimentos foram medidos e gravados no artefato de benchmark snapshotado em:
`docs/research/benchmarks/p193_benchmark_results.json`

- **Ambiente de Medição:** Linux 6.6.137+, Python 3.12.2, PyTorch 2.6.0+cu124.
- **Hardware Host:** Intel Core / NVIDIA GeForce RTX 4060 Laptop GPU (8GB VRAM).
- **Certificados Criptográficos das Descobertas:**
  - Cap set $n=3$, $|C|=9$: `9a2d6560416aeb01ff1a92e105db0d603a1fc6c9a3da24a305988e00c3b8ae67`
  - Cap set $n=4$, $|C|=20$: `8eec6bf1ec3be97193294158913bdf2ebbc465d3ec6e2d142bdf5cf644a034ee`

---

## 5. Próxima Etapa: Ponte para Solver SAT Exato (P194)

Com o motor de prioridade funcional atingindo taxas superiores a $2,9 \times 10^6$ construções/segundo, a fase P194 implementará a ponte de completamento exato:
- As funções de prioridade sintetizadas pelo bytecode constroem o "core denso" do objeto combinatorial (por exemplo, 90% a 95% do tamanho alvo).
- O espaço residual livre de conflito é codificado em CNF (DIMACS) e submetido ao solver SAT integrado (CaDiCaL/Kissat) para fechamento exato dos últimos elementos, eliminando o platô guloso.

---

*Nenhuma cota foi presumida; todo número tem fonte snapshotada.*
