# Catálogo de alvos de recorde com verificadores independentes (P163)

- **Fase:** P163 — Catálogo de alvos de recorde e conjecturas com verificadores independentes
- **Data:** 2026-10-21
- **Dependência:** P162 (gate de fidelidade de enunciados Lean) concluída
- **Catálogo congelado:** [`docs/research/targets/open_targets.json`](targets/open_targets.json) (versão 1.0.0)
- **Módulo dos oráculos:** [`src/evobyte/target_catalogue.py`](../../src/evobyte/target_catalogue.py)

---

## 1. Por que este catálogo existe

Até a P160, o EvoByte executava buscas sobre alvos triviais já conhecidos
($y = x+1$, $y = x^2+3x+7$) ou gerava instâncias sobre problemas universais
intratáveis (Erdős–Straus, Hadwiger–Nelson), onde uma busca finita nunca pode
provar um teorema. Esse regime não produz progresso científico: ou o alvo já
era conhecido, ou o alvo é inatingível por construção.

O catálogo passa a ser a **lista congelada de alvos** sobre os quais qualquer
busca futura pode ocorrer. Cada alvo satisfaz três condições:

1. **O estado da arte publicado é explícito**: valor exato (ou cota) do recorde
   atual, com autor e ano na referência do alvo.
2. **O certificado é finito e verificável em tempo polinomial** por um
   verificador independente, escrito em Python puro com `numpy`.
3. **Superar a cota publicada ou refutar a desigualdade** da conjectura
   configurada é uma afirmação matemática verificável por terceiro, sem
   depender de qualquer passo de busca.

### Os alvos não são problemas infinitos sem critério de parada

São **problemas extremais com certificado finito**. O que se verifica não é uma
propriedade de todos os inteiros, mas um objeto finito:

| Família | Objeto certificado | Consequência do certificado |
|---|---|---|
| `ramsey_vanderwaerden` | Uma coloração de $[1..N]$ com $r$ cores e sem progressão aritmética monocromática de $k$ termos | $W(r,k) \ge N+1$ |
| `additive_schur` | Uma partição de $[1..N]$ em $k$ classes sum-free (sem $x+y=z$ na mesma classe) | $S(k) \ge N$ |
| `spectral_graph_theory` | Uma matriz de adjacência de um grafo simples com um invariante abaixo do limiar | Contrexemplo do registro `AH_diam_mu2` |

Assim o critério de parada é objetivo: a busca pode terminar quando — e só
quando — um candidato finito passa no oráculo.

### O verificador é um oráculo externo independente

Nenhum dos verificadores usa o bytecode do EvoByte, o motor de evolução, a
cascata S0--S3 ou qualquer artefato da busca. São funções puras, curtas e
determinísticas sobre `numpy`, que operam **apenas** sobre o candidato
apresentado. Consequência: um veredito do oráculo não pode ser influenciado
pelo processo que produziu o candidato, e o certificado é reprodutível por
qualquer pessoa, em qualquer máquina, a partir do próprio candidato.

### Qualquer candidato aprovado tem prova matemática exata e reproduzível

Um `True` do oráculo significa, literalmente, que a propriedade finita foi
verificada por enumeração exaustiva (progressões aritméticas, triplas
sum-free) ou por álgebra linear exata sobre a matriz de adjacência. Não há
aproximação, amostragem ou estatística envolvida. O contraexemplo do registro
espectral é reprodutível a partir da matriz de adjacência do candidato.

## 2. Catálogo congelado

Conteúdo de `docs/research/targets/open_targets.json` (4 alvos, versão 1.0.0):

| `target_id` | Família | `published_bound` | Tipo de cota | Verificador |
|---|---|---:|---|---|
| `vanderwaerden_w3_3` | `ramsey_vanderwaerden` | 26.0 | `lower_bound` | `verify_vanderwaerden_coloring` |
| `vanderwaerden_w2_6` | `ramsey_vanderwaerden` | 1131.0 | `lower_bound` | `verify_vanderwaerden_coloring` |
| `schur_s5` | `additive_schur` | 160.0 | `lower_bound` | `verify_schur_partition` |
| `spectral_graph_diam_mu2` | `spectral_graph_theory` | 2.0 | `counterexample_threshold` | `verify_graph_spectral_conjecture` |

Semântica de `published_bound`: é o limiar a ser superado. Uma coloração válida
de $[1..N]$ com $N >$ `published_bound` para `vanderwaerden_w2_6` ($1131.0$)
certifica $W(2,6) \ge 1132 + 1$, ou seja, quebra o recorde publicado
$W(2,6) = 1132$ (Kouril, 2008). Para `schur_s5` ($160.0$), uma partição
sum-free de $[1..161]$ certifica $S(5) \ge 161 > 160$ (Exoo 1994; Heule 2018).
Para `vanderwaerden_w3_3` ($26.0$), uma coloração válida de $[1..27]$ certifica
$W(3,3) \ge 28 > 27$ (Chvátal, 1970).

## 3. Calibração dos oráculos contra valores publicados

Os dois verificadores de cor combinatória foram calibrados contra valores
exatos conhecidos da literatura, usando objetos pequenos e explicitamente
verificados por força bruta:

```bash
PYTHONPATH=src python3 - <<'PY'
from evobyte.target_catalogue import verify_schur_partition, verify_vanderwaerden_coloring
print(verify_vanderwaerden_coloring([1, 1, 2, 2, 1, 1, 2, 2], 2, 3))
print(verify_schur_partition([1, 2, 2, 1], 2))
PY
```

```text
(True, 'valid: zero monochromatic 3-term APs in 1..8 with 2 colors')
(True, 'valid sum-free partition of 1..4 into 2 classes')
```

- A coloração de $[1..8]$ com 2 cores sem progressão aritmética monocromática de
  3 termos certifica $W(2,3) \ge 9$, e o valor publicado exato é $W(2,3) = 9$.
- A partição sum-free de $[1..4]$ em 2 classes certifica $S(2) \ge 4$, e o valor
  publicado exato é $S(2) = 4$.

Ou seja: os oráculos **reproduzem** os valores exatos conhecidos. Um
certificado acima do limiar seria, por consequência, um recorde real.

Verificador espectral, medido no caminho $P_4$:

```text
{'n': 4, 'lambda_1': 1.6180339887498951, 'mu_2': 0.585786437626905,
 'diameter': 3.0, 'connected': True, 'lhs_value': 3.585786437626905, 'threshold': 2.0}
```

`lambda_1 = 2\cos(\pi/5)` e `mu_2 = 2-\sqrt{2}` são os valores exatos do
autovalor dominante da matriz de adjacência e da conectividade algébrica do
$P_4$; o verificador devolve `is_counterexample = False`, como esperado para
esse grafo.

## 4. Garantias do oráculo (ausência de falso positivo)

- `verify_vanderwaerden_coloring` enumera **todas** as progressões aritméticas de
  $k$ termos com $d \le (N-1)/(k-1)$, cobrindo o espaço de busca inteiro. Uma
  coloração só é aprovada quando nenhuma progressão monocromática existe.
- `verify_schur_partition` testa **todos** os pares $(x, y)$ com $x \le y$ dentro
  de cada classe, incluindo $x = y$.
- `verify_graph_spectral_conjecture` rejeita entradas malformadas (matriz não
  quadrada, assimétrica, com laço próprio, com entradas fora de $\{0,1\}$,
  matriz vazia) e só reporta contraexemplo para grafo conexo com
  `diameter + mu_2` abaixo do limiar.
- Entradas degeneradas são rejeitadas com mensagem explícita, nunca aprovadas:
  coloração vazia, $k < 2$, $r < 1$, partição vazia, $k < 1$ no oráculo de
  Schur, matriz vazia ou conjectura desconhecida.

## 5. Limitações

- O catálogo é uma **lista de alvos pré-registrados**, não um resultado. Nada
  aqui bate um recorde: as fases seguintes (P165 redescoberta cega, P166
  campanha pré-registrada) é que usam este catálogo como alvo de busca.
- A lista de alvos e as referências bibliográficas são pré-registradas e
  **dependem de validação humana** (owner da fase), não de medição automática.
- O limiar `published_bound` é a cota a superar; um candidato que apenas
  iguala a cota publicada não é um recorde.
- O registro `AH_diam_mu2` é uma **conjectura de amostra** do próprio módulo,
  usada para calibrar o caminho espectral; um contraexemplo real exigiria
  registro com conjectura declarada e limiar próprio.

## 6. Reprodução

```bash
PYTHONPATH=src python3 -m pytest tests/test_target_catalogue.py -q
python3 -m pytest tests -q
make verify
```

```bash
PYTHONPATH=src python3 - <<'PY'
from pathlib import Path
from evobyte.target_catalogue import load_catalogue
for spec in load_catalogue(Path("docs/research/targets/open_targets.json")):
    print(spec.target_id, spec.published_bound, spec.verification_fn)
PY
```

## 7. Desvio da especificação (registrado no PR)

A especificação da fase propunha, para o teste `test_vanderwaerden_valid_sample`,
a coloração `[1, 1, 2, 1, 2, 2, 1, 2]` como exemplo válido de $N = 8$, $r = 2$,
$k = 3$. **Essa coloração não é válida**: as posições 1, 4 e 7 têm a mesma cor e
formam a progressão aritmética monocromática $1, 4, 7$ (diferença 3), que o
verificador detecta e rejeita. Uma enumeração por força bruta confirma que
existem exatamente 6 colorações válidas de $[1..8]$ com 2 cores; o teste usa a
primeira delas, `[1, 1, 2, 2, 1, 1, 2, 2]`, e há um teste dedicado
(`test_vanderwaerden_specification_example_is_rejected`) que fixa o
comportamento correto do oráculo sobre o exemplo da especificação. O verificador
**não** foi alterado para acomodar o exemplo — ele é o da especificação, com
apenas guardas de entrada degenerada acrescentadas (`k < 2`, `r < 1`, matriz
vazia e matriz não quadrada unidimensional), que antes causavam exceção em vez
de veredito.
