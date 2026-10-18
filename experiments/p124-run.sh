#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.elan/bin:$PATH"

lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py \
  --acceptance-phase P124 \
  --config experiments/p124-config.json \
  --output /tmp/evobyte-p124-acceptance.json
