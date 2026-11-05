# Dossiê Científico e Matriz de Rastreabilidade da Publicação de Sistemas (P160)

**Artigo:** *EvoByte: Massively Parallel Evolutionary Discovery of Symbolic Programs via Ultra-Compact Bytecode and Deterministic Cascade Verification*
**Autoria:** Alexandre Zanata & EvoByte Research Consortium
**Status:** Concluído e Auditado (Fase P160)
**Data:** 2026-10-21
**Alvo de Publicação:** Conferências e Periódicos de Topo em Sistemas / Computação Evolutiva (GECCO, NeurIPS, IEEE TEVC, JMLR)
**Artefato Compilado:** [`docs/paper/main.pdf`](../paper/main.pdf) (7 páginas, compilação pdfLaTeX TeX Live 2023/Debian sem advertências)
**Código-Fonte LaTeX:** [`docs/paper/main.tex`](../paper/main.tex) e referências em [`docs/paper/references.bib`](../paper/references.bib)

---

## 1. Escopo e Estrutura do Manuscrito

O manuscrito consolida formalmente todo o programa de pesquisa experimental desenvolvido nas Fases P153–P159 sob o contrato falsificável da **Hipótese H1** (`docs/HYPOTHESIS.md`):

1. **Section 1 (Introduction):** Limitações fundamentais das árvores sintáticas (bloat, fragmentação de memória, perda de paralelismo SIMD/GPU) e formulação da hipótese H1.
2. **Section 2 (EvoByte Virtual Machine Architecture):** Especificação da VM linear de 64 bytes, registradores protegidos sem divergência de warp GPU, execução totalmente residente em VRAM.
3. **Section 3 (Hierarchical Verification Cascade S0–S3):** Decomposição em 4 estágios com filtragem grosseira em 32 pontos e terminação adaptativa precoce.
4. **Section 4 (Experimental Protocol):** Protocolo estrito de tempo de parede via `time.perf_counter()`, sementes independentes, alvos Level-A e Level-B, e hardware de referência (NVIDIA RTX 4060 Laptop GPU 8GB VRAM).
5. **Section 5 (Empirical Results & Statistical Verdict):** Avaliação formal dos 5 critérios falsificáveis de H1, teste não-paramétrico de Wilcoxon com ajuste Bonferroni–Holm ($p \le 0.01$) e fronteira de Pareto.
6. **Section 6 (Architectural Ablation Studies & Negative Results):** Análise dos 9 componentes medidos e relato honesto do resultado negativo do gerador neural micro (ADR-0010 / Fase P12).
7. **Section 7 (Generalization, Anti-Bloat & Extrapolation):** Splits cegos $X_{\text{hidden}}$ e $X_{\text{extrap}}$, taxa de explosão nula ($0{,}0\%$) e média compacta de 5,2 opcodes.
8. **Section 8 (Reproducibility & Open Science):** Contêiner hermético via Dockerfile com `--network none` e pacote aberto Zenodo com 461 arquivos e 100% integridade SHA-256.
9. **Section 9 (Related Work) & Section 10 (Conclusion).**

---

## 2. Matriz de Rastreabilidade das Evidências Empíricas

Cada dado quantitativo reportado no manuscrito possui rastreabilidade exata aos ensaios medidos nas fases anteriores:

| Alegação no Manuscrito | Valor Reportado no Artigo | Fonte de Dados / Fase de Origem | Validação Experimental |
|---|---|---|---|
| **Speedup do Verificador em Cascata (S1)** | $15{,}51\times$ | `experiments/p157-ablations/`, Fase P157 | Medido em 512 pontos com sementes reais |
| **Speedup da Terminação Precoce (S2)** | $3{,}00\times$ | `experiments/p157-ablations/`, Fase P157 | Medido com threshold adaptativo |
| **Speedup da Residência em VRAM GPU** | $2{,}60\times$ | `experiments/p157-ablations/`, Fase P157 | GPU VRAM vs. Host CPU round-trip |
| **Rejeição do Gerador Neural (P12)** | $0{,}38\times$ (slowdown de $2{,}6\times$) | ADR-0010, `docs/DECISIONS.md`, P12 | Rejeitado formalmente por degradar CVPS |
| **Veredito Wilcoxon (EvoByte vs. Random)** | $W = 55{,}0$, $p_{\text{Holm}} = 2{,}49 \times 10^{-3}$ | `docs/research/p158-h1-verdict-report.md`, P158 | $p_{\text{Holm}} \le 0{,}01$ comprovado |
| **MSE Médio EvoByte vs. Random** | EvoByte: $0{,}9787$ vs. Random: $36{,}417$ | `experiments/p158-verdict/`, P158 | IC 95% empírico bootstrap não sobreposto |
| **Taxa de Redescoberta de Alvos Primários** | $80{,}0\%$ ($\ge 4/5$ sementes) | `experiments/p154-matrix/`, P154 | Redescoberta Level-A comprovada |
| **Generalização em Extrapolação ($X_{\text{extrap}}$)** | $80{,}0\%$ sucesso, $0{,}0\%$ explosão | `experiments/p156-generalization/`, P156 | Zero leakage entre splits |
| **Tamanho Médio das Expressões Descobertas** | $5{,}2$ opcodes | `experiments/p156-generalization/`, P156 | Anti-bloat estrutural confirmado |
| **Envelope Não-Dominado de Pareto** | 5 pontos ótimos (Complexidade vs. MSE) | `experiments/p158-verdict/`, P158 | Mapeado sobre baselines honestos |
| **Reprodutibilidade Hermética em Contêiner** | `docker run --network none` | `Dockerfile`, `Makefile`, Fase P159 | Verificação 100% verde sem rede |
| **Pacote de Dados Abertos para Zenodo** | 461 arquivos, 3.38 MB, 100% SHA-256 | `scripts/export_zenodo_bundle.py`, P159 | Checksums verificados |

---

## 3. Veredito Final da Frente 2 (D039 / P153–P160)

Com a consolidação deste manuscrito e seu dossiê:
1. Todas as questões levantadas na auditoria histórica D013 foram integralmente superadas por medições empíricas com telemetria real em tempo de parede.
2. A **Hipótese H1** é formalmente declarada e validada como **SUPPORTED** através de testes estatísticos rigorosos ($p < 0{,}01$).
3. O pacote de submissão do artigo científico está pronto para disseminação na comunidade de inteligência artificial, computação evolutiva e sistemas acelerados.
