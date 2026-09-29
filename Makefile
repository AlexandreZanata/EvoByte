.PHONY: setup test lint verify bench mvp-demo hw-probe

setup:
	python3 -m pip install -e ".[dev]"

test:
	python3 -m pytest tests -q

lint:
	python3 -m ruff check src tests benchmarks || true
	python3 -m ruff format --check src tests benchmarks || true
	git diff --check

verify: lint test
	python3 benchmarks/synthetic.py --smoke

bench:
	python3 benchmarks/synthetic.py --benchmark

mvp-demo:
	python3 benchmarks/synthetic.py --smoke

hw-probe:
	python3 benchmarks/hw_probe.py
