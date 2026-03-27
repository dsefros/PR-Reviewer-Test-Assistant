from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


Mode = Literal["review", "test-check", "test-scenarios", "test-gen", "test-maintain"]
Severity = Literal["high", "medium", "low"]
IssueCategory = Literal[
    "bug",
    "design",
    "maintainability",
    "error_handling",
    "regression_risk",
    "testing",
]


class AnalysisRequest(BaseModel):
    diff: str
    metadata: dict[str, Any] | None = None
    context: dict[str, Any] | None = None
    existing_tests: dict[str, Any] | None = None


class ReviewIssue(BaseModel):
    severity: Severity
    category: IssueCategory
    title: str
    details: str
    file: str
    lines: str
    recommendation: str


class ReviewResponse(BaseModel):
    summary: str
    strengths: list[str] = Field(default_factory=list)
    issues: list[ReviewIssue] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class TestCheckResponse(BaseModel):
    test_required: bool
    why: list[str] = Field(default_factory=list)
    missing_scenarios: list[str] = Field(default_factory=list)
    priority: Severity
    limitations: list[str] = Field(default_factory=list)


class TestScenariosResponse(BaseModel):
    happy_path: list[str] = Field(default_factory=list)
    negative: list[str] = Field(default_factory=list)
    edge_cases: list[str] = Field(default_factory=list)
    regression: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class TestGenResponse(BaseModel):
    generated_tests: str
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class TestMaintainResponse(BaseModel):
    tests_to_review: list[str] = Field(default_factory=list)
    assertions_to_update: list[str] = Field(default_factory=list)
    mocks_to_update: list[str] = Field(default_factory=list)
    priority_files: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
