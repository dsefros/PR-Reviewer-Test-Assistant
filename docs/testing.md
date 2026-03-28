# Testing

## Main test areas

- API tests
- CLI tests
- model config tests
- readiness behavior
- mode output validation

## Minimum checks before merge

pytest -q
curl -sS http://127.0.0.1:8000/health
curl -sS http://127.0.0.1:8000/ready

## Deployment smoke

- API starts
- readiness is green
- one review request succeeds
- JSONL files are written
