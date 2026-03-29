# Branching, Release, Deploy, and Rollback Flow

## Branch policy

- `main` is the integration/dev branch.
- `prod` is the production branch.
- Feature branches must be created from `main` and merged back into `main` by PR.
- Promotion to production is done by PR from `main` -> `prod`.

## Mandatory local pre-merge checklist

Run this before opening/merging a feature PR into `main`:

```bash
bash scripts/checks/pre_merge_checklist.sh
```

Checklist steps performed by the script:

1. `pytest` unit test run.
2. Docker image build from current branch.
3. Local container startup.
4. `/health` verification.
5. `/ready` verification.
6. CLI smoke test against local container (`ai-review` when installed; module fallback otherwise).
7. HTTP API smoke test against local container.

The script fails fast with clear errors if any step fails.

## GitHub Actions behavior

Workflow file: `.github/workflows/docker.yml`

### Push to `main`

- Builds Docker image from `main`.
- Pushes to GHCR image:
  - `ghcr.io/dsefros/pr-reviewer-test-assistant:dev-latest`
  - `ghcr.io/dsefros/pr-reviewer-test-assistant:dev-<shortsha>`
- No remote deploy is performed.

### Push to `prod`

- Builds Docker image from `prod` (independent rebuild by design).
- Pushes to GHCR image:
  - `ghcr.io/dsefros/pr-reviewer-test-assistant:prod-latest`
  - `ghcr.io/dsefros/pr-reviewer-test-assistant:prod-<shortsha>`
- Executes automatic production deploy over SSH using the exact immutable tag from that run (`prod-<shortsha>`).

## Dev redeploy (developer laptop)

Use:

```bash
bash scripts/dev/redeploy_dev_local.sh
```

What it does:

- Pulls `dev-latest` from GHCR.
- Stops/removes existing local dev container if present.
- Starts new local container with `.env`.
- Preserves Ollama connectivity via `host.docker.internal` mapping.
- Verifies both `/health` and `/ready`.

## Production deploy assumptions

Production server is expected to:

- Host a clone of this repository.
- Use Docker Compose with `docker-compose.prod.yml`.
- Keep runtime files (`.env`, `models.yaml`, prompt templates, logs directory) available.

Default prod image in compose:

- `ghcr.io/dsefros/pr-reviewer-test-assistant:${IMAGE_TAG:-prod-latest}`

Server-side deploy command:

```bash
bash scripts/prod/deploy_prod.sh prod-<sha>
```

If no argument is passed, the script defaults to `prod-latest`.

Deploy script behavior:

1. Pull the requested prod tag.
2. Restart `api` service using compose.
3. Verify `/health`.
4. Verify `/ready` and require JSON field `ready=true`.
5. Exit non-zero on any failure.

## Rollback (first-class operation)

Rollback command on production server:

```bash
bash scripts/prod/rollback_prod.sh prod-<sha>
```

Rollback script behavior:

1. Pull specified `prod-<sha>` tag.
2. Restart `api` service using that tag.
3. Verify `/health`.
4. Verify `/ready` and require JSON field `ready=true`.
5. Exit non-zero on any failure.

## Required GitHub secrets for production auto-deploy

Configure these repository secrets:

- `CR_PAT` (GHCR push token)
- `SSH_HOST`
- `SSH_USER`
- `SSH_KEY`

`SSH_KEY` should be a private key allowed to SSH to the production host.
