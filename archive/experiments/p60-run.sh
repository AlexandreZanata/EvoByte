#!/bin/bash
# P60 workbench technical acceptance (frozen command). Development only; nothing promoted.
python3 benchmarks/science_matrix.py --acceptance-phase P60 --config experiments/p60-config.json --output /tmp/evobyte-p60-acceptance.json
