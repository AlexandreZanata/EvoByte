#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py \
  --acceptance-phase P147 \
  --config experiments/p147-config.json \
  --output /tmp/evobyte-p147-acceptance.json
