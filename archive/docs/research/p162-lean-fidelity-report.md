# Gate de fidelidade de enunciados Lean (P162)

- **Fase:** P162 — Gate de fidelidade de enunciados Lean e registro de revisão humana
- **Data:** 2026-10-21
- **Dependência:** P161 (retratação e guarda de integralidade) concluída
- **Origem:** auditoria D038 do programa P161–P170
- **Artefato de medição:** [`experiments/p162-lean-fidelity.json`](../../experiments/p162-lean-fidelity.json)
- **Registro de revisão humana:** [`docs/research/lean-fidelity-reviews.json`](lean-fidelity-reviews.json) (atualmente `[]`)

---

## 1. O que o gate mede

"Compila sem `sorry`" não quer dizer "provou o teorema nomeado". O caso real registrado pelo
auditor em D038 é o seguinte:

```lean
def hadwigerNelsonLowerDeGrey : Nat := 5
theorem degrey_chromatic_lower_bound : hadwigerNelsonLowerDeGrey = 5 := rfl
```

Isso prova `5 = 5`, e não que o número cromático do planoHadwiger–Nelson satisfaz `χ(ℝ²) ≥ 5`.
O classificador de P162 varre os enunciados de todos os arquivos `.lean` gerados e aplica três
rótulos:

- **`vacuous-constant`** — sem binders/quantificadores e todo identificador do enunciado é um
  `def` numérico local (ou nome de tipo básico). É o caso de `degrey_chromatic_lower_bound`.
- **`numeric-literal`** — sem binders/quantificadores e sem identificadores além de nomes de
  tipo básicos, isto é, o enunciado é uma aritmética de números literais, como
  `(3:ℤ)^2 - (2:ℤ)^3 > 0`.
- **`needs-review`** — tudo o mais. **Não significa "significativo"**: significa apenas que o
  classificador não consegue provar, por inspeção estática, que o enunciado é vazio.

### Limitação (limite inferior)

O classificador é **heurístico e conservador**. Ele nunca certifica que um teorema é
matematicamente relevante; ele apenas marca o que é *comprovadamente* vazio em relação ao
nome da matemática. Portanto **as contagens de `vacuous-constant` e `numeric-literal` são um
limite inferior** do número de teoremas sem conteúdo matemático real: um enunciado com binders
pode continuar sendo trivial (por exemplo, `∀ n, n = n`), e permanece em `needs-review`. Nenhuma
entrada em `needs-review` deve ser lida como afirmação de significado.

## 2. Números medidos

| Métrica | Valor |
|---|---:|
| Arquivos `.lean` auditados | 54 |
| Teoremas/lemas avaliados | 4888 |
| `vacuous-constant` | 51 |
| `numeric-literal` | 2012 |
| `needs-review` | 2825 |
| **Vazios comprovados (limite inferior)** | **2063 de 4888** |

Observações pontuais:

- Todos os 51 casos `vacuous-constant` estão em
  `HadwigerNelsonColoringTheorems.lean` — o arquivo onde as "provas" de limite cromático são contrações de constantes
  numéricas.
- 4 arquivos têm 100% dos enunciados classificados como vazios ou literais
  numéricos: `AsymptoticDensityTheorems.lean`, `ErdosStrausCertificates.lean`, `OptimalCertificates.lean`, `QuadraticRingTheorems.lean`.
- `needs-review` (2825 teoremas) é a categoria majoritária e **não** é um
  atestado de validade matemática.

## 3. Tabela por arquivo

Gerada a partir de `experiments/p162-lean-fidelity.json` (não digitada à mão).

| Arquivo | Total | vacuous-constant | numeric-literal | needs-review |
|---|---:|---:|---:|---:|
| `AdditiveCombinatoricsSignatures.lean` | 103 | 0 | 98 | 5 |
| `AdditiveEnergyTheorems.lean` | 79 | 0 | 69 | 10 |
| `AdditiveTacticTheorems.lean` | 71 | 0 | 57 | 14 |
| `AsymptoticDensityTheorems.lean` | 68 | 0 | 68 | 0 |
| `AutomatedTheorems.lean` | 30 | 0 | 1 | 29 |
| `BytecodeTheorems.lean` | 4 | 0 | 0 | 4 |
| `ConicParametrizations.lean` | 75 | 0 | 16 | 59 |
| `ConvexPolygonsHappyEndingTheorems.lean` | 91 | 0 | 3 | 88 |
| `CoveringSystemsTheorems.lean` | 190 | 0 | 45 | 145 |
| `CubicSurfaceFibrations.lean` | 57 | 0 | 16 | 41 |
| `CustomTacticTheorems.lean` | 30 | 0 | 1 | 29 |
| `DiophSurfaceTheorems.lean` | 79 | 0 | 16 | 63 |
| `DiscrepancyCoveringSignatures.lean` | 116 | 0 | 9 | 107 |
| `DiscrepancyTacticTheorems.lean` | 147 | 0 | 0 | 147 |
| `DiscreteGeometrySignatures.lean` | 129 | 0 | 9 | 120 |
| `DiscreteGeometryTacticTheorems.lean` | 85 | 0 | 0 | 85 |
| `DivisibilityLemmas.lean` | 104 | 0 | 0 | 104 |
| `ErdosDiscrepancyTheorems.lean` | 104 | 0 | 2 | 102 |
| `ErdosDistinctDistancesTheorems.lean` | 100 | 0 | 6 | 94 |
| `ErdosGrahamTheorems.lean` | 113 | 0 | 110 | 3 |
| `ErdosGyarfasChromaticTheorems.lean` | 79 | 0 | 72 | 7 |
| `ErdosStrausCertificates.lean` | 10 | 0 | 10 | 0 |
| `ErdosStrausIdentities.lean` | 29 | 0 | 0 | 29 |
| `ErdosTuranBasesTheorems.lean` | 70 | 0 | 60 | 10 |
| `ExtremalBoundsTheorems.lean` | 162 | 0 | 50 | 112 |
| `ExtremalConstructiveCertificates.lean` | 114 | 0 | 0 | 114 |
| `ExtremalGraphRamseySignatures.lean` | 81 | 0 | 45 | 36 |
| `GraphRamseyTacticTheorems.lean` | 80 | 0 | 70 | 10 |
| `HadwigerNelsonColoringTheorems.lean` | 100 | 51 | 20 | 29 |
| `HigherPowerTheorems.lean` | 106 | 0 | 49 | 57 |
| `InductiveLemmas.lean` | 33 | 0 | 0 | 33 |
| `MultitermTheorems.lean` | 36 | 0 | 24 | 12 |
| `ObstructionGraphTheorems.lean` | 92 | 0 | 5 | 87 |
| `OpenProblemSignatures.lean` | 108 | 0 | 6 | 102 |
| `OptimalCertificates.lean` | 32 | 0 | 32 | 0 |
| `PillaiCatalanTheorems.lean` | 175 | 0 | 152 | 23 |
| `PrimitiveSetsDivisorsTheorems.lean` | 206 | 0 | 127 | 79 |
| `QuadraticIdentities.lean` | 22 | 0 | 10 | 12 |
| `QuadraticRingTheorems.lean` | 58 | 0 | 58 | 0 |
| `QuaternionAlgebraTheorems.lean` | 72 | 0 | 16 | 56 |
| `RamseyPaleyTheorems.lean` | 80 | 0 | 16 | 64 |
| `RothSalemSpencerTheorems.lean` | 81 | 0 | 76 | 5 |
| `RothSpencerDiscrepancyTheorems.lean` | 111 | 0 | 57 | 54 |
| `SchinzelHighModuliSignatures.lean` | 213 | 0 | 137 | 76 |
| `SchinzelHighModuliTheorems.lean` | 117 | 0 | 0 | 117 |
| `SchinzelQuadraticRingSieveTheorems.lean` | 104 | 0 | 30 | 74 |
| `SchinzelTheorems.lean` | 133 | 0 | 48 | 85 |
| `SidonSetsTheorems.lean` | 70 | 0 | 60 | 10 |
| `SierpinskiTheorems.lean` | 106 | 0 | 10 | 96 |
| `SolutionMomentsTheorems.lean` | 87 | 0 | 62 | 25 |
| `SumFreeTheorems.lean` | 70 | 0 | 60 | 10 |
| `UnitDistancesSzemerediTrotterTheorems.lean` | 88 | 0 | 4 | 84 |
| `UniversalMultitermTheorems.lean` | 108 | 0 | 74 | 34 |
| `ZarankiewiczKovariSosTuranTheorems.lean` | 80 | 0 | 46 | 34 |
| **TOTAL** | **4888** | **51** | **2012** | **2825** |

## 4. Exemplos de cada categoria

Colados do mesmo JSON (campo `examples`).

- **`vacuous-constant`:** `moser_vertex_count`, `moser_edge_count`, `moser_clique_number_exact`
- **`numeric-literal`:** `sidon_sample_1_bounds`, `sidon_sample_1_pair_0`, `sidon_sample_1_pair_1`
- **`needs-review`:** `sum_comm`, `sum_assoc`, `sum_cancel_left`

## 5. Regra vigente

> **A partir de P162, nenhum documento pode chamar um teorema Lean de resultado, prova de
> conjectura ou novidade sem entrada `faithful` em `lean-fidelity-reviews.json` assinada por
> humano.**

O registro `docs/research/lean-fidelity-reviews.json` é a **única** via para essa alegação, e
cada entrada exige as 8 chaves `theorem`, `file`, `informal_statement`, `lean_statement`,
`mathlib_concepts`, `reviewer` (prefixo `human:`), `verdict` (`faithful` ou `not-faithful`) e
`reviewed_at`. A auditoria mecânica de fidelidade (este relatório) **não** produz entradas
`faithful`: essa classificação é trabalho humano, e o registro nasce vazio.

## 6. Reprodução

```bash
PYTHONPATH=src python3 -m evobyte.lean_fidelity lean_proofs/Generated
python3 -m pytest tests/test_lean_fidelity.py -q
```

O comando imprime exatamente os totais da seção 2, e o teste
`test_directory_totals_match_recorded_json` falha se o diretório auditado divergir do JSON
versionado.
