from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries

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
    DOMAIN,
    LOG_LEVELS,
    QIANFAN_EDITIONS,
    SEARCH_PROVIDERS,
)
from .websocket_transport import validate_xiaozhi_ws_endpoint


def _schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    values = {**DEFAULTS, **(defaults or {})}
    return vol.Schema(
        {
            vol.Required(CONF_XIAOZHI_WS_ENDPOINT, default=values.get(CONF_XIAOZHI_WS_ENDPOINT, "")): str,
            vol.Optional(
                CONF_XIAOZHI_WS_RECONNECT_SECONDS,
                default=values.get(CONF_XIAOZHI_WS_RECONNECT_SECONDS, 10),
            ): int,
            vol.Optional(
                CONF_XIAOZHI_WS_HEARTBEAT_SECONDS,
                default=values.get(CONF_XIAOZHI_WS_HEARTBEAT_SECONDS, 50),
            ): int,
            vol.Required(CONF_SEARCH_PROVIDER, default=values.get(CONF_SEARCH_PROVIDER, "mock")): vol.In(
                SEARCH_PROVIDERS
            ),
            vol.Optional(CONF_BOCHA_API_KEY, default=values.get(CONF_BOCHA_API_KEY, "")): str,
            vol.Optional(CONF_BOCHA_BASE_URL, default=values.get(CONF_BOCHA_BASE_URL)): str,
            vol.Optional(CONF_BAIDU_QIANFAN_API_KEY, default=values.get(CONF_BAIDU_QIANFAN_API_KEY, "")): str,
            vol.Optional(CONF_BAIDU_QIANFAN_BASE_URL, default=values.get(CONF_BAIDU_QIANFAN_BASE_URL)): str,
            vol.Optional(
                CONF_BAIDU_QIANFAN_EDITION,
                default=values.get(CONF_BAIDU_QIANFAN_EDITION, "lite"),
            ): vol.In(QIANFAN_EDITIONS),
            vol.Optional(CONF_SEARXNG_BASE_URL, default=values.get(CONF_SEARXNG_BASE_URL, "")): str,
            vol.Optional(CONF_BRAVE_API_KEY, default=values.get(CONF_BRAVE_API_KEY, "")): str,
            vol.Optional(CONF_MAX_SEARCH_RESULTS, default=values.get(CONF_MAX_SEARCH_RESULTS, 5)): int,
            vol.Optional(CONF_FETCH_TIMEOUT_SECONDS, default=values.get(CONF_FETCH_TIMEOUT_SECONDS, 10)): int,
            vol.Optional(CONF_MAX_FETCH_CHARS, default=values.get(CONF_MAX_FETCH_CHARS, 12000)): int,
            vol.Optional(CONF_SAFE_MODE, default=values.get(CONF_SAFE_MODE, True)): bool,
            vol.Optional(CONF_LOG_LEVEL, default=values.get(CONF_LOG_LEVEL, "info")): vol.In(LOG_LEVELS),
            vol.Optional(CONF_ENABLE_HA_TOOLS, default=values.get(CONF_ENABLE_HA_TOOLS, False)): bool,
            vol.Optional(CONF_HA_LLM_API, default=values.get(CONF_HA_LLM_API, "assist")): str,
            vol.Optional(CONF_HA_ASSISTANT, default=values.get(CONF_HA_ASSISTANT, "conversation")): str,
        }
    )


class XiaozhiMcpWebSearchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                validate_xiaozhi_ws_endpoint(user_input[CONF_XIAOZHI_WS_ENDPOINT])
            except ValueError:
                errors["base"] = "invalid_ws_endpoint"
            else:
                await self.async_set_unique_id("xiaozhi_mcp_websearch")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Xiaozhi MCP WebSearch",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_schema(user_input),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return XiaozhiMcpWebSearchOptionsFlow(config_entry)


class XiaozhiMcpWebSearchOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        current = {**self._config_entry.data, **self._config_entry.options}
        if user_input is not None:
            try:
                validate_xiaozhi_ws_endpoint(user_input[CONF_XIAOZHI_WS_ENDPOINT])
            except ValueError:
                errors["base"] = "invalid_ws_endpoint"
            else:
                return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=_schema(current),
            errors=errors,
        )
