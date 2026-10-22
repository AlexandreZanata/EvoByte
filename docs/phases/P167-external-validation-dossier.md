# P167 — Dossiê de validação externa e exportação de certificados autônomos

**Status:** Done (2026-10-22).
**Dependência:** P166 concluída; branch a partir de `codex/p166-preregistered-record-campaign`.
**Owner:** agente executor; revisor humano nos gates de submissão.
**Branch:** `codex/p167-external-validation-dossier`.
**Leia antes:** [regras do executor P161–P170](README.md#programa-de-descoberta-validada-p161p170-d038).

## Por que esta fase existe

Em ciência matemática, nenhum pesquisador ou mantenedor de tabela aceita um resultado porque
"o software EvoByte disse que é válido". O resultado deve ser **auto-contido e externamente verificável**:
1. O certificado da solução (ou do melhor candidato obtido) é exportado em formato padrão JSON.
2. É fornecido um script independente de verificação (`verify_certificate_standalone.py`) que usa
   **exclusivamente a biblioteca padrão do Python** (sem numpy, sem scipy, sem dependências internas).
3. Qualquer matemático no mundo pode baixar o certificado e rodar `python3 verify_certificate_standalone.py cert.json`
   para atestar a validade em menos de 1 segundo.
4. Gera a minuta padronizada de comunicação formal com a comunidade científica externa.

## Escopo

**Arquivos que você pode criar:**
- `scripts/verify_certificate_standalone.py`
- `src/evobyte/certificate_exporter.py`
- `tests/test_standalone_verifier.py`
- `docs/research/p167-external-validation-dossier.md`
- `dist/external-validation/sample_certificate.json`

**Arquivos que você pode editar:**
- `docs/phases/P167-external-validation-dossier.md`: linha de Status.

**Proibido:** exigir a instalação do pacote `evobyte` para executar o script de verificação autônomo.
O script autônomo deve rodar em qualquer máquina limpa com Python 3.9+.

## Trabalho ordenado

### Passo 1 — Branch

```bash
git status --short
git switch codex/p166-preregistered-record-campaign
git switch -c codex/p167-external-validation-dossier
```

### Passo 2 — Criar `scripts/verify_certificate_standalone.py`

Copie exatamente o código abaixo (note o uso estrito apenas da biblioteca padrão `json`, `sys`, `hashlib`):

```python
#!/usr/bin/env python3
"""Standalone certificate verifier (P167).

Requires ONLY pure Python 3 standard library.
Verifies van der Waerden colorings, Schur partitions, and graph invariants.
"""

from __future__ import annotations

import hashlib
import json
import sys


def verify_vdw_pure(coloring: list[int], r: int, k: int) -> tuple[bool, str]:
    n = len(coloring)
    if n == 0:
        return False, "empty coloring"
    for c in coloring:
        if not (1 <= c <= r):
            return False, f"invalid color {c}"

    max_d = (n - 1) // (k - 1)
    for d in range(1, max_d + 1):
        for a in range(n - (k - 1) * d):
            first = coloring[a]
            if all(coloring[a + i * d] == first for i in range(k)):
                return False, f"monochromatic AP of length {k} at a={a+1}, d={d}"

    return True, f"VERIFIED: zero monochromatic {k}-term APs in 1..{n}"


def verify_schur_pure(partition: list[int], k: int) -> tuple[bool, str]:
    n = len(partition)
    for c in partition:
        if not (1 <= c <= k):
            return False, f"invalid class {c}"

    for c in range(1, k + 1):
        elems = [i + 1 for i, cl in enumerate(partition) if cl == c]
        elem_set = set(elems)
        for i, x in enumerate(elems):
            for y in elems[i:]:
                if (x + y) in elem_set:
                    return False, f"monochromatic Schur violation: {x} + {y} = {x+y}"

    return True, f"VERIFIED: valid sum-free partition of 1..{n} into {k} classes"


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python3 verify_certificate_standalone.py <certificate.json>", file=sys.stderr)
        return 2

    path = argv[1]
    with open(path, "rb") as f:
        raw_bytes = f.read()

    sha256_hash = hashlib.sha256(raw_bytes).hexdigest()
    data = json.loads(raw_bytes.decode("utf-8"))

    cert_type = data.get("certificate_type")
    print(f"[*] Certificate target: {data.get('target_id')} (Type: {cert_type})")
    print(f"[*] File SHA-256: {sha256_hash}")

    if cert_type == "vanderwaerden":
        valid, msg = verify_vdw_pure(data["coloring"], data["r"], data["k"])
    elif cert_type == "schur":
        valid, msg = verify_schur_pure(data["partition"], data["k"])
    else:
        print(f"[!] Unsupported certificate type: {cert_type}", file=sys.stderr)
        return 1

    if valid:
        print(f"[SUCCESS] {msg}")
        return 0
    else:
        print(f"[FAILED] {msg}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

### Passo 3 — Criar `src/evobyte/certificate_exporter.py`

Implemente rotinas para transformar o melhor candidato de uma execução em um certificado JSON padronizado com campos:
- `target_id`
- `certificate_type`
- `candidate_length`
- `reference_literature`
- `sha256_checksum`
- `reproduction_seed`

### Passo 4 — Testes `tests/test_standalone_verifier.py`

Valide:
1. `test_standalone_verifier_on_valid_vdw`: Cria certificado de teste válido e roda `verify_vdw_pure` retornando `True`.
2. `test_standalone_verifier_on_corrupted_vdw`: Altera uma cor para forçar AP e confirma que o verificador falha.
3. `test_standalone_script_cli_execution`: Executa `python3 scripts/verify_certificate_standalone.py` via `subprocess.run` e confirma código de saída 0.

### Passo 5 — Dossiê `docs/research/p167-external-validation-dossier.md`

Monte o dossiê com:
- Guia passo a passo de como qualquer pesquisador externo pode clonar e rodar o verificador em 3 comandos.
- Minuta do comunicado de submissão (formato Markdown e texto puro).

## Regras de parada (PARE, não commite, reporte)

- O script `verify_certificate_standalone.py` importar qualquer módulo fora da biblioteca padrão (`sys`, `json`, `hashlib`).
- Falha na execução do subprocesso do verificador.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_standalone_verifier.py -q
python3 scripts/verify_certificate_standalone.py dist/external-validation/sample_certificate.json
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add scripts/verify_certificate_standalone.py src/evobyte/certificate_exporter.py \
  tests/test_standalone_verifier.py docs/research/p167-external-validation-dossier.md \
  dist/external-validation/sample_certificate.json docs/phases/P167-external-validation-dossier.md
git diff --cached --check
git commit -m "feat(research): implement p167 external validation standalone verifier and dossier"
git push -u origin HEAD
gh pr create --base codex/p166-preregistered-record-campaign \
  --title "feat(research): implement p167 external validation dossier" \
  --body-file /tmp/evobyte-p167-pr.md
git status --short
```

---

**Status da execução (2026-10-22):** Done.

- `scripts/verify_certificate_standalone.py` implementado com o código da especificação:
  importa **apenas** `hashlib`, `json` e `sys` (regra de parada da fase verificada por teste
  estático via AST), e roda em Python 3.9+ sem `evobyte`, `numpy` ou `scipy`.
- `src/evobyte/certificate_exporter.py` implementado: exporta o certificado JSON padronizado
  com `target_id`, `certificate_type`, `candidate_length`, `reference_literature`,
  `sha256_checksum`, `reproduction_seed` (mais `sha256_scope` e `provenance`), recusando
  qualquer candidato que não passe no verificador independente local.
- `dist/external-validation/sample_certificate.json` gerado a partir de uma execução real
  (Tabu Search, semente 42, 10,0 s, 27.517 avaliações) **idêntica** ao trial
  `10.0s|vdw_3_3_26|TabuSearch|seed 42` da campanha P166: o hash do objeto
  (`00775b4c5a10e239...`) é exatamente o `candidate_sha256` registrado no `summary.json` da
  campanha, fechando a cadeia de custódia.
- Verificação externa executada em diretório limpo, sem o pacote instalado: `SUCCESS`,
  código de saída 0, em menos de 1 s.
- `tests/test_standalone_verifier.py`: 6 testes verdes (os 3 exigidos pela especificação,
  mais a checagem do certificado de exemplo pelas duas implementações, a recusa de candidato
  inválido pelo exportador e a verificação estática de imports só-padrão).
- `docs/research/p167-external-validation-dossier.md` com o guia de 3 comandos, a cadeia de
  custódia, as limitações honestas e a minuta de comunicação em Markdown e texto puro.
- `git diff --check` limpo, `pytest tests` completo verde, `make verify` verde.

Desvios em relação a esta especificação, registrados no PR:

- **`.gitignore` foi alterado** (fora da lista de arquivos editáveis da fase) porque
  `dist/` estava ignorado e o gate da fase exige o certificado de exemplo em
  `dist/external-validation/sample_certificate.json`, que precisa ser versionado para ser
  distribuível. A mudança é mínima: `dist/` passou a `dist/*` com a exceção
  `!dist/external-validation/`; o resto de `dist/` (bundle Zenodo, tarball) continua
  ignorado, verificado com `git add -n dist/`.
- **O certificado de exemplo é um empate com o recorde publicado** ($W(3,3) = 27$), não um
  recorde novo; a minuta de comunicação declara isso explicitamente e não usa a palavra
  "novo". A fase não produziu — nem poderia, com o catálogo da P163 — um certificado que
  superasse um ótimo provado.
