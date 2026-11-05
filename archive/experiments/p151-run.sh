#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

CONFIG_PATH="${1:-experiments/p151-config.json}"
OUTPUT_PATH="${2:-/tmp/evobyte-p151-acceptance.json}"

echo "=============================================================================="
echo "RUNNING P151 BLIND CONFIRMATION AUDIT (HOLM FWER alpha=0.01)"
echo "  Config: ${CONFIG_PATH}"
echo "  Output: ${OUTPUT_PATH}"
echo "=============================================================================="

python3 benchmarks/science_matrix.py \
    --acceptance-phase P151 \
    --config "${CONFIG_PATH}" \
    --output "${OUTPUT_PATH}"

echo "P151 execution completed successfully."
