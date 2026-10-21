# P168 — Certificados formais com fidelidade verificada em Lean 4

**Status:** Proposed.
**Dependência:** P167 concluída; branch a partir de `codex/p167-external-validation-dossier`.
**Owner:** agente executor; revisor formal humano (Alexandre) assina a revisão em `lean-fidelity-reviews.json`.
**Branch:** `codex/p168-faithful-formal-certificates`.
**Leia antes:** [regras do executor P161–P170](README.md#programa-de-descoberta-validada-p161p170-d038).

## Por que esta fase existe

A auditoria P162 comprovou que 51 teoremas de fases anteriores eram meras tautologias de constantes
locais (ex: `hadwigerNelsonLowerDeGrey = 5 := rfl`).
Esta fase estabelece o padrão formal correto para **certificados de verificação exata em Lean 4**:
1. O enunciado Lean formula o problema combinatório real com quantificadores e tipos matemáticos
   legítimos (ex: ausência de progressão aritmética monocromática em `Fin N`).
2. A prova do certificado opera por computação exata no kernel do Lean 4 via `by decide`.
3. O teorema passa pelo linter de fidelidade de P162 e é registrado em `lean-fidelity-reviews.json`
   com aprovação humana explícita.
4. Total de tokens `sorry`: **estritamente zero**.

## Escopo

**Arquivos que você pode criar:**
- `lean_proofs/Generated/FaithfulExtremalCertificates.lean`
- `tests/test_faithful_formal_certificates.py`
- `docs/research/p168-formal-certificates-report.md`

**Arquivos que você pode editar:**
- `docs/research/lean-fidelity-reviews.json`: adicionar entradas `faithful` assinadas.
- `docs/phases/P168-faithful-formal-certificates.md`: linha de Status.

**Proibido:** criar teoremas que apenas afirmam igualdades de definições numéricas locais sem
conteúdo lógico combinatório. Proibido usar `sorry`.

## Trabalho ordenado

### Passo 1 — Branch

```bash
git status --short
git switch codex/p167-external-validation-dossier
git switch -c codex/p168-faithful-formal-certificates
```

### Passo 2 — Criar `lean_proofs/Generated/FaithfulExtremalCertificates.lean`

Copie exatamente o código abaixo:

```lean
import Mathlib.Tactic

/-!
# Faithful Extremal Certificates in Lean 4 (P168)

Mechanically verified proofs of concrete combinatorial certificates:
- Van der Waerden monochromatic progression absence in finite colorings.
- Schur sum-free partitions.

All theorems state actual combinatorial claims and are proved by the Lean 4 kernel.
-/

namespace EvoByte.Faithful

/-- Monochromatic arithmetic progression predicate on a finite coloring. -/
def HasMonoAP (n k : Nat) (col : Fin n → Nat) : Prop :=
  ∃ (a d : Nat), d ≥ 1 ∧ a + (k - 1) * d < n ∧
    ∀ (i : Fin k), col ⟨a + i.val * d, by omega⟩ = col ⟨a, by omega⟩

/-- Sum-free partition violation predicate on a partition of 1..n into k classes. -/
def HasSchurViolation (n : Nat) (part : Fin n → Nat) : Prop :=
  ∃ (x y : Nat), x ≥ 1 ∧ y ≥ 1 ∧ x + y ≤ n ∧
    part ⟨x - 1, by omega⟩ = part ⟨y - 1, by omega⟩ ∧
    part ⟨x - 1, by omega⟩ = part ⟨x + y - 1, by omega⟩

/-- Concrete certified coloring for W(3,3) lower bound certification on [1..8]. -/
def vdwSampleColoring8 : Fin 8 → Nat
  | ⟨0, _⟩ => 1
  | ⟨1, _⟩ => 1
  | ⟨2, _⟩ => 2
  | ⟨3, _⟩ => 1
  | ⟨4, _⟩ => 2
  | ⟨5, _⟩ => 2
  | ⟨6, _⟩ => 1
  | ⟨7, _⟩ => 2

/-- Decidable certification that vdwSampleColoring8 contains no monochromatic 3-AP. -/
theorem vdw_sample_8_valid : ¬ HasMonoAP 8 3 vdwSampleColoring8 := by
  decide

/-- Concrete certified sum-free partition of 1..4 into 2 classes. -/
def schurSamplePartition4 : Fin 4 → Nat
  | ⟨0, _⟩ => 1
  | ⟨1, _⟩ => 2
  | ⟨2, _⟩ => 2
  | ⟨3, _⟩ => 1

/-- Decidable certification that schurSamplePartition4 has no monochromatic Schur violations. -/
theorem schur_sample_4_valid : ¬ HasSchurViolation 4 schurSamplePartition4 := by
  decide

end EvoByte.Faithful
```

### Passo 3 — Compilar no kernel via Lake

```bash
(cd lean_proofs && lake build)
```

O comando deve compilar sem nenhum aviso de `sorry`.

### Passo 4 — Validar fidelidade e registrar no catálogo

Execute o linter de fidelidade implementado em P162:

```bash
PYTHONPATH=src python3 -m evobyte.lean_fidelity lean_proofs/Generated/FaithfulExtremalCertificates.lean
```

Confira que `vacuous-constant == 0`.
Adicione as entradas aprovadas pelo revisor humano em `docs/research/lean-fidelity-reviews.json`:
- `theorem`: `EvoByte.Faithful.vdw_sample_8_valid`
- `informal_statement`: "A coloração concreta de [1..8] em 2 cores não possui nenhuma progressão aritmética monocromática de tamanho 3."
- `mathlib_concepts`: `["Fin", "HasMonoAP"]`
- `reviewer`: `human:Alexandre`
- `verdict`: `faithful`

### Passo 5 — Testes `tests/test_faithful_formal_certificates.py`

Valide que:
1. `test_faithful_file_compiles_cleanly`: Lake build termina com código 0.
2. `test_faithful_file_has_zero_vacuous_theorems`: O linter de P162 retorna 0 constantes vazias.
3. `test_faithful_entries_in_human_review_log`: As entradas de P168 existem no JSON de revisões com status `faithful`.

## Regras de parada (PARE, não commite, reporte)

- `lake build` falhar com erro de sintaxe ou tipo.
- O linter classificar qualquer teorema deste arquivo como `vacuous-constant`.
- Falha no pytest.

## Gate de saída

```bash
git diff --check
(cd lean_proofs && lake build)
python3 -m pytest tests/test_faithful_formal_certificates.py -q
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add lean_proofs/Generated/FaithfulExtremalCertificates.lean \
  tests/test_faithful_formal_certificates.py docs/research/lean-fidelity-reviews.json \
  docs/research/p168-formal-certificates-report.md docs/phases/P168-faithful-formal-certificates.md
git diff --cached --check
git commit -m "feat(formal): implement p168 faithful formal certificates in lean 4"
git push -u origin HEAD
gh pr create --base codex/p167-external-validation-dossier \
  --title "feat(formal): implement p168 faithful formal certificates" \
  --body-file /tmp/evobyte-p168-pr.md
git status --short
```
