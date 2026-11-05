# Makefile for EvoByte Bivariate Bicycle Codes & Projective Geometry Discovery Manuscript (P220)

.PHONY: all check pdf clean

all: check pdf

pdf: main.tex references.bib
	pdflatex -halt-on-error -interaction=nonstopmode main.tex
	bibtex main || true
	pdflatex -halt-on-error -interaction=nonstopmode main.tex
	pdflatex -halt-on-error -interaction=nonstopmode main.tex

check: main.tex
	@echo "Checking manuscript for banned terms (sorry, TODO, unchecked claims)..."
	@! grep -i "sorry" main.tex || (echo "ERROR: 'sorry' found in main.tex" && exit 1)
	@! grep -i "TODO" main.tex || (echo "ERROR: 'TODO' found in main.tex" && exit 1)
	@! grep -i "FIXME" main.tex || (echo "ERROR: 'FIXME' found in main.tex" && exit 1)
	@! grep -i "quebramos" main.tex || (echo "ERROR: 'quebramos' found in main.tex" && exit 1)
	@python3 -c 'import sys; text = open("main.tex").read().lower(); [sys.exit(f"ERROR: Unverified claim: {p}") for p in ["we broke the record", "descobrimos novo recorde", "new record discovered"] if p in text]; print("Static check passed: 0 banned keywords, 0 uncertified claims.")'

clean:
	rm -f *.aux *.log *.out *.bbl *.blg *.toc *.synctex.gz
