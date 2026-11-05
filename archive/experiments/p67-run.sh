#!/bin/bash
# P67 macro compression audit (frozen command). Development only; outcome reported, nothing promoted.
python3 benchmarks/science_matrix.py --acceptance-phase P67 --config experiments/p67-config.json --output /tmp/evobyte-p67-acceptance.json
