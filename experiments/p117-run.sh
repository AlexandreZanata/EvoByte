#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py --acceptance-phase P117 --config experiments/p117-config.json --output /tmp/evobyte-p117-acceptance.json
