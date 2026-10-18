#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py \
  --acceptance-phase P128 \
  --config experiments/p128-config.json \
  --output /tmp/evobyte-p128-acceptance.json
