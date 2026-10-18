#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py --acceptance-phase P114 --config experiments/p114-config.json --output /tmp/evobyte-p114-acceptance.json
