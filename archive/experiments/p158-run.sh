#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

CONFIG_PATH="${1:-experiments/p158-config.json}"
OUTPUT_PATH="${2:-/tmp/evobyte-p158-acceptance.json}"

echo "=============================================================================="
echo "RUNNING P158 HYPOTHESIS H1 STATISTICAL VERDICT & PARETO ANALYSIS AUDIT"
echo "  Config: ${CONFIG_PATH}"
echo "  Output: ${OUTPUT_PATH}"
echo "=============================================================================="

python3 benchmarks/science_matrix.py \
    --acceptance-phase P158 \
    --config "${CONFIG_PATH}" \
    --output "${OUTPUT_PATH}"

echo "P158 execution completed successfully."
