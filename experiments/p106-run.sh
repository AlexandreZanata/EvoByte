#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py --acceptance-phase P106 --config experiments/p106-config.json --output /tmp/evobyte-p106-acceptance.json
