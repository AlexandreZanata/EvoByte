#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py \
  --acceptance-phase P138 \
  --config experiments/p138-config.json \
  --output /tmp/evobyte-p138-acceptance.json
