# Architecture

## Layers

### Interface layer
- src/api/main.py
- src/cli/main.py

### Application layer
- AnalysisOrchestrator
- mode registry

### Domain layer
- schemas
- test requirement rule
- output formatters

### Infrastructure layer
- prompt rendering
- LLM adapter/backends
- JSONL repositories
- runtime settings and model profiles

## Runtime topology

- API in Docker
- Ollama on host
- JSONL persistence in mounted storage

## Core flow

1. Request enters API or CLI
2. Diff is preprocessed
3. Prompt is rendered
4. LLM backend is called
5. Output is validated and normalized
6. Trace and result are persisted
