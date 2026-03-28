# Quickstart

## 1) Install `pipx`

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

## 2) Build and install the package

From the repository root:

```bash
python -m build
pip install dist/*.whl
ai-review --help
```

This exposes the `ai-review` command without activating a virtual environment.

If your environment has package-index access and you prefer `pipx`, you can also run:

```bash
pipx install .
```

## 3) Run the API server

```bash
uvicorn src.api.main:create_app --factory --host 0.0.0.0 --port 8000
```

Model selection defaults to `models.yaml` -> `default_model`. To override at runtime:

```bash
ACTIVE_MODEL_PROFILE=mock-default uvicorn src.api.main:create_app --factory --host 0.0.0.0 --port 8000
ACTIVE_MODEL_PROFILE=ollama-local-llama3 uvicorn src.api.main:create_app --factory --host 0.0.0.0 --port 8000
ACTIVE_MODEL_PROFILE=llama-cpp-default uvicorn src.api.main:create_app --factory --host 0.0.0.0 --port 8000
```

In another shell, check health:

```bash
curl http://localhost:8000/health
```

## 4) Run the CLI in HTTP mode (default)

```bash
git diff main...HEAD | ai-review review --server-url http://localhost:8000
```

Other supported HTTP routes:

```bash
git diff main...HEAD | ai-review test-check --server-url http://localhost:8000 --json
git diff main...HEAD | ai-review test-scenarios --server-url http://localhost:8000 --json
```

## 5) Run in local development mode

```bash
git diff main...HEAD | ai-review review --transport local --json
```

Use `--transport local` only for local development/debugging.
