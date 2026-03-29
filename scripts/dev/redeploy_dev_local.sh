#!/usr/bin/env bash
set -euo pipefail

IMAGE="ghcr.io/dsefros/pr-reviewer-test-assistant:dev-latest"
CONTAINER_NAME="pr-reviewer-dev"
HOST_PORT="8000"
CONTAINER_PORT="8000"

wait_for_health() {
  local endpoint="$1"
  local max_attempts="${2:-30}"
  local attempt=1

  while [[ "$attempt" -le "$max_attempts" ]]; do
    if curl -fsS "$endpoint" >/dev/null 2>&1; then
      echo "[ok] Endpoint is healthy: $endpoint"
      return 0
    fi
    echo "[wait] $endpoint not ready yet (attempt $attempt/$max_attempts)"
    sleep 2
    attempt=$((attempt + 1))
  done

  echo "[error] Endpoint did not become healthy in time: $endpoint" >&2
  return 1
}

wait_for_ready_true() {
  local endpoint="$1"
  local max_attempts="${2:-30}"
  local attempt=1

  while [[ "$attempt" -le "$max_attempts" ]]; do
    local response
    response="$(curl -fsS "$endpoint")" || true
    if python -c 'import json,sys; payload=json.loads(sys.stdin.read()); raise SystemExit(0 if payload.get("ready") is True else 1)' <<<"$response"; then
      echo "[ok] Endpoint is ready=true: $endpoint"
      return 0
    fi
    echo "[wait] $endpoint ready=false/not-valid yet (attempt $attempt/$max_attempts)"
    sleep 2
    attempt=$((attempt + 1))
  done

  echo "[error] Endpoint did not report ready=true in time: $endpoint" >&2
  return 1
}

if [[ ! -f .env ]]; then
  echo "[error] .env file not found in repository root. Create it before redeploying." >&2
  exit 1
fi

if [[ ! -f models.yaml ]]; then
  echo "[error] models.yaml is required for runtime and was not found." >&2
  exit 1
fi

if [[ ! -d src/infrastructure/prompts/templates ]]; then
  echo "[error] Prompt templates directory not found at src/infrastructure/prompts/templates." >&2
  exit 1
fi

mkdir -p logs

echo "[step] Pulling image: $IMAGE"
docker pull "$IMAGE"

if docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
  echo "[step] Removing existing container: $CONTAINER_NAME"
  docker rm -f "$CONTAINER_NAME"
fi

echo "[step] Starting fresh local dev container"
docker run -d \
  --name "$CONTAINER_NAME" \
  --env-file .env \
  -e RUNTIME_ROOT=/app \
  -e MODELS_CONFIG_PATH=/app/runtime/models.yaml \
  -e PROMPT_TEMPLATES_PATH=/app/runtime/prompts \
  -e LOGS_DIR=/app/runtime/logs \
  -e TRACES_JSONL_PATH=/app/runtime/logs/traces.jsonl \
  -e RESULTS_JSONL_PATH=/app/runtime/logs/results.jsonl \
  --add-host host.docker.internal:host-gateway \
  -p "${HOST_PORT}:${CONTAINER_PORT}" \
  -v "$(pwd)/models.yaml:/app/runtime/models.yaml:ro" \
  -v "$(pwd)/src/infrastructure/prompts/templates:/app/runtime/prompts:ro" \
  -v "$(pwd)/logs:/app/runtime/logs" \
  "$IMAGE"

wait_for_health "http://127.0.0.1:${HOST_PORT}/health"
wait_for_ready_true "http://127.0.0.1:${HOST_PORT}/ready"

echo "[done] Local dev redeploy finished successfully."
