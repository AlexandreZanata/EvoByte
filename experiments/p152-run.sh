#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

CONFIG_PATH="${1:-experiments/p152-config.json}"
OUTPUT_PATH="${2:-/tmp/evobyte-p152-acceptance.json}"

echo "=============================================================================="
echo "RUNNING P152 CONSTRUCTIVE ALGEBRAIC GRAND CAMPAIGN AUDIT (54 MODULES, 0 SORRY)"
echo "  Config: ${CONFIG_PATH}"
echo "  Output: ${OUTPUT_PATH}"
echo "=============================================================================="

python3 benchmarks/science_matrix.py \
    --acceptance-phase P152 \
    --config "${CONFIG_PATH}" \
    --output "${OUTPUT_PATH}"

echo "P152 execution completed successfully."
