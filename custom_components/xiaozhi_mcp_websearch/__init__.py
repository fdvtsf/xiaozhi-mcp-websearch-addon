from __future__ import annotations

import asyncio
import contextlib
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .models import Settings
from .security import sanitize_log_value
from .websocket_transport import async_run_forever


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    settings = Settings.from_config({**entry.data, **entry.options})
    _LOGGER.info("Starting Xiaozhi MCP WebSearch integration: %s", sanitize_log_value(settings.safe_summary()))

    stop_event = asyncio.Event()
    task = hass.async_create_task(async_run_forever(hass, settings, stop_event))
    hass.data[DOMAIN][entry.entry_id] = {
        "settings": settings,
        "stop_event": stop_event,
        "task": task,
    }

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    runtime = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if runtime is None:
        return True

    runtime["stop_event"].set()
    runtime["task"].cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await runtime["task"]
    return True

