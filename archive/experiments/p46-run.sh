#!/bin/bash
# P46 acceptance run (frozen command). Validates the sourced catalogue; human review is separate.
python3 benchmarks/science_matrix.py --acceptance-phase P46 --config experiments/p46-config.json --output /tmp/evobyte-p46-acceptance.json
