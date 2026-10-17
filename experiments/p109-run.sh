#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py \
  --acceptance-phase P109 \
  --config experiments/p109-config.json \
  --output /tmp/evobyte-p109-acceptance.json
