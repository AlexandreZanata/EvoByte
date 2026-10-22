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
BASIC_TOKENS = frozenset(
    {
        "Nat",
        "Int",
        "Rat",
        "Real",
        "True",
        "False",
        "true",
        "false",
        "Bool",
        "Prop",
    }
)
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
    totals = {
        k: sum(r[k] for r in per_file)
        for k in ("total", "vacuous-constant", "numeric-literal", "needs-review")
    }
    return {"root": str(root), "totals": totals, "files": per_file}


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path("lean_proofs/Generated")
    print(json.dumps(audit_directory(root)["totals"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
