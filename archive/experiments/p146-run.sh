#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py \
  --acceptance-phase P146 \
  --config experiments/p146-config.json \
  --output /tmp/evobyte-p146-acceptance.json
