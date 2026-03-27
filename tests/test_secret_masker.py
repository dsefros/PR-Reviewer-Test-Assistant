from src.application.services.secret_masker import mask_secrets


def test_mask_api_key_and_password():
    raw = "API_KEY=abc123\npassword: supersecret"
    masked, redactions = mask_secrets(raw)
    assert "abc123" not in masked
    assert "supersecret" not in masked
    assert redactions >= 2
