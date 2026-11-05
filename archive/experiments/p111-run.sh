#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py \
  --acceptance-phase P111 \
  --config experiments/p111-config.json \
  --output /tmp/evobyte-p111-acceptance.json
