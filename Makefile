.PHONY: install test demo
install: ; pip install -e ".[dev]"
test: ; pytest -q
demo: ; copilot samples/rfp-retail-analytics.md -o out/sample-proposal.md
