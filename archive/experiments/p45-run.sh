#!/bin/bash
# P45 acceptance run (frozen command). Real 60s + 600s budgets at scale 1.0.
python3 benchmarks/science_matrix.py --acceptance-phase P45 --config experiments/p45-config.json --output /tmp/evobyte-p45-acceptance.json
