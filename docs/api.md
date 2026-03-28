# API

## Health endpoints

- GET /health
- GET /ready

## Main analysis routes

- POST /api/v1/analyze/review
- POST /api/v1/analyze/test-check
- POST /api/v1/analyze/test-scenarios

## Legacy routes

- POST /review
- POST /test-check
- POST /test-scenarios
- POST /test-gen
- POST /test-maintain

## Request body

AnalysisRequest fields:
- diff
- metadata
- context
- existing_tests

## Response behavior

Responses are validated and normalized against mode-specific schemas.
