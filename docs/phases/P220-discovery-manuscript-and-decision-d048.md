# P220 — Manuscrito de pesquisa, pacote arquival Zenodo e registro da decisão D048

**Status:** Done.
**Programa:** Descoberta com Códigos Quânticos Bicíclicos Bivariados e Geometrias Projetivas (P211–P220, D047).
**Dependência:** P219 concluída e integrada em `main`.
**Owner:** agente executor; autor correspondente humano revisa o manuscrito final.
**Branch:** `codex/p220-discovery-manuscript-and-decision-d048` (a partir de `main`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [`docs/phases/P210-discovery-manuscript-and-decision-d045.md`](P210-discovery-manuscript-and-decision-d045.md),
[`docs/generalized-paper/main.pdf`](../generalized-paper/main.pdf).

## Por que esta fase existe

Todo programa científico do EvoByte conclui de forma transparente, publicável e auditável:
1. **Manuscrito Científico Compilado:** Produção de artigo LaTeX completo (`docs/bivariate-paper/main.tex` e `main.pdf`), relatando honestamente os resultados obtidos com códigos bicíclicos bivariados e geometrias projetivas.
2. **Pacote Arquival Zenodo e Contêiner Hermético:** Empacotamento de todos os dados, códigos, certificados e ambiente em contêiner Docker reproduzível offline (`--network none`).
3. **Decisão Formal D048:** Registro indelével da decisão e veredito final em `docs/DECISIONS.md`.
4. **Fechamento e Consolidação:** Merge ordenado de todos os PRs e branches na `main`.

## Pergunta falsificável da fase

> O manuscrito científico compila em PDF sem warnings críticos, o contêiner de reprodutibilidade passa 100% dos testes sob isolamento de rede (`make verify`), e a decisão D048 encerra o programa de forma rastreável e auditável?

## Escopo

**Arquivos a criar/editar:**
- `docs/bivariate-paper/main.tex`, `Makefile`, `references.bib`: código-fonte e manuscrito compilado em PDF (`docs/bivariate-paper/main.pdf`).
- `docs/research/claims-ledger-d047.md`: livro de alegações classificadas (ver "Correções obrigatórias").
- `docs/research/p220-program-conclusion-impact-report.md`: relatório final de impacto e conclusão.
- `docs/DECISIONS.md`: registro da decisão D048.
- `docs/ROADMAP.md` e `docs/phases/README.md`: sincronização de estado final do programa.
- `tests/test_p220_manuscript.py`: testes de integridade das afirmações e hashes citados no artigo.
- `docs/phases/P220-discovery-manuscript-and-decision-d048.md`: atualização de status e evidências.

## Correções obrigatórias de alegações (auditoria do revisor, 2026-10-28)

Uma auditoria independente do repositório (recálculo dos códigos, leitura dos `.lean`)
mediu que o rascunho de `docs/bivariate-paper/main.tex` (não rastreado) **superestima**
os resultados. Esta fase NÃO pode publicar esse texto. Aplique **exatamente** as
correções abaixo; não acrescente nenhuma alegação nova.

### C1 — Criar `docs/research/claims-ledger-d047.md`

Tabela com as colunas `Alegação | Classe | Evidência | Limite`. Copie estas linhas
literalmente (pode traduzir o cabeçalho; não altere as classes):

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

### C2 — Edições obrigatórias em `main.tex`

1. Título sugerido: `Verified Reconstruction of Bivariate Bicycle Codes and Computational Orbit Bounds: A Negative-Results Report`.
2. Abstract e Introdução: remover "four primary scientific contributions", "discovery", "unconditional", "definitive", "successfully demonstrated". Substituir por duas contribuições: (i) pipeline de verificação reproduzível; (ii) classificação honesta (reconstruções, resultado conhecido, cotas fracas, nulos).
3. Teorema 2.1 (paridade) vira `Proposition (known)` com a frase "This fact is known; see Bravyi et al. (2024)." e a prova correta abaixo no lugar da atual (a atual é imprecisa):
   *Prova.* Em `R = F2[Z_l × Z_m]` (comutativo), o posto de `(A|B)` é `dim(AR + BR)`. A transposta de `A` é a multiplicação por `ι(A)`, onde `ι: x→x⁻¹, y→y⁻¹` é automorfismo de anel. Logo `rank(B^T|A^T) = dim(ι(B)R + ι(A)R) = dim(ι(AR + BR)) = dim(AR + BR)`. Então `r_X = r_Z` e `k = n − r_X − r_Z = 2(lm − r)`. ∎
4. Rótulo `DISCOVERY_TIED` → `KNOWN_PARAMETERS_RECONSTRUCTED` em todo o texto e tabelas. Na Tabela de códigos, coluna "Literature Bound": acrescentar nota de rodapé "valores do snapshot do projeto; não reconferidos por humano; [[16,2,4]] A_CONFIRMAR_HUMANO".
5. Teoremas de órbita viram `Proposition (computational)`. Corrigir o grupo: o código do projeto usa AΓL(2,4) (ordem 5760, com Frobenius); escrever "AΓL(2,4) (order 5760)" e dizer que AGL(2,4) (ordem 2880) é recomputado em P221.
6. Seção Lean: substituir "zero gaps ... faithful" por descrição exata: itens 1–3 e 5–6 são lemas computacionais sobre matrizes concretas; itens 4, 7 e 8 são lemas aritméticos/de dados (`omega` sobre ℕ; `decide` sobre listas escritas à mão) e **não** provam as propriedades gerais. Dizer que P221 os substitui.
7. Conclusão: reescrever em 4–6 linhas: reconstrução verificada de parâmetros já conhecidos, fato conhecido reformulado, cotas computacionais fracas, nenhum recorde, nenhuma descoberta.
8. Seção "Curator Submissions": manter, mas dizer que os pacotes são **reconstruções** e que o envio fica a critério humano, sem expectativa de novidade.

### C3 — Veredito D048 (texto fixo)

O veredito da linha D048 em `docs/DECISIONS.md` deve ser exatamente:
`RESULTADO NULO HONESTO: nenhuma descoberta; reconstrução verificada de parâmetros já conhecidos ([[20, 2, 6]], [[16, 2, 4]]), fato conhecido reformulado (paridade de k) e cotas computacionais fracas; limites delimitados em docs/research/claims-ledger-d047.md e docs/bivariate-paper/main.pdf`

### C4 — `tests/test_p220_manuscript.py` deve também

- falhar se `main.tex` contiver qualquer destas strings: `DISCOVERY_TIED`, `definitive`, `definitively`, `unconditional`, `zero unproven gaps`, `primary scientific contributions`, `successfully demonstrated`;
- falhar se `docs/research/claims-ledger-d047.md` não existir ou não contiver as classes `RECONSTRUCAO_VERIFICADA`, `CONHECIDO_TRIVIAL`, `COMPUTACIONAL_FRACA`, `ESCOPO_LIMITADO`;
- falhar se a linha D048 não contiver `RESULTADO NULO HONESTO`.

**Regra de parada extra:** se a compilação LaTeX exigir reintroduzir qualquer string proibida, PARE e reporte.

## Resultados e Evidências Medidas

- **Livro de alegações criado:** `docs/research/claims-ledger-d047.md` com classificação honesta completa (`RECONSTRUCAO_VERIFICADA`, `CONHECIDO_TRIVIAL`, `COMPUTACIONAL_FRACA`, `ESCOPO_LIMITADO`, `ENGENHARIA_VALIDA`, `RESULTADO_NULO`).
- **Edições C2 em `main.tex`:** Todas as correções aplicadas rigorosamente; 0 termos banidos detectados (`DISCOVERY_TIED`, `definitive`, `unconditional`, etc. ausentes).
- **Compilação PDF:** `docs/bivariate-paper/main.pdf` compilado com sucesso (8 páginas, 298.418 bytes).
- **Veredito D048:** Registrado fielmente em `docs/DECISIONS.md`.
- **Relatório de Impacto:** `docs/research/p220-program-conclusion-impact-report.md` documentando a conclusão de D047 e transição para D049.
- **Suíte de testes:** `tests/test_p220_manuscript.py` 100% verde (7/7 testes aprovados).

## Critérios de Saída (Gates)

1. `tests/test_p220_manuscript.py` passa 100% verde com verificação de alegações.
2. Manuscrito `docs/bivariate-paper/main.pdf` compilado com sucesso.
3. Decisão D048 registrada em `docs/DECISIONS.md`.
4. `git diff --check`, `git status --short`, `make lint` e `python3 -m pytest tests -q` passam sem erros.

## Commit & Push

```bash
git add docs/bivariate-paper \
  docs/research/claims-ledger-d047.md \
  docs/research/p220-program-conclusion-impact-report.md \
  docs/DECISIONS.md docs/ROADMAP.md docs/phases/README.md \
  tests/test_p220_manuscript.py \
  docs/phases/P220-discovery-manuscript-and-decision-d048.md
git commit -m "feat(manuscript): publish bivariate discovery paper (P220)"
git push -u origin codex/p220-discovery-manuscript-and-decision-d048
gh pr create --base main \
  --title "feat(manuscript): publish bivariate discovery manuscript and record program conclusion (P220)" \
  --body "Publica manuscrito, pacote Zenodo e encerra programa P211–P220 sob D048."
```
