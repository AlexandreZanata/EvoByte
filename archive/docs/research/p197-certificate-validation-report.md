# Relatório de Extração de Certificados e Validação Independente (P197)

**Data:** 2026-10-26  
**Programa:** Descoberta Algébrica Estruturada e Síntese Funcional (P191–P200, D043)  
**Status:** Concluído / Verde  
**Artefatos:**
- Verificador Zero-Dep: [`scripts/verify_structured_certificate.py`](../../scripts/verify_structured_certificate.py)
- Extrator Canônico: [`src/evobyte/certificate_extractor.py`](../../src/evobyte/certificate_extractor.py)
- Certificado $C(15, 8, 4) = 30$: [`experiments/certificates/covering_C_15_8_4_tied_record.json`](../../experiments/certificates/covering_C_15_8_4_tied_record.json)
- Certificado $\text{SQS}(10) = 30$: [`experiments/certificates/covering_C_10_4_3_sqs10.json`](../../experiments/certificates/covering_C_10_4_3_sqs10.json)
- Certificado $[[8, 3, 3]]$ QECC: [`experiments/certificates/qecc_8_3_3_gottesman.json`](../../experiments/certificates/qecc_8_3_3_gottesman.json)
- Suite de Testes: [`tests/test_structured_certificate.py`](../../tests/test_structured_certificate.py)

---

## 1. Resposta à Pergunta Falsificável da Fase

> **Pergunta:** O script standalone de dependência zero valida o certificado extraído da campanha em tempo $< 5$ segundos, acusando erro imediato se qualquer bloco, comutador ou vetor for corrompido artificialmente por mutação de 1 bit?

**Resposta: SIM.**
- **Tempo de Validação:** A verificação completa sob `python3 -S` (isolado sem `site-packages`) consome:
  - $0.76$ ms para o certificado de descoberta $C(15, 8, 4) = 30$ ($1.365$ 4-subconjuntos).
  - $0.24$ ms para a calibração $\text{SQS}(10)$ ($120$ 3-subconjuntos).
  - $0.54$ ms para a calibração quântica Gottesman $[[8, 3, 3]]$ ($276$ erros de peso 1 e 2).
  - Todos $< 1.0$ ms, margem de segurança $> 5.000\times$ em relação ao teto de $5$ segundos.
- **Sensibilidade a Mutações Adversariais:** Taxa de detecção de $100\%$ em todos os cenários de corrupção deliberada (código de saída `1` imediato).

---

## 2. Especificação do Formato de Certificado Canônico (v2.0.0)

O formato foi desenhado para transparência e portabilidade matemática absoluta, sem dependência de classes internas ou formatos binários:

```json
{
  "certificate_version": "2.0.0",
  "certificate_type": "covering_design",
  "target_id": "covering_C_15_8_4",
  "verdict": "DISCOVERY_TIED",
  "parameters": {
    "v": 15,
    "k": 8,
    "t": 4,
    "claimed_blocks": 30,
    "published_best": 30
  },
  "candidate": {
    "indexing": 1,
    "num_blocks": 30,
    "blocks": [
      [1, 2, 3, 4, 5, 6, 11, 13],
      ...
    ],
    "symmetry": {
      "group": "Z_15",
      "order": 15,
      "num_base_blocks": 2,
      "base_blocks": [
        [1, 2, 3, 4, 5, 6, 11, 13],
        [1, 2, 3, 4, 6, 8, 9, 12]
      ]
    }
  },
  "metadata": {
    "generator": "EvoByte-Structured-SAT-Engine",
    "git_commit": "38dcbc9068d955b88f9d371b89ee52e4ac02fab2",
    "literature_record": "LJCR Gordon (1996) C(15, 8, 4) <= 30",
    "source_campaign": "P196",
    "timestamp": "2026-10-26T17:19:28Z"
  },
  "sha256_checksum": "f349dd840e20d797fb33002a7d36d24bce4f3465f6aac204e7f58ece2f628af7"
}
```

---

## 3. Auditoria dos Certificados Gerados

### 3.1. Cobertura $C(15, 8, 4) = 30$ (`DISCOVERY_TIED`)
- **Problema:** Cobrir todos os $\binom{15}{4} = 1.365$ subconjuntos de $4$ elementos de um universo de $15$ pontos usando blocos de tamanho $8$.
- **Recorde da Literatura:** $C(15, 8, 4) \le 30$ (Gordon LJCR 1996).
- **Descoberta:** Exatamente $30$ blocos obtidos pela órbita cíclica $Z_{15}$ de apenas $2$ blocos base:
  - Base 1 (1-indexada): $(1, 2, 3, 4, 5, 6, 11, 13)$
  - Base 2 (1-indexada): $(1, 2, 3, 4, 6, 8, 9, 12)$
- **Verificação Externa:** $1.365 / 1.365$ subconjuntos cobertos, $0$ repetições inválidas, $0.76$ ms em Python puro.

### 3.2. Steiner Quadruple System $\text{SQS}(10)$ ($C(10, 4, 3) = 30$)
- **Problema:** Cobrir todos os $\binom{10}{3} = 120$ trios de $10$ pontos com blocos de $4$ pontos.
- **Teorema de Mills (1979):** Limite exato $C(10, 4, 3) = 30$.
- **Estrutura:** Órbita $Z_{10}$ de $3$ blocos base:
  - $(1, 2, 3, 7)$, $(1, 2, 4, 5)$, $(1, 3, 5, 8)$
- **Verificação Externa:** $120 / 120$ trios cobertos com zero dependências em $0.24$ ms.

### 3.3. Código Estabilizador Quântico Gottesman $[[8, 3, 3]]$
- **Problema:** Síntese cega de $5$ geradores de Pauli independentes e comutativos em $8$ qubits com distância $d \ge 3$.
- **Geradores Identificados:**
  1. `YYXYYYYY`
  2. `ZYYYIXXI`
  3. `IYZZZYZI`
  4. `IYYIXZYX`
  5. `ZXXZIIZY`
- **Álgebra Simplética Independente:**
  - Produto simplético nulo para todos os $\binom{5}{2} = 10$ pares.
  - Posto em $\text{GF}(2) = 5$.
  - Distância $d=3$: Todos os $276$ erros de Pauli de peso 1 ($24$) e peso 2 ($252$) anticomutam com ao menos um gerador, provando $d \ge 3$ rigorosamente em $0.54$ ms.

---

## 4. Matriz de Testes de Estresse e Corrupção Deliberada

| Teste | Mutação Aplicada | Resultado Esperado | Detecção | Tempo |
|---|---|---|---|---|
| **Integridade SHA-256** | 1 bit alterado no hash do payload | Falha na verificação de integridade | `[FAILED] SHA-256 payload checksum mismatch` | 0.35 ms |
| **Elemento em Bloco** | $(15, 8, 4)$ bloco 0 elemento 13 alterado para 14 | Descoberta de subconjuntos não cobertos | `[FAILED] 13/1365 4-subsets uncovered` | 0.65 ms |
| **Remoção de Bloco** | Remoção de 1 bloco (29 blocos restantes) | Violação de cobertura combinatorial | `[FAILED] 21/1365 4-subsets uncovered` | 0.60 ms |
| **Elemento Fora de Faixa** | Elemento 11 inserido em design com $v=10$ | Violação de limites de parâmetros | `[FAILED] element 11 out of range 1..10` | 0.22 ms |
| **Elemento Duplicado** | Elemento duplicado dentro do mesmo bloco | Violação de cardinalidade de subconjunto | `[FAILED] duplicate element in block` | 0.21 ms |
| **Comutação QECC** | 1 letra Pauli alterada (`Y` $\to$ `Z`) no gerador 0 | Violação de álgebra simplética | `[FAILED] generators do not commute` | 0.29 ms |
| **Posto GF(2) QECC** | Gerador duplicado (quebrando independência linear) | Redução do posto $\text{GF}(2) < 5$ | `[FAILED] linearly dependent over GF(2)` | 0.25 ms |
| **Distância Falsificada** | Alegação de $d=4$ em código com $d=3$ | Descoberta de operador lógico de peso 3 | `[FAILED] undetected logical operator` | 0.38 ms |
| **Argumentos CLI** | Arquivo inexistente ou JSON corrompido | Código de saída 2 ou 1 | Mensagem de erro informativa | 0.15 ms |

---

## 5. Garantia Arquitetural de Dependência Zero

A análise da Árvore Sintática Abstrata (AST) executada em [`tests/test_structured_certificate.py`](../../tests/test_structured_certificate.py) inspeciona todos os nós `ast.Import` e `ast.ImportFrom` de [`scripts/verify_structured_certificate.py`](../../scripts/verify_structured_certificate.py) e comprova:
- Módulos importados: `sys`, `os`, `json`, `hashlib`, `math`, `itertools`, `time`, `typing`.
- Pacotes externos detectados: **0** (`numpy`, `pysat`, `scipy`, `evobyte` expressamente ausentes).
- Executável com `python3 -S` confirmado.
