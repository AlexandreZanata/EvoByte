#!/bin/bash
# P41 acceptance run (frozen command). Smoke executes in a fresh exclusive dir.
python3 benchmarks/science_matrix.py --acceptance-phase P41 --config experiments/p41-config.json --output /tmp/evobyte-p41-acceptance.json
