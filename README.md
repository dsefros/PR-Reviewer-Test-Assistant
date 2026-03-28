# PR Reviewer + Test Assistant

A FastAPI server + thin CLI client that analyzes git diffs and supports five modes:

1. `review`
2. `test-check`
3. `test-scenarios`
4. `test-gen`
5. `test-maintain`

> Recommended production flow is remote CLI -> API server. CLI local mode is available for development only.
> Default transport is `http`, so pass `--server-url` unless you explicitly use `--transport local`.

## Architecture Overview

- **FastAPI API layer** in `src/api`
- **Typer CLI** in `src/cli`
- **Orchestration layer** in `src/application/orchestrators`
- **Domain rules and formatters** in `src/domain`
- **LLM adapter + backend implementations** in `src/infrastructure/llm`
- **Externalized prompts** in `src/infrastructure/prompts/templates`
- **Repository interfaces + JSONL persistence** in `src/infrastructure/storage/repositories`
- **Canonical model config loader** in `src/config/models.py` with `models.yaml`

### Key decisions

- Canonical model profiles are loaded from `models.yaml`, with `ACTIVE_MODEL_PROFILE` and optional `MODEL_BACKEND` override.
- `LLMAdapter` uses lazy backend initialization so heavy runtime deps do not load in help/smoke paths.
- Business logic is orchestrated outside API endpoints.
- Input safety includes secret masking + diff degradation limits.
- MVP persistence is JSONL repositories behind interfaces (DB-ready extension path).

## Supported Modes and Endpoints

### API Endpoints

- `POST /api/v1/analyze/review`
- `POST /api/v1/analyze/test-check`
- `POST /api/v1/analyze/test-scenarios`
- Legacy `POST /review`
- `POST /test-gen`
- `POST /test-maintain`
- `GET /health`
- `GET /ready`

Request body:

```json
{
  "diff": "...",
  "metadata": {},
  "context": {},
  "existing_tests": {}
}
```

### CLI Commands

- `ai-review review`
- `ai-review test-check`
- `ai-review test-scenarios`
- `ai-review test-gen`
- `ai-review test-maintain`

Examples:

```bash
git diff main...HEAD | ai-review review --server-url http://localhost:8000
git diff main...HEAD | ai-review test-check --server-url http://localhost:8000 --json
ai-review review --diff pr.patch --server-url http://localhost:8000
ai-review test-gen --diff pr.patch --metadata metadata.json --server-url http://localhost:8000
ai-review review --diff pr.patch --transport local --json
```

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
cp models.yaml.example models.yaml
uvicorn src.api.main:app --reload
```

## Package build/install validation (clean-env friendly)

```bash
python -m build
pip install dist/*.whl
ai-review --help
```

If your environment allows network/index access, you can additionally use:

```bash
pipx install .
```

## Docker Setup

```bash
docker compose up --build
```

Optional ollama profile:

```bash
docker compose --profile ollama up --build
```

## Configuration

- `.env.example` contains runtime settings (limits, ports, logging, masking).
- `models.yaml.example` contains profile definitions for:
  - `mock`
  - `ollama`
  - `llama_cpp`

## Large Diff Strategy

Configurable defaults:

- `MAX_DIFF_BYTES=300000`
- `MAX_DIFF_LINES=5000`
- `MAX_CHANGED_FILES=50`

When exceeded, the system truncates safely and records limitations in output.

## Security

Secret masking occurs before prompt rendering. The masker handles likely credentials including API keys, tokens, passwords, bearer values, and private keys.

## Sample patch input

`./samples/sample.patch`

## Sample output (review)

```json
{
  "summary": "Mock review summary.",
  "strengths": ["Structure is clear."],
  "issues": [],
  "risks": ["Potential uncovered logic branches."],
  "recommendations": ["Add tests for changed branches."],
  "limitations": ["Mock backend response."]
}
```

## MVP Limitations / Follow-ups

- Adjacent code context and existing tests are interface-level only (no deep parser yet).
- Multi-pass/chunked analysis is prepared by structure, not fully implemented.
- `llama_cpp` runtime requires optional dependency installation and local model files.


## Quickstart

See `docs/quickstart.md` for `pipx` installation and client/server run examples.
