# Known Issues

## Current known limitations

- Model quality depends heavily on selected Ollama profile
- Small models may fail to follow strict JSON schemas on real diffs
- Review quality must be validated separately from deployment correctness

## Operational caveats

- API container depends on Ollama availability on host
- Incorrect OLLAMA_BASE_URL_OVERRIDE breaks readiness
- Prompt and model profile alignment materially affects output quality
