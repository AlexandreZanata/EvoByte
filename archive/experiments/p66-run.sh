#!/bin/bash
# P66 packet comparison (frozen command). Development only; outcome reported, nothing promoted.
python3 benchmarks/science_matrix.py --acceptance-phase P66 --config experiments/p66-config.json --output /tmp/evobyte-p66-acceptance.json
