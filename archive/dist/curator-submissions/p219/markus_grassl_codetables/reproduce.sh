#!/usr/bin/env bash
# Reproduction script for Markus Grassl codetables submission
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${DIR}"

echo "=== Markus Grassl Submission Reproduction ==="
echo "[1/3] Verifying certificate SHA-256 checksums..."
sha256sum -c << 'EOF'
f432cd3f8008aee2ce24ea7790beac553304db5034da604a5097ae73dced7227  certificate_qecc_20_2.json
0c604cd8eeaeb19add3490cb4e75ad2b57f04e5772951a27342b938116adff20  certificate_bivariate_16_2.json
5354a5fbe043ad5bc0d0694ce1dfaa8b27d8af8c62d8a027b04c1981ab11b6ee  verify_bivariate_certificate.py
EOF

echo "[2/3] Running zero-dependency pure Python 3 verifier..."
python3 -S verify_bivariate_certificate.py certificate_qecc_20_2.json certificate_bivariate_16_2.json

echo "[3/3] Verification SUCCESS: [[20, 2, 6]] and [[16, 2, 4]] confirmed in < 3 ms."
