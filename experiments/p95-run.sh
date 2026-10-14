#!/bin/bash
# P95 extreme-scale blind confirmation audit (frozen command).
python3 benchmarks/science_matrix.py --acceptance-phase P95 --config experiments/p95-config.json --output /tmp/evobyte-p95-acceptance.json
