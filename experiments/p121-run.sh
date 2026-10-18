#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.elan/bin:$PATH"

lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py \
  --acceptance-phase P121 \
  --config experiments/p121-config.json \
  --output /tmp/evobyte-p121-acceptance.json
