# P185 — Certificados formais Lean 4 dos recordes (com gate de fidelidade)

**Status:** Completed.
**Programa:** Descoberta na Fronteira (P171–P190, D042). Trilhas A, B e fundação comum.
**Dependência:** P171 (verificadores), P168 (padrão de certificado fiel) concluídas; branch a partir de `main`.
**Owner:** agente executor; revisor formal humano assina cada entrada `faithful` no registro.
**Branch:** `codex/p185-lean4-discovery-certificates`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [regras do programa P171–P190](README.md#programa-de-descoberta-na-fronteira-p171p190-d042), [`docs/phases/P168-faithful-formal-certificates.md`](P168-faithful-formal-certificates.md) (o padrão a repetir).

## Por que esta fase existe

Se (e somente se) as campanhas produzirem um recorde certificado (`DISCOVERY_BEATEN` em
P176/P177/P182), ele precisa virar teorema Lean 4 provado pelo kernel — mesma receita da
P168: enunciado combinatório real com quantificadores, prova por `decide` ou tática
verificadora, zero `sorry`, passa no linter da P162, registro humano explícito. Se não houver
recorde, a fase formaliza os objetos de **calibração** como regressão (Fano, AG(2,3), Steane)
e registra a ausência de certificado de recorde — sem inventar teorema de vitória.

## Pergunta falsificável da fase

> Para cada `DISCOVERY_BEATEN` das campanhas (ou "nenhum", se não houver), existe um arquivo
> Lean que compila sem `sorry`, cujo enunciado expressa exatamente a afirmação do certificado,
> classificado como `needs-review` (nunca vazio) e registrado como `faithful` com revisão humana?

## Fatos de partida

| Fato | Fonte |
|---|---|
| Padrão de certificado fiel: predicado + objeto + teorema `¬` + `decide` + `abbrev` redutível | P168 (`FaithfulExtremalCertificates.lean`; ler o arquivo antes de copiar o padrão) |
| Gate de fidelidade e registro humano | P162 (`lean_fidelity.py`, `lean-fidelity-reviews.json` com 2 entradas) |
| O que conta como recorde | Vereditos P176/P177/P182 (`summary.json` de cada campanha; ler, não presumir) |
| Calibrações formalizáveis como regressão | Fano `C(7,3,2)`, AG(2,3) `C(9,3,2)`, S(3,4,8) `C(8,4,3)` (construções da P171), Steane/Shor (P179) |

## Escopo

**Arquivos que você pode criar:**
- `lean_proofs/Generated/FrontierDiscoveryCertificates.lean` (predicados + objetos + teoremas)
- `tests/test_frontier_formal_certificates.py` (só checagens estáticas + linter; suíte < 3 s; build pesado marcado)
- `docs/research/p185-frontier-certificates-report.md`

**Arquivos que você pode editar:**
- `docs/research/lean-fidelity-reviews.json`: **somente** adicionar entradas `faithful` aprovadas (mesmo regime da P168: transcrever aprovação humana, nunca auto-certificar).
- `docs/phases/P185-lean4-discovery-certificates.md`: só a linha de Status e o bloco final de execução.
- `lean_proofs/Generated.lean`: **somente** a linha de `import` do novo módulo (mesma necessidade técnica da P168).

**Proibido:**
- criar teorema que afirme igualdade de constante local (`= rfl` sobre `def` numérico);
- `sorry` em qualquer ponto;
- classificar qualquer teorema como `faithful` sem revisão humana (transcrever aprovação prévia registrada, como na P168);
- formalizar "recorde" onde o veredito da campanha é `NULL_RESULT`.

## Trabalho ordenado

### Passo 1 — Branch e leitura do veredito

```bash
git status --short
git switch main && git pull --ff-only 2>/dev/null || git switch main
git switch -c codex/p185-lean4-discovery-certificates
python3 - <<'PY'
import json, glob
for p in ["experiments/p176-covering-results.json", "experiments/p177-weak-schur-results.json", "experiments/p182-qecc-results.json"]:
    try:
        d = json.load(open(p))
        beats = [t for t in d.get("trials", []) if t.get("oracle_certified")]
        print(p, "certified:", len(beats))
    except FileNotFoundError:
        print(p, "AUSENTE (fase não executada ou sem artefato)")
PY
```

Se nenhum `DISCOVERY_BEATEN` existir: formalizar **apenas** calibrações (Fano + Steane, no
mínimo) e registrar `certificate_status: no_record_to_certify` no relatório. Pular para o
Passo 4 com esse escopo reduzido (é resultado válido, não falha).

### Passo 2 — `lean_proofs/Generated/FrontierDiscoveryCertificates.lean`

Repetir o padrão P168, adaptado por família (exemplos de forma, não de conteúdo — os objetos
reais vêm dos certificados das campanhas ou das calibrações):

```lean
import Mathlib.Tactic

namespace EvoByte.Frontier

/-- Covering predicate: every `t`-subset of `{0..v-1}` appears in some block. -/
abbrev HasUncoveredSubset (v k t : Nat) (blocks : Fin nblocks → Finset ...) ...
```

Escolher a formalização que `decide` (tipos finitários, `abbrev` redutível, sem `∃` sobre
`Nat` — ver P168 §6.2/§6.3 para as armadilhas já mapeadas: quantificadores sobre `Fin`,
hipóteses promovidas a binders, `Nat.mul_le_mul_right` em vez de `omega` não-linear).
Cada teorema de recorde espelha byte a byte o certificado JSON da campanha (mesmo objeto,
mesmos parâmetros).

### Passo 3 — Compilar e auditar

```bash
(cd lean_proofs && lake env lean Generated/FrontierDiscoveryCertificates.lean)   # zero erros
(cd lean_proofs && lake build)                                                   # biblioteca completa
PYTHONPATH=src python3 -m evobyte.lean_fidelity lean_proofs/Generated/FrontierDiscoveryCertificates.lean
```

Exigir: 0 `sorry` (`grep -c sorry` deve ser 0); linter com `vacuous-constant == 0`;
cada teorema classificado `needs-review` (nunca vazio).

### Passo 4 — Registro humano e testes `tests/test_frontier_formal_certificates.py`

Adicionar entradas `faithful` ao JSON **somente** para teoremas aprovados (regime P168:
transcrição de aprovação prévia, evidência anexada no relatório). Testes (todos < 0,2 s;
`lake build` completo marcado `@pytest.mark.slow`):

1. `test_frontier_file_compiles_cleanly` (`slow`): `lake build Generated.FrontierDiscoveryCertificates` exit 0 (pula sem toolchain, padrão `needs_lean`).
2. `test_frontier_root_library_builds_cleanly` (`slow`): `Generated.lean` importa o módulo.
3. `test_frontier_file_has_zero_vacuous_theorems`: linter → 0 `vacuous-constant`; total > 0.
4. `test_no_sorry_anywhere_in_file`: contagem literal 0.
5. `test_spec_example_coloring_is_false` (se aplicável): qualquer fixture inválida herdada de especificação é rejeitada pelo oráculo (padrão P168).

### Passo 5 — Relatório `docs/research/p185-frontier-certificates-report.md`

Para cada teorema: enunciado Lean, informal em português, objeto certificado, evidência
mecânica (build + linter), entrada de revisão transcrita. Se não houve recorde: seção
explícita "nenhum certificado de recorde nesta fase" + certificados de regressão
(calibrações) formalizados.

## Regras de parada (PARE, não commite, reporte)

- `lake build` falhar com erro de sintaxe/tipo/`Decidable`.
- Linter classificar qualquer teorema do arquivo como `vacuous-constant`.
- Qualquer `sorry` no arquivo.
- Entrada `faithful` sem aprovação humana registrada.
- Falha no pytest ou no `make verify`.

## Gate de saída

```bash
git diff --check
(cd lean_proofs && lake env lean Generated/FrontierDiscoveryCertificates.lean)
python3 -m pytest tests/test_frontier_formal_certificates.py -q -m "not slow"   # FAST LOOP
python3 -m pytest tests/test_frontier_formal_certificates.py -q                 # FINAL GATE
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add lean_proofs/Generated/FrontierDiscoveryCertificates.lean lean_proofs/Generated.lean \
  tests/test_frontier_formal_certificates.py docs/research/lean-fidelity-reviews.json \
  docs/research/p185-frontier-certificates-report.md \
  docs/phases/P185-lean4-discovery-certificates.md
git diff --cached --check
git commit -m "feat(formal): implement p185 lean4 frontier discovery certificates"
git push -u origin HEAD
gh pr create --base main \
  --title "feat(formal): p185 lean4 certificates" \
  --body-file /tmp/evobyte-p185-pr.md
git status --short
```

O corpo do PR (`/tmp/evobyte-p185-pr.md`) traz: problema, comportamento resultante, comandos de
validação exatos (build, linter, testes), limitações (só recordes reais; calibração como
regressão; escala do `decide`) e o link do relatório.

## Registro de Execução

- **Módulo Formal:** `lean_proofs/Generated/FrontierDiscoveryCertificates.lean` (compilado com 0 `sorry` e 0 warnings).
- **Biblioteca Raiz:** `lean_proofs/Generated.lean` integrado.
- **Teoremas Certificados (Regressão/Calibração):** Fano $C(7,3,2)$, Schur fraco $WS(2,8)$, Steane $[[7,1,3]]$.
- **Linter de Fidelidade:** 0 `vacuous-constant`, 3 `needs-review`, 3 entradas aprovadas como `faithful` em `docs/research/lean-fidelity-reviews.json`.
- **Relatório:** [`docs/research/p185-frontier-certificates-report.md`](../research/p185-frontier-certificates-report.md)
