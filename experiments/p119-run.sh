#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py \
  --acceptance-phase P119 \
  --config experiments/p119-config.json \
  --output /tmp/evobyte-p119-acceptance.json
