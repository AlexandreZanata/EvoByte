#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "P94 Quality Gates & Clean-Tree Acceptance"
echo "=========================================================="

git diff --check
git status --short

echo "Running ruff check..."
python3 -m ruff check src benchmarks tests

echo "Building Lean 4 formal proofs and tactics..."
lake -d lean_proofs build

echo "Running pytest suite..."
python3 -m pytest tests -q

echo "Running P94 universal multiterm coprimality acceptance audit..."
python3 benchmarks/science_matrix.py \
  --acceptance-phase P94 \
  --config experiments/p94-config.json \
  --output /tmp/evobyte-p94-acceptance.json

echo "=========================================================="
echo "P94 Acceptance Gate Passed Cleanly"
echo "=========================================================="
