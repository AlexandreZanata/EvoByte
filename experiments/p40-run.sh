#!/bin/bash
# P40 acceptance run (frozen command). No search budgets: audit inspects manifests.
python3 benchmarks/science_matrix.py --acceptance-phase P40 --config experiments/p40-config.json --output /tmp/evobyte-p40-acceptance.json
