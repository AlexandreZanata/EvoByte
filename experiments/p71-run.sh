#!/bin/bash
# P71 fresh confirmation (frozen command). Fresh final only; provisional at best without the independent rerun.
python3 benchmarks/science_matrix.py --acceptance-phase P71 --config experiments/p71-config.json --output /tmp/evobyte-p71-acceptance.json
