# CLI

## Main command

ai-review

## Modes

- review
- test-check
- test-scenarios
- test-gen
- test-maintain

## Common usage

git diff main...HEAD | ai-review review --server-url http://localhost:8000
git diff main...HEAD | ai-review test-check --server-url http://localhost:8000 --json
git diff main...HEAD | ai-review test-scenarios --server-url http://localhost:8000 --json

## Local transport

git diff main...HEAD | ai-review review --transport local --json

## Inputs

- diff from stdin
- diff from file
- optional metadata/context/existing tests
