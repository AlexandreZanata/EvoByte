#!/bin/bash
# P79 blind residue confirmation audit (frozen command).
python3 benchmarks/science_matrix.py --acceptance-phase P79 --config experiments/p79-config.json --output /tmp/evobyte-p79-acceptance.json
