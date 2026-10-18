#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py --acceptance-phase P116 --config experiments/p116-config.json --output /tmp/evobyte-p116-acceptance.json
