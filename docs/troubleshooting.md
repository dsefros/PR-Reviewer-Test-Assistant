# Troubleshooting

## API is up but /ready is false

Check:
- models.yaml path
- prompt templates path
- logs path
- Ollama connectivity
- active model profile

Command:
curl -sS http://127.0.0.1:8000/ready

## Ollama connectivity failed: No address associated with hostname

Cause:
- host.docker.internal is not resolvable in container

Fix:
- use extra_hosts with host-gateway in docker-compose

## Ollama connectivity failed: Connection refused

Cause:
- Ollama listens only on 127.0.0.1

Fix:
- set OLLAMA_HOST=0.0.0.0:11434 in systemd override
- restart ollama

Commands:
ss -ltnp | grep 11434 || true
curl -sS http://127.0.0.1:11434/api/version

## Port 8000 already in use

Find process:
ss -ltnp | grep :8000 || true

Stop local uvicorn:
pkill -f 'uvicorn src.api.main:create_app' || true

## Logs are not written

Check:
- logs directory exists
- mount path is correct
- permissions are correct

Commands:
ls -la logs
tail -n 5 logs/traces.jsonl
tail -n 5 logs/results.jsonl

## Wrong model profile is active

Check:
grep -n "ACTIVE_MODEL_PROFILE" .env

Verify:
python - <<'PY'
from src.config.models import load_model_config, clear_model_config_cache
clear_model_config_cache()
_, profile = load_model_config()
print(profile.name, profile.backend)
PY
