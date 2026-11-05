#!/bin/bash
# P42 acceptance run (frozen command). Revalidates P35 positives by exact verification.
python3 benchmarks/science_matrix.py --acceptance-phase P42 --config experiments/p42-config.json --output /tmp/evobyte-p42-acceptance.json
