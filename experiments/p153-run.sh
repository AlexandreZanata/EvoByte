#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

CONFIG_PATH="${1:-experiments/p153-config.json}"
OUTPUT_PATH="${2:-/tmp/evobyte-p153-acceptance.json}"

echo "=============================================================================="
echo "RUNNING P153 CLEAN REPRODUCTION HARNESS AUDIT (P13 / FRENTE 2 D039)"
echo "  Config: ${CONFIG_PATH}"
echo "  Output: ${OUTPUT_PATH}"
echo "=============================================================================="

python3 benchmarks/synthetic.py --smoke

python3 benchmarks/science_matrix.py \
    --acceptance-phase P153 \
    --config "${CONFIG_PATH}" \
    --output "${OUTPUT_PATH}"

echo "P153 execution completed successfully."
