#!/usr/bin/env bash
set -euo pipefail

python3 benchmarks/science_matrix.py --acceptance-phase P112 --config experiments/p112-config.json --output /tmp/evobyte-p112-acceptance.json
