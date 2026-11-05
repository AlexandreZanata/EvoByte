#!/bin/bash
# P52 acceptance run (frozen command). 100% recheck; disjoint splits; billed teacher.
python3 benchmarks/science_matrix.py --acceptance-phase P52 --config experiments/p52-config.json --output /tmp/evobyte-p52-acceptance.json
