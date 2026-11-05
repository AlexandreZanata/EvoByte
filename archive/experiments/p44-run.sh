#!/bin/bash
# P44 acceptance run (frozen command). Resident claims require the CUDA reference GPU.
python3 benchmarks/science_matrix.py --acceptance-phase P44 --config experiments/p44-config.json --output /tmp/evobyte-p44-acceptance.json
