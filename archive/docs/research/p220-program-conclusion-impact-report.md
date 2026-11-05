# P220 — Relatório Final de Conclusão e Impacto do Programa D047

**Data:** 2026-10-28
**Programa:** Descoberta com Códigos Quânticos Bicíclicos Bivariados e Geometrias Projetivas (P211–P220, D047)
**Status do Programa:** CONCLUÍDO
**Veredito Global:** `RESULTADO NULO HONESTO: nenhuma descoberta; reconstrução verificada de parâmetros já conhecidos ([[20, 2, 6]], [[16, 2, 4]]), fato conhecido reformulado (paridade de k) e cotas computacionais fracas; limites delimitados em docs/research/claims-ledger-d047.md e docs/bivariate-paper/main.pdf`
**Autor:** Agente Executor EvoByte
**Autor Correspondente Humano:** Alexandre Zanata

---

## 1. Visão Geral e Conclusão do Programa

O programa **D047 (P211–P220)** foi executado e encontra-se oficialmente **CONCLUÍDO**.
O programa investigou a exploração sistemática de álgebras de grupo abelianas bidimensionais $\mathbb{F}_2[\mathbb{Z}_\ell \times \mathbb{Z}_m]$ (códigos bicíclicos bivariados / 2D lifted products) e ações de grupos projetivos $\operatorname{PGL}(2, q)$ e afins bidimensionais $\operatorname{A\Gamma L}(2, 4)$.

Uma auditoria independente do repositório realizada em 2026-10-28 auditou rigorosamente todos os códigos, cálculos de distância, teoremas em Lean 4 e comparações com a literatura mundial. Em estrita conformidade com os princípios do EvoByte de evidência sobre alegações e integridade científica, o programa é encerrado sob o veredito de **RESULTADO NULO HONESTO**:
1. **Reconstruções Verificadas (sem novidade de parâmetros):**
   - Construção explícita do código CSS bicíclico bivariado $[[20, 2, 6]]$ sobre $\mathbb{F}_2[\mathbb{Z}_5 \times \mathbb{Z}_2]$ (postos $9/9$, $k=2$, $d=6$ verificado via SAT incremental com CaDiCaL). Os parâmetros coincidem com cotas já alcançadas na literatura (codetables.de de Markus Grassl); trata-se de uma reconstrução verificada (`RECONSTRUCAO_VERIFICADA` / `KNOWN_PARAMETERS_RECONSTRUCTED`), sem quebra de recorde.
   - Construção explícita do código CSS bicíclico bivariado $[[16, 2, 4]]$ sobre $\mathbb{F}_2[\mathbb{Z}_2 \times \mathbb{Z}_4]$ (postos $7/7$, $k=2$, $d=4$). Também se trata de reconstrução de parâmetros conhecidos (`RECONSTRUCAO_VERIFICADA`). A cota de tabela $d=4$ do snapshot do projeto não foi conferida manualmente por humano (`A_CONFIRMAR_HUMANO`).
2. **Invariante de Paridade (Fato Conhecido):**
   - A demonstração de que $k = 2(\ell m - r)$ é estritamente par em códigos bicíclicos bivariados simétricos comuta com o resultado conhecido da literatura (Bravyi et al., 2024, onde $k = 2 \cdot \dim(\ker A \cap \ker B)$). Constitui fato conhecido reformulado (`CONHECIDO_TRIVIAL`), e não descoberta teórica original.
3. **Cotas Computacionais Fracas:**
   - A enumeração de órbitas sob $\operatorname{PGL}(2, 13)$ em 6-subconjuntos de 14 pontos (menor órbita $91 > 25$) e sob $\operatorname{A\Gamma L}(2, 4)$ em 7-subconjuntos de 16 pontos (menor órbita $160 > 24$) exclui unicamente cobrimentos invariantes sob esses grupos de automorfismos específicos (`COMPUTACIONAL_FRACA`), não demonstrando impossibilidade geral de cobrimentos combinatórios.
4. **Alvos Não Alcançados:**
   - Os alvos $[[20, 3, 5]]$ e $[[18, 3, 5]]$ não foram alcançados sob o orçamento de busca da campanha P216 (`RESULTADO_NULO`).

---

## 2. Tabela de Execução das Fases (P211–P220)

| Fase | Título | Veredito | PR / Commit |
| :--- | :--- | :--- | :--- |
| **P211** | Alvos bivariados e projetivos de gap estreito | Concluída | PR #260 (`c7d4bbe`) |
| **P212** | Motor de grupos projetivos e álgebra bivariada | Concluída | PR #261 (`631e6b7`) |
| **P213** | Gerador e verificador bicíclico bivariado | Concluída | PR #262 (`36e7884`) |
| **P214** | Codificação SAT de distância e BP-OSD | Concluída | PR #263 (`6c07579`) |
| **P215** | Calibração cega bivariada e projetiva | Concluída | PR #264 (`8f0b7b9`) |
| **P216** | Campanha pré-registrada bivariada | Concluída | PR #265 (`ec02e30`) |
| **P217** | Certificados canônicos v4.0.0 e verificador autônomo | Concluída | PR #266 (`f226e5f`) |
| **P218** | Certificação formal no micronúcleo Lean 4 | Concluída | PR #267 (`dd953ce`) |
| **P219** | Auditoria mundial e dossiês de curadores | Concluída | PR #268 (`ab3ff2b`) |
| **P220** | Manuscrito de pesquisa, ledger e decisão D048 | Concluída | PR corrente |

---

## 3. Livro de Alegações Classificadas (Claims Ledger D047)

Conforme registrado em `docs/research/claims-ledger-d047.md`:

| Alegação | Classe | Evidência | Limite |
|---|---|---|---|
| Código bivariado [[20,2,6]] sobre Z5×Z2 existe | `RECONSTRUCAO_VERIFICADA` | recálculo independente: postos 9/9, k=2, d=6 | paridade já alcançada na literatura segundo snapshot do projeto; o snapshot NÃO foi reconferido por humano |
| Código bivariado [[16,2,4]] sobre Z2×Z4 existe | `RECONSTRUCAO_VERIFICADA` | recálculo independente: postos 7/7, k=2, d=4 | o limite de tabela d=4 declarado como "ótimo" NÃO foi verificado e é suspeito; marcar `A_CONFIRMAR_HUMANO` |
| Invariante de paridade: k é par em BB simétrico | `CONHECIDO_TRIVIAL` | Bravyi et al. 2024 (k = 2·dim(ker A ∩ ker B)) | não é contribuição original |
| Cota nula: órbitas mínimas sob PGL(2,13) em C(14,6,3) = 91 > 25 | `COMPUTACIONAL_FRACA` | enumeração de órbitas | só exclui uma classe de simetria; sem valor de descoberta |
| Cota nula: órbitas mínimas sob AGL/AΓL(2,4) em C(16,7,3) = 160 > 24 | `COMPUTACIONAL_FRACA` | enumeração; AGL(2,4) tem ordem 2880 e AΓL(2,4) ordem 5760 (o rascunho confundia os dois) | idem |
| Teoremas Lean `parity_invariant`, `*_orbit_obstruction` | `ESCOPO_LIMITADO` | `omega`/`decide` sobre aritmética e sobre listas de tamanhos escritas à mão | NÃO provam as propriedades sobre os objetos reais; P221 corrige |
| Verificador standalone e certificados v4 | `ENGENHARIA_VALIDA` | execução do verificador | não é resultado matemático |
| [[20,3,5]], [[18,3,5]] não alcançados | `RESULTADO_NULO` | campanha P216 | orçamento esgotado, não impossibilidade |

---

## 4. Auditoria dos Teoremas Lean 4 e Escopo Real

A auditoria identificou com precisão o escopo das formalizações em `lean_proofs/Generated/BivariateDiscovery.lean`:
- **Itens 1–3 e 5–6 (Lemas computacionais válidos):** Verificação mecânica via `decide` da comutatividade simplética binária de matrizes concretas ($[[20, 2, 6]]$, $[[16, 2, 4]]$, Steane) e cobrimento de pares do plano afim $AG(2, 3)$.
- **Itens 4, 7 e 8 (Escopo limitado):**
  - `bivariate_bicycle_parity_invariant` prova meramente $2(\ell m - r) \ne 3$ por `omega` aritmético em $\mathbb{N}$, sem provar a igualdade dos postos de $H_X$ e $H_Z$ nem a representação em anel.
  - `pgl2_13_orbit_obstruction` e `agl2_4_orbit_obstruction` executam `decide` sobre listas numéricas escritas à mão, sem construir a ação de grupo formal sobre subconjuntos.
  - A fase P221 do próximo programa foi desenhada especificamente para substituir esses enunciados por provas formais sobre os objetos matemáticos genuínos.

---

## 5. Pacotes de Curadores e Reprodutibilidade

- Os pacotes em `dist/curator-submissions/p219/` foram gerados sob custódia humana (`pending_human_submission`).
- Ficou registrado explicitamente que esses pacotes representam **reconstruções** de parâmetros conhecidos, devendo ser submetidos apenas a critério humano e sem expectativa de novidade científica.
- O verificador standalone `scripts/verify_bivariate_certificate.py` funciona em Python 3 puro sem dependências (`python3 -S`), verificando os 7 certificados v4.0.0 em tempo médio $< 3.0$\,ms.
- O manuscrito científico completo foi compilado em PDF de 8 páginas (`docs/bivariate-paper/main.pdf`, ~298 KB).

---

## 6. Transição para o Programa D049 (P221–P228)

Com o registro da Decisão **D048**, o programa D047 é encerrado de forma auditável e transparente. O próximo ciclo de pesquisa, **Programa de Progresso Científico Verificável (P221–P228, D049)**, substitui a expansão por:
1. Honestidade formal e recálculo independente (P221).
2. Censo exaustivo e exato de códigos bicíclicos bivariados pequenos (P222).
3. Portão humano obrigatório de auditoria de novidade (P223).
4. Ablação rigorosa do método contra baselines fortes (P224).
5. Busca de fronteira e certificação exata sob condições estritas (P225–P228).
