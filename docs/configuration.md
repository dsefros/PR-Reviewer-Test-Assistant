# Configuration

## Main runtime settings

- API_HOST
- API_PORT
- RUNTIME_ROOT
- MODELS_CONFIG_PATH
- PROMPT_TEMPLATES_PATH
- LOGS_DIR
- TRACES_JSONL_PATH
- RESULTS_JSONL_PATH
- ACTIVE_MODEL_PROFILE
- OLLAMA_BASE_URL_OVERRIDE
- PERSISTENCE_ENABLED
- JSONL_FSYNC_ENABLED

## Configuration sources

- .env
- models.yaml

## Rules

- Runtime paths should be explicit in container deployments
- Active model profile should be set deliberately
- Ollama base URL must be correct for the deployment topology
