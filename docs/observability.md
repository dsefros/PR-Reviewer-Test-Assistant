# Observability

## Runtime signals

- container logs and stdout
- /health
- /ready

## Product artifacts

- logs/traces.jsonl
- logs/results.jsonl

## What to inspect first

1. /ready
2. API container logs
3. Ollama host availability
4. JSONL output paths and permissions

## Readiness coverage

- model config
- active profile
- prompt readability
- persistence writability
- backend connectivity
