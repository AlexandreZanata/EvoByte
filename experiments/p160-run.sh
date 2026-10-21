#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

CONFIG_PATH="${1:-experiments/p160-config.json}"
OUTPUT_PATH="${2:-/tmp/evobyte-p160-acceptance.json}"

echo "=============================================================================="
echo "RUNNING P160 SYSTEMS RESEARCH MANUSCRIPT PUBLICATION AUDIT"
echo "  Config: ${CONFIG_PATH}"
echo "  Output: ${OUTPUT_PATH}"
echo "=============================================================================="

# Ensure LaTeX figures/tables are generated and PDF is compiled
python3 docs/paper/generate_figures.py
(cd docs/paper && pdflatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null)

python3 benchmarks/science_matrix.py \
    --acceptance-phase P160 \
    --config "${CONFIG_PATH}" \
    --output "${OUTPUT_PATH}"

echo "P160 execution completed successfully."
