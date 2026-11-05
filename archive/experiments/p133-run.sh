#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.elan/bin:$PATH"

lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py \
  --acceptance-phase P133 \
  --config experiments/p133-config.json \
  --output /tmp/evobyte-p133-acceptance.json
