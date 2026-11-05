#!/bin/bash
# P80 certified formal campaign audit (frozen command).
python3 benchmarks/science_matrix.py --acceptance-phase P80 --config experiments/p80-config.json --output /tmp/evobyte-p80-acceptance.json
