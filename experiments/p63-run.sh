#!/bin/bash
# P63 one-scorer feedback comparison (frozen command). Development only; outcome reported, nothing promoted.
python3 benchmarks/science_matrix.py --acceptance-phase P63 --config experiments/p63-config.json --output /tmp/evobyte-p63-acceptance.json
