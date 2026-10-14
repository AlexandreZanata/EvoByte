#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "P88 Quality Gates & Clean-Tree Acceptance"
echo "=========================================================="

git diff --check
git status --short

echo "Running ruff check..."
python3 -m ruff check src benchmarks tests

echo "Building Lean 4 formal proofs..."
lake -d lean_proofs build

echo "Running pytest suite..."
python3 -m pytest tests -q

echo "Running P88 meta-theorem formal campaign acceptance audit..."
python3 benchmarks/science_matrix.py \
  --acceptance-phase P88 \
  --config experiments/p88-config.json \
  --output /tmp/evobyte-p88-acceptance.json

echo "P88 acceptance audit completed successfully!"
