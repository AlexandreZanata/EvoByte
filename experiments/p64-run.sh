#!/bin/bash
# P64 obstruction economics (frozen command). Declared boxes only; outcome reported, nothing promoted.
python3 benchmarks/science_matrix.py --acceptance-phase P64 --config experiments/p64-config.json --output /tmp/evobyte-p64-acceptance.json
