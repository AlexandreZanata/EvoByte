#!/usr/bin/env bash
# Reproduction script for C(14, 6, 3) and C(16, 7, 3) null bound certificates
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${DIR}"

echo "=== Dan Gordon LJCR Submission Reproduction ==="
echo "[1/3] Verifying certificate SHA-256 checksums..."
sha256sum -c << 'EOF'
1c027552c349c9cd55e80b6b63bed2f8fa71397d395571edf2b5f780c9e7d8d6  certificate_C_14_6_3.json
745f6d08d07b631717a86a9bf819d3e3e8a6224844ec5905cca28f3bce29bb1d  certificate_C_16_7_3.json
5354a5fbe043ad5bc0d0694ce1dfaa8b27d8af8c62d8a027b04c1981ab11b6ee  verify_bivariate_certificate.py
EOF

echo "[2/3] Running zero-dependency pure Python 3 verifier..."
python3 -S verify_bivariate_certificate.py certificate_C_14_6_3.json certificate_C_16_7_3.json

echo "[3/3] Verification SUCCESS: C(14, 6, 3) and C(16, 7, 3) null bounds confirmed in < 1 ms."
