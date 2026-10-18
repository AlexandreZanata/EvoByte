#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py \
  --acceptance-phase P127 \
  --config experiments/p127-config.json \
  --output /tmp/evobyte-p127-acceptance.json
