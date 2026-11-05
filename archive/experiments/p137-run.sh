#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py \
  --acceptance-phase P137 \
  --config experiments/p137-config.json \
  --output /tmp/evobyte-p137-acceptance.json
