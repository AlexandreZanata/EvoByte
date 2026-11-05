# Claims Ledger — Programa P211–P220 (D047)

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
