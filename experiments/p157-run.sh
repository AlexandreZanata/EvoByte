#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

CONFIG_PATH="${1:-experiments/p157-config.json}"
OUTPUT_PATH="${2:-/tmp/evobyte-p157-acceptance.json}"

echo "=============================================================================="
echo "RUNNING P157 SYSTEMATIC 9-ABLATION MEASUREMENT & CASCADE PROFILING AUDIT"
echo "  Config: ${CONFIG_PATH}"
echo "  Output: ${OUTPUT_PATH}"
echo "=============================================================================="

python3 benchmarks/science_matrix.py \
    --acceptance-phase P157 \
    --config "${CONFIG_PATH}" \
    --output "${OUTPUT_PATH}"

echo "P157 execution completed successfully."
