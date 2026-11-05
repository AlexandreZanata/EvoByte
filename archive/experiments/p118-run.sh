#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py --acceptance-phase P118 --config experiments/p118-config.json --output /tmp/evobyte-p118-acceptance.json
