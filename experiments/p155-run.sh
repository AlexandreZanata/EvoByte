#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

CONFIG_PATH="${1:-experiments/p155-config.json}"
OUTPUT_PATH="${2:-/tmp/evobyte-p155-acceptance.json}"

echo "=============================================================================="
echo "RUNNING P155 HONEST COMPETITIVE BASELINES AUDIT (EQUAL WALL-CLOCK BUDGETS)"
echo "  Config: ${CONFIG_PATH}"
echo "  Output: ${OUTPUT_PATH}"
echo "=============================================================================="

python3 benchmarks/science_matrix.py \
    --acceptance-phase P155 \
    --config "${CONFIG_PATH}" \
    --output "${OUTPUT_PATH}"

echo "P155 execution completed successfully."
