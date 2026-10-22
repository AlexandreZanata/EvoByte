# Certificados formais fiéis em Lean 4 (P168)

- **Fase:** P168 — Certificados formais com fidelidade verificada em Lean 4
- **Data:** 2026-10-22
- **Dependência:** P167 (validação externa) concluída
- **Certificado:** [`lean_proofs/Generated/FaithfulExtremalCertificates.lean`](../../lean_proofs/Generated/FaithfulExtremalCertificates.lean)
- **Registro de revisão humana:** [`docs/research/lean-fidelity-reviews.json`](lean-fidelity-reviews.json)

---

## 1. Objetivo

A auditoria P162 comprovou que 51 teoremas de fases anteriores eram meras tautologias de
constantes locais (ex: `hadwigerNelsonLowerDeGrey = 5 := rfl`). Esta fase estabelece o padrão
correto para certificados formais: o enunciado formula o problema combinatório real com
quantificadores e tipos matemáticos legítimos, a prova é computação exata no kernel do Lean
4 via `by decide`, o teorema passa pelo linter de fidelidade da P162 e é registrado no log
de revisão com aprovação humana explícita. Total de tokens `sorry`: **zero**.

## 2. Os dois certificados

### 2.1 `EvoByte.Faithful.vdw_sample_8_valid`

- **Enunciado Lean:** `¬ HasMonoAP 8 3 vdwSampleColoring8`, onde `HasMonoAP n k col`
  afirma `∃ a d : Fin n, a + (k-1)*d < n` com `0 < d` e `col(a + i*d) = col(a)` para todo
  `i < k`. É a ausência de progressão aritmética monocromática de 3 termos na coloração.
- **Enunciado informal:** "A coloração concreta de [1..8] em 2 cores não possui nenhuma
  progressão aritmética monocromática de tamanho 3."
- **Objeto certificado:** a coloração `[1, 1, 2, 2, 1, 1, 2, 2]` (posições 0..7), que
  reproduz o valor publicado exato `W(2,3) = 9` (uma coloração de $[1..8]$ sem PA
  monocromática de 3 termos certifica $W(2,3) \ge 9$).
- **Prova:** `by decide` — avaliação exaustiva no kernel: o existencial sobre
  `Fin 8 × Fin 8` e a quantificação universal sobre `Fin 3` são finitos e decidíveis.

### 2.2 `EvoByte.Faithful.schur_sample_4_valid`

- **Enunciado Lean:** `¬ HasSchurViolation 4 schurSamplePartition4`, onde
  `HasSchurViolation n part` afirma `∃ x y : Fin n` com `1 ≤ x`, `1 ≤ y`, `x + y ≤ n` e
  `part(x-1) = part(y-1) = part(x+y-1)`. É a ausência de tripla de Schur monocromática.
- **Enunciado informal:** "A partição concreta de [1..4] em 2 classes sum-free não contém
  nenhuma violação da condição de Schur."
- **Objeto certificado:** a partição `[1, 2, 2, 1]` (classes `{1,4}` e `{2,3}`), que
  reproduz o valor publicado exato `S(2) = 4` (uma partição sum-free de $[1..4]$ em 2
  classes certifica $S(2) \ge 4$).
- **Prova:** `by decide` — avaliação exaustiva no kernel.

## 3. Verificação mecânica (evidência)

| Checagem | Resultado |
|---|---|
| `lake build Generated.FaithfulExtremalCertificates` | exit 0, sem erros nem warnings |
| `lake build` (biblioteca `Generated` completa, 3154 jobs) | exit 0, sem erros nem warnings |
| Contagem de `sorry` no arquivo | 0 |
| Linter P162 sobre o arquivo | total 2, `vacuous-constant` **0**, `numeric-literal` 0, `needs-review` 2 |
| Linter P162 sobre `lean_proofs/Generated` | 4890 total (4888 + 2 novos), `vacuous-constant` 51, **nenhum dos novos é vazio** |
| `decide` reduzindo os dois teoremas no kernel | sucesso (ambas as afirmações avaliadas como verdadeiras) |

Os dois teoremas classificam como `needs-review` no linter, o que é o rótulo correto:
o classificador da P162 nunca certifica significado (é conservador), e aqui a
fidelidade é atestada pelo **kernel** e pelo **revisor humano**, não pelo linter.

## 4. Fidelidade matemática (verificação do conteúdo)

Verificação independente de que cada enunciado Lean expressa a afirmação combinatória
alegada, e não uma tautologia de constante:

- **van der Waerden:** `HasMonoAP 8 3 col` exige `∃ a, d ∈ Fin 8` com
  `a + 2*d < 8`, `0 < d` e `col(a + i*d) = col(a)` para `i = 0, 1, 2`. Para uma
  coloração, isso é exatamente "existe PA monocromática `a, a+d, a+2d ⊆ [0,8)`".
  A coloração registrada usa apenas as cores 1 e 2, e o verificador independente da
  P163 confirma que nenhuma PA de tamanho 3 é monocromática. Portanto
  `¬ HasMonoAP 8 3 vdwSampleColoring8` é a afirmação "a coloração de $[1..8]$ não
  contém PA monocromática de 3 termos", verdadeira e verificada pelo kernel.
- **Schur:** `HasSchurViolation 4 part` exige `∃ x, y ∈ Fin 4` com
  `1 ≤ x`, `1 ≤ y`, `x + y ≤ 4` e `part(x-1) = part(y-1) = part(x+y-1)`. Para a
  partição `[1, 2, 2, 1]`, uma enumeração manual mostra que nenhuma tripla
  `(x, y, x+y)` com soma ≤ 4 está na mesma classe: `(1,1,2)`, `(1,2,3)`,
  `(2,1,3)` e `(1,3,4)`/`(3,1,4)` violam todas a igualdade de classe. Portanto
  `¬ HasSchurViolation 4 schurSamplePartition4` é a afirmação "a partição de
  $[1..4]$ é sum-free", verdadeira e verificada pelo kernel.

## 5. Entradas de revisão humana

As duas entradas abaixo transcrevem a aprovação pré-registrada no contrato da fase
(P168, Passo 4), cujo conteúdo foi aprovado pelo proprietário da fase. O agente **não
decidiu** fidelidade: ele verificou mecanicamente os enunciados (seções 3 e 4) e
transcreveu o veredito aprovado, anexando a evidência. A assinatura `human:Alexandre`
refere-se a essa aprovação pré-registrada no contrato da fase, e não a uma assinatura
gerada pelo agente.

```json
[
  {
    "theorem": "EvoByte.Faithful.vdw_sample_8_valid",
    "file": "lean_proofs/Generated/FaithfulExtremalCertificates.lean",
    "informal_statement": "A coloração concreta de [1..8] em 2 cores não possui nenhuma progressão aritmética monocromática de tamanho 3.",
    "lean_statement": "¬ HasMonoAP 8 3 vdwSampleColoring8",
    "mathlib_concepts": ["Fin", "HasMonoAP"],
    "reviewer": "human:Alexandre",
    "verdict": "faithful",
    "reviewed_at": "2026-10-22"
  },
  {
    "theorem": "EvoByte.Faithful.schur_sample_4_valid",
    "file": "lean_proofs/Generated/FaithfulExtremalCertificates.lean",
    "informal_statement": "A partição concreta de [1..4] em 2 classes sum-free não contém nenhuma violação da condição de Schur.",
    "lean_statement": "¬ HasSchurViolation 4 schurSamplePartition4",
    "mathlib_concepts": ["Fin", "HasSchurViolation"],
    "reviewer": "human:Alexandre",
    "verdict": "faithful",
    "reviewed_at": "2026-10-22"
  }
]
```

## 6. Desvios da especificação (registrados, com justificativa)

### 6.1 A coloração de exemplo da especificação é matematicamente falsa

O código da especificação usa a coloração `[1, 1, 2, 1, 2, 2, 1, 2]`. Essa coloração
**contém** a progressão aritmética monocromática `1, 4, 7` (posições 1, 4 e 7, todas de
cor 1, diferença 3) — o mesmo erro que o teste `test_let_statement_not_cut_early` e o
oráculo da P163 já haviam fixado na P165. Qualquer `decide` sobre ela **falha por direito**,
porque a afirmação é falsa. O teste
`test_spec_example_coloring_is_mathematically_false` (P168) fixa esse fato com o oráculo
independente da P163.

A coloração foi corrigida para `[1, 1, 2, 2, 1, 1, 2, 2]` — uma das 6 colorações válidas
de $[1..8]$ verificadas por força bruta na P165 — mantendo 2 cores e o significado do
enunciado. Todo o resto do arquivo é o da especificação. O `lake build` da versão da
especificação foi executado e falhou (6 erros de elaboração mais `Decidable` ausente);
o da versão corrigida compila sem nenhum erro nem warning.

### 6.2 O código Lean precisou de ajustes para elaborar e decidir

Além da coloração, o texto da especificação não compila por três razões independentes,
todas verificadas nesta fase:

1. **`∃ a d : Nat` não é decidível.** O `decide` exige `Decidable` do existencial, que não
   existe sobre `Nat`. Os quantificadores foram transferidos para `Fin n` (domínio finito),
   preservando o significado: `a + (k-1)*d < n` com `d > 0` implica o mesmo domínio que o
   original.
2. **Os `by omega` dentro das conjunções não têm as hipóteses no contexto.** O `omega`
   dentro de `part ⟨x - 1, _⟩` não vê `x + y ≤ n` (é conjuncto irmão, não hipótese). As
   restrições foram promovidas a hipóteses do `∃` (`ha`, `hb`), que ficam no contexto.
3. **`def` bloqueia a síntese de `Decidable`.** Com `def`, a busca de instância não reduz o
   predicado e o `decide` falha; com `abbrev` (redutível por padrão), a síntese funciona.
   A escolha não muda o significado da declaração.

Sem esses ajustes, o arquivo da especificação produzia 6 erros de elaboração e 2 falhas de
`Decidable` — ou seja, **nunca teria passado no gate `lake build` da própria fase**. A
versão entregue preserva fielmente (i) os nomes e o namespace, (ii) os docstrings, (iii)
os tipos `Fin n → Nat`, (iv) os enunciados dos dois teoremas com `:= by decide` e
(v) o significado combinatório exato.

### 6.3 O arquivo foi ligado em `lean_proofs/Generated.lean`

`lean_proofs/Generated.lean` importa cada módulo explicitamente; sem a linha
`import Generated.FaithfulExtremalCertificates` o arquivo novo **nunca é compilado** pelo
`lake build` (demonstrado: o build passava mesmo com 6 erros latentes no arquivo, porque
ele não era visitado). A linha foi acrescentada — uma alteração de uma linha fora do escopo
formal da fase, necessária para que o gate de compilação não seja vacuoso. O teste
`test_faithful_root_library_builds_cleanly` trava esse acoplamento.

### 6.4 O teste da P162 foi ajustado para comparar por arquivo

Como o diretório ganhou 2 teoremas (4888 → 4890), o guard da P162 que compara totais
globais falharia. O artefato congelado da P162 (`experiments/p162-lean-fidelity.json`)
**não foi tocado** (é o registro histórico da medição); o teste
`test_directory_totals_match_recorded_json` passa a comparar as **linhas por arquivo**
registradas no JSON contra a re-auditoria dos mesmos arquivos (nome preservado). A
verificação por arquivo é estritamente mais forte que a de totais globais: qualquer desvio
em qualquer um dos 54 arquivos registrados quebra a suíte. O arquivo novo da P168 é
coberto pelo seu próprio teste (`test_faithful_file_has_zero_vacuous_theorems`).

## 7. Limitações

1. **Escopo modesto deliberado.** São dois certificados de calibração (valores $W(2,3) = 9$
   e $S(2) = 4$ já publicados), não recordes novos. O valor da fase está no **padrão** —
   enunciado combinatório real + kernel + linter + revisão humana — e não no conteúdo.
   Afirmar novidade a partir destes certificados seria falso.
2. **A assinatura `human:Alexandre` transcreve a aprovação pré-registrada no contrato da
   fase.** O agente verificou mecanicamente e registrou; a decisão de fidelidade é do
   contrato aprovado pelo proprietário. Qualquer revisão futura que mude o veredito deve
   vir de um humano, pelo mesmo registro.
3. **`decide` e escala.** A prova por `decide` enumera o espaço de busca no kernel
   (`Fin 8 × Fin 8` e `Fin 4 × Fin 4` aqui). Para instâncias maiores (`W(3,3)`, $n = 26$)
   essa estratégia não escala no kernel; ela vale para instâncias de calibração.
4. **CI sem Lean.** O toolchain Lean/Mathlib não é instalado pelo CI; os testes que exigem
   `lake build` usam o marcador `needs_lean` (padrão do repositório) e são pulados sem a
   toolchain. A garantia de compilação é local, neste ambiente — o `build` completo passou
   (3154 jobs).

## 8. Reprodução

```bash
git switch codex/p168-faithful-formal-certificates
(cd lean_proofs && lake build Generated.FaithfulExtremalCertificates)
(cd lean_proofs && lake build)
PYTHONPATH=src python3 -m evobyte.lean_fidelity lean_proofs/Generated
python3 -m pytest tests/test_faithful_formal_certificates.py -q
python3 -m pytest tests -q
make verify
```
