#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py \
  --acceptance-phase P108 \
  --config experiments/p108-config.json \
  --output /tmp/evobyte-p108-acceptance.json
