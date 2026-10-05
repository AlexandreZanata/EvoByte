#!/bin/bash
# P48 acceptance run (frozen command). Compiles the frozen challenge in a separate process.
python3 benchmarks/science_matrix.py --acceptance-phase P48 --config experiments/p48-config.json --output /tmp/evobyte-p48-acceptance.json
