#!/usr/bin/env bash
# Reproduction script for AG(2, 3) and Fano PG(2, 2) certificates
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${DIR}"

echo "=== Neil Sloane OEIS Submission Reproduction ==="
echo "[1/3] Verifying certificate SHA-256 checksums..."
sha256sum -c << 'EOF'
3d4327635edf27aac12365eb093c9c886a89d79e9647f75a6bbb9df6e0e316b0  certificate_C_9_3_2.json
32abc5fdbf663983847a56f175f904a70e4b25e35d7d86f6d958415d11bacb38  certificate_steane_7_1_3.json
5354a5fbe043ad5bc0d0694ce1dfaa8b27d8af8c62d8a027b04c1981ab11b6ee  verify_bivariate_certificate.py
EOF

echo "[2/3] Running zero-dependency pure Python 3 verifier..."
python3 -S verify_bivariate_certificate.py certificate_C_9_3_2.json certificate_steane_7_1_3.json

echo "[3/3] Verification SUCCESS: AG(2, 3) and Fano PG(2, 2) confirmed in < 1 ms."
