#!/usr/bin/env bash
set -euo pipefail

IMAGE_TAG="pr-reviewer-local-check"
CONTAINER_NAME="pr-reviewer-local-check"
PORT="18000"

cleanup() {
  docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
}
trap cleanup EXIT

[[ -f .env ]] || { echo "[error] Missing .env in repo root." >&2; exit 1; }
[[ -f models.yaml ]] || { echo "[error] Missing models.yaml in repo root." >&2; exit 1; }

mkdir -p logs

echo "[1/7] Unit tests"
pytest

echo "[2/7] Docker build"
docker build -t "$IMAGE_TAG" .

echo "[3/7] Start local container"
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
  -p "${PORT}:8000" \
  -v "$(pwd)/models.yaml:/app/runtime/models.yaml:ro" \
  -v "$(pwd)/src/infrastructure/prompts/templates:/app/runtime/prompts:ro" \
  -v "$(pwd)/logs:/app/runtime/logs" \
  "$IMAGE_TAG"

echo "[4/7] /health check"
for attempt in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
    break
  fi
  [[ "$attempt" -lt 30 ]] || { echo "[error] /health failed" >&2; exit 1; }
  sleep 2
done

echo "[5/7] /ready check (ready=true required)"
for attempt in $(seq 1 30); do
  response="$(curl -fsS "http://127.0.0.1:${PORT}/ready")" || true
  if python -c 'import json,sys; payload=json.loads(sys.stdin.read()); raise SystemExit(0 if payload.get("ready") is True else 1)' <<<"$response"; then
    break
  fi
  [[ "$attempt" -lt 30 ]] || { echo "[error] /ready failed (ready!=true)" >&2; exit 1; }
  sleep 2
done

echo "[6/7] CLI smoke test"
printf '%s\n' '+ return 1;' > /tmp/pre_merge_check.diff
if command -v ai-review >/dev/null 2>&1; then
  ai-review review --server-url "http://127.0.0.1:${PORT}" --diff /tmp/pre_merge_check.diff --json >/tmp/pre_merge_cli_output.json
else
  python -m src.cli.main review --server-url "http://127.0.0.1:${PORT}" --diff /tmp/pre_merge_check.diff --json >/tmp/pre_merge_cli_output.json
fi

echo "[7/7] HTTP API smoke test"
curl -fsS "http://127.0.0.1:${PORT}/api/v1/analyze/review" \
  -H 'content-type: application/json' \
  -d '{"diff":"+ return 1;","metadata":{},"context":{},"existing_tests":{}}' >/tmp/pre_merge_http_output.json

echo "[done] Mandatory pre-merge checklist completed successfully."
