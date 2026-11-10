# Changelog

## Unreleased

- Added a "Run it in 60 seconds" section to the README (install + `copilot` on the sample retail RFP). The documented command now uses `python3` rather than `python3.11`.
- Added GitHub issue and pull request templates.
- Added tests that the estimate's cost equals `total_days * RATE_PER_DAY_USD`, and that the CLI writes a draft proposal file.

## 0.1.0 - 2026-10-14

Initial public release: a four-agent LangGraph copilot that turns an RFP into a traceability matrix, solution outline, effort estimate, risk register and Markdown proposal. Defaults to a mock LLM.
