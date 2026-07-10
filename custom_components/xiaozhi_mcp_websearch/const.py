DOMAIN = "xiaozhi_mcp_websearch"
NAME = "Xiaozhi MCP WebSearch"
VERSION = "0.3.0"

CONF_XIAOZHI_WS_ENDPOINT = "xiaozhi_ws_endpoint"
CONF_XIAOZHI_WS_RECONNECT_SECONDS = "xiaozhi_ws_reconnect_seconds"
CONF_XIAOZHI_WS_HEARTBEAT_SECONDS = "xiaozhi_ws_heartbeat_seconds"
CONF_SEARCH_PROVIDER = "search_provider"
CONF_BOCHA_API_KEY = "bocha_api_key"
CONF_BOCHA_BASE_URL = "bocha_base_url"
CONF_BAIDU_QIANFAN_API_KEY = "baidu_qianfan_api_key"
CONF_BAIDU_QIANFAN_BASE_URL = "baidu_qianfan_base_url"
CONF_BAIDU_QIANFAN_EDITION = "baidu_qianfan_edition"
CONF_SEARXNG_BASE_URL = "searxng_base_url"
CONF_BRAVE_API_KEY = "brave_api_key"
CONF_MAX_SEARCH_RESULTS = "max_search_results"
CONF_FETCH_TIMEOUT_SECONDS = "fetch_timeout_seconds"
CONF_MAX_FETCH_CHARS = "max_fetch_chars"
CONF_SAFE_MODE = "safe_mode"
CONF_LOG_LEVEL = "log_level"
CONF_ENABLE_HA_TOOLS = "enable_ha_tools"
CONF_HA_LLM_API = "ha_llm_api"
CONF_HA_ASSISTANT = "ha_assistant"

SEARCH_PROVIDERS = ["mock", "bocha", "baidu_qianfan", "searxng", "brave"]
QIANFAN_EDITIONS = ["lite", "standard"]
LOG_LEVELS = ["debug", "info", "warning", "error"]

DEFAULTS = {
    CONF_XIAOZHI_WS_RECONNECT_SECONDS: 10,
    CONF_XIAOZHI_WS_HEARTBEAT_SECONDS: 50,
    CONF_SEARCH_PROVIDER: "mock",
    CONF_BOCHA_BASE_URL: "https://api.bochaai.com/v1/web-search",
    CONF_BAIDU_QIANFAN_BASE_URL: "https://qianfan.baidubce.com/v2/ai_search/web_search",
    CONF_BAIDU_QIANFAN_EDITION: "lite",
    CONF_MAX_SEARCH_RESULTS: 5,
    CONF_FETCH_TIMEOUT_SECONDS: 10,
    CONF_MAX_FETCH_CHARS: 12000,
    CONF_SAFE_MODE: True,
    CONF_LOG_LEVEL: "info",
    CONF_ENABLE_HA_TOOLS: False,
    CONF_HA_LLM_API: "assist",
    CONF_HA_ASSISTANT: "conversation",
}
