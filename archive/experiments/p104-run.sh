#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py --acceptance-phase P104 --config experiments/p104-config.json --output /tmp/evobyte-p104-acceptance.json
