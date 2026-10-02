#!/bin/bash
# P43 acceptance run (frozen command). Continuation runs in a fresh OS process.
python3 benchmarks/science_matrix.py --acceptance-phase P43 --config experiments/p43-config.json --output /tmp/evobyte-p43-acceptance.json
