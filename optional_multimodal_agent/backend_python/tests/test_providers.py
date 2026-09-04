from app.providers.factory import SUPPORTED_PROVIDERS, get_provider, provider_status


def test_only_real_providers_are_exposed() -> None:
    assert SUPPORTED_PROVIDERS == ("openai", "gemini", "ollama")
    assert "mock" not in {item["provider"] for item in provider_status()}


def test_mock_provider_is_rejected() -> None:
    try:
        get_provider("mock")
        assert False, "mock Provider를 허용하면 안 됩니다."
    except ValueError as error:
        assert "지원하지 않는 Provider" in str(error)
