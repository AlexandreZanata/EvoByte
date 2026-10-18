#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py --acceptance-phase P113 --config experiments/p113-config.json --output /tmp/evobyte-p113-acceptance.json
