#!/bin/bash
# P56 acceptance run (frozen command). Fresh sealed tasks; frozen method; no discovery label.
python3 benchmarks/science_matrix.py --acceptance-phase P56 --config experiments/p56-config.json --output /tmp/evobyte-p56-acceptance.json
