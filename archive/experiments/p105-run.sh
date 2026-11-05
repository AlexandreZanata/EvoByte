#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py --acceptance-phase P105 --config experiments/p105-config.json --output /tmp/evobyte-p105-acceptance.json
