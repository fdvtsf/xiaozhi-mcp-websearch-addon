from __future__ import annotations

import asyncio
import contextlib
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
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
    runtime = {
        "settings": settings,
        "stop_event": stop_event,
        "task": None,
        "unsub_start": None,
    }
    hass.data[DOMAIN][entry.entry_id] = runtime

    async def _async_start(_event=None) -> None:
        if stop_event.is_set() or runtime["task"] is not None:
            return
        runtime["unsub_start"] = None
        _LOGGER.info("Home Assistant startup complete; starting Xiaozhi MCP connection")
        runtime["task"] = hass.async_create_task(async_run_forever(hass, settings, stop_event))

    if hass.is_running:
        await _async_start()
    else:
        runtime["unsub_start"] = hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _async_start)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    runtime = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if runtime is None:
        return True

    if runtime["unsub_start"] is not None:
        runtime["unsub_start"]()
    runtime["stop_event"].set()
    if runtime["task"] is not None:
        runtime["task"].cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await runtime["task"]
    return True
