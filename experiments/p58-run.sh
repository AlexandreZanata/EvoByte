#!/bin/bash
# P58 acceptance run (frozen command). Reconciliation only; no new search, no discovery claimed.
python3 benchmarks/science_matrix.py --acceptance-phase P58 --config experiments/p58-config.json --output /tmp/evobyte-p58-acceptance.json
