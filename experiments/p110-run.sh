#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py \
  --acceptance-phase P110 \
  --config experiments/p110-config.json \
  --output /tmp/evobyte-p110-acceptance.json
