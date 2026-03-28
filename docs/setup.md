# Setup

## Local setup

python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
uvicorn src.api.main:create_app --factory --host 0.0.0.0 --port 8000

## Docker setup

docker compose up --build -d
curl -sS http://127.0.0.1:8000/health
curl -sS http://127.0.0.1:8000/ready

## Registry-based setup

Use docker-compose.registry.yml to run from a prebuilt image in GHCR.

## Server deployment baseline

- Ollama runs on the host
- Ollama listens on 0.0.0.0:11434
- API container uses host.docker.internal with host-gateway
