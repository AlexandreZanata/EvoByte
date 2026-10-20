#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py \
  --acceptance-phase P148 \
  --config experiments/p148-config.json \
  --output /tmp/evobyte-p148-acceptance.json
