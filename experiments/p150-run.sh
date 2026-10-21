#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

CONFIG_PATH="${1:-experiments/p150-config.json}"
OUTPUT_PATH="${2:-/tmp/evobyte-p150-acceptance.json}"

echo "=============================================================================="
echo "RUNNING P150 WORLD LITERATURE NOVELTY DUAL AUDIT"
echo "  Config: ${CONFIG_PATH}"
echo "  Output: ${OUTPUT_PATH}"
echo "=============================================================================="

python3 benchmarks/science_matrix.py \
    --acceptance-phase P150 \
    --config "${CONFIG_PATH}" \
    --output "${OUTPUT_PATH}"

echo "P150 execution completed successfully."
