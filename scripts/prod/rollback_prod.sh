#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 1 ]]; then
  echo "Usage: $0 prod-<shortsha>" >&2
  exit 1
fi

ROLLBACK_TAG="$1"
if [[ ! "$ROLLBACK_TAG" =~ ^prod-[a-f0-9]{7,40}$ ]]; then
  echo "[error] Invalid tag format: $ROLLBACK_TAG (expected prod-<sha>)" >&2
  exit 1
fi

IMAGE_REPO="ghcr.io/dsefros/pr-reviewer-test-assistant"
COMPOSE_FILE="docker-compose.prod.yml"
SERVICE_NAME="api"
BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "[error] $COMPOSE_FILE not found. Run from repository root on the prod host." >&2
  exit 1
fi

echo "[step] Pulling rollback image ${IMAGE_REPO}:${ROLLBACK_TAG}"
docker pull "${IMAGE_REPO}:${ROLLBACK_TAG}"

echo "[step] Restarting ${SERVICE_NAME} with ${ROLLBACK_TAG}"
IMAGE_TAG="$ROLLBACK_TAG" docker compose -f "$COMPOSE_FILE" up -d "$SERVICE_NAME"

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
      echo "[error] ${endpoint} failed after rollback" >&2
      exit 1
    fi
    sleep 2
  done
done

echo "[done] Rollback complete (${ROLLBACK_TAG})."
