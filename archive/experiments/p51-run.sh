#!/bin/bash
# P51 acceptance run (frozen command). Sampled map; replay rebuilds declared segments.
python3 benchmarks/science_matrix.py --acceptance-phase P51 --config experiments/p51-config.json --output /tmp/evobyte-p51-acceptance.json
