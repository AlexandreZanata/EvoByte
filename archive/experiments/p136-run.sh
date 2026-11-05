#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py \
  --acceptance-phase P136 \
  --config experiments/p136-config.json \
  --output /tmp/evobyte-p136-acceptance.json
