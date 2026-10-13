#!/bin/bash
# P72 novelty nomination campaign (frozen command). Target erdos-242 from reviewed catalogue; accepted components only.
python3 benchmarks/science_matrix.py --acceptance-phase P72 --config experiments/p72-config.json --output /tmp/evobyte-p72-acceptance.json
