#!/usr/bin/env bash
# =============================================================================
# scripts/verify_lean_p221.sh — Hermetic Lean 4 Verification Gate (P221)
#
# Verifies:
# 1. `lake build Generated.BivariateReal` exits with code 0.
# 2. Zero occurrences of `sorry` in BivariateReal.lean.
# 3. `#print axioms` strictly restricted to [propext, Classical.choice, Quot.sound].
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LEAN_DIR="${REPO_ROOT}/lean_proofs"
LEAN_FILE="${LEAN_DIR}/Generated/BivariateReal.lean"

echo "=== P221 Lean 4 Formal Verification Gate ==="
echo "[*] Repo root: ${REPO_ROOT}"
echo "[*] Lean file: ${LEAN_FILE}"

# 1. Check file existence
if [[ ! -f "${LEAN_FILE}" ]]; then
  echo "[!] ERROR: Formal Lean file not found at ${LEAN_FILE}" >&2
  exit 1
fi

# 2. Strict text check: zero 'sorry' tokens
echo "[*] Checking for forbidden 'sorry' tokens..."
if grep -nw "sorry" "${LEAN_FILE}"; then
  echo "[!] ERROR: Forbidden 'sorry' token found in ${LEAN_FILE}" >&2
  exit 1
fi
echo "[+] Zero 'sorry' tokens confirmed."

# 3. Run hermetic Lake build
echo "[*] Compiling Generated.BivariateReal via lake build..."
cd "${LEAN_DIR}"
BUILD_OUTPUT=$(lake build Generated.BivariateReal 2>&1)
echo "${BUILD_OUTPUT}"

# 4. Axiom check: ensure only standard axioms appear
echo "[*] Validating emitted axioms..."
ALLOWED_AXIOMS=("propext" "Classical.choice" "Quot.sound")

# Grep lines mentioning "depends on axioms"
while IFS= read -r line; do
  if [[ -n "${line}" ]]; then
    echo "[*] Axiom line: ${line}"
    # Extract list inside brackets: [axiom1, axiom2, ...]
    if [[ "${line}" =~ \[([^\]]*)\] ]]; then
      axioms_str="${BASH_REMATCH[1]}"
      IFS=',' read -ra AXIOM_LIST <<< "${axioms_str}"
      for ax in "${AXIOM_LIST[@]}"; do
        # Trim whitespace
        ax_trimmed=$(echo "${ax}" | xargs)
        if [[ -n "${ax_trimmed}" ]]; then
          allowed=0
          for ok_ax in "${ALLOWED_AXIOMS[@]}"; do
            if [[ "${ax_trimmed}" == "${ok_ax}" ]]; then
              allowed=1
              break
            fi
          done
          if [[ "${allowed}" -eq 0 ]]; then
            echo "[!] ERROR: Disallowed non-standard axiom detected: '${ax_trimmed}'" >&2
            exit 1
          fi
        fi
      done
    fi
  fi
done < <(echo "${BUILD_OUTPUT}" | grep "depends on axioms" || true)

echo "[SUCCESS] All P221 Lean 4 formal verification gates passed cleanly!"
exit 0
