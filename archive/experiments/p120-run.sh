#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py \
  --acceptance-phase P120 \
  --config experiments/p120-config.json \
  --output /tmp/evobyte-p120-acceptance.json
