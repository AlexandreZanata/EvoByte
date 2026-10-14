#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "P89 Quality Gates & Clean-Tree Acceptance"
echo "=========================================================="

git diff --check
git status --short

echo "Running ruff check..."
python3 -m ruff check src benchmarks tests

echo "Building Lean 4 formal proofs and tactics..."
lake -d lean_proofs build

echo "Running pytest suite..."
python3 -m pytest tests -q

echo "Running P89 custom tactic metaprogramming acceptance audit..."
python3 benchmarks/science_matrix.py \
  --acceptance-phase P89 \
  --config experiments/p89-config.json \
  --output /tmp/evobyte-p89-acceptance.json

echo "=========================================================="
echo "P89 Acceptance Gate Passed Cleanly"
echo "=========================================================="
