#!/usr/bin/env bash
# Reproduction script for SQS(10) / C(10, 4, 3) = 30 covering design certificate
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${DIR}"

echo "=== Neil Sloane OEIS Submission Reproduction ==="
echo "[1/3] Verifying certificate SHA-256 checksum..."
sha256sum -c << 'EOF'
e20a8c24a3ae395b6a8d481c95f7b84f89589a290448bad290b80e6b0196cc64  certificate.json
26107b4b94304f62a95ba29e977f8d7f2996e7d0e92f86fe3fa6452cece0a2b0  verify_structured_certificate.py
EOF

echo "[2/3] Running zero-dependency standalone verifier..."
python3 -S verify_structured_certificate.py certificate.json

echo "[3/3] Verification SUCCESS: SQS(10) = 30 confirmed in < 1 ms."
