#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py \
  --acceptance-phase P107 \
  --config experiments/p107-config.json \
  --output /tmp/evobyte-p107-acceptance.json
