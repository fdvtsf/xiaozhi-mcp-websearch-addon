from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .const import (
    CONF_BAIDU_QIANFAN_API_KEY,
    CONF_BAIDU_QIANFAN_BASE_URL,
    CONF_BAIDU_QIANFAN_EDITION,
    CONF_BOCHA_API_KEY,
    CONF_BOCHA_BASE_URL,
    CONF_BRAVE_API_KEY,
    CONF_ENABLE_HA_TOOLS,
    CONF_FETCH_TIMEOUT_SECONDS,
    CONF_HA_ASSISTANT,
    CONF_HA_LLM_API,
    CONF_LOG_LEVEL,
    CONF_MAX_FETCH_CHARS,
    CONF_MAX_SEARCH_RESULTS,
    CONF_SAFE_MODE,
    CONF_SEARCH_PROVIDER,
    CONF_SEARXNG_BASE_URL,
    CONF_XIAOZHI_WS_ENDPOINT,
    CONF_XIAOZHI_WS_HEARTBEAT_SECONDS,
    CONF_XIAOZHI_WS_RECONNECT_SECONDS,
    DEFAULTS,
)


@dataclass(slots=True)
class Settings:
    xiaozhi_ws_endpoint: str
    xiaozhi_ws_reconnect_seconds: int = 10
    xiaozhi_ws_heartbeat_seconds: int = 50
    search_provider: str = "mock"
    bocha_api_key: str = ""
    bocha_base_url: str = "https://api.bochaai.com/v1/web-search"
    baidu_qianfan_api_key: str = ""
    baidu_qianfan_base_url: str = "https://qianfan.baidubce.com/v2/ai_search/web_search"
    baidu_qianfan_edition: str = "lite"
    searxng_base_url: str = ""
    brave_api_key: str = ""
    max_search_results: int = 5
    fetch_timeout_seconds: int = 10
    max_fetch_chars: int = 12000
    safe_mode: bool = True
    log_level: str = "info"
    enable_ha_tools: bool = False
    ha_llm_api: str = "assist"
    ha_assistant: str = "conversation"

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "Settings":
        data = {**DEFAULTS, **config}
        return cls(
            xiaozhi_ws_endpoint=str(data.get(CONF_XIAOZHI_WS_ENDPOINT, "")).strip(),
            xiaozhi_ws_reconnect_seconds=int(data.get(CONF_XIAOZHI_WS_RECONNECT_SECONDS, 10)),
            xiaozhi_ws_heartbeat_seconds=int(data.get(CONF_XIAOZHI_WS_HEARTBEAT_SECONDS, 50)),
            search_provider=str(data.get(CONF_SEARCH_PROVIDER, "mock")).strip(),
            bocha_api_key=str(data.get(CONF_BOCHA_API_KEY, "")).strip(),
            bocha_base_url=str(data.get(CONF_BOCHA_BASE_URL, DEFAULTS[CONF_BOCHA_BASE_URL])).strip(),
            baidu_qianfan_api_key=str(data.get(CONF_BAIDU_QIANFAN_API_KEY, "")).strip(),
            baidu_qianfan_base_url=str(
                data.get(CONF_BAIDU_QIANFAN_BASE_URL, DEFAULTS[CONF_BAIDU_QIANFAN_BASE_URL])
            ).strip(),
            baidu_qianfan_edition=str(data.get(CONF_BAIDU_QIANFAN_EDITION, "lite")).strip(),
            searxng_base_url=str(data.get(CONF_SEARXNG_BASE_URL, "")).strip(),
            brave_api_key=str(data.get(CONF_BRAVE_API_KEY, "")).strip(),
            max_search_results=int(data.get(CONF_MAX_SEARCH_RESULTS, 5)),
            fetch_timeout_seconds=int(data.get(CONF_FETCH_TIMEOUT_SECONDS, 10)),
            max_fetch_chars=int(data.get(CONF_MAX_FETCH_CHARS, 12000)),
            safe_mode=bool(data.get(CONF_SAFE_MODE, True)),
            log_level=str(data.get(CONF_LOG_LEVEL, "info")).strip(),
            enable_ha_tools=bool(data.get(CONF_ENABLE_HA_TOOLS, False)),
            ha_llm_api=str(data.get(CONF_HA_LLM_API, "assist")).strip() or "assist",
            ha_assistant=str(data.get(CONF_HA_ASSISTANT, "conversation")).strip() or "conversation",
        )

    def safe_summary(self) -> dict[str, Any]:
        data = {
            "xiaozhi_ws_endpoint": "***" if self.xiaozhi_ws_endpoint else "",
            "xiaozhi_ws_reconnect_seconds": self.xiaozhi_ws_reconnect_seconds,
            "xiaozhi_ws_heartbeat_seconds": self.xiaozhi_ws_heartbeat_seconds,
            "search_provider": self.search_provider,
            "bocha_api_key": "***" if self.bocha_api_key else "",
            "bocha_base_url": self.bocha_base_url,
            "baidu_qianfan_api_key": "***" if self.baidu_qianfan_api_key else "",
            "baidu_qianfan_base_url": self.baidu_qianfan_base_url,
            "baidu_qianfan_edition": self.baidu_qianfan_edition,
            "searxng_base_url": self.searxng_base_url,
            "brave_api_key": "***" if self.brave_api_key else "",
            "max_search_results": self.max_search_results,
            "fetch_timeout_seconds": self.fetch_timeout_seconds,
            "max_fetch_chars": self.max_fetch_chars,
            "safe_mode": self.safe_mode,
            "log_level": self.log_level,
            "enable_ha_tools": self.enable_ha_tools,
            "ha_llm_api": self.ha_llm_api,
            "ha_assistant": self.ha_assistant,
        }
        return data
