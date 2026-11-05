#!/bin/bash
# P47 acceptance run (frozen command). Validates the frozen nomination; human review is separate.
python3 benchmarks/science_matrix.py --acceptance-phase P47 --config experiments/p47-config.json --output /tmp/evobyte-p47-acceptance.json
