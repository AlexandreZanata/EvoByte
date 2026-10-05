#!/bin/bash
# P50 acceptance run (frozen command). Same criterion, billed costs, no isolated win.
python3 benchmarks/science_matrix.py --acceptance-phase P50 --config experiments/p50-config.json --output /tmp/evobyte-p50-acceptance.json
