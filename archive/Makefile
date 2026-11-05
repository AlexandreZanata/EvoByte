.PHONY: setup test lint verify bench mvp-demo hw-probe verify-container export-bundle

setup:
	python3 -m pip install -e ".[dev]"

test:
	python3 -m pytest tests -q

lint:
	python3 -m ruff check --select E9,F63,F7,F82,F821,F822,F823 src tests benchmarks
	test -d .git && git diff --check || true

verify: lint test
	python3 benchmarks/synthetic.py --smoke

verify-container:
	docker build -t evobyte:reproducible -f Dockerfile .
	docker run --rm --network none evobyte:reproducible make verify

export-bundle:
	python3 scripts/export_zenodo_bundle.py --output-dir dist/zenodo-bundle

bench:
	python3 benchmarks/synthetic.py --benchmark

qforge-smoke:
	python3 benchmarks/qforge_smoke.py --seeds 3

mvp-demo:
	python3 benchmarks/synthetic.py --smoke

hw-probe:
	python3 benchmarks/hw_probe.py
