#!/usr/bin/env bash
# Reproduction script for C(13, 5, 3) and C(15, 10, 4) null bound certificates
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${DIR}"

echo "=== Dan Gordon LJCR Submission Reproduction ==="
echo "[1/3] Verifying certificate SHA-256 checksums..."
sha256sum -c << 'EOF'
eb9ecdd536f6cad416f960f762149d6a53eeb6574b9fa48ca829e9eff724f80f  certificate_C_13_5_3.json
f15d7f56c526aea33aa234fb9bb3b44b43e28e51b3347367a2d1a732edf3a928  certificate_C_15_10_4.json
af73fd48fa609e6c93079664ab4d96d46361097dbe2085fffa8b05105b183991  verify_generalized_certificate.py
EOF

echo "[2/3] Running zero-dependency pure Python 3 verifier..."
python3 -S verify_generalized_certificate.py certificate_C_13_5_3.json certificate_C_15_10_4.json

echo "[3/3] Verification SUCCESS: C(13, 5, 3) and C(15, 10, 4) null bounds confirmed in < 1 ms."
