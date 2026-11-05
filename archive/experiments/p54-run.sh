#!/bin/bash
# P54 acceptance run (frozen command). Screen 10 s, confirm top-2 plus classical 60 s.
python3 benchmarks/science_matrix.py --acceptance-phase P54 --config experiments/p54-config.json --output /tmp/evobyte-p54-acceptance.json
