# Developer Workflow

## Branch model

- main — integration / dev
- prod — production (not used yet)
- feature branches — from main

---

## 1. Start feature

git checkout main
git pull --ff-only origin main
git checkout -b feat/<name>

---

## 2. Development

- implement changes
- run locally if needed

---

## 3. Mandatory pre-merge check

Run:

bash scripts/checks/pre_merge_checklist.sh

Includes:
- pytest (hermetic)
- docker build
- container run
- /health
- /ready (ready=true)
- CLI smoke test
- HTTP API smoke test

Do NOT merge if this fails.

---

## 4. Create PR → main

- push branch
- open PR
- review changes

---

## 5. Merge to main

After merge:

GitHub Actions:
- builds image
- pushes:
  - dev-latest
  - dev-<sha>

---

## 6. Verify CI

gh run list --limit 5

Ensure latest run on main = success.

---

## 7. Update local dev

bash scripts/dev/redeploy_dev_local.sh

---

## 8. Smoke test (local dev)

printf '%s\n' '+ return 1;' > /tmp/check.diff

ai-review review \
  --server-url http://127.0.0.1:8000 \
  --diff /tmp/check.diff \
  --json

curl -sS http://127.0.0.1:8000/api/v1/analyze/review \
  -H 'content-type: application/json' \
  -d '{"diff":"+ return 1;","metadata":{},"context":{},"existing_tests":{}}'

---

## 9. Production (future)

Flow (planned):

main → PR → prod → auto-deploy → verify → rollback if needed

Scripts:
- scripts/prod/deploy_prod.sh
- scripts/prod/rollback_prod.sh

---

## Notes

- Tests are hermetic (mock profile enforced)
- dev-latest exists only after successful main workflow
- /ready must return {"ready": true}
- Do not rely on local .env for test behavior
