#!/bin/bash
# P57 acceptance run (frozen command). Bounded instances; no discovery claimed.
python3 benchmarks/science_matrix.py --acceptance-phase P57 --config experiments/p57-config.json --output /tmp/evobyte-p57-acceptance.json
