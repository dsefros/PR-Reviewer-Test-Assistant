# Runbook

## 1. Install base packages

sudo apt update
sudo apt install -y git curl docker.io docker-compose-plugin

sudo systemctl enable docker
sudo systemctl start docker

## 2. Install Ollama

curl -fsSL https://ollama.com/install.sh | sh

## 3. Make Ollama reachable from Docker containers

sudo mkdir -p /etc/systemd/system/ollama.service.d

sudo tee /etc/systemd/system/ollama.service.d/override.conf >/dev/null <<'EOT'
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOT

sudo systemctl daemon-reload
sudo systemctl restart ollama

## 4. Verify Ollama

ss -ltnp | grep 11434 || true
curl -sS http://127.0.0.1:11434/api/version

## 5. Pull required model

ollama pull qwen2.5-coder:7b
ollama list

## 6. Login to GHCR

echo 'YOUR_GHCR_TOKEN' | docker login ghcr.io -u dsefros --password-stdin

## 7. Clone project

cd ~
git clone https://github.com/dsefros/PR-Reviewer-Test-Assistant.git
cd PR-Reviewer-Test-Assistant

## 8. Prepare env

cp .env.example .env

sed -i 's|^ACTIVE_MODEL_PROFILE=.*|ACTIVE_MODEL_PROFILE=local-qwen25-coder-7b|' .env || true

grep -q '^OLLAMA_BASE_URL_OVERRIDE=' .env \
  && sed -i 's|^OLLAMA_BASE_URL_OVERRIDE=.*|OLLAMA_BASE_URL_OVERRIDE=http://host.docker.internal:11434|' .env \
  || echo 'OLLAMA_BASE_URL_OVERRIDE=http://host.docker.internal:11434' >> .env

mkdir -p logs

## 9. Start service from registry

docker compose -f docker-compose.registry.yml up -d

## 10. Verify service

docker compose -f docker-compose.registry.yml ps
docker compose -f docker-compose.registry.yml logs --tail=100 api

curl -sS http://127.0.0.1:8000/health
echo
curl -sS http://127.0.0.1:8000/ready

## 11. Smoke test

printf '%s\n' '+ return 1;' > /tmp/check.diff
ai-review review --server-url http://127.0.0.1:8000 --diff /tmp/check.diff --json

## 12. Update service later

cd ~/PR-Reviewer-Test-Assistant
git pull --ff-only origin main
docker compose -f docker-compose.registry.yml pull
docker compose -f docker-compose.registry.yml up -d

## 13. Mandatory pre-merge checks (local dev)

Run from repository root before merging to `main`:

```bash
bash scripts/checks/pre_merge_checklist.sh
```

## 14. Laptop dev redeploy from GHCR dev image

```bash
bash scripts/dev/redeploy_dev_local.sh
```

`dev-latest` exists only after a successful workflow run on `main`; run at least one `main` push first.

## 15. Prod deploy and rollback on server

Deploy latest prod tag:

```bash
bash scripts/prod/deploy_prod.sh prod-<sha-from-prod-build>
```

Rollback to a specific immutable prod image tag:

```bash
bash scripts/prod/rollback_prod.sh prod-<sha>
```

