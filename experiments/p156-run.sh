#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

CONFIG_PATH="${1:-experiments/p156-config.json}"
OUTPUT_PATH="${2:-/tmp/evobyte-p156-acceptance.json}"

echo "=============================================================================="
echo "RUNNING P156 BLIND GENERALIZATION & EXTRAPOLATION AUDIT (CRITERION 4 H1)"
echo "  Config: ${CONFIG_PATH}"
echo "  Output: ${OUTPUT_PATH}"
echo "=============================================================================="

python3 benchmarks/science_matrix.py \
    --acceptance-phase P156 \
    --config "${CONFIG_PATH}" \
    --output "${OUTPUT_PATH}"

echo "P156 execution completed successfully."
