#!/bin/bash
# P55 acceptance run (frozen command). Optional hypothesis; explicit DEFERRED without budget.
python3 benchmarks/science_matrix.py --acceptance-phase P55 --config experiments/p55-config.json --output /tmp/evobyte-p55-acceptance.json
