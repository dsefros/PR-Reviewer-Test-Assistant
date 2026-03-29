#!/usr/bin/env bash
set -euo pipefail

IMAGE_REPO="ghcr.io/dsefros/pr-reviewer-test-assistant"
IMAGE_TAG="${1:-prod-latest}"
COMPOSE_FILE="docker-compose.prod.yml"
SERVICE_NAME="api"
BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "[error] $COMPOSE_FILE not found. Run from repository root on the prod host." >&2
  exit 1
fi

echo "[step] Pulling ${IMAGE_REPO}:${IMAGE_TAG}"
docker pull "${IMAGE_REPO}:${IMAGE_TAG}"

echo "[step] Restarting service ${SERVICE_NAME} via compose"
IMAGE_TAG="$IMAGE_TAG" docker compose -f "$COMPOSE_FILE" up -d "$SERVICE_NAME"

for endpoint in /health /ready; do
  echo "[step] Verifying ${BASE_URL}${endpoint}"
  for attempt in $(seq 1 30); do
    response="$(curl -fsS "${BASE_URL}${endpoint}")" || true
    if [[ "$endpoint" == "/ready" ]]; then
      if python -c 'import json,sys; payload=json.loads(sys.stdin.read()); raise SystemExit(0 if payload.get("ready") is True else 1)' <<<"$response"; then
        echo "[ok] ${endpoint} check passed (ready=true)"
        break
      fi
    else
      if [[ -n "$response" ]]; then
        echo "[ok] ${endpoint} check passed"
        break
      fi
    fi
    if [[ "$attempt" -eq 30 ]]; then
      echo "[error] ${endpoint} did not become healthy after restart" >&2
      exit 1
    fi
    sleep 2
  done
done

echo "[done] Production deploy successful (${IMAGE_TAG})."
