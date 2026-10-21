#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

CONFIG_PATH="${1:-experiments/p154-config.json}"
OUTPUT_PATH="${2:-/tmp/evobyte-p154-acceptance.json}"

echo "=============================================================================="
echo "RUNNING P154 FULL WALL-CLOCK BENCHMARK MATRIX AUDIT (20 SEEDS, VRAM < 6GB)"
echo "  Config: ${CONFIG_PATH}"
echo "  Output: ${OUTPUT_PATH}"
echo "=============================================================================="

python3 benchmarks/science_matrix.py \
    --acceptance-phase P154 \
    --config "${CONFIG_PATH}" \
    --output "${OUTPUT_PATH}"

echo "P154 execution completed successfully."
