#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py \
  --acceptance-phase P149 \
  --config experiments/p149-config.json \
  --output /tmp/evobyte-p149-acceptance.json
