from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .models import Settings


_LOGGER = logging.getLogger(__name__)


async def async_list_ha_tools(hass: HomeAssistant, settings: Settings, tool_type: Any) -> list[Any]:
    api = await _async_get_ha_llm_api(hass, settings)
    if api is None:
        return []

    tools: list[Any] = []
    for tool in getattr(api, "tools", []):
        try:
            name = _tool_name(tool)
            if not name:
                continue
            input_schema = _convert_tool_schema(tool)
            tools.append(
                tool_type(
                    name=name,
                    description=getattr(tool, "description", "") or name,
                    inputSchema=input_schema,
                )
            )
        except Exception as exc:  # pragma: no cover - defensive against HA API shape changes
            _LOGGER.warning("Failed to expose HA LLM tool %s: %s", getattr(tool, "name", "unknown"), exc)
    return tools


async def async_call_ha_tool(hass: HomeAssistant, name: str, arguments: dict[str, Any], settings: Settings) -> Any:
    api = await _async_get_ha_llm_api(hass, settings)
    if api is None:
        raise ValueError("Home Assistant tools are disabled")

    for tool in getattr(api, "tools", []):
        if _tool_name(tool) == name:
            return await _async_call_tool(api, tool, arguments)
    raise ValueError(f"unknown Home Assistant tool: {name}")


async def _async_get_ha_llm_api(hass: HomeAssistant, settings: Settings) -> Any | None:
    if not settings.enable_ha_tools:
        return None

    from homeassistant.helpers import llm

    api_id = settings.ha_llm_api or getattr(llm, "LLM_API_ASSIST", "assist")
    context = _create_llm_context(llm, settings)
    return await llm.async_get_api(hass, api_id, context)


def _create_llm_context(llm_module: Any, settings: Settings) -> Any:
    llm_context = getattr(llm_module, "LLMContext")
    kwargs = {
        "platform": DOMAIN,
        "context": None,
        "language": "zh-CN",
        "assistant": settings.ha_assistant or "conversation",
        "device_id": None,
    }
    try:
        return llm_context(**kwargs)
    except TypeError:
        kwargs.pop("device_id", None)
        try:
            return llm_context(**kwargs)
        except TypeError:
            kwargs.pop("assistant", None)
            return llm_context(**kwargs)


def _convert_tool_schema(tool: Any) -> dict[str, Any]:
    parameters = getattr(tool, "parameters", None)
    if parameters is None:
        return {"type": "object", "properties": {}}

    try:
        import voluptuous_openapi

        converted = voluptuous_openapi.convert(parameters)
        return converted if isinstance(converted, dict) else {"type": "object", "properties": {}}
    except Exception:
        return {"type": "object", "properties": {}}


async def _async_call_tool(api: Any, tool: Any, arguments: dict[str, Any]) -> Any:
    if hasattr(api, "async_call_tool"):
        try:
            from homeassistant.helpers import llm

            tool_input = llm.ToolInput(tool_name=_tool_name(tool), tool_args=arguments)
            return await api.async_call_tool(tool_input)
        except TypeError:
            return await api.async_call_tool(_tool_name(tool), arguments)

    if hasattr(tool, "async_call"):
        return await tool.async_call(arguments)
    raise ValueError(f"Home Assistant tool cannot be called: {_tool_name(tool)}")


def _tool_name(tool: Any) -> str:
    return str(getattr(tool, "name", "")).strip()
