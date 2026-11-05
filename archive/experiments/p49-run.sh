#!/bin/bash
# P49 acceptance run (frozen command). Conformance only; no search, no claims.
python3 benchmarks/science_matrix.py --acceptance-phase P49 --config experiments/p49-config.json --output /tmp/evobyte-p49-acceptance.json
