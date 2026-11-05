#!/bin/bash
# P53 acceptance run (frozen command). One small proposer; real training; independent reload.
python3 benchmarks/science_matrix.py --acceptance-phase P53 --config experiments/p53-config.json --output /tmp/evobyte-p53-acceptance.json
