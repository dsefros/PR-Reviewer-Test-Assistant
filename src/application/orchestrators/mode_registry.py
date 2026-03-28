from __future__ import annotations

from src.domain.models.schemas import (
    ReviewResponse,
    TestCheckResponse,
    TestGenResponse,
    TestMaintainResponse,
    TestScenariosResponse,
)

MODE_REGISTRY = {
    "review": {"schema": ReviewResponse, "template": "review"},
    "test-check": {"schema": TestCheckResponse, "template": "test-check"},
    "test-scenarios": {"schema": TestScenariosResponse, "template": "test-scenarios"},
    "test-gen": {"schema": TestGenResponse, "template": "test-gen"},
    "test-maintain": {"schema": TestMaintainResponse, "template": "test-maintain"},
}
