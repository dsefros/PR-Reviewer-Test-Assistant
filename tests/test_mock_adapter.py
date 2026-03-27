from src.config.models import MockModelProfile
from src.infrastructure.llm.adapter import LLMAdapter


def test_mock_adapter_returns_json():
    profile = MockModelProfile(name="mock-default", backend="mock", model_name="mock-v1")
    adapter = LLMAdapter(profile=profile, mode="review")
    payload = adapter.generate_json("hello")
    assert "summary" in payload
    adapter.close()
