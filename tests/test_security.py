import pytest

from app.config import Settings
from app.security import is_url_allowed, sanitize_log_value


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:8123",
        "http://192.168.1.1",
    ],
)
def test_private_urls_are_rejected(url):
    assert is_url_allowed(url, safe_mode=True) is False


@pytest.mark.parametrize("url", ["file:///etc/passwd", ""])
def test_invalid_urls_raise(url):
    with pytest.raises(ValueError):
        is_url_allowed(url, safe_mode=True)


def test_api_key_not_in_safe_summary_or_log_value():
    settings = Settings(
        search_provider="bocha",
        bocha_api_key="bocha-secret-value",
        baidu_qianfan_api_key="qianfan-secret-value",
        brave_api_key="brave-secret-value",
    )
    summary = str(settings.safe_summary())
    assert "bocha-secret-value" not in summary
    assert "qianfan-secret-value" not in summary
    assert "brave-secret-value" not in summary

    message = sanitize_log_value("brave_api_key=brave-secret-value")
    assert "brave-secret-value" not in message
    assert "***" in message

    bearer = sanitize_log_value("X-Appbuilder-Authorization: Bearer qianfan-secret-value")
    assert "qianfan-secret-value" not in bearer
    assert "***" in bearer

    endpoint = sanitize_log_value("wss://example.com/mcp?token=xiaozhi-secret-value")
    assert "xiaozhi-secret-value" not in endpoint
