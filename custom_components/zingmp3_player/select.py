"""Select entities for Zing MP3 Player integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .media_player import ZingMP3PlayerEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zing MP3 Player select entities from a config entry."""
    dropdowns = entry.data.get("dropdowns", [])
    if not dropdowns:
        return
        
    # Find the media player entity
    for entity in hass.data[DOMAIN].values():
        if isinstance(entity, ZingMP3PlayerEntity):
            entities = []
            if "speakers" in dropdowns:
                entities.append(ZingMP3SpeakerSelect(entity))
            if "playmode" in dropdowns:
                entities.append(ZingMP3PlayModeSelect(entity))
            if "repeatmode" in dropdowns:
                entities.append(ZingMP3RepeatModeSelect(entity))
            async_add_entities(entities)
            break


class ZingMP3SpeakerSelect(SelectEntity):
    """Select entity for speakers."""

    def __init__(self, player: ZingMP3PlayerEntity) -> None:
        """Initialize the select."""
        self._player = player
        self._attr_name = f"{player.name} Speaker"
        self._attr_unique_id = f"{player.unique_id}_speakers"
        self._attr_icon = "mdi:speaker"

    @property
    def current_option(self) -> str | None:
        """Return the current selected speaker."""
        return self._player.source

    @property
    def options(self) -> list[str]:
        """Return the list of available speakers."""
        return self._player.source_list

    async def async_select_option(self, option: str) -> None:
        """Select a speaker."""
        await self._player.async_select_source(option)
        self.async_write_ha_state()


class ZingMP3PlayModeSelect(SelectEntity):
    """Select entity for play mode."""

    def __init__(self, player: ZingMP3PlayerEntity) -> None:
        """Initialize the select."""
        self._player = player
        self._attr_name = f"{player.name} Play Mode"
        self._attr_unique_id = f"{player.unique_id}_playmode"
        self._attr_icon = "mdi:play-speed"
        self._attr_options = ["Normal", "Shuffle"]

    @property
    def current_option(self) -> str | None:
        """Return the current play mode."""
        return "Shuffle" if self._player.shuffle else "Normal"

    async def async_select_option(self, option: str) -> None:
        """Select play mode."""
        await self._player.async_set_shuffle(option == "Shuffle")
        self.async_write_ha_state()


class ZingMP3RepeatModeSelect(SelectEntity):
    """Select entity for repeat mode."""

    def __init__(self, player: ZingMP3PlayerEntity) -> None:
        """Initialize the select."""
        self._player = player
        self._attr_name = f"{player.name} Repeat Mode"
        self._attr_unique_id = f"{player.unique_id}_repeatmode"
        self._attr_icon = "mdi:repeat"
        self._attr_options = ["Off", "One", "All"]

    @property
    def current_option(self) -> str | None:
        """Return the current repeat mode."""
        return self._player.repeat.value.capitalize()

    async def async_select_option(self, option: str) -> None:
        """Select repeat mode."""
        from homeassistant.components.media_player import RepeatMode
        mode_map = {
            "Off": RepeatMode.OFF,
            "One": RepeatMode.ONE,
            "All": RepeatMode.ALL,
        }
        await self._player.async_set_repeat(mode_map[option])
        self.async_write_ha_state()
