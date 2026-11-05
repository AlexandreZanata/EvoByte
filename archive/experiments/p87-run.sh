#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "P87 Quality Gates & Clean-Tree Acceptance"
echo "=========================================================="

git diff --check
git status --short

echo "Running ruff check..."
python3 -m ruff check src benchmarks tests

echo "Building Lean 4 formal proofs..."
lake -d lean_proofs build

echo "Running pytest suite..."
python3 -m pytest tests -q

echo "Running P87 science matrix acceptance audit..."
python3 benchmarks/science_matrix.py \
  --acceptance-phase P87 \
  --config experiments/p87-config.json \
  --output /tmp/evobyte-p87-acceptance.json

echo "P87 acceptance audit completed successfully!"
