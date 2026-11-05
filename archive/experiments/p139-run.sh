#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py \
  --acceptance-phase P139 \
  --config experiments/p139-config.json \
  --output /tmp/evobyte-p139-acceptance.json
