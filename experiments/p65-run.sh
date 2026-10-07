#!/bin/bash
# P65 paired library comparison (frozen command). Development only; outcome reported, nothing promoted.
python3 benchmarks/science_matrix.py --acceptance-phase P65 --config experiments/p65-config.json --output /tmp/evobyte-p65-acceptance.json
