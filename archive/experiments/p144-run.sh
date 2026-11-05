#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py \
  --acceptance-phase P144 \
  --config experiments/p144-config.json \
  --output /tmp/evobyte-p144-acceptance.json
