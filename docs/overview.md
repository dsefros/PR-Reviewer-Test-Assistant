# PR Reviewer + Test Assistant — Overview

## What this product is
PR Reviewer + Test Assistant is a Python service for analyzing git diffs through multiple modes such as review, test-check, and test-scenarios.

## Interfaces
- FastAPI API
- Typer CLI

## Core behavior
- Accepts a diff
- Renders a mode-specific prompt
- Calls an LLM backend
- Validates output against schemas
- Persists traces/results into JSONL artifacts

## Main docs
- Setup: docs/setup.md
- Configuration: docs/configuration.md
- CLI: docs/cli.md
- API: docs/api.md
- Architecture: docs/architecture.md
- Review flow: docs/flows/review_flow.md
- Test check flow: docs/flows/test_check_flow.md
- Test scenarios flow: docs/flows/test_scenarios_flow.md
- Extension guide: docs/extension_guide.md
- Testing: docs/testing.md
- Observability: docs/observability.md
- Roadmap: docs/roadmap.md
- Known issues: docs/known_issues.md

## Current architecture summary
- API runs in Docker
- Ollama runs on the host
- API connects to Ollama through explicit runtime configuration
- JSONL files are used for trace/result persistence
