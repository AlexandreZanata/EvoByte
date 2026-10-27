#!/usr/bin/env bash
# Reproduction script for C(9, 3, 2) = 12 affine plane certificate
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${DIR}"

echo "=== Neil Sloane OEIS Submission Reproduction ==="
echo "[1/3] Verifying certificate SHA-256 checksums..."
sha256sum -c << 'EOF'
0579a842ee6928770d39d8c1ac4309c8db08225b86646a956ab0c7c7b87f6c01  certificate_C_9_3_2.json
af73fd48fa609e6c93079664ab4d96d46361097dbe2085fffa8b05105b183991  verify_generalized_certificate.py
EOF

echo "[2/3] Running zero-dependency pure Python 3 verifier..."
python3 -S verify_generalized_certificate.py certificate_C_9_3_2.json

echo "[3/3] Verification SUCCESS: C(9, 3, 2) = 12 confirmed in < 1 ms."
