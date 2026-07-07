import pytest

from app.xiaozhi_ws import validate_xiaozhi_ws_endpoint


def test_validate_xiaozhi_ws_endpoint_accepts_ws_urls():
    assert validate_xiaozhi_ws_endpoint("wss://example.com/mcp") == "wss://example.com/mcp"


@pytest.mark.parametrize("endpoint", ["", "http://example.com/mcp", "wss:///missing-host"])
def test_validate_xiaozhi_ws_endpoint_rejects_invalid_urls(endpoint):
    with pytest.raises(ValueError):
        validate_xiaozhi_ws_endpoint(endpoint)
