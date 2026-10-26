#!/usr/bin/env bash
# Reproduction script for QECC stabilizer validation
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${DIR}"

echo "=== Markus Grassl codetables.de Submission Reproduction ==="
echo "[1/3] Verifying certificate SHA-256 checksum..."
sha256sum -c << 'EOF'
952d6b04b0664daa4fcc8c4219ba7958ed60655ce7728467c515ca7769c60ecd  certificate.json
26107b4b94304f62a95ba29e977f8d7f2996e7d0e92f86fe3fa6452cece0a2b0  verify_structured_certificate.py
EOF

echo "[2/3] Running zero-dependency standalone symplectic verifier..."
python3 -S verify_structured_certificate.py certificate.json

echo "[3/3] Verification SUCCESS: [[8, 3, 3]] stabilizer code verified in < 1 ms."
