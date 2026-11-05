#!/bin/bash
# P99 algebraic sieve on quaternion orders audit (frozen command).
python3 benchmarks/science_matrix.py --acceptance-phase P99 --config experiments/p99-config.json --output /tmp/evobyte-p99-acceptance.json
