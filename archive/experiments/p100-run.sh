#!/bin/bash
# P100 dioph_surface metatactic audit (frozen command).
python3 benchmarks/science_matrix.py --acceptance-phase P100 --config experiments/p100-config.json --output /tmp/evobyte-p100-acceptance.json
