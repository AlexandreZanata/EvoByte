# P162 — Gate de fidelidade de enunciados Lean

**Status:** Done (2026-10-21).
**Dependência:** P161 concluída; branch a partir de `codex/p161-claim-retraction-integrality-guard`.
**Owner:** agente executor; revisor humano obrigatório para qualquer entrada `faithful` no registro.
**Branch:** `codex/p162-lean-statement-fidelity-gate`.
**Leia antes:** [regras do executor P161–P170](README.md#programa-de-descoberta-validada-p161p170-d038).

## Por que esta fase existe

"Compila sem `sorry`" não quer dizer "provou o teorema nomeado". Exemplo real:

```lean
def hadwigerNelsonLowerDeGrey : Nat := 5
theorem degrey_chromatic_lower_bound : hadwigerNelsonLowerDeGrey = 5 := rfl
```

Isso prova `5 = 5`, não que χ(ℝ²) ≥ 5. Esta fase mede quantos teoremas gerados são desse tipo.
Também cria um **registro de revisão humana**, que passa a ser a única via para chamar um
teorema Lean de "resultado".

## Escopo

**Criar:**
- `src/evobyte/lean_fidelity.py`
- `tests/test_lean_fidelity.py`
- `experiments/p162-lean-fidelity.json`: saída completa de `audit_directory`.
- `docs/research/p162-lean-fidelity-report.md`
- `docs/research/lean-fidelity-reviews.json`: conteúdo inicial exatamente `[]`.

**Editar:**
- `docs/research/p144-discrepancy-covering-dossier.md` e `p152-constructive-algebraic-dossier.md`:
  acrescentar ao aviso REVISADO (P161) uma linha com os números medidos aqui.
- `docs/phases/P162-lean-statement-fidelity-gate.md`: Status.

**Proibido:** editar ou apagar arquivos em `lean_proofs/`, mudar o classificador para "melhorar"
números, classificar qualquer teorema como `faithful` sem revisor humano.

## Trabalho ordenado

### Passo 1 — Branch

```bash
git status --short
git switch codex/p161-claim-retraction-integrality-guard
git switch -c codex/p162-lean-statement-fidelity-gate
```

### Passo 2 — Criar `src/evobyte/lean_fidelity.py`

Use exatamente este código. Ele é **conservador**: só rotula como vazio o que é comprovadamente
vazio. Tudo o mais fica `needs-review`, o que **não** quer dizer "significativo".

```python
"""Lean statement fidelity classifier (P162).

Heuristic, conservative classification of theorem statements in generated Lean
files. It never certifies that a theorem is meaningful; it only flags statements
that are provably vacuous with respect to the named mathematics:

- ``vacuous-constant``: no binders/quantifiers and every identifier is a local
  numeric ``def`` or a basic type name. Example: ``hadwigerNelsonLowerDeGrey = 5``.
- ``numeric-literal``: no binders/quantifiers and no identifiers besides basic
  type names, e.g. ``(3:ℤ)^2 - (2:ℤ)^3 > 0``.
- ``needs-review``: everything else (may or may not be meaningful).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_DEF_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)?(?:noncomputable\s+)?def\s+([A-Za-z_][A-Za-z0-9_']*)\s*:\s*"
    r"(?:Nat|ℕ|Int|ℤ|ℚ|Rat|Real|ℝ)\s*:=\s*(.+?)\s*$"
)
_NUMERIC_BODY_RE = re.compile(r"^[-0-9 ().+*/^]+$")
_THEOREM_RE = re.compile(r"^\s*(?:private\s+)?(?:theorem|lemma)\s+([^\s:({\[]+)(.*)$")
_IDENT_RE = re.compile(r"[A-Za-z_\u0370-\u03FF\u1D00-\u1DBF][A-Za-z0-9_'.\u0370-\u03FF]*")
BASIC_TOKENS = frozenset({
    "Nat", "Int", "Rat", "Real", "True", "False", "true", "false", "Bool", "Prop",
})
UNICODE_TYPES = frozenset({"ℕ", "ℤ", "ℚ", "ℝ"})
_BINDER_MARKERS = ("∀", "∃", "fun ", "λ", "Π", "→")


def local_numeric_defs(text: str) -> set[str]:
    names = set()
    for line in text.splitlines():
        m = _DEF_RE.match(line)
        if m and _NUMERIC_BODY_RE.match(m.group(2)):
            names.add(m.group(1))
    return names


def extract_statements(text: str) -> list[tuple[str, str]]:
    """Return (theorem_name, statement_text) pairs.

    The statement ends at the first ``:=`` on a line that does not start with
    ``let``. Lines starting with ``let`` belong to the statement.
    """
    lines = text.splitlines()
    out: list[tuple[str, str]] = []
    i = 0
    while i < len(lines):
        m = _THEOREM_RE.match(lines[i])
        if not m:
            i += 1
            continue
        name, rest = m.group(1), m.group(2)
        parts = []
        cur = rest
        j = i
        while True:
            stripped = cur.lstrip()
            if ":=" in cur and not stripped.startswith("let "):
                parts.append(cur.split(":=", 1)[0])
                break
            parts.append(cur)
            j += 1
            if j >= len(lines):
                break
            cur = lines[j]
        out.append((name, " ".join(p.strip() for p in parts).strip()))
        i = j + 1
    return out


def classify_statement(statement: str, local_defs: set[str]) -> str:
    s = statement.strip()
    if s.startswith(("(", "{", "[", "⦃")) or any(mk in s for mk in _BINDER_MARKERS):
        return "needs-review"
    if s.startswith(":"):
        s = s[1:]
    if "let " in s:
        return "needs-review"
    idents = [tok for tok in _IDENT_RE.findall(s) if tok not in BASIC_TOKENS]
    idents = [tok for tok in idents if tok not in UNICODE_TYPES]
    if not idents:
        return "numeric-literal"
    if all(tok in local_defs for tok in idents):
        return "vacuous-constant"
    return "needs-review"


def audit_file(path: Path, extra_defs: set[str] | None = None) -> dict:
    text = path.read_text(encoding="utf-8")
    defs = local_numeric_defs(text) | (extra_defs or set())
    counts = {"vacuous-constant": 0, "numeric-literal": 0, "needs-review": 0}
    examples: dict[str, list[str]] = {k: [] for k in counts}
    for name, stmt in extract_statements(text):
        label = classify_statement(stmt, defs)
        counts[label] += 1
        if len(examples[label]) < 3:
            examples[label].append(name)
    return {"file": path.name, "total": sum(counts.values()), **counts, "examples": examples}


def audit_directory(root: Path) -> dict:
    files = sorted(root.glob("*.lean"))
    all_defs: set[str] = set()
    for f in files:
        all_defs |= local_numeric_defs(f.read_text(encoding="utf-8"))
    per_file = [audit_file(f, all_defs) for f in files]
    totals = {k: sum(r[k] for r in per_file) for k in
              ("total", "vacuous-constant", "numeric-literal", "needs-review")}
    return {"root": str(root), "totals": totals, "files": per_file}


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path("lean_proofs/Generated")
    print(json.dumps(audit_directory(root)["totals"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

Rode:

```bash
PYTHONPATH=src python3 -m evobyte.lean_fidelity lean_proofs/Generated
```

Valores esperados no commit de partida: `total 4888`, `vacuous-constant 51`,
`numeric-literal 2012`, `needs-review 2825`. Se diferirem, **PARE**. Isso só é aceitável se
`lean_proofs/` mudou desde D038; nesse caso, explique no PR com `git log -- lean_proofs`.

### Passo 3 — Gerar o JSON completo

```bash
PYTHONPATH=src python3 - <<'PY'
import json
from pathlib import Path
from evobyte.lean_fidelity import audit_directory
data = audit_directory(Path("lean_proofs/Generated"))
Path("experiments/p162-lean-fidelity.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
PY
```

### Passo 4 — Registro de revisão humana

Crie `docs/research/lean-fidelity-reviews.json` com conteúdo `[]`. O esquema de cada entrada
futura, usado em P169/P170, é:

```json
{
  "theorem": "Namespace.nome_do_teorema",
  "file": "lean_proofs/....lean",
  "informal_statement": "enunciado matemático em português, completo",
  "lean_statement": "texto exato do enunciado Lean",
  "mathlib_concepts": ["SimpleGraph.chromaticNumber"],
  "reviewer": "human:Alexandre",
  "verdict": "faithful | not-faithful",
  "reviewed_at": "AAAA-MM-DD"
}
```

### Passo 5 — Testes `tests/test_lean_fidelity.py`

Nomes exatos, todos obrigatórios:

1. `test_constant_statement_is_vacuous`: fixture
   `def foo : Nat := 5\ntheorem bar : foo = 5 := rfl\n` → `vacuous-constant`.
2. `test_numeric_literal`: `theorem t : (3:ℤ)^2 - (2:ℤ)^3 > 0 := by decide\n` → `numeric-literal`.
3. `test_binder_needs_review`: `theorem t (n : ℕ) (h : n ≥ 2) : n^2 ≥ 4 := by nlinarith\n` → `needs-review`.
4. `test_let_statement_not_cut_early`: o bloco `schinzel_identity_a5_m840_r1`, copiado do arquivo
   Lean, gera um enunciado que contém `let Z` e é `needs-review`.
5. `test_degrey_is_flagged`: no arquivo real `HadwigerNelsonColoringTheorems.lean`,
   `degrey_chromatic_lower_bound` é `vacuous-constant`.
6. `test_directory_totals_match_recorded_json`: `audit_directory(...)["totals"]` é igual a
   `experiments/p162-lean-fidelity.json["totals"]`.
7. `test_reviews_registry_schema`: carrega `lean-fidelity-reviews.json`. Deve ser uma lista, e
   cada entrada precisa ter as 8 chaves acima, `reviewer` começando com `human:` e `verdict` em
   `{"faithful", "not-faithful"}`.

### Passo 6 — Relatório `docs/research/p162-lean-fidelity-report.md`

1. Explique as três categorias e a limitação: é heurística, e os números de vazio são um
   **limite inferior**.
2. Tabela por arquivo (`file | total | vacuous-constant | numeric-literal | needs-review`), gerada
   do JSON e não digitada à mão.
3. Os 3 exemplos de cada categoria, colados do JSON.
4. Regra nova, em negrito: **"A partir de P162, nenhum documento pode chamar um teorema Lean de
   resultado, prova de conjectura ou novidade sem entrada `faithful` em
   `lean-fidelity-reviews.json` assinada por humano."**

### Passo 7 — Atualizar os avisos dos dossiês

Acrescente ao bloco REVISADO (P161) do P144 e do P152 uma linha:
`> P162 mediu: X de Y teoremas são vacuous-constant ou numeric-literal (limite inferior). Ver p162-lean-fidelity-report.md.`
X e Y vêm do JSON e somam todos os arquivos.

## Regras de parada

- Os totais do Passo 2 diferem e `lean_proofs/` não mudou.
- Qualquer teste existente quebra.
- Você sentiu vontade de marcar algo como `faithful`. Não marque: isso é trabalho humano.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests -q
python3 -m pytest tests/test_lean_fidelity.py -q     # 7 testes passam
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add src/evobyte/lean_fidelity.py tests/test_lean_fidelity.py experiments/p162-lean-fidelity.json \
  docs/research/p162-lean-fidelity-report.md docs/research/lean-fidelity-reviews.json \
  docs/research/p144-discrepancy-covering-dossier.md docs/research/p152-constructive-algebraic-dossier.md \
  docs/phases/P162-lean-statement-fidelity-gate.md
git diff --cached --check
git commit -m "feat(formal): add p162 lean statement fidelity gate"
git push -u origin HEAD
gh pr create --base codex/p161-claim-retraction-integrality-guard \
  --title "feat(formal): add p162 lean statement fidelity gate" --body-file /tmp/evobyte-p162-pr.md
git status --short
```

---

**Status da execução (2026-10-21):** Done.

- Classificador `src/evobyte/lean_fidelity.py` implementado e executado sobre
  `lean_proofs/Generated` (54 arquivos): `total 4888`, `vacuous-constant 51`,
  `numeric-literal 2012`, `needs-review 2825` — exatamente os valores esperados no Passo 2.
  `lean_proofs/` não mudou desde D038 (última alteração em `10ae8b7`, fase P149).
- Artefato completo versionado em `experiments/p162-lean-fidelity.json`; o teste
  `test_directory_totals_match_recorded_json` falha se o diretório divergir do JSON.
- Registro de revisão humana `docs/research/lean-fidelity-reviews.json` criado **vazio** (`[]`).
  Nenhum teorema foi classificado como `faithful`: essa decisão é humana e reversa.
- Relatório `docs/research/p162-lean-fidelity-report.md` com a tabela por arquivo gerada do
  JSON, os 3 exemplos de cada categoria e a regra vigente.
- Avisos de P144 e P152 atualizados com os números medidos.
- 7 testes de `tests/test_lean_fidelity.py` verdes; `make verify` e `python3 -m pytest tests -q`
  verdes; `git diff --check` limpo.

Desvios em relação a esta especificação, registrados no PR:

- A branch de origem `codex/p161-claim-retraction-integrality-guard` foi removida do remoto
  quando o PR #203 foi mergeado em `main`; a fase foi branched a partir de `main`, que já
  contém a P161, e o PR foi aberto contra `main`.
- Nenhuma linha foi acrescentada em `docs/DECISIONS.md`: a especificação da fase não inclui
  esse arquivo no escopo de edição.
