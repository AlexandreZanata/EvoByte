#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py --acceptance-phase P115 --config experiments/p115-config.json --output /tmp/evobyte-p115-acceptance.json
