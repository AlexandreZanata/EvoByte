#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py \
  --acceptance-phase P145 \
  --config experiments/p145-config.json \
  --output /tmp/evobyte-p145-acceptance.json
